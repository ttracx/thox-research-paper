#!/usr/bin/env python3
"""
E8 - Admission-rule divergence under Algorithm 1 semantics
(ThoxWork paper v1.1.0).

WHY THIS RUN EXISTS.  The comprehensive companion edition measured the
divergence between its reference-kit placement rule and a port of the
paper's pooled rule.  The port deviates from Algorithm 1 in three ways,
each visible in the delivered source: (1) the kit's request-level
denials are pre-applied to the pooled arm, so the comparison does not
isolate placement; (2) the pooled sum runs over free memory in GB on
every node, not over the Definition 1 resource units of the devices
that run the requested resource (Definition 5 membership); (3) the
harness holds nothing in use, so the WAIT branch never fires.  This run
repeats the divergence study under the paper's own semantics and
quantifies each deviation.

SEMANTICS.  The verdict order is the oracle's admit()
(exp/thoxwork_experiments.py, v1.0.x, quoted verbatim):

    if not task.required_resource_ids.issubset(group.approved_resource_ids):
        return ("DENIED", "UNAPPROVED_RESOURCE")
    if task.demand_ru > pooled_capacity(group):
        return ("DENIED", "UNPLACEABLE")
    if task.demand_ru > free_ru:
        return ("WAIT", None)
    return ("ADMITTED", None)

Node refinement (stated in the paper): capacity(P, r) and free(P, r)
are summed over the devices of P that run r (Definitions 1 and 5).
The oracle's group-level pooled_capacity is the special case where
every approved resource is hosted on every device.

ARMS.
  P  Algorithm 1 as above (pooled, membership-aware, WAIT live).
  S  Strict single-node capacity rule: admit iff some device running r
     has free_j >= d.  (The honest single-node comparator.  The
     reference kit's own placement rule performs no capacity test at
     all; that flaw belongs to the E7 evidence family and is not
     re-measured here.)
  X  The companion port's semantics, re-implemented for deviation
     accounting only: the pooled sum runs over free units on ALL
     devices regardless of membership, and there is no WAIT branch
     (a would-be WAIT is returned as a refusal).  The approved-set
     gate is applied identically in all arms, isolating deviations
     (2) and (3); deviation (1) is documented from the delivered port
     source, not re-run.

PHASE 1 (probe): stateless verdicts of all three arms on identical
(snapshot, request) pairs: 25 replicates x 800 probes = 20,000.
PHASE 2 (stream): a sequential arrival stream (25 x 400 arrivals plus
a drain phase) under arm P, with completions freeing units, the WAIT
queue re-evaluated each tick, and the safety invariants asserted on
every tick.  Arm S runs the same stream on independent state for
context.

Seeds follow the oracle family convention: seed(E, rep) =
20261104 + 10000*E + rep, here E = 8.  Demand model and world
parameters are recorded in the output.  A re-run with the same code
reproduces every count exactly.

Usage: python3 e8_divergence.py [out.json]
Default out: results/e8_divergence.json next to this script.
"""

import json
import random
import sys
from pathlib import Path

MASTER = 20261104
MODELS = ["M0", "M1", "M2", "M3", "M4"]
UNAPPROVED = "MX"
NODE_CAPS = [60, 120, 240]
HOST_PROB = 0.55
REPLICATES = 25
PROBES_PER_REP = 800
ARRIVALS_PER_REP = 400
DRAIN_TICKS = 400


def draw_demand(rng):
    u = rng.random()
    if u < 0.50:
        return rng.randint(5, 60)
    if u < 0.80:
        return rng.randint(61, 240)
    if u < 0.92:
        return rng.randint(241, 480)
    return rng.randint(481, 1200)


def draw_request(rng):
    r = rng.choice(MODELS) if rng.random() < 0.88 else UNAPPROVED
    return r, draw_demand(rng)


def build_world(rng):
    nodes = []
    for j in range(12):
        hosts = {m for m in MODELS if rng.random() < HOST_PROB}
        nodes.append({"id": f"n{j}", "cap": rng.choice(NODE_CAPS),
                      "hosts": hosts})
    for m in MODELS:  # every approved model hosted by at least two devices
        hosting = [n for n in nodes if m in n["hosts"]]
        while len(hosting) < 2:
            n = rng.choice(nodes)
            if m not in n["hosts"]:
                n["hosts"].add(m)
                hosting.append(n)
    return nodes


def capacity(nodes, r):
    return sum(n["cap"] for n in nodes if r in n["hosts"])


def free_pool(free, nodes, r):
    return sum(free[n["id"]] for n in nodes if r in n["hosts"])


def verdict_pooled(nodes, free, r, d):
    """Algorithm 1 (oracle admit() order), node-refined."""
    if r not in MODELS:
        return "DENIED"
    if d > capacity(nodes, r):
        return "UNPLACEABLE"
    if d > free_pool(free, nodes, r):
        return "WAIT"
    return "ADMITTED"


