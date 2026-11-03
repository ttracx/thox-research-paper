# ThoxOS and ThoxInux: An Evidence-Bounded Architecture for a Local-First AI Operating System (v1.0.0)

THOX.ai Research technical report v1.0.0, 2026-11-03. Preprint, not peer reviewed. Builds on revision 0.2.0-review in the parent directory (Zenodo DOI 10.5281/zenodo.23876230).

| Path | Contents |
|---|---|
| `dist/THOX_ThoxOS_Research_Paper_v1.0.0.pdf` | The paper, 16 pages |
| `dist/THOX_ThoxOS_Research_Paper_v1.0.0.html` | Standalone HTML, fonts and KaTeX embedded |
| `dist/ThoxOS_Demo_v1.0.0.html` | Browser demo: entitlement contract with known-answer tests, A/B health gate stepper, memory budget, ledger lookup |
| `dist/THOX_ThoxOS_Paper_v1.0.0_artifact.zip` | Reproducibility artifact as delivered |
| `exp/` | Experiments, raw results, `summary.json` (single source of every number) |
| `wp/` | Reference fetch, figures, build, render, PDF, demo build, QA |

## Headline results

| Result | Value | Evidence class |
|---|---|---|
| Ed25519 entitlement verify (HMAC) | 196 us (12 us) on a 2-vCPU host; HMAC design forgeable by any verifier | measured |
| A/B contract under injected faults | 200/200 updates end known-good, at most 3 recovery boots | simulated, 30 seeds |
| Traced agent loop vs ledger at the ThoxInux pin | 10 of 56 distinct syscalls Complete, 46 Partial, 0 Policy-denied | observed and measured |
| ThoxOS-Kernel-4B Q4_K_M on the 4 GB Mini floor | 7,350-token context at a 1 GB reserve; no fit at 1.5 GB | calculated |

No ThoxInux boot, device, model inference or security assessment was executed.

## Reproduce

```
pip install cryptography numpy matplotlib pypdf pillow && cd wp && npm install && cd ..
curl -o /home/claude/ginux_ledger/LINUX-COMPATIBILITY.md https://raw.githubusercontent.com/gmkurtzer/ginux/36503bda2d87465765e1b94e65f9d100f27ed5be/docs/LINUX-COMPATIBILITY.md
python3 exp/entitlement_experiments.py && python3 exp/update_sim.py && python3 exp/memory_budget.py && python3 exp/syscall_ledger.py
python3 exp/analyze.py && python3 wp/figures.py && python3 wp/build.py
node wp/katex_render.cjs wp/paper.src.html wp/paper.html && node wp/pdf.cjs wp/paper.html wp/cover.pdf wp/body.pdf && python3 wp/merge_pdf.py
python3 wp/build_demo.py && node wp/qa.cjs && python3 wp/qa_pdf.py
```
