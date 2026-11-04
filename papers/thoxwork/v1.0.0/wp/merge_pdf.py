"""Merge cover.pdf and body.pdf into the final paper PDF and set metadata."""
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "wp"
OUT = ROOT / "dist" / "THOX_ThoxWork_Enterprise_Paper_v1.0.0.pdf"
OUT.parent.mkdir(exist_ok=True)

writer = PdfWriter()
cover = PdfReader(W / "cover.pdf")
writer.add_page(cover.pages[0])
for page in PdfReader(W / "body.pdf").pages:
    writer.add_page(page)
writer.add_metadata({
    "/Title": "ThoxWork for the Enterprise: Governed Digital Employees, MeshGroups, Rolodex and Evidence-First Teamwork",
    "/Author": "Craig Ross and Tommy Xaypanya (corresponding author), THOX.ai Research",
    "/Subject": "THOX.ai Research technical report, comprehensive edition v1.0.0, preprint, not peer reviewed",
    "/Keywords": "ThoxWork, Digital Employees, MeshGroups, Rolodex, ThoxEmployee, approval gates, tamper-evident logs, HMAC, governance, local-first AI",
    "/Creator": "THOX paper pipeline (build.py, katex_render.cjs, pdf.cjs, merge_pdf.py)",
})
with OUT.open("wb") as f:
    writer.write(f)
print("wrote", OUT, "pages", len(writer.pages))
