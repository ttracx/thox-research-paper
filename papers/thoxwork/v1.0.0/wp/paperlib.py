"""Shared helpers for the ThoxWork paper build: references, citations and HTML blocks."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS = json.loads((ROOT / "wp" / "refs.json").read_text())
REFS_RAW = json.loads((ROOT / "wp" / "refs_raw.json").read_text())
for _extra in ("refs_manual.json", "refs_extra.json"):
    _p = ROOT / "wp" / _extra
    if _p.exists():
        REFS.update(json.loads(_p.read_text()))
FIG = ROOT / "wp" / "figures"
OUT: list[str] = []

CITED: list[str] = []


def ref_entry(key: str) -> dict:
    """arXiv entries: exact title and authors from the live arXiv API (refs_raw.json);
    venue from the verified notes (refs.json). Other entries: refs.json as verified live."""
    if key not in REFS:
        raise KeyError(f"unknown citation key {key}")
    r = REFS[key]
    raw = REFS_RAW.get(key)
    if raw and raw.get("status") == "resolved":
        venue = r["venue"]
        if "arxiv" not in venue.lower():
            venue = venue + f"; arXiv:{raw['arxiv_id'].split('v')[0]}"
        return {"authors": raw["authors"], "title": raw["title"], "venue": venue, "url": r["url"]}
    return {"authors": r["authors"], "title": r["title"], "venue": r["venue"], "url": r["url"]}


def cite(text: str) -> str:
    def repl(m):
        keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
        nums = []
        for k in keys:
            ref_entry(k)
            if k not in CITED:
                CITED.append(k)
            nums.append(str(CITED.index(k) + 1))
        return '<span class="cite">[' + ", ".join(nums) + "]</span>"
    return re.sub(r"\[@([^\]]+)\]", repl, text)


# ----------------------------------------------------------------------------
# HTML helpers
# ----------------------------------------------------------------------------
OUT: list[str] = []


def p(text: str):
    OUT.append(f"<p>{cite(text)}</p>")


def h2(num: str, text: str, anchor: str):
    OUT.append(f'<h2 id="{anchor}"><span class="num">{num}</span>{text}</h2>')


def h3(text: str):
    OUT.append(f"<h3>{text}</h3>")


def eq(tex: str, display: bool = True):
    OUT.append(f'<div class="eq"><span class="katex-src" data-display="{1 if display else 0}">{html.escape(tex)}</span></div>')


def ieq(tex: str) -> str:
    return f'<span class="katex-src" data-display="0">{html.escape(tex)}</span>'


def table(headers: list[str], rows: list[list[str]], caption: str = "", cls: str = ""):
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cite(c)}</td>" for c in r) + "</tr>" for r in rows)
    cap = f"<caption>{cite(caption)}</caption>" if caption else ""
    OUT.append(f'<table class="{cls}">{cap}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>')


def figure(svg: str, num: int, caption: str):
    content = (FIG / svg).read_text()
    content = re.sub(r"<\?xml[^>]*\?>", "", content)
    content = re.sub(r"<!DOCTYPE[^>]*>", "", content)
    m = re.search(r'<svg[^>]*\bwidth="([0-9.]+)pt"', content)
    cap = f' style="max-width:{float(m.group(1)) * 1.6:.0f}px;margin:0 auto"' if m else ""
    OUT.append(f'<figure id="fig{num}"><div class="figwrap"{cap}>{content}</div><figcaption><b>Figure {num}.</b> {cite(caption)}</figcaption></figure>')


def callout(title: str, body: str, kind: str = "note"):
    OUT.append(f'<div class="callout {kind}"><div class="ct">{title}</div><div>{cite(body)}</div></div>')


def algo(title: str, lines: list[str]):
    body = "\n".join(html.escape(l) for l in lines)
    OUT.append(f'<div class="algo"><div class="at">{title}</div><pre>{body}</pre></div>')


def ul(items: list[str]):
    OUT.append("<ul>" + "".join(f"<li>{cite(i)}</li>" for i in items) + "</ul>")


def ol(items: list[str]):
    OUT.append("<ol>" + "".join(f"<li>{cite(i)}</li>" for i in items) + "</ol>")


def fmt(x: float, nd: int = 2) -> str:
    return f"{x:,.{nd}f}"




def image_grid(items: list[tuple[str, str]], num: int, caption: str, width: int = 900) -> None:
    """Embed real screenshots as JPEG data URIs in a two-column grid.

    items: (path, label) pairs. Images are resized to `width` pixels and re-encoded at
    quality 80 so the single-file HTML stays small; originals ship in the package.
    """
    import base64
    import io

    from PIL import Image

    cells = []
    for path, label in items:
        im = Image.open(path).convert("RGB")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=80, optimize=True)
        uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
        cells.append(f'<div class="shot"><img src="{uri}" alt="{html.escape(label)}"><div class="shot-l">{html.escape(label)}</div></div>')
    OUT.append(f'<figure id="fig{num}"><div class="shots">{"".join(cells)}</div><figcaption><b>Figure {num}.</b> {cite(caption)}</figcaption></figure>')
