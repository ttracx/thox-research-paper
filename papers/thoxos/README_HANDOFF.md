# Manuscript continuation handoff

**Artifact:** ThoxOS / ThoxInux research draft, 0.2.0-review

**Parent source baseline:** `ttracx/thox-research-paper` at `ad92ec44116e4dd895f1f82f7b8c279de1241401`

**Current reviewed kernel source:** `Thox-ai/thoxinux` at `fbad5952f20281ef6ad7eaefc1f54f7db4c0c6e9`

**Status:** Internally reviewed technical draft; no arXiv submission or product acceptance claim.

## Resume without losing source identity

1. Read `README.md`, `ARXIV_STATUS.md`, `evidence-ledger.json`, and this file. Preserve the original reference and its license.
2. Compare current repository and model-card revisions with the ledger. A changed source requires a scoped delta review before updating affected claims.
3. Build with `make pdf`. Check the log and inspect every page of the new PDF. Keep a review record bound to the exact TeX, bibliography, and PDF hashes.
4. Keep one integrator for `main.tex` and `references.bib`. Reviewers return findings instead of editing competing manuscript copies.

## Next bounded research work

| Work | Inputs | Exit evidence |
| --- | --- | --- |
| Resident-agent feasibility | Pinned Ginux/ThoxInux payload, exact legacy failure record, supervised-agent workload | Serial and audit logs, payload hash, attempted-run inventory, completed-loop or failure result. Do not transfer legacy failures to unified bytes. |
| Runtime/model compatibility | Named runtime, actual quantized model, tokenizer/template, controlled Linux baseline | Reproducible load/inference run, memory and latency measurements, failures, matched baseline. |
| Model quality and action controls | Held-out tasks, fixed scoring rules, published templates, external tool harness | Full completion and final-answer scores, abstentions, denied actions, unsafe proposals, unauthorized executions, exact artifact identities. |
| Offline and update behavior | Built image, bootloader/RAUC configuration, declared Core features | Network observations, invalid-token behavior, failure injection, boot attempts, recovery and data-integrity records. |
| Physical device feasibility | Named supported board and architecture, memory/runtime envelope | Physical run record. Host, emulated, and peer results retain their actual execution locations. |

These are prepared assignments, not a claim that another runtime has received or accepted them. Current external owners and execution permissions must be resolved at pickup.

## Stop conditions

- Do not publish an unapproved manuscript merely because the repository is public or write access exists.
- Do not submit to arXiv from a passing local build or static preflight.
- Do not write a physical disk, change a deployment, spend money, send email, or alter sharing as part of this document handoff alone.
- Preserve failed tests, proprietary boundaries, upstream rights, source-specific licenses, and user authorization requirements.
- Never relabel container execution as Ginux execution, x86 emulation as an Arm port, or model-card scores as independent device results.

## Authorship and credit

Keep Craig Ross and Tommy Xaypanya in the supplied order, with both user-provided ORCID identifiers. Sadie Weaving and the independent AI review lanes contributed integration and review; the original Grok package and historical synthetic drafter remain credited. Internal AI review is not external scholarly peer review.
