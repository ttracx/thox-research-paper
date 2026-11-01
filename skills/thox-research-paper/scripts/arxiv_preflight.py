#!/usr/bin/env python3
"""Offline, non-destructive arXiv upload audit. Never logs in or publishes.

Python 3.10+. Static checks are deliberately not a TeX compiler, a complete
secret detector, a scientific review, or a substitute for arXiv PDF preview.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath

MAX_FILE_BYTES = 50 * 1024 * 1024  # Scanner safety bound, not an arXiv quota.
TEXT_TYPES = {'.tex', '.bib', '.bbl', '.sty', '.cls', '.bst', '.def', '.cfg', '.txt', '.md', '.json', '.yaml', '.yml', '.ini', '.toml', '.xml', '.csv'}
PRIVATE_TYPES = {'.pem', '.key', '.p12', '.pfx', '.sqlite', '.db', '.bak', '.swp'}
BUILD_TYPES = {'.aux', '.log', '.blg', '.out', '.toc', '.fls', '.fdb_latexmk'}
SECRET = re.compile(
    r'-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----|'
    r'(?i:(?:password|passwd|api[_-]?key|access[_-]?token|client[_-]?secret)[\x22\x27]?\s*[:=]\s*\S+)'
)
MANUAL_CHECKS = [
    'Verify the declared authoring format and include TeX source when applicable.',
    'Review every staged file, comments, hidden content and binary metadata for archival safety.',
    'Compile the exact staged source in an isolated environment and resolve missing files, citations and references.',
    'Review every page of the final PDF, including arXiv-generated output after upload.',
    'Verify authors, affiliations, metadata, rights, license, category and applicable AI disclosure.',
    'Verify authenticated account identity, eligibility, current limits and exact-artifact publication authority.',
    'Acknowledge archival permanence; withdrawal does not erase previous announced versions.',
]


def safe_name(name: str) -> bool:
    """Require portable relative names; reject hidden components and traversal."""
    if not isinstance(name, str) or not name or '\\' in name:
        return False
    p = PurePosixPath(name)
    return (not p.is_absolute() and str(p) == name and
            all(not x.startswith('.') and re.fullmatch(r'[A-Za-z0-9_+.,=-]+', x)
                for x in p.parts))


def audit(root: Path, source_format: str, main: str) -> dict:
    root = Path(root)
    errors, warnings, files, texts = [], [], {}, {}

    def issue(target, code, path='', line=None):
        item = {'code': code, 'path': path}
        if line is not None:
            item['line'] = line
        target.append(item)  # Never include source excerpts or credential values.

    if source_format not in {'tex', 'pdf-other'}:
        issue(errors, 'INVALID_SOURCE_FORMAT')
    if not safe_name(main):
        issue(errors, 'UNSAFE_MAIN_PATH')
    if root.is_symlink() or not root.is_dir():
        issue(errors, 'INVALID_STAGING_DIRECTORY')
    else:
        seen = set()
        for base, dirs, names in os.walk(root, followlinks=False,
                                        onerror=lambda _: issue(errors, 'DIRECTORY_READ_ERROR')):
            for d in sorted(dirs[:]):
                p = Path(base) / d
                rel = p.relative_to(root).as_posix()
                if p.is_symlink() or not safe_name(rel):
                    issue(errors, 'UNSAFE_DIRECTORY', rel)
                    dirs.remove(d)
            for name in sorted(names):
                p = Path(base) / name
                rel = p.relative_to(root).as_posix()
                if not safe_name(rel) or p.is_symlink() or not p.is_file():
                    issue(errors, 'UNSAFE_FILE', rel)
                    continue
                if rel.casefold() in seen:
                    issue(errors, 'CASE_COLLISION', rel)
                seen.add(rel.casefold())
                suffix = p.suffix.lower()
                if suffix in PRIVATE_TYPES or re.search(r'(?i)(credential|cookie|session|secret)', name):
                    issue(errors, 'PRIVATE_FILE', rel)
                    continue
                if suffix in BUILD_TYPES:
                    issue(errors, 'BUILD_ARTIFACT', rel)
                    continue
                try:
                    if p.stat().st_size > MAX_FILE_BYTES:
                        issue(errors, 'SCANNER_SIZE_LIMIT', rel)
                        continue
                    with p.open('rb') as stream:
                        data = stream.read(MAX_FILE_BYTES + 1)
                    if len(data) > MAX_FILE_BYTES:
                        issue(errors, 'SCANNER_SIZE_LIMIT', rel)
                        continue
                except OSError:
                    issue(errors, 'FILE_READ_ERROR', rel)
                    continue
                files[rel] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
                if suffix in TEXT_TYPES:
                    try:
                        text = data.decode('utf-8')
                    except UnicodeDecodeError:
                        issue(errors, 'UNSUPPORTED_TEXT_ENCODING', rel)
                        continue
                    texts[rel] = text
                    for n, line in enumerate(text.splitlines(), 1):
                        if SECRET.search(line):
                            issue(errors, 'POSSIBLE_SECRET', rel, n)
                        if suffix in {'.tex', '.sty', '.cls', '.bbl'}:
                            for match in re.finditer('%', line):
                                i = match.start()
                                slashes = len(line[:i]) - len(line[:i].rstrip('\\'))
                                if slashes % 2 == 0:
                                    if line[i+1:].strip():
                                        issue(warnings, 'TEX_COMMENT_REVIEW', rel, n)
                                    break
                    if re.search(r'\\(?:iffalse|todo|fixme)\b|\\begin\{comment\}', text):
                        issue(warnings, 'HIDDEN_OR_DRAFT_CONTENT_REVIEW', rel)
                    if re.search(r'\\(?:write18|immediate\s*\\write18)\b', text):
                        issue(errors, 'SHELL_ESCAPE_DIRECTIVE', rel)
                else:
                    issue(warnings, 'BINARY_OR_OTHER_FILE_REVIEW', rel)

    if main not in files:
        issue(errors, 'MISSING_MAIN_FILE', main)
    if source_format == 'tex' and (not main.endswith('.tex') or main not in texts):
        issue(errors, 'TEX_SOURCE_REQUIRED', main)
    if source_format == 'pdf-other':
        if not main.lower().endswith('.pdf'):
            issue(errors, 'PDF_MAIN_REQUIRED', main)
        if any(x.endswith('.tex') for x in files):
            issue(warnings, 'AUTHORING_FORMAT_REVIEW')

    # Literal includes only. Macro expansion and full dependency/citation resolution
    # are verified by an isolated compilation and the mandatory manual checklist.
    pattern = r'\\(input|include|includegraphics)\*?(?:\[[^\]]*\])?\s*\{([^}]+)\}'
    for rel, text in texts.items():
        if not rel.endswith('.tex'):
            continue
        if '\\graphicspath' in text:
            issue(warnings, 'GRAPHICSPATH_REQUIRES_COMPILE', rel)
        for command, target in re.findall(pattern, text):
            if not safe_name(target):
                issue(errors, 'UNRESOLVED_OR_UNSAFE_INCLUDE', rel)
                continue
            if command == 'includegraphics' and '\\graphicspath' in text:
                continue
            extensions = ['', '.pdf', '.png', '.jpg', '.jpeg', '.eps', '.ps'] if command == 'includegraphics' else ['', '.tex']
            candidates = {str(base / (target + ext)) for base in [PurePosixPath('.'), PurePosixPath(rel).parent] for ext in extensions}
            if not candidates.intersection(files):
                issue(errors, 'MISSING_INCLUDED_FILE', target)
        for group in re.findall(r'\\bibliography\{([^}]+)\}', text):
            for bib in group.split(','):
                bib = bib.strip()
                if not safe_name(bib):
                    issue(errors, 'UNSAFE_BIBLIOGRAPHY_PATH', rel)
                    continue
                bibfile = bib if bib.endswith('.bib') else bib + '.bib'
                candidates = {bibfile, str(PurePosixPath(rel).parent / bibfile), (str(PurePosixPath(main).with_suffix('.bbl')) if safe_name(main) else '')}
                if not candidates.intersection(files):
                    issue(errors, 'MISSING_BIBLIOGRAPHY', bib)
        for bib in re.findall(r'\\addbibresource(?:\[[^\]]*\])?\{([^}]+)\}', text):
            if not safe_name(bib):
                issue(errors, 'UNSAFE_BIBLIOGRAPHY_PATH', rel)
            elif not {bib, str(PurePosixPath(rel).parent / bib), (str(PurePosixPath(main).with_suffix('.bbl')) if safe_name(main) else '')}.intersection(files):
                issue(errors, 'MISSING_BIBLIOGRAPHY', bib)

    inventory = [{'path': p, **files[p]} for p in sorted(files)]
    digest = hashlib.sha256(json.dumps(inventory, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'schema_version': 1, 'static_checks_passed': not errors, 'publication_ready': False,
            'source_format': source_format, 'main': main, 'inventory_sha256': digest,
            'files': inventory, 'errors': errors, 'warnings': warnings,
            'manual_checks_required': MANUAL_CHECKS,
            'limitations': 'Heuristic static audit only. No compilation, full secret scan, authentication, upload or publication was performed.'}


def cli() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('staging', type=Path)
    p.add_argument('--source-format', required=True, choices=['tex', 'pdf-other'])
    p.add_argument('--main', required=True)
    args = p.parse_args()
    report = audit(args.staging, args.source_format, args.main)
    print(json.dumps(report, indent=2))
    return 0 if report['static_checks_passed'] else 2


if __name__ == '__main__':
    raise SystemExit(cli())
