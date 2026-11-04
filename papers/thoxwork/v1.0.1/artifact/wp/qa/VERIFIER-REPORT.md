# ThoxWork Paper — Independent Verifier Report (Non-Producer)

Verifier role: independent, non-producer re-verification of the single evidence source
`exp/results/summary.json` against `lanes/lane-d-protocol.md`.
Date of verification: 2026-11-04. Evidence class for every number below: **SIMULATED**
(ratios are CALCULATED arithmetic over simulated counts). No number in this report is
MEASURED on a device, network, or production system.
Constraint honoured: the experiments script and `summary.json` were not edited.

---

## 1. Reproducibility re-run (determinism check)

Command run by the verifier:

```
cd <paper artifact directory> && python3 exp/thoxwork_experiments.py --out /tmp/verify_summary.json
```

Outcome:

- Exit code: 0
- Script stdout: `{"self_test_determinism": true, "all_hypotheses_passed": true}`
- File size, both files: 32,089 bytes
- SHA-256 of `exp/results/summary.json` (committed evidence):
  `f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6cdb071dd79`
- SHA-256 of `/tmp/verify_summary.json` (verifier re-run):
  `f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6cdb071dd79`
- `cmp` result: **BYTE_IDENTICAL** — YES, the two files are byte-identical.

Verdict: the evidence file reproduces exactly from the script with default arguments.
Determinism claim (§3 of the protocol) is confirmed by direct re-execution.

Top-level fields in `summary.json`: `schema_version = thoxwork-summary/1.0`,
`paper_id = thoxwork`, `lab = thoxwork-virtual-lab`, `master_seed = 20261104`,
`all_hypotheses_passed = true`, and all four `invariant_checks` are `true`
(`e1_no_unapproved_resource_ever_ran`, `e2_all_handoff_chains_complete`,
`e3_no_oversized_task_placed`, `e4_all_done_tasks_legitimately_reviewed`).
Config: `replicates_e1_e4 = 20`, `replicates_e5_per_cell = 10`, `tick_budget_e5 = 200000`.

---

## 2. Headline numbers (read directly from `exp/results/summary.json`)

All aggregate metric objects below report mean = min = max with sd = 0.0 over
20 replicates (E1–E4) unless noted. Totals are summed over replicates; totals-based
rates were spot-recomputed by the verifier and agree with the reported metric means.

### E1 — Policy enforcement: unapproved resources never run

| Item | Value |
|---|---|
| violating_attempts (totals) | 12,000 |
| leaked_attempts (totals) | 0 |
| legit_attempts (totals) | 8,000 |
| legit_blocked (totals) | 0 |
| leak_rate (mean) | 0.0 |
| block_rate (mean) | 1.0 |
| false_block_rate (mean) | 0.0 |
| audit_coverage (mean) | 1.0 |
| passed (file) | true |

Hypothesis in file: `leak_rate = 0 and false_block_rate <= 0.01`.

### E2 — Handoff integrity: reassignment chains stay complete

| Item | Value |
|---|---|
| reassigned_tasks (totals) | 5,000 |
| complete_chains (totals) | 5,000 |
| total_entries (totals) | 15,000 |
| negative_probes (totals) | 4,000 |
| probe_leaks (totals) | 0 |
| chain_completeness (mean) | 1.0 |
| note_coverage (mean) | 1.0 |
| probe_leak_rate (mean) | 0.0 |
| max_chain_depth (mean / min / max) | 5.0 / 5.0 / 5.0 |
| passed (file) | true |

Hypothesis in file: `chain_completeness = 1.0 and note_coverage = 1.0`.

### E3 — Admission control: oversized work is denied, never spilled

| Item | Value |
|---|---|
| oversized_tasks (totals) | 4,000 |
| correctly_denied (totals) | 4,000 |
| right_sized_tasks (totals) | 6,000 |
| placed (totals) | 6,000 |
| silently_placed (totals) | 0 |
| cross_group_spills (totals) | 0 |
| stranded (totals) | 0 |
| unplaceable_recall (mean) | 1.0 |
| silent_overflow_rate (mean) | 0.0 |
| right_sized_placement_rate (mean) | 1.0 |
| stranded_rate (mean) | 0.0 |
| deny_latency_ticks_mean (mean over replicates) | 0.0 |
| deny_latency_ticks_max (mean over replicates) | 0.0 |
| passed (file) | true |

Hypothesis in file: `silent_overflow_rate = 0, unplaceable_recall = 1.0, right_sized_placement_rate >= 0.99`.

Demand-fraction table (`by_demand_fraction`, summed over 20 replicates; 1,000 tasks
per fraction = 50 per replicate × 20):

