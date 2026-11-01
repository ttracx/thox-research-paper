# Preflight Checklist for New Submissions

Required before every new arXiv submission. Re-run applicable checks for replacements. This is a publication gate, not evidence that a paper or account has already passed. Checked against official guidance on 2026-10-31; refresh platform requirements before each submission.

## Four mandatory checks

- [ ] **TeX source included.** When a paper was authored in TeX/LaTeX, upload its source and required dependencies, not just the compiled PDF. A PDF generated from TeX is not a substitute for source. [Why TeX source is required](https://info.arxiv.org/help/faq/whytex.html).
- [ ] **One clean upload directory prepared.** Make a separate staging copy containing only the intended upload files. Preserve the working repository. Review every included file and retain valid relative paths; one staging folder does not require flattening every subdirectory. [Author preparation guide](https://trevorcampbell.me/html/arxiv.html).
- [ ] **No missing content or references.** Check the main source, included sections, figures, custom styles/macros, bibliography, citations, cross-references and appendices. Compile the exact staging copy, resolve warnings, and inspect the arXiv-generated PDF after upload. [Common processing mistakes](https://info.arxiv.org/help/faq/mistakes.html).
- [ ] **Archival-safety review complete.** Treat the submitted source and ancillary files as public archival material. Review TeX comments, disabled sections, TODOs, metadata and unused files. Exclude credentials, cookies, personal or confidential data, working notes, backups, build logs and version-control directories. Preserve required third-party license notices. Announced versions remain part of the record; withdrawal is not deletion. [Author checklist](https://www.ianhuston.net/2011/03/checklist-for-arxiv-submission/) and [official withdrawal policy](https://info.arxiv.org/help/withdraw.html).

## Implementation checks

Run the bundled offline checker with Python 3.10+:

```sh
python skills/thox-research-paper/scripts/arxiv_preflight.py \
  /absolute/path/to/clean-upload --source-format tex --main main.tex \
  > /absolute/path/outside-upload/preflight-report.json
```

Use `pdf-other` only when the main document was not authored in TeX. That declaration must be verified, not inferred from an extension. Never run against the repository root or put reports, credentials, account state or review records in the upload directory.

The checker inventories and hashes files, detects common unsafe paths, hidden/private/build files, probable credentials, source omissions, literal missing includes and missing bibliography inputs. It flags comments for review without stripping them. It performs no network requests, credential handling, TeX execution, upload or publication. Exit 0 means static checks passed; exit 2 means blocked. `publication_ready` is always false because further checks are mandatory.

The static scanner is heuristic. It does not resolve arbitrary TeX macros, prove citation correctness, validate binary metadata, find every secret or certify scientific claims. Review each warning. Compile in an isolated, resource-limited environment without shell escape or network access; inspect the final build log for unresolved citations/references and missing dependencies. Do not execute untrusted TeX on a privileged host.

Current [official TeX guidance](https://info.arxiv.org/help/submit_tex.html) supports `.bib` or `.bbl` inputs. Do not blindly delete `.bib` files or apply old author-blog workarounds. Check the chosen processor and bibliography compatibility against current arXiv requirements.

Keep the report, build receipt and completed checklist outside the upload directory. Bind them to the exact inventory hash. Any file change invalidates the previous review and requires rechecking. Review source text as well as PDF pages; PDF inspection alone cannot reveal private source comments.

## Final submission gate

Before final submission, verify human authorship and consent, affiliations, title/abstract, category, rights/license, relevant AI-use disclosure, account identity, endorsement/eligibility and current submission limits. Review the server-generated PDF. Use existing valid authorization covering this exact artifact and destination; do not invent approval from a login request or a passing static report.

Record the submission receipt and distinguish uploaded draft, submitted, announced, held and declined. Submission and arXiv moderation do not imply peer-reviewed acceptance. Follow [account operations](arxiv-account-workflow.md) for authentication and authorized actions.
