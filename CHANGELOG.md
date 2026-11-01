# Changelog

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
