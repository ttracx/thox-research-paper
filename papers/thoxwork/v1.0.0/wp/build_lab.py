"""Build the ThoxWork Evidence Lab page from lab/template.html.

Inlines the four lab modules, Inter and JetBrains Mono (woff2 data URIs) and
the measured figures from exp/results/summary.json, then writes:
  dist/ThoxWork_Evidence_Lab_v1.0.0.html   full document, opens offline
  lab/artifact/ThoxWork_Evidence_Lab.html  page content for the Artifact publish

Usage: python3 wp/build_lab.py
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NM = ROOT / "wp" / "node_modules" / "@fontsource"
VERSION = "1.0.0"


def font_css() -> str:
    out = []
    for fam, pkg, weights in (("Inter", "inter", (400, 500, 600, 700)), ("JetBrains Mono", "jetbrains-mono", (400, 500, 600, 700))):
        for w in weights:
            f = NM / pkg / "files" / f"{pkg}-latin-{w}-normal.woff2"
            if not f.exists():
                continue
            b64 = base64.b64encode(f.read_bytes()).decode()
            out.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    return "".join(out)


def measured() -> dict | None:
    p = ROOT / "exp" / "results" / "summary.json"
    if not p.exists():
        return None
    s = json.loads(p.read_text())
    ev, mg = s.get("evidence"), s.get("meshgroup")
    if not ev or not mg:
        return None
    h = ev["host"]
    return {
        "mg_agree": mg["agreement"]["agree"], "mg_total": mg["agreement"]["total"],
        "mg_lab_us_100": mg["timing"]["lab_js_n100"]["us_per_decision"]["median"],
        "ev_append_us_1000": ev["timing"]["n1000_keyed"]["append_us_per_record"]["median"],
        "ev_verify_ms_10000": ev["timing"]["n10000_keyed"]["verify_ms_total"]["median"],
        "matrix": ev["matrix"], "trials": ev["trials_per_cell"],
        "pl_agree": (s.get("planner") or {}).get("agree_all"), "pl_total": (s.get("planner") or {}).get("total"),
        "host": f"{h['cpus']} vCPU {h['cpu_model'] or h['arch']}, Node {h['node']}",
    }


def main() -> None:
    tpl = (ROOT / "lab" / "template.html").read_text()
    src = ROOT / "lab" / "src"
    page = (tpl.replace("/*__FONTS__*/", font_css())
               .replace("/*__EVIDENCE_JS__*/", (src / "evidence.js").read_text())
               .replace("/*__MESHGROUP_JS__*/", (src / "meshgroup.js").read_text())
               .replace("/*__GOVERNANCE_JS__*/", (src / "governance.js").read_text())
               .replace("/*__PLANNER_JS__*/", (src / "planner.js").read_text())
               .replace("/*__SUMMARY_JSON__*/null", json.dumps(measured())))
    assert "/*__" not in page, "unfilled template slot"
    art = ROOT / "lab" / "artifact"
    art.mkdir(parents=True, exist_ok=True)
    (art / "ThoxWork_Evidence_Lab.html").write_text(page)
    full = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">"
            "<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}[hidden]{display:none!important}img{max-width:100%}</style></head><body>"
            + page + "</body></html>")
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    out = dist / f"ThoxWork_Evidence_Lab_v{VERSION}.html"
    out.write_text(full)
    print("wrote", out, f"{out.stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    main()
