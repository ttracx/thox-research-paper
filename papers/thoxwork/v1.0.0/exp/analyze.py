"""Reduce raw experiment JSON to exp/results/summary.json.

Every number in the paper, the figures and the lab page's measured-results panel
is read from summary.json. Medians and quartiles use the inclusive method.

Usage: python3 exp/analyze.py
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

R = Path(__file__).resolve().parent / "results"


def q(values: list[float]) -> dict:
    v = sorted(values)
    if len(v) < 2:
        return {"n": len(v), "median": v[0] if v else None, "q1": None, "q3": None, "min": v[0] if v else None, "max": v[-1] if v else None}
    q1, med, q3 = statistics.quantiles(v, n=4, method="inclusive")
    return {"n": len(v), "median": med, "q1": q1, "q3": q3, "min": v[0], "max": v[-1]}


def load(name: str):
    p = R / name
    return json.loads(p.read_text()) if p.exists() else None


def evidence_summary(e1: dict) -> dict:
    timing = {}
    for n in sorted({t["n"] for t in e1["timing"]}):
        for keyed in (False, True):
            rows = [t for t in e1["timing"] if t["n"] == n and t["keyed"] == keyed]
            timing[f"n{n}_{'keyed' if keyed else 'plain'}"] = {
                "n": n, "keyed": keyed, "reps": len(rows),
                "append_us_per_record": q([r["append_us_per_record"] for r in rows]),
                "verify_us_per_record": q([r["verify_us_per_record"] for r in rows]),
                "verify_ms_total": q([r["verify_ms"] for r in rows]),
                "bundle_bytes": rows[0]["bundle_bytes"] if rows else None,
                "bundle_bytes_per_record": (rows[0]["bundle_bytes"] / n) if rows else None,
            }
    det = {}
    for d in e1["detection"]:
        key = f"{d['attack']}|{'keyed' if d['keyed'] else 'plain'}|{'anchored' if d['anchored'] else 'unanchored'}"
        det[key] = {"rate": d["rate"], "detected": d["detected"], "trials": d["trials"], "exact_position": d["chain_detected_at_exact_position"], "by": d["by"]}
    attacks = sorted({d["attack"] for d in e1["detection"]})
    configs = [("plain", "unanchored"), ("keyed", "unanchored"), ("plain", "anchored"), ("keyed", "anchored")]
    matrix = {a: {f"{k}|{an}": det[f"{a}|{k}|{an}"]["rate"] for k, an in configs} for a in attacks}
    # Position accuracy among chain-detected in-place edits (where an exact index exists).
    edits = [d for d in e1["detection"] if d["attack"] in ("edit_payload", "edit_actor") ]
    pos_ok = sum(d["chain_detected_at_exact_position"] for d in edits)
    pos_n = sum(d["detected"] for d in edits)
    return {
        "kat": e1["known_answer_tests"], "host": e1["host"], "seed": e1["seed"], "timing": timing,
        "detection": det, "matrix": matrix, "trials_per_cell": e1["detection"][0]["trials"],
        "chain_length_for_detection": 1000, "edit_position_accuracy": pos_ok / pos_n if pos_n else None,
        "cells_total": len(e1["detection"]), "cells_full_detection": sum(1 for d in e1["detection"] if d["rate"] == 1.0),
        "cells_zero_detection": sum(1 for d in e1["detection"] if d["rate"] == 0.0),
    }


def meshgroup_summary(lab: dict, ref: dict) -> dict:
    timing = {}
    for impl, rows_all in (("lab_js", lab["timing"]), ("reference_python", ref["timing"])):
        for n in (10, 100, 1000):
            rows = [r for r in rows_all if r["n_nodes"] == n]
            timing[f"{impl}_n{n}"] = {"impl": impl, "n_nodes": n, "reps": len(rows), "us_per_decision": q([r["us_per_decision"] for r in rows])}
    a = lab["agreement"]
    total = a["total"]
    by = a["by_reference_outcome"]
    return {
        "agreement": {"total": total, "agree": a["agree"], "rate": a["rate"], "mismatches": len(a["mismatches"])},
        "outcome_mix": {k: {"count": v, "share": v / total} for k, v in sorted(by.items())},
        "scenarios": 200, "requests_per_scenario": 100, "nodes_per_scenario": 50,
        "exclusion_reason_counts": lab["exclusion_reason_counts"],
        "timing": timing, "host_js": lab["host"], "host_py": ref["host"],
    }


def product_tests_summary(pt: dict) -> dict:
    """Keep the harness output and add the figures the paper quotes, product suites only."""
    counted = [x for x in pt["suites"] if x.get("product") and x.get("counts_in_totals") and x.get("unit") == "tests"
               and x.get("mode") in ("run", "log") and x.get("passed") is not None]
    rerun = [x for x in counted if x["mode"] == "run"]
    logged = [x for x in counted if x["mode"] == "log"]
    tot = lambda rows, k: sum(int(x.get(k) or 0) for x in rows)
    repos = sorted({x["repo"] for x in pt["suites"] if x.get("product")})
    s = pt["summary"]
    s.update({
        "repos": len(repos), "repo_names": repos, "suites_with_counts": len(counted),
        "tests_passed": s["product_totals"]["tests_passed"], "tests_failed": s["product_totals"]["tests_failed"],
        "tests_skipped": s["product_totals"]["tests_skipped"], "tests_errors": s["product_totals"]["tests_errors"],
        "rerun_suites": len(rerun), "rerun_passed": tot(rerun, "passed"), "rerun_failed": tot(rerun, "failed"),
        "rerun_skipped": tot(rerun, "skipped"),
        "log_suites": len(logged), "log_passed": tot(logged, "passed"), "log_failed": tot(logged, "failed"),
        "log_errors": tot(logged, "errors"), "log_skipped": tot(logged, "skipped"),
        "not_run": [x["id"] for x in pt["suites"] if x.get("mode") == "not_run"],
        "rerun_repos": len({x["repo"] for x in rerun}),
        # The contract check is excluded: as configured it regenerates outputs without comparing them, so it cannot fail.
        "checks_run": sum(1 for x in pt["suites"] if x.get("unit") != "tests" and x.get("mode") == "run"
                          and x.get("check_passed") is not None and x.get("id") != "tw-contract"),
        "lab_tests": tot([x for x in pt["suites"] if not x.get("product")], "passed"),
    })
    return {"summary": s, "suites": pt["suites"], "host": pt.get("host"), "finished": pt.get("finished")}


def planner_summary(agr: dict, tim: dict | None) -> dict:
    """E3 agreement and E4 timing for the ThoxWork routing planner vs the lab re-implementation."""
    gen = agr["generator"]
    out = {
        "total": agr["total"], "agree_all": agr["agree_all"], "agree_strict": agr["agree_strict"],
        "mismatches": len(agr.get("mismatches") or []),
        "candidates_compared": agr["candidates"]["compared"], "candidates_agree": agr["candidates"]["agree"],
        "directories": gen["directories"], "requests_per_directory": gen["requestsPerDirectory"],
        "max_nodes": gen["nodesPerDirectory"]["max"], "max_groups": gen["groupsPerDirectory"]["max"],
        "outcome_mix": agr["outcomeMix"], "reasons_seen": len(agr["reasonMix"]),
        "candidate_reasons_seen": len(agr["candidateReasonCounts"]),
        "product_commit": agr["product"]["commit"][:7], "schema_valid": agr["inputs"]["schemaValid"],
        "invalid_total": agr["validationAgreement"]["total"], "invalid_agree": agr["validationAgreement"]["agree"],
        "invalid_kinds": len(agr["validationAgreement"]["byMutation"]),
        "early_denials_seen": len(agr["coverage"]["earlyDenialsSeen"]),
    }
    if tim:
        def med(exp: str, impl: str, param: str, value: int):
            # Experiment names changed between harness versions (b-preview and c-lab became b-c-preview);
            # the implementation and parameter identify the row.
            alias = {"product-requestSchema-parse-only": ("product-requestSchema-parse-only", "product-requestSchema-safeParse-only")}
            impls = alias.get(impl, (impl,))
            for r in tim["rows"]:
                if r["impl"] in impls and r["param"] == param and r["value"] == value:
                    return r["summary"]["usPerCallMedian"]
            return None
        t = {"reps": tim["protocol"]["repetitions"]}
        for n in (10, 50, 100):
            t[f"product_preview_us_n{n}"] = med("b-preview", "product-previewMeshGroupRoute", "nodes", n)
            t[f"product_parse_us_n{n}"] = med("b-preview", "product-requestSchema-parse-only", "nodes", n)
            t[f"lab_preview_us_n{n}"] = med("c-lab", "lab-preview", "nodes", n)
            t[f"lab_plan_us_n{n}"] = med("c-lab", "lab-plan-only", "nodes", n)
        for g in (1, 10, 50, 100):
            t[f"product_validate_us_g{g}"] = med("a-validation", "product-schema", "groups", g)
            t[f"lab_validate_us_g{g}"] = med("a-validation", "lab-validateDirectory", "groups", g)
        t["loadavg"] = tim.get("loadavg")
        out["timing"] = t
    return out


def main() -> None:
    summary: dict = {"version": "1.0.0"}
    e1 = load("evidence.json")
    if e1:
        summary["evidence"] = evidence_summary(e1)
    lab, ref = load("meshgroup_lab.json"), load("meshgroup_reference_timing.json")
    if lab and ref:
        summary["meshgroup"] = meshgroup_summary(lab, ref)
    div = load("admission_divergence.json")
    if div:
        summary["divergence"] = {k: div[k] for k in ("counts", "none_vs_pooled_causes", "shares", "reference_placements", "reference_placements_on_too_small_node",
                                                    "share_of_reference_placements_on_too_small_node", "demand_model", "seed")}
    agr = load("planner_agreement.json")
    if agr:
        summary["planner"] = planner_summary(agr, load("planner_timing.json"))
    pt = load("product_tests.json")
    if pt is not None:
        summary["product_tests"] = product_tests_summary(pt)
    for extra in ("kernel_gateway.json", "lab_flows.json"):
        data = load(extra)
        if data is not None:
            summary[extra.replace(".json", "")] = data.get("summary", data)
    (R / "summary.json").write_text(json.dumps(summary, indent=1))
    print("wrote", R / "summary.json", "sections:", ", ".join(k for k in summary if k != "version"))


if __name__ == "__main__":
    main()