def verdict_single(nodes, free, r, d):
    if r not in MODELS:
        return "REFUSED"
    if any(free[n["id"]] >= d for n in nodes if r in n["hosts"]):
        return "ADMITTED"
    return "REFUSED"


def verdict_port(nodes, free, r, d):
    """Port semantics: membership-blind sum, no WAIT."""
    if r not in MODELS:
        return "REFUSED"
    total_cap = sum(n["cap"] for n in nodes)
    total_free = sum(free.values())
    if d > total_cap:
        return "REFUSED"
    if d > total_free:
        return "REFUSED"
    return "ADMITTED"


# ---------------------------------------------------------------- phase 1

def phase1():
    counts = {
        "probes": 0,
        "P": {"ADMITTED": 0, "WAIT": 0, "UNPLACEABLE": 0, "DENIED": 0},
        "P_admitted_spanning_required": 0,
        "P_admitted_single_node_fit": 0,
        "S": {"ADMITTED": 0, "REFUSED": 0},
        "X": {"ADMITTED": 0, "REFUSED": 0},
        "pooled_only_admissions": 0,          # P admits, S refuses
        "pooled_only_spanning": 0,
        "pooled_only_waitclass": 0,           # P WAIT, S refuses (queueable only under pooling discipline)
        "S_admits_P_refuses": 0,              # must be 0 for ADMITTED-class
        "X_phantom_admissions": 0,            # X admits while free(P, r) < d
        "X_wait_collapse": 0,                 # X refuses while P says WAIT
        "X_admits_P_unplaceable": 0,          # X admits while d > capacity(P, r)
        "agree_all": 0,
    }
    examples = []
    for rep in range(REPLICATES):
        rng = random.Random(MASTER + 10000 * 8 + rep)
        nodes = build_world(rng)
        for _ in range(PROBES_PER_REP):
            free = {}
            for n in nodes:
                used = round(n["cap"] * rng.uniform(0.0, 0.95))
                free[n["id"]] = n["cap"] - used
            r, d = draw_request(rng)
            vp = verdict_pooled(nodes, free, r, d)
            vs = verdict_single(nodes, free, r, d)
            vx = verdict_port(nodes, free, r, d)
            counts["probes"] += 1
            counts["P"][vp] += 1
            counts["S"][vs] += 1
            counts["X"][vx] += 1
            if vp == "ADMITTED":
                single_fit = any(
                    free[n["id"]] >= d for n in nodes if r in n["hosts"])
                if single_fit:
                    counts["P_admitted_single_node_fit"] += 1
                else:
                    counts["P_admitted_spanning_required"] += 1
                if vs == "REFUSED":
                    counts["pooled_only_admissions"] += 1
                    if not single_fit:
                        counts["pooled_only_spanning"] += 1
                    if len(examples) < 12:
                        examples.append({
                            "model": r, "demand_ru": d,
                            "pool_free_ru": free_pool(free, nodes, r),
                            "largest_single_free_ru": max(
                                (free[n["id"]] for n in nodes
                                 if r in n["hosts"]), default=0),
                        })
            if vp == "WAIT" and vs == "REFUSED":
                counts["pooled_only_waitclass"] += 1
            if vs == "ADMITTED" and vp in ("UNPLACEABLE", "DENIED"):
                counts["S_admits_P_refuses"] += 1
            if vx == "ADMITTED" and r in MODELS:
                if d > capacity(nodes, r):
                    counts["X_admits_P_unplaceable"] += 1
                elif free_pool(free, nodes, r) < d:
                    counts["X_phantom_admissions"] += 1
            if vx == "REFUSED" and vp == "WAIT":
                counts["X_wait_collapse"] += 1
            p_class = "A" if vp == "ADMITTED" else "R"
            s_class = "A" if vs == "ADMITTED" else "R"
            x_class = "A" if vx == "ADMITTED" else "R"
            if p_class == s_class == x_class:
                counts["agree_all"] += 1
    return counts, examples


# ---------------------------------------------------------------- phase 2

def consume(free, nodes, r, d):
    """Greedy fill across hosting devices, largest free first.
    Returns (allocation dict node->ru, nodes_touched)."""
    hosting = sorted(
        (n for n in nodes if r in n["hosts"]),
        key=lambda n: -free[n["id"]],
    )
    alloc = {}
    remaining = d
    for n in hosting:
        if remaining <= 0:
            break
        take = min(free[n["id"]], remaining)
        if take > 0:
            alloc[n["id"]] = take
            free[n["id"]] -= take
            remaining -= take
    assert remaining == 0, "consume called without sufficient pool"
    return alloc, len(alloc)


