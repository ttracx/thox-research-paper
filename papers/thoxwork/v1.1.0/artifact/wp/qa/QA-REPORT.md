# QA Report — ThoxWork Research Paper v1.1.0 (Comprehensive Edition)

Build: `wp/build.py` (WeasyPrint 70) from `src/paper.src.html`, assembled by
`surgery.py` from the comprehensive-edition source with every merge edit
asserted (36 edits + style assembly). Dist HTML is the same self-contained
source (data-URI fonts, inline SVG figures, data-URI screenshots).

## Render QA (inspected, 2026-11-04)
- 38 pages. Contact sheets `contact-1.png` (pp. 1-20) and `contact-2.png`
  (pp. 21-38) inspected page by page; hi-res spot checks of the cover,
  Introduction (p. 4), Figure 7 + Section 7.7 (p. 26).
- Template v1.0 design: dark cover (matches the canonical MeshStack v1.0.1
  example), #05A451 sole accent, evidence-class labels on stat cards
  (MEASURED set; Section 7.7 table labelled measured; E5 kept SIMULATED).
- Defect found and fixed during QA: the source edition's embedded Inter and
  JetBrains Mono woff2 instances misrender under WeasyPrint (body glyphs
  scattered). The build substitutes the fleet TTF faces used by every prior
  THOX paper build; KaTeX faces and CSS are unchanged. Re-render verified
  clean on all 38 pages, including the Section 4.2/4.5 equations.
- No Appendix C (errata reconciled into the text); Appendix D is document
  control, authorship and publication boundary. No AI-assistance disclosure.
  No internal hostnames, IPs or paths anywhere in the PDF text.

## Numbers proof
`numbers-proof.json`: 35/35 checks pass. Every headline number in the built
PDF was matched against `exp/results/summary.json` (schema
thoxwork-summary/1.1.0), the single evidence source that merges the product
test record, planner and reference-kit agreement studies, the admission
divergence study, the Evidence Lab record, the simulated protocol oracle
(labelled SIMULATED) and the live core-service acceptance (labelled
MEASURED, Section 7.7), including both DOIs and the D1 ruling text.

## Files (SHA-256 in the flip report)
- dist/THOX_ThoxWork_Research_Paper_v1.1.0.pdf (38 pp)
- dist/THOX_ThoxWork_Research_Paper_v1.1.0.html (single file)
- dist/ThoxWork_Demo_v1.1.0.html (interactive demo, byte-identical to the
  demo shipped with v1.0.1)
