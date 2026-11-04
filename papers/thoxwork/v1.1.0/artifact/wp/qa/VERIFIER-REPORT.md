# Verifier Report — ThoxWork Paper v1.1.0 New Evidence (E8, E9)

Independent re-runs by verifiers who did not produce the artifacts.
Producer outputs were compared field by field; verifiers wrote only to
scratch paths and edited no artifact.

## E8 — admission divergence under Algorithm 1 semantics: PASS

- Re-run of `exp/e8_divergence.py` produced a file **identical** to
  `exp/results/e8_divergence.json` in every count of both phases.
- Phase 1 (20,000 probes): P ADMITTED 15,982 / WAIT 1,212 /
  UNPLACEABLE 523 / DENIED 2,283; spanning-required 3,882;
  single-node-fit 12,100; S ADMITTED 12,100 / REFUSED 7,900;
  X ADMITTED 17,138 / REFUSED 2,862; pooled-only admissions 3,882
  (all spanning); S_admits_P_refuses 0; X phantom admissions 967;
  X admits-P-unplaceable 189; X wait-collapse 245; agree_all 14,962.
- Phase 2 (10,000 arrivals): admitted immediate 3,311;
  waited-then-admitted 5,093; still waiting 74; UNPLACEABLE 306;
  denied unapproved 1,216; admissions spanning 4,625 / single-node
  3,779; invariant violations 0; S admitted 1,266 / refused 8,734;
  S refused-P admitted 2,244.
- Internal consistency verified: P verdicts sum to 20,000;
  X admitted − P admitted = 1,156 = 967 + 189; Phase 2 outcomes sum
  to 10,000.

## Oracle integrity: PASS

- SHA-256 of the frozen oracle `exp/results/summary.json` computed
  independently: f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6cdb071dd79
  — exactly the value asserted by the merge script and printed in the
  paper (Section 14). The original file was never written by any
  v1.1.0 tooling.

## Companion port-study reproduction: PASS

- The delivered `admission_divergence.js` was re-executed with the lab
  admission module extracted byte-faithfully from the delivered
  Evidence Lab HTML (its "MeshGroup admission" UMD script block) and
  the delivered `meshgroup_cases.json`. Output JSON is **byte-identical**
  to the delivered `admission_divergence.json`: total 20,000;
  reference placements 4,570; placements on a too-small node 2,572
  (56.3%); split 1,655 spanning / 2,678 cross-site of the 4,333.
  These figures appear in the paper only as properties of the kit and
  the port (Section 7.8, Appendix A), never as measurements of
  Algorithm 1.

## E9 — audit-chain detection matrix: PASS

- Re-run of `exp/e9_detection_matrix.py` plus
  `exp/e9_rebuild_supplement.py`: **all 32 detection counts
  (8 attacks × 4 configurations) and all per-check breakdowns
  identical** to `exp/results/e9_detection_matrix.json`;
  KAT 7/7 identical; honest-chain property held on all 500 trials
  (asserted in-run); seed family 20261104 + 10000·9 + trial;
  500 trials per attack; 1,000 records per chain.
- Observed grid (detected of 500): modify, delete, reorder, renumber
  = 500 in all four configurations; truncate = 0 / 500 / 0 / 500
  (plain / +anchor / keyed / keyed+anchor); append-nokey = 0 / 500 /
  500 / 500; append-withkey = 0 / 500 / 0 / 500; rebuild = 0 / 500 /
  500 / 500.
- Costs are host timing measurements and were excluded from the
  reproduction comparison, as stated in Appendix A of the paper.

## Not re-executed (stated in the paper, Section 12, item 4)

E6 (planner agreement) and E7 (kit agreement) report the companion
review's runs. Their delivered result files were read and cross-checked
for this edition (12,000/12,000 strict agreement at product commit
ab29b61; kit agreement 20,000/20,000 with outcome mix 4,570 / 4,377 /
11,053 summing exactly; commit pins as printed in Table 7), but the
runs were not re-executed because the product planner and kit sources
are THOX-internal and were not part of this edition's artifact set.
No number was dropped on reproduction grounds; no number in the paper
rests on an artifact that failed to reproduce.
