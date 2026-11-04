# Publication Record and Agent Handoff — ThoxWork v1.0.1

Folder: `papers/thoxwork/v1.0.1/` in `ttracx/thox-research-paper`
(public) — publication record for the THOX.ai Research paper "ThoxWork:
One Workplace, One Connected Team. A Policy-Bounded DigitalHuman Work
Platform for Enterprise Use", authors Craig Ross (CEO) and Tommy
Xaypanya (CTO & Co-Founder, corresponding author).

## Status

- Edition v1.0.1 (public edition) published 2026-11-04. v1.0.0 was an
  internal edition and was never published as this paper; it differs
  from v1.0.1 only in edition marking plus one factual correction to
  the RolodexGo product-status wording in Section 4, disclosed in the
  paper's own document control (Section 12).
- Version DOI: 10.5281/zenodo.23963936 · Concept DOI:
  10.5281/zenodo.23963935 · Zenodo record:
  https://zenodo.org/records/23963936 (v1.0.1, CC BY 4.0, both creators
  with ORCIDs, verified by public read-back 2026-11-04).
- Publication authorization: Tommy Xaypanya's global approval for
  all THOX papers (standing, confirmed 2026-11-04 15:17 CT), executed
  on his flip order of 2026-11-04 13:54 CT ("Publish paper and flip
  whatever you're waiting on do videos after").
- Zenodo file note: the record carries the paper PDF (190,880 bytes,
  SHA-256 428b813729882fc1d77319f3c76f518e29465d77dc32c3482ae5a197832aeeba).
  The HTML edition was uploaded to the draft and listed there, but did
  not survive the publish step, and a published record's bucket is
  locked; it cannot be added without a new Zenodo version, which would
  change the version DOI cited inside the paper itself. The identical
  HTML bytes (SHA-256 e59465ff8fe61b6df7b026659b19c2a83c9065e5142ed49c8d49aa31bf7ebdb7)
  are carried on the website, this folder, and the Hugging Face dataset.

## Surfaces

- Zenodo (version of record): https://zenodo.org/records/23963936
- thox.ai paper page: https://thox.ai/research/papers/thoxwork
  (website PR ttracx/Thox.ai #495, merged at the flip)
- HF dataset Thox-ai/thox-whitepapers, folder `thoxwork/` (PDF + HTML)
- This folder: `paper/` (PDF + HTML + demo v1.1.0), `artifact/` (oracle
  code + summary.json + verifier report)
- Registry: research-publishing-pipeline, paper id `thoxwork`,
  manifest `manifests/thoxwork.json`

## Key files

- `paper/` — canonical edition bytes; hashes in `README.md`;
  folder-wide hashes in `MANIFEST.sha256`.
- `artifact/exp/results/summary.json` — single evidence source;
  SHA-256 f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6cdb071dd79.
- `artifact/wp/qa/VERIFIER-REPORT.md` — independent verification
  (byte-identical summary reproduced by a non-producer).

## Conventions

- All evaluation numbers are SIMULATED and are labelled so everywhere
  they appear. Never restate a lab number as a product measurement.
- The demo is hosted on thox.ai (Zenodo serves HTML as text); the copy
  in `paper/` is the downloadable one.
- New editions follow `docs/DEVELOPMENT.md`'s release checklist and
  publish under Tommy Xaypanya's global paper approval.
