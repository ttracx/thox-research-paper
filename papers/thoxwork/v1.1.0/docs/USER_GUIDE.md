# User Guide — ThoxWork paper repository

This repository is the publication record for the THOX.ai Research
paper "ThoxWork: One Workplace, One Connected Team. A Policy-Bounded
DigitalHuman Work Platform for Enterprise Use", v1.1.0. It is a paper
and evidence repository, not the ThoxWork product.

## Reading the paper

- `paper/THOX_ThoxWork_Research_Paper_v1.1.0.pdf` — the canonical
  edition (45 pages).
- `paper/THOX_ThoxWork_Research_Paper_v1.1.0.html` — the same edition
  as a single self-contained HTML file (fonts and figures embedded);
  open it in any browser.
- The paper page at https://thox.ai/research/papers/thoxwork carries
  the same files plus the interactive demo, and the Zenodo record
  (DOI in the README) is the citable version of record.

## Running the demo

Open `paper/ThoxWork_Demo_v1.2.0.html` in a browser. It is a standalone
interactive walkthrough of the model's rules (Rolodex board, MeshGroup
admission, review gate) with preset cases, including the policy-block
case. It needs no network and installs nothing. On the website the demo
is hosted on thox.ai, because Zenodo serves HTML files as plain text.

## Checking the evidence

Every evaluation number in the paper comes from
`artifact/exp/results/summary.json`. To verify it:

```bash
python3 artifact/exp/thoxwork_experiments.py
```

The suite is deterministic: a fresh run reproduces `summary.json`
byte for byte (SHA-256 in the README). This edition's added evidence
(E8, E9) lives in `artifact/exp/results/summary-v110.json` and
reproduces the same way from `e8_divergence.py` and
`e9_detection_matrix.py`. `artifact/wp/qa/VERIFIER-REPORT.md` is the
non-producer verifier's independent re-judgement of the numbers;
`QA-REPORT.md` sits beside it. Results carry tier labels (SIMULATED
for the oracle tier, MEASURED for the code/lab and live-replay tiers);
the paper and the artifact README state what each tier does and does
not establish.

## Citing

Use `CITATION.cff` (GitHub renders a "Cite this repository" button
from it) or `CITATION.bib` for BibTeX. The DOI in those files is the
version DOI of record.
