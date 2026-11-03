"""Merge cover.pdf and body.pdf into the final paper PDF and set metadata."""
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "wp"
OUT = ROOT / "dist" / "THOX_ThoxOS_Research_Paper_v1.0.1.pdf"
OUT.parent.mkdir(exist_ok=True)

writer = PdfWriter()
cover = PdfReader(W / "cover.pdf")
writer.add_page(cover.pages[0])
for page in PdfReader(W / "body.pdf").pages:
    writer.add_page(page)
writer.add_metadata({
    "/Title": "ThoxOS and ThoxInux: An Evidence-Bounded Architecture for a Local-First AI Operating System",
    "/Author": "Craig Ross and Tommy Xaypanya (corresponding author), THOX.ai Research",
    "/Subject": "Technical report v1.0.1, preprint, not peer reviewed",
    "/Keywords": "ThoxOS, ThoxInux, Ginux, local-first AI, entitlement, A/B updates, Linux ABI, kernel models",
    "/Creator": "THOX paper pipeline (build.py, katex_render.cjs, pdf.cjs, merge_pdf.py)",
})
with OUT.open("wb") as f:
    writer.write(f)
print("wrote", OUT, "pages", len(writer.pages))