def phase2():
    agg = {
        "arrivals": 0,
        "admitted_immediate": 0,
        "waited_then_admitted": 0,
        "still_waiting_at_end": 0,
        "unplaceable": 0,
        "denied_unapproved": 0,
        "admissions_spanning": 0,
        "admissions_single_node": 0,
        "invariant_violations": 0,
        "S_admitted": 0,
        "S_refused": 0,
        "S_refused_P_admitted": 0,
    }
    for rep in range(REPLICATES):
        rng = random.Random(MASTER + 10000 * 8 + 5000 + rep)
        nodes = build_world(rng)
        free = {n["id"]: n["cap"] for n in nodes}
        free_s = dict(free)
        stream = []
        for _ in range(ARRIVALS_PER_REP):
            r, d = draw_request(rng)
            stream.append((r, d, rng.randint(5, 40)))
        running = []   # (end_tick, alloc)
        queue = []     # (r, d, dur)
        p_verdict = {}
        for tick in range(ARRIVALS_PER_REP + DRAIN_TICKS):
            # completions
            still = []
            for end, alloc in running:
                if end <= tick:
                    for nid, ru in alloc.items():
                        free[nid] += ru
                else:
                    still.append((end, alloc))
            running = still
            # queue re-evaluation (FIFO scan; non-blocking)
            remaining_q = []
            for (r, d, dur) in queue:
                v = verdict_pooled(nodes, free, r, d)
                if v == "ADMITTED":
                    alloc, touched = consume(free, nodes, r, d)
                    running.append((tick + dur, alloc))
                    agg["waited_then_admitted"] += 1
                    if touched > 1:
                        agg["admissions_spanning"] += 1
                    else:
                        agg["admissions_single_node"] += 1
                else:
                    remaining_q.append((r, d, dur))
            queue = remaining_q
            # arrival
            if tick < ARRIVALS_PER_REP:
                idx = tick
                r, d, dur = stream[idx]
                agg["arrivals"] += 1
                v = verdict_pooled(nodes, free, r, d)
                p_verdict[idx] = v
                if v == "ADMITTED":
                    alloc, touched = consume(free, nodes, r, d)
                    running.append((tick + dur, alloc))
                    agg["admitted_immediate"] += 1
                    if touched > 1:
                        agg["admissions_spanning"] += 1
                    else:
                        agg["admissions_single_node"] += 1
                elif v == "WAIT":
                    queue.append((r, d, dur))
                elif v == "UNPLACEABLE":
                    agg["unplaceable"] += 1
                else:
                    agg["denied_unapproved"] += 1
                # arm S on independent state, same stream
                vs = verdict_single(nodes, free_s, r, d)
                if vs == "ADMITTED":
                    # consume on the largest-free hosting device
                    host = max(
                        (n for n in nodes if r in n["hosts"]),
                        key=lambda n: free_s[n["id"]],
                    )
                    free_s[host["id"]] -= d
                    agg["S_admitted"] += 1
                else:
                    agg["S_refused"] += 1
                    if v == "ADMITTED":
                        agg["S_refused_P_admitted"] += 1
            # invariants
            for n in nodes:
                if free[n["id"]] < 0 or free[n["id"]] > n["cap"]:
                    agg["invariant_violations"] += 1
            in_use = sum(n["cap"] - free[n["id"]] for n in nodes)
            accounted = sum(sum(a.values()) for _, a in running)
            if in_use != accounted:
                agg["invariant_violations"] += 1
        agg["still_waiting_at_end"] += len(queue)
    return agg


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).parent / "results" / "e8_divergence.json"
    )
    p1, examples = phase1()
    p2 = phase2()
    result = {
        "experiment": "E8 admission-rule divergence under Algorithm 1 "
                      "semantics (v1.1.0)",
        "semantics": "Oracle admit() verdict order (v1.0.x "
                     "exp/thoxwork_experiments.py) with Definition 1/5 "
                     "node refinement: capacity(P, r) and free(P, r) "
                     "summed over devices running r.",
        "arms": {
            "P": "Algorithm 1: pooled, membership-aware, WAIT live",
            "S": "strict single-node capacity rule (no queue)",
            "X": "companion port semantics: membership-blind free sum, "
                 "no WAIT (deviation accounting only)",
        },
        "seed_family": "20261104 + 10000*8 + rep (phase 2 offset +5000)",
        "world": {
            "nodes_per_group": 12,
            "node_caps_ru": NODE_CAPS,
            "models": MODELS,
            "host_prob": HOST_PROB,
            "demand_model": "mixture: 50% U[5,60], 30% U[61,240], "
                            "12% U[241,480], 8% U[481,1200] RU; "
                            "12% of requests ask an unapproved resource",
        },
        "phase1_probe": p1,
        "phase1_examples_pooled_only": examples,
        "phase2_stream": p2,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=1))
    print(json.dumps({"phase1": p1, "phase2": p2}, indent=1))
    print("wrote", out_path)


if __name__ == "__main__":
    main()
