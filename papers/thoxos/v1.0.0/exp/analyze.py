"""Single source of truth for the ThoxOS paper: write exp/results/summary.json."""
from __future__ import annotations

import json
from pathlib import Path

R = Path(__file__).with_name("results")


def load(n):
    return json.loads((R / n).read_text())


def main() -> int:
    e = load("entitlement.json"); u = load("update.json"); m = load("memory.json"); s = load("syscalls.json")
    pol = u["policies"]
    maxctx = {(x["model"], x["quant"], x["class"], x["reserve_gb"]): x["max_context_tokens"] for x in m["max_context"]}
    summary = {
        "entitlement": {
            "hmac": e["hmac"], "ed25519": e["ed25519"], "known_answer": e["known_answer"], "grace_days": e["grace_days"],
            "kpi_hmac_us": e["hmac"]["timing"]["us_per_verify_median"],
            "kpi_ed_us": e["ed25519"]["timing"]["us_per_verify_median"],
            "kpi_hmac_forged_accepted": e["hmac"]["properties"]["P9_forged_accepted"],
            "kpi_ed_forged_accepted": e["ed25519"]["properties"]["P9_forged_accepted"],
            "kpi_rollback_wall_accepted": e["ed25519"]["properties"]["P10_rollback_wall_accepted"],
            "kpi_rollback_hwm_rejected": e["ed25519"]["properties"]["P10_rollback_hwm_rejected"],
            "kpi_token_bytes_hmac": e["hmac"]["properties"]["token_bytes"],
            "kpi_token_bytes_ed": e["ed25519"]["properties"]["token_bytes"],
            "properties_pass": all(v for k, v in e["ed25519"]["properties"].items() if k.startswith("P") and not k.startswith("P9")),
        },
        "update": {
            "policies": pol, "faults": u["fault_probabilities"], "updates": u["updates_per_run"], "seeds": u["seeds"], "attempts": u["attempts"],
            "kpi_contract_good": pol["contract"]["known_good_end"]["median"], "kpi_contract_bricked": pol["contract"]["bricked"]["median"],
            "kpi_contract_rollbacks": pol["contract"]["rollbacks"]["median"], "kpi_contract_maxboots": pol["contract"]["recovery_boots_max"]["median"],
            "kpi_nosig_tampered": pol["no_sig"]["booted_tampered"]["median"], "kpi_nocounter_bricked": pol["no_counter"]["bricked"]["median"],
            "kpi_inplace_bricked": pol["in_place"]["bricked"]["median"], "kpi_inplace_good": pol["in_place"]["known_good_end"]["median"],
        },
        "memory": {
            "models": m["models"], "classes": m["classes"], "contexts": m["contexts"], "reserves_gb": m["reserves_gb"], "max_context": m["max_context"],
            "kpi_08b_air_ctx_r1": maxctx[("ThoxOS-Kernel-0.8B", "Q4_K_M", "E2 (Air, 2 GB)", 1.0)],
            "kpi_08b_air_ctx_r15": maxctx[("ThoxOS-Kernel-0.8B", "Q4_K_M", "E2 (Air, 2 GB)", 1.5)],
            "kpi_4b_mini_ctx_r1": maxctx[("ThoxOS-Kernel-4B", "Q4_K_M", "P4 (Mini, 4 GB)", 1.0)],
            "kpi_4b_mini_ctx_r15": maxctx[("ThoxOS-Kernel-4B", "Q4_K_M", "P4 (Mini, 4 GB)", 1.5)],
            "kpi_4b_clip_ctx_r1": maxctx[("ThoxOS-Kernel-4B", "Q4_K_M", "P6 (Clip, 6 GB)", 1.0)],
            "kpi_4b_air_ctx_r06": maxctx[("ThoxOS-Kernel-4B", "Q4_K_M", "E2 (Air, 2 GB)", 0.6)],
            "kpi_4b_q8_mini_ctx_r1": maxctx[("ThoxOS-Kernel-4B", "Q8_0", "P4 (Mini, 4 GB)", 1.0)],
            "kpi_27b_host16_ctx_r1": maxctx[("ThoxOS-Kernel-27B", "Q4_K_M", "Host 16 GB", 1.0)],
            "kpi_27b_host32_ctx_r1": maxctx[("ThoxOS-Kernel-27B", "Q4_K_M", "Host 32 GB", 1.0)],
            "kpi_27b_q8_host32_ctx_r1": maxctx[("ThoxOS-Kernel-27B", "Q8_0", "Host 32 GB", 1.0)],
            "kpi_27b_q8_host64_ctx_r1": maxctx[("ThoxOS-Kernel-27B", "Q8_0", "Host 64 GB", 1.0)],
        },
        "syscalls": {
            "pin": s["pin"], "totals": s["ledger_totals"], "by_area": s["by_area"], "traced_loop": s["traced_loop"],
            "loop_distinct": s["loop_distinct_by_status"], "loop_calls": s["loop_calls_by_status"], "loop_last_log_line": s["loop_last_log_line"],
            "kpi_total": sum(s["ledger_totals"].values()), "kpi_complete": s["ledger_totals"]["Complete"],
            "kpi_partial": s["ledger_totals"]["Partial"], "kpi_denied": s["ledger_totals"]["Policy-denied"],
            "kpi_loop_distinct_total": sum(s["loop_distinct_by_status"].values()),
            "kpi_loop_distinct_complete": s["loop_distinct_by_status"].get("Complete", 0),
            "kpi_loop_distinct_partial": s["loop_distinct_by_status"].get("Partial", 0),
            "kpi_loop_distinct_denied": s["loop_distinct_by_status"].get("Policy-denied", 0),
            "kpi_loop_distinct_missing": s["loop_distinct_by_status"].get("not-in-pinned-table", 0),
            "kpi_loop_calls_total": sum(s["loop_calls_by_status"].values()),
            "kpi_loop_calls_partial": s["loop_calls_by_status"].get("Partial", 0),
            "kpi_files_partial": s["by_area"]["files"].get("Partial", 0), "kpi_files_complete": s["by_area"]["files"].get("Complete", 0),
            "kpi_network_complete": s["by_area"]["network"].get("Complete", 0), "kpi_network_partial": s["by_area"]["network"].get("Partial", 0),
            "kpi_security_denied": s["by_area"]["security"].get("Policy-denied", 0), "kpi_identity_denied": s["by_area"]["identity"].get("Policy-denied", 0),
        },
    }
    (R / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: v for sec in summary.values() for k, v in sec.items() if k.startswith("kpi")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
