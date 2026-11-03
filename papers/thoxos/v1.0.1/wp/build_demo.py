"""Embed summary.json into the ThoxOS demo page."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = json.loads((ROOT / "exp" / "results" / "summary.json").read_text())
slim = {"entitlement": {k: v for k, v in s["entitlement"].items() if k.startswith("kpi") or k in ("known_answer", "grace_days")} | {"core_features": ["local-chat", "local-models", "meshstack-local", "ota-security-updates", "device-portal"], "paid_features": ["meshstack-pro", "thoxroute-cloud", "fleet-console", "thoxbrain-sync"]},
        "update": {"kpi_contract_good": s["update"]["kpi_contract_good"], "updates": s["update"]["updates"]},
        "memory": {"models": s["memory"]["models"], "classes": s["memory"]["classes"], "kpi_4b_mini_ctx_r1": s["memory"]["kpi_4b_mini_ctx_r1"]},
        "syscalls": {"rows": json.loads((ROOT / "exp" / "results" / "syscalls.json").read_text())["rows"], "traced_loop": s["syscalls"]["traced_loop"], "kpi_loop_distinct_complete": s["syscalls"]["kpi_loop_distinct_complete"], "kpi_loop_distinct_total": s["syscalls"]["kpi_loop_distinct_total"]}}
out = (ROOT / "wp" / "demo_template.html").read_text().replace("/*__SUMMARY__*/", json.dumps(slim).replace("</", "<\\/"))
(ROOT / "dist").mkdir(exist_ok=True)
(ROOT / "dist" / "ThoxOS_Demo_v1.0.1.html").write_text(out)
print("demo", len(out) // 1000, "KB")
