# Version 1.1.1 validation and handoff

Date: 2026-10-31, America/Chicago.

## Changed

Added the mandatory new-submission checklist, secure account-operations workflow with a separate SWORD-permission gate, an offline preflight checker, 27 synthetic-fixture regression tests and local-data exclusions. The plugin loads the new references before arXiv preparation or account operations. Existing research-standard dependencies remain required; they are not bundled or newly validated by this update.

## Executed

`python -m unittest discover -s tests -v`: 27 tests passed locally. Tests cover TeX-source requirements, hidden/private/build files, literal includes, bibliography inputs, comments and escaped percent signs, possible-secret redaction, symlinks, case collisions, hash changes, path safety, invalid formats and shell-escape directives. Additional local packaging checks verify manifest versions and referenced file existence.

These are local automated tests of the new scanner, not independent scientific review, full TeX compilation, live account authentication or arXiv end-to-end tests. The scanner never marks a paper publication-ready.

## Remaining operational work

A secure authenticated browser or supported account connector must be connected and verified. No password, cookie, account profile or real submission record is included. No paper was uploaded or submitted during this update. Live authentication, server-preview review and final submission must be tested with an authorized, fully reviewed artifact and recorded provider receipts. Do not use a dummy manuscript to test real publication.

Public source and private operational records must remain separate. Preserve the source inventory hash, build evidence, completed checklist and exact-artifact authorization in private storage. One writer owns each submission; reviewers return findings without independently publishing.
