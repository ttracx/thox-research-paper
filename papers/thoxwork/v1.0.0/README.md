# ThoxWork for the Enterprise (v1.0.0)

**Governed Digital Employees, MeshGroups, Rolodex and Evidence-First Teamwork.** THOX.ai Research technical report v1.0.0, 2026-11-04. Preprint, not peer reviewed. Authors: Craig Ross (Chief Executive Officer, ORCID 0009-0005-9872-3673) and Tommy Xaypanya (CTO and Co-Founder, corresponding author, ORCID 0009-0000-4425-9565), THOX.ai LLC. Comprehensive edition that extends the internal THOX ThoxWork research paper v1.0.0.

| Path | Contents |
|---|---|
| `dist/THOX_ThoxWork_Enterprise_Paper_v1.0.0.pdf` | The paper, 35 pages including the cover |
| `dist/THOX_ThoxWork_Enterprise_Paper_v1.0.0.html` | Standalone HTML, fonts, figures and KaTeX embedded |
| `dist/ThoxWork_Evidence_Lab_v1.0.0.html` | The Evidence Lab: one HTML file that runs offline in any modern browser |
| `lab/` | Lab modules (`evidence.js`, `meshgroup.js`, `governance.js`, `planner.js`), their unit tests and the page template |
| `exp/` | Experiments that use only public code, and every result file (local paths removed) |
| `wp/` | Paper build, figures, references, PDF pipeline and QA scripts |
| `evidence/screens/` | Reviewed subset of product screenshots, 1280 by 800 and 390 by 844 |
| `evidence/video/` | Product screen recordings, the Evidence Lab tour, and the 78-second narrated summary (16:9 with SRT captions, and a 9:16 cut); the narration voice is AI-generated |
| `MANIFEST.sha256` | SHA-256 of every file in this directory |

## Headline results

| Result | Value | Evidence class |
|---|---|---|
| Tests rerun for the paper in 9 THOX code bases (10 reviewed) | 3,747 passed, 3 failed, 18 suites | measured |
| Evidence Lab planner vs the ThoxWork routing planner | 12,000 of 12,000 seeded previews identical, 55,832 per-node verdicts | measured |
| Evidence Lab admission module vs the THOX reference admission kit | 20,000 of 20,000 decisions identical | measured |
| Reference-rule placements on a node smaller than the request | 56.3% under an illustrative demand model | measured |
| Tail truncation caught: hash links alone vs with an external anchor | 0% vs 100%, 500 seeded trials each | measured |
| Keyed append, 1,000-record chain (pure JavaScript SHA-256) | 27.6 microseconds per record, median of 30 | measured |

Nothing here is measured on a THOX device or a customer deployment. ThoxWork is coming soon; no price or date is stated.

## Reproduce

```
cd wp && npm install && cd ..
node --test lab/test/lab.test.js lab/test/planner.test.js        # 75 lab unit tests
node exp/evidence_experiments.js                                    # E1 evidence chain detection and cost
node exp/meshgroup_lab.js                                           # E2 lab side (uses exp/results/meshgroup_cases.json)
node exp/admission_divergence.js                                    # E5 admission rule divergence
python3 exp/analyze.py                                              # rebuilds exp/results/summary.json
python3 wp/figures.py && python3 wp/build.py
node wp/katex_render.cjs wp/paper.src.html wp/paper.html
node wp/pdf.cjs wp/paper.html wp/cover.pdf wp/body.pdf && python3 wp/merge_pdf.py && python3 wp/build_lab.py
```

Four comparisons use THOX source that is not redistributed: the reference side of E2 (THOX reference admission kit), E3 and E4 (the ThoxWork routing planner) and the product test harness. Their recorded outputs are in `exp/results/` so every comparison can be re-checked without that source.

## Lineage and licenses

The ThoxWork desktop and server shell is built on the open-source OpenWork project and the OpenCode engine, used under their upstream licenses, whose notices are carried. The Digital Humans Python runtime is built on the open-source Hermes Agent. Text and figures in this directory are CC BY 4.0; lab and experiment code is Apache-2.0, as is this repository. Product screenshots and recordings show THOX software and remain THOX.ai LLC's; role names in the Evidence Lab are illustrative.

Your AI. Your Data. Your Rules.™