| Demand fraction | Tasks | Admitted | Denied | Waited-then-admitted |
|---|---|---|---|---|
| 0.10 | 1,000 | 1,000 | 0 | 0 |
| 0.25 | 1,000 | 1,000 | 0 | 0 |
| 0.50 | 1,000 | 1,000 | 0 | 0 |
| 0.75 | 1,000 | 1,000 | 0 | 0 |
| 0.90 | 1,000 | 1,000 | 0 | 0 |
| **1.00** | **1,000** | **1,000** | **0** | **0** |
| **1.01** | **1,000** | **0** | **1,000** | **0** |
| 1.25 | 1,000 | 0 | 1,000 | 0 |
| 1.50 | 1,000 | 0 | 1,000 | 0 |
| 2.00 | 1,000 | 0 | 1,000 | 0 |

The required rows: at fraction **1.00** all 1,000 tasks are admitted and none denied;
at fraction **1.01** all 1,000 tasks are denied and none admitted. The pooled capacity
is 120 RU, so 1.00 corresponds to demand 120 RU and 1.01 to demand 121 RU after rounding.

### E4 — Review gate: no DONE without human review

| Item | Value |
|---|---|
| bypass_attempts (totals) | 6,000 |
| bypass_successes (totals) | 0 |
| done_tasks_total (totals) | 4,000 |
| done_without_review_count (totals) | 0 |
| legitimate_tasks (totals) | 4,000 |
| legitimate_completions (totals) | 4,000 |
| bypass_success_rate (mean) | 0.0 |
| done_without_review_rate (mean) | 0.0 |
| legitimate_completion_rate (mean) | 1.0 |
| rejection_integrity (mean) | 1.0 |
| passed (file) | true |

Per-class bypass (`bypass_by_class`; each class = 50 attempts per replicate × 20 = 1,000):

| Class | Attempts | Successes | Success rate |
|---|---|---|---|
| B1 (direct finish) | 1,000 | 0 | 0.0 |
| B2 (skip review) | 1,000 | 0 | 0.0 |
| B3 (self-review) | 1,000 | 0 | 0.0 |
| B4 (wrong role) | 1,000 | 0 | 0.0 |
| B5 (non-member reviewer) | 1,000 | 0 | 0.0 |
| B6 (stale approval) | 1,000 | 0 | 0.0 |

Control arm (`control_no_review_gate`, gate disabled by design, reported separately
and not merged into H4): legitimate_tasks = 4,000, completions_without_review = 4,000.
With the gate off, every legitimate task completes without review — the checker
distinguishes gated from ungated completion as the protocol intends.

Hypothesis in file: `bypass_success_rate = 0, done_without_review_count = 0, legitimate_completion_rate >= 0.99`.

### E5 — Scale and throughput under a stated simulated-latency model

Grid: team sizes N ∈ {2, 4, 8, 16} × MeshGroup counts G ∈ {1, 2, 4, 8} = 16 cells,
10 replicates per cell, 2,000 tasks per cell-replicate, tick budget 200,000.

- **Completion rate:** mean = 1.0 in **every one of the 16 cells**; per-cell min and
  max are also 1.0 (sd = 0.0). **Min across cells = 1.0, max across cells = 1.0.**
  No cell is below 1.0.
- **Throughput (`throughput_per_1000_ticks`, CALCULATED from simulated ticks):**
  - Range of cell means: **124.855** (N=2, G=1) to **9,551.194** (N=16, G=8) tasks per 1,000 ticks.
  - Range over all individual replicates: minimum replicate value **124.363** (N=2, G=1)
    to maximum replicate value **9,615.385** (N=16, G=8).
  - Cell means in full (tasks / 1,000 ticks): N=2: 124.855 (G=1), 249.101 (G=2),
    467.783 (G=4), 830.537 (G=8); N=4: 374.447, 746.865, 1,392.389, 2,468.244;
    N=8: 869.952, 1,727.910, 3,217.032, 5,621.240; N=16: 1,317.958, 2,603.832,
    5,058.183, 9,551.194.
- **scaling_efficiency** (at G=1, baseline N=2 = 1.0): `"2": 1.0`, `"4": 1.499532`,
  `"8": 1.741928`, `"16": 1.319492`.
- **group_scaling_ratio** (at N=8, baseline G=1 = 1.0): `"1": 1.0`, `"2": 1.986215`,
  `"4": 3.697944`, `"8": 6.461555`.
- passed (file): true. Hypothesis in file:
  `every cell completion_rate >= 0.99 and scaling_efficiency(16) >= 0.50`.

---

## 3. Protocol §11 pre-registered bars — PASS / FAIL from the numbers alone

Bars are those in `lanes/lane-d-protocol.md` §11 (fixed 2026-11-04 before any run).
Judgement uses only the numbers in §2 above.

