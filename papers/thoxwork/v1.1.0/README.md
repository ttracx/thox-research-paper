# ThoxWork: One Workplace, One Connected Team — v1.1.0 (expanded edition)

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](LICENSE)
[![THOX.ai Research](https://img.shields.io/badge/THOX.ai-Research-05A451)](https://thox.ai/research)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23965699-1f6feb)](https://doi.org/10.5281/zenodo.23965699)

**THOX.ai Research technical report, v1.1.0 (expanded comprehensive
edition), published 2026-11-04.**
Authors: Craig Ross, Chief Executive Officer, THOX.ai, and Tommy Xaypanya,
Chief Technology Officer & Co-Founder, THOX.ai (corresponding author).
ORCIDs: Craig Ross [0009-0005-9872-3673](https://orcid.org/0009-0005-9872-3673);
Tommy Xaypanya [0009-0000-4425-9565](https://orcid.org/0009-0000-4425-9565).
Preprint, not peer reviewed. License: CC BY 4.0 (paper and evidence);
experiment code Apache-2.0 (see `NOTICE.md`).

This folder is the publication record for the paper inside
`ttracx/thox-research-paper`. It carries the current edition, v1.1.0.
The sibling folder `../v1.0.1/` carries the prior public edition, and
`../v1.0.0/` carries a separate expanded enterprise edition prepared
for internal review.

![Paper cover](docs/previews/cover-v1.1.0.png)

## About the paper

Enterprise adoption of AI agents is outrunning enterprise governance of
them. THOX's answer is a work platform, not another agent framework. In
the ThoxWork model, work lives in shared workspaces; DigitalHumans are
named, role-holding colleagues (ThoxEmployees) who can be assigned tasks
and held to account for them; Rolodex is the team interface through which
a person assigns a task, checks in, and reviews results; a MeshGroup
binds a named team to the exact set of resources it is approved to use;
and MeshStack connects those approved resources.

This comprehensive edition (45 pages) defines the model formally, audits
the code built toward it, and reports evidence in three labelled tiers:
the model's five invariants evaluated in a deterministic virtual lab
(SIMULATED); the rules measured against the product's own code and a
re-implemented evidence lab (MEASURED, code and lab); and the full
evaluation replayed against thoxwork-core, the live Rust implementation
of the model (MEASURED, live implementation replay). It also reconciles
the record it found: three admission definitions and five assignment
state machines side by side, with the one material disagreement
dispositioned (pooled admission stands). ThoxWork as a purchasable
enterprise platform remains in development; THOX's own product copy says
so, and this paper claims nothing further.

## DOI and canonical copies

- **DOI: [10.5281/zenodo.23965699](https://doi.org/10.5281/zenodo.23965699)** (concept DOI, all versions: [10.5281/zenodo.23963935](https://doi.org/10.5281/zenodo.23963935); prior version v1.0.1: [10.5281/zenodo.23963936](https://doi.org/10.5281/zenodo.23963936))
- Zenodo record: https://zenodo.org/records/23965699 — the version of record (paper PDF + HTML edition; this version carries both files)
- Paper page: https://thox.ai/research/papers/thoxwork
- Interactive demo (hosted on thox.ai; Zenodo serves HTML as text, so the demo does not live on the record): linked from the paper page, and in this folder at `paper/ThoxWork_Demo_v1.2.0.html`
- Hugging Face: folder `thoxwork/` in the [Thox-ai/thox-whitepapers](https://huggingface.co/datasets/Thox-ai/thox-whitepapers) dataset (paper PDF + HTML edition, both versions)
- This folder: paper PDF + HTML edition + demo in `paper/`, evidence in `artifact/exp/`

| File | SHA-256 |
|---|---|
| `paper/THOX_ThoxWork_Research_Paper_v1.1.0.pdf` (315,564 bytes) | `77aa1e51bd5f9e36c912cfacf36c0feba8a5a37ed0ae4a5d1b47d92c162e6187` |
| `paper/THOX_ThoxWork_Research_Paper_v1.1.0.html` (1,718,984 bytes) | `8fbc6eef88201694e03467b2486f98d2ccc0404a17af72f74e54e18dc6136ecf` |
| `paper/ThoxWork_Demo_v1.2.0.html` (42,167 bytes) | `65ff2a97a994eb0e3243ddf4987e0796b4aafed83e2dcb23a4a2a33956c62dfa` |
| `artifact/exp/results/summary.json` (32,089 bytes; frozen v1.0.1 oracle output, unchanged) | `f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6cdb071dd79` |
| `artifact/exp/results/summary-v110.json` (9,317 bytes; this edition's E8 + E9 evidence) | `37496b599d5055e8045dfee79eff7b3ff9b1add86fa41b2b49a5b3bc941363ad` |

`MANIFEST.sha256` in this folder lists the SHA-256 of every file in the
folder.

## Headline results, tier 1 (SIMULATED, protocol oracle E1–E5)

From `artifact/exp/results/summary.json`, the frozen evidence source of
v1.0.1, carried forward unchanged; 20 replicates per experiment, master
seed 20261104:

- **E1, policy enforcement:** 0 of 12,000 violating attempts leaked an
  unapproved resource; 0 of 8,000 legitimate attempts were falsely
  blocked; audit coverage 1.0.
- **E2, handoff integrity:** 5,000 of 5,000 reassigned tasks kept a
  complete handoff chain (15,000 entries); 0 of 4,000 negative probes
  leaked chain data across groups.
- **E3, admission control:** 4,000 of 4,000 oversized tasks denied
  UNPLACEABLE, 0 silently placed, 0 spilled across groups; at exactly
  1.00x pooled capacity work is admitted, at 1.01x it is denied.
- **E4, review gate:** 0 of 6,000 bypass attempts in six classes
  succeeded; 4,000 of 4,000 legitimate completions passed through
  eligible human review. With the gate switched off in the control arm,
  4,000 of 4,000 completed without review, which is what proves the
  checker discriminates.
- **E5, scale:** all 16 cells (team sizes 2/4/8/16 x group counts
  1/2/4/8; 320,000 simulated tasks) reached completion 1.0. The paper's
  falsifiable claim is non-collapse, not speedup; apparent efficiency
  above 1.0 is identified in the paper as a model artifact, and the
  reviewer bottleneck at team size 16 is reported as the real signal.

## Headline results, tier 2 (MEASURED, code and lab, E6–E10)

- **E6, planner agreement:** the evidence lab's re-implementation of the
  product routing planner agrees with the product code on 12,000 of
  12,000 seeded previews (companion-run results, read and cross-checked
  for this edition; see the paper's Section 12, item 4).
- **E7, kit agreement:** agreement with the reference admission kit on
  20,000 of 20,000 seeded decisions (same provenance note as E6).
- **E8, admission divergence under the paper's own semantics (new run
  for this edition):** pooled admission admits 3,882 of 20,000 probed
  requests that no single node could serve, all of them spanning; a
  looser port of the same rule over-admits by exactly 1,156 (967 phantom
  admissions plus 189 above pool capacity) and flattens 245 WAIT
  outcomes. Phase 2 stream: 5,093 waited-then-admitted, 0 invariant
  violations. Independently re-run byte-identical.
- **E9, audit-chain detection matrix (new run for this edition):**
  across 8 attacks x 4 configurations, a truncated chain is detected
  0/500 unanchored and 500/500 with an external anchor; a rebuilt chain
  defeats plain hash links (0/500) and is caught by key and anchor
  (500/500). KAT 7/7. Independently re-run, all 32 counts identical.
- **E10:** the companion port study, reproduced byte-identically from
  its delivered artifacts; its figures appear in the paper only as
  properties of the kit and the port, never as measurements of the
  paper's Algorithm 1.

## Headline results, tier 3 (MEASURED, live implementation replay, E11)

The tier-1 generators replayed against the live thoxwork-core API:

- 0 of 12,000 unapproved-resource attempts leaked.
- Admission boundary exact on the live system: demand 120 RU admitted,
  121 RU denied UNPLACEABLE, in every replicate.
- 0 of 6,000 review-gate bypasses; the gate-off control arm completed
  4,000 of 4,000 without review, so the check discriminates.
- Three independent judges (verifier API, verifier CLI, harness
  checker) agree on 102 of 102 workspaces.

## Quick start

```bash
git clone https://github.com/ttracx/thox-research-paper.git
cd thox-research-paper/papers/thoxwork/v1.1.0
# Read the paper:
open paper/THOX_ThoxWork_Research_Paper_v1.1.0.pdf        # macOS
xdg-open paper/THOX_ThoxWork_Research_Paper_v1.1.0.pdf    # Linux
# Run the interactive demo (single file, no network needed):
open paper/ThoxWork_Demo_v1.2.0.html
# Reproduce the tier-1 evidence (Python 3, standard library only):
python3 artifact/exp/thoxwork_experiments.py
# Reproduce this edition's E8 / E9 evidence:
python3 artifact/exp/e8_divergence.py
python3 artifact/exp/e9_detection_matrix.py
# Compare against the shipped evidence sources:
# artifact/exp/results/summary.json and summary-v110.json, SHA-256 above.
```

## Folder layout

| Path | Contents |
|---|---|
| `paper/` | The shipped edition: paper PDF, single-file HTML edition, interactive demo (canonical bytes, hashes above). |
| `artifact/exp/` | The evidence suite: `thoxwork_experiments.py` (deterministic oracle, Python standard library only) with `results/summary.json` (frozen tier-1 source), and this edition's `e8_divergence.py`, `e9_detection_matrix.py`, `e9_rebuild_supplement.py`, `merge_summary_v110.py` with `results/summary-v110.json` and the raw E8/E9 result files. |
| `artifact/wp/qa/` | `QA-REPORT.md` (build QA and binding dispositions) and `VERIFIER-REPORT.md` (independent re-runs of E8 and E9: all counts identical, oracle hash exact). |
| `docs/` | `USER_GUIDE.md`, `QUICKSTART.md`, `DEVELOPMENT.md`, `previews/` (rendered cover). |
| `HANDOFF.md` | Publication record and agent handoff: status, surfaces, key files, conventions. |
| `CITATION.cff`, `CITATION.bib` | Citation set. |
| `LICENSE`, `LICENSE-CODE.txt`, `NOTICE.md` | CC BY 4.0 for the paper and evidence, Apache-2.0 for the experiment code, and IP attribution. |
| `MANIFEST.sha256` | SHA-256 of every file in this folder. |

The ThoxWork platform source code is not in this repository. This folder
is the paper and its evidence record; the products the paper describes
(ThoxWork, Rolodex, ThoxEmployee) live in their own repositories under
their own terms.

## Documentation map

- User guide: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- Quick start: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- Development: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- Publication record: [HANDOFF.md](HANDOFF.md)

Your AI. Your Data. Your Rules.™
