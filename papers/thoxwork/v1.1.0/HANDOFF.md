# Publication Record and Agent Handoff — ThoxWork v1.1.0

Folder: `papers/thoxwork/v1.1.0/` in `ttracx/thox-research-paper`
(public) — publication record for the THOX.ai Research paper "ThoxWork:
One Workplace, One Connected Team. A Policy-Bounded DigitalHuman Work
Platform for Enterprise Use", authors Craig Ross (CEO) and Tommy
Xaypanya (CTO & Co-Founder, corresponding author).

## Status

- Edition v1.1.0 (expanded comprehensive edition, 45 pages) published
  2026-11-04. It supersedes v1.0.1 as the current edition under the
  same concept DOI. v1.0.1 remains published and citable as the prior
  version; v1.0.0 was an internal edition and was never published as
  this paper.
- Version DOI: 10.5281/zenodo.23965699 · Concept DOI:
  10.5281/zenodo.23963935 · Zenodo record:
  https://zenodo.org/records/23965699 (v1.1.0, CC BY 4.0, both creators
  with ORCIDs, verified by public read-back 2026-11-04; both deposited
  files download byte-identical to the files in this folder).
- Publication authorization: Tommy Xaypanya's global approval for all
  THOX papers (standing, confirmed 2026-11-04). Per-paper co-author
  consent is not a publication gate under that approval.
- Zenodo file note: unlike v1.0.1 (whose record carries the PDF only),
  the v1.1.0 record carries BOTH the paper PDF (315,564 bytes, SHA-256
  77aa1e51bd5f9e36c912cfacf36c0feba8a5a37ed0ae4a5d1b47d92c162e6187)
  and the HTML edition (1,718,984 bytes, SHA-256
  8fbc6eef88201694e03467b2486f98d2ccc0404a17af72f74e54e18dc6136ecf),
  closing the series' HTML gap. The deposited bytes are the
  deposit-time rebuild with the version DOI substituted into the
  paper's document control (Section 14); the pre-substitution
  inspection build is preserved in the internal edition record.
- Deposit integrity note: the Zenodo new-version draft was found
  pre-loaded with a superseded parallel build's files (a 38-page
  companion-body artefact) and that build's title in the draft
  metadata. Before publishing, every deposited file was replaced with
  the canonical build and the metadata title and description were
  restored to this paper's title and abstract; file checksums (MD5 via
  the deposit API, SHA-256 via public download after publish) were
  verified against the canonical build at each step. What is on the
  record is the canonical v1.1.0 edition and nothing else.

## Surfaces

- Zenodo (version of record): https://zenodo.org/records/23965699
- thox.ai paper page: https://thox.ai/research/papers/thoxwork
  (updated to v1.1.0 at publication; demo v1.2.0 unchanged)
- HF dataset Thox-ai/thox-whitepapers, folder `thoxwork/` (v1.1.0 PDF +
  HTML added alongside v1.0.1; card names v1.1.0 as the current edition)
- This folder: `paper/` (PDF + HTML + demo v1.2.0), `artifact/` (oracle
  + frozen summary.json, E8/E9 suite + summary-v110.json, QA and
  verifier reports)
- Registry: research-publishing-pipeline, paper id `thoxwork`,
  manifest `manifests/thoxwork.json`

## Key files

- `paper/` — canonical edition bytes; hashes in `README.md`;
  folder-wide hashes in `MANIFEST.sha256`.
- `artifact/exp/results/summary.json` — tier-1 evidence source,
  frozen from v1.0.1; SHA-256
  f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6cdb071dd79.
- `artifact/exp/results/summary-v110.json` — this edition's E8 + E9
  evidence source; SHA-256
  37496b599d5055e8045dfee79eff7b3ff9b1add86fa41b2b49a5b3bc941363ad.
- `artifact/wp/qa/VERIFIER-REPORT.md` — independent verification of
  E8 and E9 (byte-identical re-runs by non-producers; oracle hash
  exact). `QA-REPORT.md` records the build's binding dispositions;
  its public copy carries one scrub note where an internal build
  path was replaced by a description.

## Conventions

- Evaluation numbers carry their tier labels everywhere: SIMULATED
  (tier 1, protocol oracle), MEASURED code and lab (tier 2, E6–E10),
  MEASURED live implementation replay (tier 3, E11). Never restate a
  lab number as a product measurement.
- The demo is hosted on thox.ai (Zenodo serves HTML as text); the
  copy in `paper/` is the downloadable one.
- New editions follow `docs/DEVELOPMENT.md`'s release checklist and
  publish under Tommy Xaypanya's global paper approval.
