#!/usr/bin/env python3
"""Emit public THOX authors or private research handoffs. No network or writes.

Structural checks do not establish scientific validity, consent, authentication,
remote persistence or publication readiness. Python 3.10+, standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROFILE = Path(__file__).resolve().parents[1] / 'references/publication-authors.json'
STAGES = ('intake', 'literature', 'outline', 'draft_and_audit', 'refine', 'validate', 'handoff')
MAX_CHECKPOINT_BYTES = 2 * 1024 * 1024
PUBLIC_FIELDS = ('id', 'name', 'given_name', 'family_name', 'position', 'position_short', 'affiliation', 'orcid', 'orcid_url')


def author_profile() -> dict[str, Any]:
    """Read the bundled public profile, never the operator account configuration."""
    obj = json.loads(PROFILE.read_text(encoding='utf-8'))
    if obj.get('schema_version') != 1 or not isinstance(obj.get('default_authors'), list):
        raise ValueError('INVALID_AUTHOR_PROFILE')
    required = {'craig-ross', 'tommy-xaypanya'}
    ids = [a.get('id') for a in obj['default_authors'] if isinstance(a, dict)]
    if len(ids) != len(obj['default_authors']) or len(ids) != len(set(ids)) or not required.issubset(ids):
        raise ValueError('INVALID_DEFAULT_AUTHORS')
    for author in obj['default_authors']:
        if any(not isinstance(author.get(k), str) or not author[k].strip()
               for k in ('id', 'name', 'given_name', 'family_name', 'position', 'affiliation')):
            raise ValueError('INVALID_AUTHOR_FIELDS')
        orcid = author.get('orcid')
        if orcid is not None and (not isinstance(orcid, str) or not re.fullmatch(r'\d{4}-\d{4}-\d{4}-\d{3}[\dX]', orcid)):
            raise ValueError('INVALID_ORCID_FORMAT')
        if author.get('orcid_url') != (f'https://orcid.org/{orcid}' if orcid else None):
            raise ValueError('ORCID_URL_MISMATCH')
    return obj


def publication_authors() -> list[dict[str, Any]]:
    """Allowlist only public publication fields to prevent account-data leakage."""
    return [{k: a.get(k) for k in PUBLIC_FIELDS} for a in author_profile()['default_authors']]


def tex_escape(text: str) -> str:
    replacements = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
                    '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
                    '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(replacements.get(c, c) for c in text)


def render_authors(format_name: str) -> str:
    authors = publication_authors()
    if format_name == 'json':
        return json.dumps({'authors': authors}, indent=2, ensure_ascii=False)
    if format_name == 'markdown':
        blocks = []
        for a in authors:
            block = f"**{a['name']}**\n{a['position']}, {a['affiliation']}"
            if a['orcid']:
                block += f"\nORCID: {a['orcid_url']}"
            blocks.append(block)
        return '\n\n'.join(blocks)
    if format_name == 'tex':
        # Article-class snippet only. The actual venue may require different macros.
        blocks = []
        for a in authors:
            lines = [tex_escape(a['name']), tex_escape(a['affiliation'])]
            if a['orcid']:
                lines.append('ORCID: '+tex_escape(a['orcid']))
            blocks.append(r'\\'.join(lines))
        return '\\author{' + '\n\\and\n'.join(blocks) + '}'
    raise ValueError('UNSUPPORTED_FORMAT')


def checkpoint(project_id: str, topic: str) -> dict[str, Any]:
    if not isinstance(project_id, str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,95}', project_id):
        raise ValueError('INVALID_PROJECT_ID')
    if not isinstance(topic, str) or not topic.strip() or len(topic) > 2000:
        raise ValueError('INVALID_TOPIC')
    profile = author_profile()
    return {
        'schema_version': 1,
        'project_id': project_id,
        'revision': 1,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'topic': topic.strip(),
        'stage': 'intake',
        'classification': 'private-draft',
        'author_profile_version': profile['profile_version'],
        'authors': publication_authors(),
        'source_refs': [], 'artifact_refs': [], 'claim_ledger': [], 'findings': [],
        'next_actions': ['Resolve current project evidence and research question',
                         'Discover authenticated Studio tools or retain a private handoff',
                         'Review relevant primary literature and establish an evaluation protocol'],
        'refinement': {'completed_cycles': 0, 'maximum_cycles_per_run': 5},
        'connection': {'status': 'STUDIO_NOT_CONNECTED', 'remote_project_id': None, 'receipt': None},
        'publication': {'ready': False, 'submitted': False, 'authorization_ref': None},
        'limitations': ['No experiments, independent reviews, remote saves or publications have been performed by this helper.']
    }


def validate_checkpoint(obj: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(obj, dict):
        return {'structurally_valid': False, 'publication_ready': False, 'errors': ['EXPECTED_OBJECT']}
    if type(obj.get('schema_version')) is not int or obj['schema_version'] != 1:
        errors.append('INVALID_SCHEMA_VERSION')
    pid = obj.get('project_id')
    if not isinstance(pid, str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,95}', pid):
        errors.append('INVALID_PROJECT_ID')
    if type(obj.get('revision')) is not int or obj['revision'] < 1:
        errors.append('INVALID_REVISION')
    topic = obj.get('topic')
    if not isinstance(topic, str) or not topic.strip() or len(topic) > 2000:
        errors.append('INVALID_TOPIC')
    if obj.get('stage') not in STAGES:
        errors.append('INVALID_STAGE')
    if obj.get('classification') != 'private-draft':
        errors.append('PRIVATE_HANDOFF_REQUIRED')
    if obj.get('author_profile_version') != author_profile()['profile_version']:
        errors.append('AUTHOR_PROFILE_MIGRATION_REQUIRED')
    authors = obj.get('authors')
    if not isinstance(authors, list) or any(not isinstance(a, dict) for a in authors):
        errors.append('INVALID_AUTHORS')
    else:
        ids = [a.get('id') for a in authors]
        if any(not isinstance(i, str) for i in ids):
            errors.append('INVALID_AUTHOR_ID')
        elif len(ids) != len(set(ids)):
            errors.append('DUPLICATE_AUTHORS')
        for expected in publication_authors():
            matches = [a for a in authors if a.get('id') == expected['id']]
            if not matches:
                errors.append('DEFAULT_AUTHOR_MISSING')
            elif any(matches[0].get(k) != expected.get(k) for k in PUBLIC_FIELDS):
                errors.append('AUTHOR_PROFILE_MISMATCH')
    for k in ('source_refs', 'artifact_refs', 'claim_ledger', 'findings', 'next_actions', 'limitations'):
        if not isinstance(obj.get(k), list):
            errors.append('INVALID_'+k.upper())
    refinement = obj.get('refinement')
    if (not isinstance(refinement, dict) or type(refinement.get('completed_cycles')) is not int
            or not 0 <= refinement['completed_cycles'] <= 5
            or type(refinement.get('maximum_cycles_per_run')) is not int
            or refinement['maximum_cycles_per_run'] != 5):
        errors.append('INVALID_REFINEMENT_BOUND')
    publication = obj.get('publication')
    if (not isinstance(publication, dict) or type(publication.get('ready')) is not bool
            or type(publication.get('submitted')) is not bool):
        errors.append('INVALID_PUBLICATION_RECORD')
    connection = obj.get('connection')
    if not isinstance(connection, dict) or connection.get('status') not in {'STUDIO_NOT_CONNECTED', 'STUDIO_VERIFIED'}:
        errors.append('INVALID_CONNECTION_RECORD')
    elif connection['status'] == 'STUDIO_VERIFIED' and not (connection.get('remote_project_id') and connection.get('receipt')):
        errors.append('CONNECTION_RECEIPT_REQUIRED')
    return {'structurally_valid': not errors, 'publication_ready': False,
            'errors': sorted(set(errors)),
            'limitations': 'Structural checks only. Verify current sources, artifacts, consent and provider receipts independently.'}


def cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    authors = sub.add_parser('authors', help='Print public author metadata only')
    authors.add_argument('--format', choices=('json', 'markdown', 'tex'), default='json')
    init = sub.add_parser('checkpoint', help='Print a new private checkpoint; does not persist it')
    init.add_argument('--project-id', required=True)
    init.add_argument('--topic', required=True)
    validate = sub.add_parser('validate-checkpoint', help='Check a private checkpoint structure only')
    validate.add_argument('path', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'authors':
            print(render_authors(args.format))
            return 0
        if args.command == 'checkpoint':
            print(json.dumps(checkpoint(args.project_id, args.topic), indent=2, ensure_ascii=False))
            return 0
        if args.path.is_symlink() or not args.path.is_file():
            raise ValueError('INVALID_CHECKPOINT_FILE')
        with args.path.open('rb') as f:
            data = f.read(MAX_CHECKPOINT_BYTES + 1)
        if len(data) > MAX_CHECKPOINT_BYTES:
            raise ValueError('CHECKPOINT_TOO_LARGE')
        report = validate_checkpoint(json.loads(data.decode('utf-8')))
        print(json.dumps(report, indent=2))
        return 0 if report['structurally_valid'] else 2
    except (ValueError, KeyError, TypeError, OSError, UnicodeError):
        # Avoid echoing arbitrary source text or paths into logs.
        print(json.dumps({'error': 'CONTEXT_INPUT_OR_PROFILE_INVALID', 'publication_ready': False}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(cli())
