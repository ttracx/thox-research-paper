"""ThoxOS paper figures from exp/results/summary.json (SVG, Inter / JetBrains Mono, THOX green)."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import NullFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
S = json.loads((ROOT / "exp" / "results" / "summary.json").read_text())
FIG = ROOT / "wp" / "figures"
FIG.mkdir(exist_ok=True)
GREEN = "#047C3D"; GREEN2 = "#05A451"; INK = "#111827"; GREY = "#6B7280"; LIGHT = "#C7CCD4"; PALE = "#E6F4EC"; RED = "#B91C1C"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "600",
                     "axes.edgecolor": GREY, "axes.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "xtick.color": GREY, "ytick.color": GREY, "legend.fontsize": 8, "legend.frameon": False})
MONO = {"family": "JetBrains Mono"}


def save(fig, name):
    fig.savefig(FIG / name, format="svg", bbox_inches="tight"); plt.close(fig); print("wrote", name)


def fig_syscalls():
    s = S["syscalls"]
    areas = ["files", "process", "memory", "security", "identity", "network", "ipc", "time", "other"]
    st = ["Complete", "Partial", "Policy-denied"]
    cols = {"Complete": GREEN, "Partial": LIGHT, "Policy-denied": INK}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.2), gridspec_kw={"width_ratios": [3, 2]})
    x = np.arange(len(areas)); bottom = np.zeros(len(areas))
    for k in st:
        vals = np.array([s["by_area"].get(a, {}).get(k, 0) for a in areas])
        a1.bar(x, vals, 0.65, bottom=bottom, color=cols[k], label=k)
        for i, (v, b) in enumerate(zip(vals, bottom)):
            if v >= 8:
                a1.text(i, b + v / 2, str(int(v)), ha="center", va="center", fontsize=7, color="#fff" if k != "Partial" else INK, **MONO)
        bottom += vals
    a1.set_xticks(x, areas, fontsize=8)
    a1.set_ylabel("Dispatched syscalls at the pin")
    a1.set_title(f"A. Ledger at the pin: {s['kpi_total']} syscalls by area")
    a1.legend(loc="upper right")
    loop = s["traced_loop"]
    top = loop[:18]
    names = [j["name"] for j in top][::-1]; calls = [j["calls"] for j in top][::-1]
    c = [cols.get(j["status"], RED) for j in top][::-1]
    a2.barh(np.arange(len(names)), calls, color=c)
    a2.set_yticks(np.arange(len(names)), names, fontsize=7, **MONO)
    a2.set_xscale("log")
    a2.set_xlabel("calls per run (authoring host, strace)")
    a2.set_title(f"B. Reference loop: {s['kpi_loop_distinct_total']} distinct,\n{s['kpi_loop_distinct_complete']} Complete, {s['kpi_loop_distinct_partial']} Partial", fontsize=9)
    save(fig, "fig_syscalls.svg")


def fig_memory():
    m = S["memory"]
    classes = list(m["classes"].keys())
    models = list(m["models"].keys())
    fig, ax = plt.subplots(figsize=(9.0, 3.3))
    x = np.arange(len(classes)); w = 0.26
    cols = [GREEN2, GREEN, INK]
    for i, (mod, col) in enumerate(zip(models, cols)):
        vals = [next(r["max_context_tokens"] for r in m["max_context"] if r["model"] == mod and r["quant"] == "Q4_K_M" and r["class"] == c and r["reserve_gb"] == 1.0) for c in classes]
        bars = ax.bar(x + (i - 1) * w, [max(v, 1) for v in vals], w, color=col, label=mod + " Q4_K_M")
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, max(v, 1) * 1.25, "no fit" if v == 0 else f"{v/1000:.0f}k", ha="center", fontsize=6.5, color=RED if v == 0 else INK, **MONO)
    ax.set_yscale("log"); ax.set_ylim(1, 1e8)
    ax.axhline(2048, color=GREY, lw=0.7, ls=":", label="2,048 and 32,768-token contexts")
    ax.axhline(32768, color=GREY, lw=0.7, ls=":")
    ax.set_xticks(x, classes, fontsize=7.5)
    ax.set_ylabel("Largest context that fits (tokens, log)")
    ax.set_title("Memory budget (eq. 3): fully resident Q4_K_M weights plus bf16 KV, 1.0 GB OS/runtime reserve")
    ax.legend(loc="upper left", ncol=4, fontsize=7)
    save(fig, "fig_memory.svg")


def fig_entitlement():
    e = S["entitlement"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.4, 3.2), gridspec_kw={"width_ratios": [1.4, 3.2], "wspace": 0.5})
    kinds = ["hmac", "ed25519"]; labels = ["HMAC-SHA256\n(shared secret)", "Ed25519\n(public key)"]
    med = [e[k]["timing"]["us_per_verify_median"] for k in kinds]
    lo = [e[k]["timing"]["us_per_verify_median"] - e[k]["timing"]["us_q1"] for k in kinds]
    hi = [e[k]["timing"]["us_q3"] - e[k]["timing"]["us_per_verify_median"] for k in kinds]
    a1.bar([0, 1], med, 0.55, color=[LIGHT, GREEN], yerr=[lo, hi], error_kw={"ecolor": INK, "lw": 0.8, "capsize": 3})
    for i, v in enumerate(med):
        a1.text(i, v * 1.05, f"{v:.0f} us", ha="center", fontsize=7.5, color=INK, **MONO)
    a1.set_xticks([0, 1], labels, fontsize=7.5)
    a1.set_ylabel("Verify time per token (us), median of 30 x 1,000")
    a1.set_title("A. Verify cost on the authoring host")
    a1.set_ylim(0, max(med) * 1.3)
    rows = ["P1 valid paid", "P2 grace +29 d", "P3 grace +31 d", "P4 tampered", "P5 malformed", "P6 Core unconditional", "P7 U and O required", "P8 unknown feature", "P9 forged by verifier holder", "P10 clock rollback (wall)", "P10 clock rollback (hwm)"]
    keys = ["P1_valid_paid_allowed", "P2_grace_29d_allowed", "P3_grace_31d_denied", "P4_tampered_denied", "P5_malformed_denied", "P6_core_unconditional", "P7_eq2_conjunction", "P8_unknown_denied", "P9_forged_accepted", "P10_rollback_wall_accepted", "P10_rollback_hwm_rejected"]
    want = {"P9_forged_accepted": False, "P10_rollback_wall_accepted": False}
    a2.axis("off")
    cell = []
    colors = []
    for k in keys:
        r = []; c = []
        for kind in kinds:
            v = e[kind]["properties"][k]
            if k in ("P9_forged_accepted", "P10_rollback_wall_accepted"):
                r.append("ACCEPTED" if v else "rejected"); c.append("#FDE2E2" if v else PALE)
            else:
                r.append("pass" if v else "FAIL"); c.append(PALE if v else "#FDE2E2")
        cell.append(r); colors.append(c)
    t = a2.table(cellText=cell, rowLabels=rows, colLabels=["HMAC design", "Ed25519 design"], cellColours=colors, loc="center", cellLoc="center", bbox=[0.42, 0.0, 0.58, 0.95])
    t.auto_set_font_size(False); t.set_fontsize(7); t.scale(1, 1.15)
    a2.set_title("B. Property outcomes (red = the hazard the design leaves open)")
    save(fig, "fig_entitlement.svg")


def fig_update():
    u = S["update"]["policies"]
    pols = ["contract", "no_sig", "no_counter", "in_place"]
    labels = ["full contract", "no signature check", "no attempt counter", "single slot in place"]
    metrics = [("known_good_end", "ends on known-good slot", GREEN), ("bricked", "left unbootable", RED), ("booted_tampered", "booted tampered image", INK), ("rollbacks", "automatic rollbacks", LIGHT)]
    fig, ax = plt.subplots(figsize=(8.6, 3.0))
    x = np.arange(len(pols)); w = 0.2
    for i, (k, lab, col) in enumerate(metrics):
        med = [u[p][k]["median"] for p in pols]; lo = [u[p][k]["median"] - u[p][k]["q1"] for p in pols]; hi = [u[p][k]["q3"] - u[p][k]["median"] for p in pols]
        bars = ax.bar(x + (i - 1.5) * w, med, w, color=col, label=lab, yerr=[lo, hi], error_kw={"ecolor": GREY, "lw": 0.7})
        for b, v in zip(bars, med):
            ax.text(b.get_x() + b.get_width() / 2, v + 3, f"{v:.0f}", ha="center", fontsize=6.5, color=INK, **MONO)
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_ylabel(f"per {S['update']['updates']} updates, median and IQR ({S['update']['seeds']} seeds)")
    ax.set_title("A/B update contract under injected faults (simulation)")
    ax.set_ylim(0, 240); ax.legend(ncol=4, fontsize=7, loc="upper center")
    save(fig, "fig_update.svg")


if __name__ == "__main__":
    fig_syscalls(); fig_memory(); fig_entitlement(); fig_update()