| Exp | Bar ( §11 ) | Numbers | Verdict |
|---|---|---|---|
| E1 | leaked_attempts = 0 (every replicate) | leaked = 0; leak_rate max = 0.0 | **PASS** |
| E1 | aggregate false_block_rate ≤ 0.01 | 0.0 | **PASS** |
| E1 | audit_coverage = 1.0 (every replicate) | mean/min/max = 1.0 | **PASS** |
| E2 | chain_completeness = 1.0 | 1.0 (5,000 / 5,000) | **PASS** |
| E2 | note_coverage = 1.0 | 1.0 (15,000 entries) | **PASS** |
| E2 | probe_leaks = 0 | 0 of 4,000 probes | **PASS** |
| E3 | silent_overflow_rate = 0 | 0.0; silently_placed = 0 | **PASS** |
| E3 | cross_group_spills = 0 | 0 | **PASS** |
| E3 | unplaceable_recall = 1.0 | 1.0 (4,000 / 4,000) | **PASS** |
| E3 | stranded_rate = 0 | 0.0; stranded = 0 | **PASS** |
| E3 | aggregate right_sized_placement_rate ≥ 0.99 | 1.0 (6,000 / 6,000) | **PASS** |
| E4 | bypass_successes = 0 in every class | 0 in each of B1–B6 (0 / 6,000 total) | **PASS** |
| E4 | done_without_review_count = 0 | 0 of 4,000 DONE | **PASS** |
| E4 | rejection_integrity = 1.0 | 1.0 | **PASS** |
| E4 | aggregate legitimate_completion_rate ≥ 0.99 | 1.0 (4,000 / 4,000) | **PASS** |
| E5 | every cell aggregate completion_rate ≥ 0.99 | 1.0 in all 16 cells | **PASS** |
| E5 | scaling_efficiency(16) ≥ 0.50 at G=1 | 1.319492 | **PASS** (numerically; see §4.1 for interpretation) |

**Overall from the numbers alone: E1 PASS, E2 PASS, E3 PASS, E4 PASS, E5 PASS.**
This agrees with the file's own `passed` flags and `all_hypotheses_passed = true`.
Passing the bars means the modelled rules enforce the stated invariants inside this
simulation. It does not, by itself, support any claim about a production system
(see §4).

---

## 4. Sanity critique — model artifacts the paper must explain honestly

The following are not bar failures. They are places where a reader could misread a
simulation artifact as a real-world finding unless the paper names the mechanism.

### 4.1 Scaling efficiency above 1.0 is a model artifact, not a speedup finding (E5)

`scaling_efficiency` is 1.499532 at N=4, 1.741928 at N=8, and 1.319492 at N=16 — all
above 1.0, i.e. apparently *superlinear*: throughput per member rises as members are
added. No real coordination system gets more efficient per person by adding people
indefinitely, and the paper must not present these values as performance. The mechanism
is in the protocol's own latency model (§E5): all 2,000 tasks arrive at tick 0 (batch
workload); service time per task is small and independent; the only coordination cost,
`coordination_ticks = floor(0.5 * (G - 1))`, depends on group count G and not at all
on team size N; reviewers are cooperative and always approve; there are no failures,
no offline members, and no contention cost that grows with N. With tiny teams the
makespan is dominated by serial queueing behind few workers, so adding parallel workers
plus an overlapped review pipeline mechanically raises per-member throughput past the
N=2 baseline. The non-monotonic shape (peak at N=8, falling to 1.319 at N=16) coincides
with `review_wait_share` jumping from ≈0 at N ∈ {2, 4}, to at most ≈0.0057 at N=8, to
≈0.20–0.30 at N=16 — i.e. the single-reviewer-per-group bottleneck only binds at N=16
in this parameterisation. The honest sentence for the paper is: efficiency above 1.0
reflects the baseline's queueing starvation and the absence of any N-dependent
coordination cost in the model; the falsifiable content of E5 is only that completion
did not collapse (every cell at 1.0) and that efficiency stayed above the pre-registered
0.50 floor. Any stronger reading is unsupported.

### 4.2 Deny latency of 0 ticks means "same tick", not "instant" (E3)

Both `deny_latency_ticks_mean` and `deny_latency_ticks_max` are 0.0. Under §2.3/§2.2-T7
admission is a synchronous function evaluated at creation, and a DENIED verdict is
recorded in the same tick. Zero ticks is therefore true *by construction of the tick
semantics*, and a tick is an abstract unit (the protocol's optional intuition is
"1 tick = 100 ms of simulated time (model assumption)"). The paper must not convert
0 ticks into any wall-clock latency claim, and should state plainly that denial is
decided at the admission call in the model, so no queueing or network delay is being
measured.

### 4.3 E5 event-driven / tick semantics bound what throughput can mean (E5)

