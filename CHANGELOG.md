# Changelog

## ThoxWork for the Enterprise v1.0.0 - 2026-11-04

- Added `papers/thoxwork/v1.0.0/`: technical report (PDF, HTML), the ThoxWork Evidence Lab, lab modules with 75 unit tests, public experiment scripts (E1, E2 lab side, E5), every result file with local paths removed, figures, a reviewed subset of product captures, the narrated summary video with SRT (16:9) and a 9:16 cut, and `MANIFEST.sha256`.
- Experiments that compare against THOX source that is not redistributed (E2 reference side, E3, E4, product test harness) ship as recorded outputs only.
- An independent review ran before publication; its fixes are in this release (approval-role wording, the action gateway order in Algorithm 1, component labels in place of repository names, redacted failure details, equations that fit the printed column). A disclosure scan ran over every text file. No skill code or plugin version changed.

## ThoxOS manuscript 0.2.0-review - 2026-11-01

- Replaced the paper placeholders with a corrected architecture and validation-status draft, bibliography, PDF, evidence ledger, build instructions, and status documentation.
- Reconciled the current ThoxInux/Ginux foundation, proprietary boundaries, payload-specific system evidence, and qualified model-card results.
- Preserved the historical CC BY 4.0 whitepaper and recovered its six missing SVGs from the matching public source.
- Recorded clean compilation and complete PDF review while preserving the public-manuscript and arXiv submission gates. No skill code or plugin version changed.

## 1.2.0 - 2026-11-01

- Added automatic Research Studio routing and private cross-session handoff instructions.
- Added shared publication authors: Craig Ross, CEO, and Tommy Xaypanya, CTO and Co-Founder, THOX.ai LLC, with Tommy's user-provided ORCID.
- Added public author-block and checkpoint helpers with regression tests.
- Kept the operator account alias only in the private plugin; no credentials stored.
- Preserved preflight and publication gates. No remote Studio connector or account authentication was deployed.


## 1.1.1 - 2026-10-31

- Added the verified SWORD-permission prerequisite and integrated preflight into both skill entry points.

## 1.1.0 - 2026-10-31

- Added mandatory arXiv preflight: TeX source, clean staging, complete files/references and archival-safety review.
- Added secure account-management and authorized-submission workflow instructions.
- Added an offline Python checker with per-file SHA-256 inventory and 27 regression tests.
- Kept credentials, real account state and unpublished papers out of public source.
- Live account connection and automatic submission are not enabled by this release.
