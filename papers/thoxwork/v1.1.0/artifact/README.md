# Artifact README — ThoxWork paper evidence

This folder is the evidence record for "ThoxWork: One Workplace, One
Connected Team" v1.1.0 (THOX.ai Research). It holds everything needed
to re-derive every evaluation number printed in the paper.

## Contents

- `exp/thoxwork_experiments.py` — the deterministic evaluation suite
  (the "virtual lab" oracle) behind tier 1 (E1–E5). Python 3, standard
  library only, no network, no timestamps in the output. Master seed
  20261104; per-experiment seeds follow
  `20261104 + 10000 * experiment_index + replicate`. Apache-2.0 (see
  `../../LICENSE-CODE.txt`).
- `exp/results/summary.json` — the tier-1 evidence source, frozen from
  v1.0.1 and carried into this edition byte-identical. SHA-256
  `f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6cdb071dd79`.
  Two independent runs of the suite (producer and verifier) produce a
  byte-identical file. CC BY 4.0 (see `../../LICENSE`).
- `exp/e8_divergence.py`, `exp/e9_detection_matrix.py`,
  `exp/e9_rebuild_supplement.py`, `exp/merge_summary_v110.py` — this
  edition's new evidence producers (tier 2, E8 and E9), with
  `exp/results/summary-v110.json` as the merged evidence source
  (SHA-256
  `37496b599d5055e8045dfee79eff7b3ff9b1add86fa41b2b49a5b3bc941363ad`)
  and the raw result files `e8_divergence.json` and
  `e9_detection_matrix.json` beside it. Apache-2.0 for the code, CC BY
  4.0 for the results.
- `wp/qa/QA-REPORT.md` — the build QA record: binding dispositions,
  the blocker sweep, and the page-count and sibling-tree flags.
- `wp/qa/VERIFIER-REPORT.md` — the independent verifier's report:
  E8 re-run byte-identical in every count; E9 all 32 detection counts
  and KAT 7/7 identical; the frozen oracle's hash recomputed exactly;
  the companion port study reproduced byte-identically. E6 and E7
  were read and cross-checked from their delivered result files, not
  re-executed (their sources are THOX-internal); the paper states
  this in Section 12, item 4.

## Honesty labels

Tier 1 (E1–E5) results are SIMULATED in a deterministic discrete-tick
model: no result is measured on a device, a network, or a production
system, and ratios described as CALCULATED are arithmetic over
simulated counts. Tier 2 (E6–E10) results are MEASURED against code
and lab artifacts. Tier 3 (E11) is a MEASURED replay of the tier-1
generators against the live thoxwork-core implementation; its
acceptance record lives with the implementation, and the paper's
Section 7.11 reports it. Host timing figures in E9 are host
measurements and are excluded from all reproduction claims, as stated
in the paper's Appendix A.