E5 advances a discrete-tick loop over active tasks only: tasks are created at tick 0,
advanced one service tick at a time, moved to IN_REVIEW when a reviewer slot is free,
and approved after a fixed 3 review ticks. Consequences the paper must carry as
limitations: (a) throughput is tasks divided by simulated makespan — a CALCULATED
ratio over simulated ticks, spanning a ≈76× range of cell means (124.855 to 9,551.194)
that is driven almost entirely by total worker count (N × G ranges from 2 to 128), not
by any measured efficiency; (b) `handoff_cost_ticks = 2` is defined but never incurred
because E5 uses 0 reassignments, so E5 says nothing about handoff cost at scale;
(c) group scaling (ratio 6.461555 at G=8, sublinear) and team scaling (superlinear,
§4.1) are asymmetric purely because the cost term is a function of G only — the
asymmetry is an assumption, not a result; (d) batch arrivals, cooperative reviewers,
and zero failures are stated simplifications (protocol §10.3) and each one flatters
completion and throughput relative to enterprise load.

### 4.4 Perfect scores with zero variance are determinism, not robustness (E1–E4)

Every E1–E4 rate sits exactly on its ideal value (0.0 or 1.0) with sd = 0.0 across all
20 replicates. That is the expected output of a deterministic rule engine tested
against the same rules: the RNG varies task shapes, but no stochastic failure channel
exists in the model that could produce a leak, a dropped note, or a bypass. The paper
should frame E1–E4 as *invariant checks over enumerated adversarial inputs* (3 E1 modes,
4 E2 probe types, 6 E4 bypass classes) — a single violation would have falsified the
hypothesis, and none occurred — and must not describe the zero rates as error rates
observed in operation. Unenumerated bypasses are not excluded (protocol §10.2).

### 4.5 The E3 cliff at 1.00 → 1.01 is the definition, and the WAIT path is untested in E3

Admission switches from 1,000/1,000 admitted at demand fraction 1.00 to 1,000/1,000
denied at 1.01 because placeability is the binary test `demand_ru > 120`. The sharp
boundary is correct behaviour for the claim under test, but it is a threshold in the
model's definition, not a discovered phase transition. Separately,
`waited_then_admitted = 0` at **every** fraction: the E3 protocol drains the group to
empty before each task precisely so the current-fit WAIT branch never fires. E3
therefore provides no evidence about WAIT/retry behaviour, and the paper must not cite
it as doing so.

### 4.6 Checker independence is definitional, not implementation-independent (all)

Per protocol §5 and §10.5, the independent checker reads only the event log and final
task objects and does not call the engine — that separation was respected in the design
this verifier reviewed — but checker and engine share the protocol's own definitions
(§2.4 chain completeness, §2.5 legitimate DONE). A wrong definition would pass both
sides. The mitigation already required by the protocol is to state the definitions in
the paper itself so readers can falsify them; the verifier confirms this limitation is
disclosed in §10.5 of the protocol and must survive into the paper's limitations
section verbatim in substance. The E4 control arm (4,000 / 4,000 completions without
review when the gate is disabled) is good evidence the checker can tell gated from
ungated completion, but it is the same codebase with a flag flipped, not an independent
implementation.

### 4.7 Totals cross-checks performed by the verifier

Totals are internally consistent with the protocol's per-replicate sizes × 20
replicates: E1 600 violating + 400 legit per replicate → 12,000 / 8,000; E2 250
reassigned tasks and 200 probes per replicate → 5,000 / 4,000, with 15,000 chain entries
consistent with depths 0–5 at 50 tasks per depth per replicate; E3 500 tasks per
replicate → 10,000 total, split 6,000 right-sized / 4,000 oversized, matching the ten
fractions × 1,000; E4 300 bypass + 200 legitimate per replicate → 6,000 / 4,000. No
arithmetic inconsistency was found. E5 per-cell replicate counts are 10 throughout,
matching the stated config.

---

## 5. Verifier conclusion

1. The evidence file reproduces byte-identically on re-run (SHA-256
   `f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6cdb071dd79` for both copies).
2. Every headline number in §2 was read from `exp/results/summary.json` itself; no
   number was taken from paper prose.
3. Against the pre-registered §11 bars, judged from the numbers alone: **E1 PASS,
   E2 PASS, E3 PASS, E4 PASS, E5 PASS.**
4. The paper may claim the five invariants hold in this deterministic simulation under
   the enumerated adversarial inputs, with evidence class SIMULATED (ratios CALCULATED).
   It must carry the §4 explanations — superlinear scaling efficiency as a model
   artifact, 0-tick denial as same-tick semantics, E5 throughput as a ratio over
   simulated ticks under batch arrivals with no N-dependent coordination cost, zero
   variance as determinism, the E3 threshold as definitional with the WAIT path
   untested, and the shared-definition checker limitation — or the same numbers will
   mislead.

— Independent verifier (non-producer), ThoxWork paper evidence, 2026-11-04.
