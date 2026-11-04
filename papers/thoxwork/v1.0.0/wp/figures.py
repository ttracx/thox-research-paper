"""Render the paper's data figures from exp/results/summary.json (and raw E1 timing).

SVG with svg.fonttype none so text renders in Inter and JetBrains Mono from the
page's embedded fonts. Brand: #047C3D on white, ink #09090B, neutral greys.

Usage: python3 wp/figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
S = json.loads((ROOT / "exp" / "results" / "summary.json").read_text())
FIG = ROOT / "wp" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GREEN, INK, GREY, LIGHT, RED, AMBER = "#047C3D", "#09090B", "#6B7280", "#D1D5DB", "#B91C1C", "#A15C07"
plt.rcParams.update({
    "svg.fonttype": "none", "font.family": "Inter", "font.size": 8.5, "axes.edgecolor": GREY, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 9,
    "axes.titleweight": "semibold", "legend.frameon": False, "legend.fontsize": 7.8,
})


def save(fig, name: str) -> None:
    fig.savefig(FIG / name, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", FIG / name)


def fig_detection() -> None:
    ev = S["evidence"]
    names = {"edit_payload": "Edit a decision", "edit_actor": "Change the actor", "swap_adjacent": "Swap two records",
             "delete_middle": "Delete a record", "truncate_tail": "Cut the tail", "rechain_suffix": "Edit and rebuild hashes"}
    order = ["edit_payload", "edit_actor", "swap_adjacent", "delete_middle", "truncate_tail", "rechain_suffix"]
    cols = [("plain|unanchored", "Hash links"), ("keyed|unanchored", "+ HMAC key"), ("plain|anchored", "+ Anchor"), ("keyed|anchored", "+ Key and anchor")]
    data = [[ev["matrix"][a][c] for c, _ in cols] for a in order]
    cmap = LinearSegmentedColormap.from_list("thox", ["#FEE2E2", "#FFFFFF", "#D1FAE5", GREEN])
    fig, ax = plt.subplots(figsize=(6.2, 2.6))
    ax.imshow(data, cmap=cmap, vmin=0, vmax=1, aspect="auto", rasterized=True)
    ax.set_xticks(range(len(cols)), [c[1] for c in cols])
    ax.set_yticks(range(len(order)), [names[a] for a in order])
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    for i, row in enumerate(data):
        for j, v in enumerate(row):
            ax.text(j, i, f"{v*100:.0f}%", ha="center", va="center", fontsize=8.5, fontfamily="JetBrains Mono",
                    color="#FFFFFF" if v > 0.75 else (RED if v < 0.25 else INK), fontweight="bold")
    ax.set_title(f"Detection rate, {ev['trials_per_cell']} seeded trials per cell, 1,000-record chain", loc="left")
    save(fig, "fig_detection.svg")


def fig_admission_latency() -> None:
    t = S["meshgroup"]["timing"]
    ns = [10, 100, 1000]
    fig, ax = plt.subplots(figsize=(3.2, 2.5))
    for impl, label, color, marker in (("lab_js", "Lab module (JavaScript)", GREEN, "o"), ("reference_python", "Reference policy (Python)", INK, "s")):
        med = [t[f"{impl}_n{n}"]["us_per_decision"]["median"] for n in ns]
        lo = [t[f"{impl}_n{n}"]["us_per_decision"]["q1"] for n in ns]
        hi = [t[f"{impl}_n{n}"]["us_per_decision"]["q3"] for n in ns]
        ax.plot(ns, med, marker=marker, color=color, label=label, lw=1.6, ms=4)
        ax.fill_between(ns, lo, hi, color=color, alpha=0.15, lw=0)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Nodes in inventory"); ax.set_ylabel("Microseconds per decision")
    ax.set_xticks(ns, ["10", "100", "1,000"])
    ax.legend(loc="upper left")
    ax.set_title("Admission decision cost (median, IQR band)", loc="left")
    save(fig, "fig_admission_latency.svg")


def fig_chain_cost() -> None:
    tm = S["evidence"]["timing"]
    ns = [100, 1000, 10000]
    fig, ax = plt.subplots(figsize=(3.2, 2.9))
    for keyed, color in ((False, GREY), (True, GREEN)):
        tag = "keyed" if keyed else "plain"
        for metric, ls, lab in (("append_us_per_record", "-", "append"), ("verify_us_per_record", "--", "verify")):
            med = [tm[f"n{n}_{tag}"][metric]["median"] for n in ns]
            ax.plot(ns, med, ls=ls, marker="o", ms=3.5, color=color, lw=1.5, label=f"{lab}, {'HMAC keyed' if keyed else 'hash only'}")
    ax.set_xscale("log")
    ax.set_xticks(ns, ["100", "1,000", "10,000"])
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Records in chain"); ax.set_ylabel("Microseconds per record")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=2, fontsize=6.8, columnspacing=1.0, handlelength=1.8)
    ax.set_title("Evidence chain cost (median of 30)", loc="left")
    save(fig, "fig_chain_cost.svg")


def fig_outcomes() -> None:
    mg = S["meshgroup"]
    mix = mg["outcome_mix"]
    labels = {"PLACE": "Placed", "NONE": "Admitted, no eligible node", "DENY:classification exceeds group policy": "Denied: classification",
              "DENY:tenant mismatch": "Denied: tenant", "DENY:unknown group": "Denied: unknown group"}
    order = ["PLACE", "NONE", "DENY:classification exceeds group policy", "DENY:tenant mismatch", "DENY:unknown group"]
    vals = [mix[k]["count"] for k in order if k in mix]
    names = [labels[k] for k in order if k in mix]
    fig, ax = plt.subplots(figsize=(6.2, 1.9))
    colors = [GREEN, AMBER, RED, RED, RED]
    ax.barh(names[::-1], vals[::-1], color=colors[: len(vals)][::-1], height=0.62)
    for i, v in enumerate(vals[::-1]):
        ax.text(v + max(vals) * 0.01, i, f"{v:,}", va="center", fontsize=8, fontfamily="JetBrains Mono", color=INK)
    ax.set_xlim(0, max(vals) * 1.14)
    ax.set_xlabel(f"Requests (of {mg['agreement']['total']:,}); every outcome matched the reference policy")
    ax.set_title("Admission outcomes across 200 seeded scenarios", loc="left")
    save(fig, "fig_outcomes.svg")


def fig_divergence() -> None:
    dv = S["divergence"]["counts"]
    cats = [
        ("Both admit; one node fits", dv["both_admit_fits_one_node"], GREEN),
        ("Reference places on a too-small\nnode; pooled rule fits one node", dv["reference_places_node_too_small"], AMBER),
        ("Both admit; pooled rule\nneeds several nodes", dv["both_admit_pooled_needs_spanning"], AMBER),
        ("Reference places; pooled\nrule denies UNPLACEABLE", dv["reference_places_pooled_denies_unplaceable"], RED),
        ("Reference finds no node;\npooled rule admits (sites)", dv["reference_none_pooled_admits"], RED),
        ("Both refuse", dv["both_refuse"], GREY),
    ]
    fig, ax = plt.subplots(figsize=(6.2, 2.7))
    names = [c[0] for c in cats][::-1]; vals = [c[1] for c in cats][::-1]; cols = [c[2] for c in cats][::-1]
    ax.barh(names, vals, color=cols, height=0.62)
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.01, i, f"{v:,}", va="center", fontsize=8, fontfamily="JetBrains Mono", color=INK)
    ax.set_xlim(0, max(vals) * 1.14)
    ax.tick_params(axis="y", labelsize=7.6)
    ax.set_xlabel(f"Requests (of {S['divergence']['counts']['total']:,})")
    ax.set_title("Reference rule vs pooled rule on the same requests", loc="left")
    save(fig, "fig_divergence.svg")


if __name__ == "__main__":
    fig_divergence()
    fig_detection()
    fig_admission_latency()
    fig_chain_cost()
    fig_outcomes()
