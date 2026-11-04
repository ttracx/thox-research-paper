#!/usr/bin/env python3
"""Build ThoxWork v1.1.0 PDF + dist HTML from src/paper.src.html.
The source is already self-contained (data-URI fonts incl. KaTeX, inline SVG
figures, data-URI screenshots), so the dist HTML is the source itself and the
PDF renders from the same bytes via WeasyPrint."""
from pathlib import Path
from weasyprint import HTML
V = Path(__file__).resolve().parent.parent
src = (V / 'src' / 'paper.src.html').read_text(encoding='utf-8')
STEM = 'THOX_ThoxWork_Research_Paper_v1.1.0'
(V / 'dist').mkdir(exist_ok=True)
(V / 'dist' / f'{STEM}.html').write_text(src, encoding='utf-8')
HTML(string=src, base_url=str(V / 'src')).write_pdf(str(V / 'dist' / f'{STEM}.pdf'))
print('built', STEM)
