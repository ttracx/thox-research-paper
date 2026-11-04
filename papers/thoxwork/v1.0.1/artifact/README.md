# Artifact README — ThoxWork paper evidence

This folder is the evidence record for "ThoxWork: One Workplace, One
Connected Team" v1.0.1 (THOX.ai Research). It holds everything needed
to re-derive every evaluation number printed in the paper.

## Contents

- `exp/thoxwork_experiments.py` — the deterministic evaluation suite
  (the "virtual lab" oracle). Python 3, standard library only, no
  network, no timestamps in the output. Master seed 20261104; per-
  experiment seeds follow `20261104 + 10000 * experiment_index +
  replicate`. Apache-2.0 (see `../../LICENSE-CODE.txt`).
- `exp/results/summary.json` — the single evidence source. SHA-256
  `f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6cdb071dd79`.
  Two independent runs of the suite (producer and verifier) produce a
  byte-identical file. CC BY 4.0 (see `../../LICENSE`).
- `wp/qa/VERIFIER-REPORT.md` — the independent verifier's report: all
  pre-registered pass bars (protocol Section 11) re-judged from the
  numbers alone, including the standing critiques the paper carries
  (the E5 efficiency-above-1.0 model artifact, the definitional E3
  boundary, the reviewer bottleneck at team size 16).

## Honesty labels

All results are SIMULATED in a deterministic discrete-tick model. No
result is measured on a device, a network, or a production system.
Ratios described as CALCULATED are arithmetic over simulated counts.
The suite checks invariants of the ThoxWork model as formalised in the
paper's protocol; it is not a benchmark of any shipped product.
