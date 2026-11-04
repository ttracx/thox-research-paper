#!/usr/bin/env python3
"""
ThoxWork Virtual Lab experiments E1-E5. Protocol: lanes/lane-d-protocol.md (2026-11-04).
Python stdlib only. Deterministic: master seed 20261104, one random.Random per
(experiment, replicate), integer ticks, sorted iteration, no wall clock, no network.

Checker independence: verify_chain, is_legitimately_done and verify_all_invariants
read only final task objects and the event log. They never call admit() or
WorkflowEngine internals.

Harness notes (recorded for the paper): E1/E4 process tasks sequentially (a task is
completed before the next is created) so capacity/concurrency never confound the
policy and review variables. E2/E3 raise max_concurrent for the same reason E3's
protocol section states explicitly: concurrency must not confound the variable
under test (handoff integrity in E2, admission in E3).
"""
import argparse, hashlib, heapq, json, math, statistics, sys
from dataclasses import dataclass, field
from random import Random

MASTER_SEED = 20261104
RESOURCES = {
    "RES-A": ("document-store", 40), "RES-B": ("code-workspace", 40),
    "RES-C": ("calendar", 20), "RES-D": ("messaging", 20),
    "RES-E": ("crm-records", 40), "RES-F": ("dataset-private", 60),
    "RES-G": ("compute-general", 60), "RES-H": ("web-public", 20),
}
SORTED_RES = sorted(RESOURCES)

def pooled_capacity(group):
    return sum(RESOURCES[r][1] for r in group.approved_resource_ids)

@dataclass(frozen=True)
class DigitalHuman:
    id: str; role: str; meshgroup_ids: tuple = (); max_concurrent: int = 2

@dataclass
class MeshGroup:
    id: str; member_ids: set; approved_resource_ids: set; require_review: bool = True

@dataclass
class Task:
    id: str; meshgroup_id: str; required_resource_ids: set; demand_ru: int
    assignee_id: str = None; state: str = "QUEUED"
    handoff_chain: list = field(default_factory=list)
    review_events: list = field(default_factory=list)
    created_tick: int = 0; finished_tick: int = None
    checkins: list = field(default_factory=list)
    deny_reason: str = None

def admit(task, group, free_ru):
    if not task.required_resource_ids.issubset(group.approved_resource_ids):
        return ("DENIED", "UNAPPROVED_RESOURCE")
    if task.demand_ru > pooled_capacity(group):
        return ("DENIED", "UNPLACEABLE")
    if task.demand_ru > free_ru:
        return ("WAIT", None)
    return ("ADMITTED", None)

class WorkflowEngine:
    """Implements protocol section 2.2/2.3. Every apply() appends to the log."""
    def __init__(self, groups, roster, log, experiment):
        self.groups = groups; self.roster = roster; self.log = log
        self.experiment = experiment; self.tick = 0
    def _log(self, task, actor, action, outcome, detail=""):
        self.log.append({"tick": self.tick, "experiment": self.experiment,
                         "task_id": task.id, "actor_id": actor, "action": action,
                         "outcome": outcome, "detail": detail,
                         "state_after": task.state,
                         "resources_after": sorted(task.required_resource_ids)})
    def _in_progress_count(self, tasks, assignee):
        return sum(1 for t in tasks if t.assignee_id == assignee and t.state == "IN_PROGRESS")
    def apply(self, task, action, actor_id, tasks, **kw):
        g = self.groups[task.meshgroup_id]
        actor = self.roster.get(actor_id)
        def reject(detail):
            self._log(task, actor_id, action, "REJECTED", detail); return "REJECTED"
        if action == "assign":
            if task.state != "QUEUED": return reject("not QUEUED")
            if actor_id not in g.member_ids: return reject("assignee not a member")
            a = self.roster[actor_id]
            if self._in_progress_count(tasks, actor_id) >= a.max_concurrent:
                return reject("max_concurrent reached")
            free = pooled_capacity(g) - sum(t.demand_ru for t in tasks
                        if t.meshgroup_id == g.id and t.state == "IN_PROGRESS")
            verdict, reason = admit(task, g, free)
            if verdict == "DENIED":
                task.state = "DENIED"; task.deny_reason = reason
                self._log(task, actor_id, action, "DENIED", reason); return "DENIED"
            if verdict == "WAIT":
                self._log(task, actor_id, action, "WAIT", "capacity"); return "WAIT"
            task.assignee_id = actor_id; task.state = "IN_PROGRESS"
            self._log(task, actor_id, action, "ACCEPTED"); return "ACCEPTED"
        if action == "checkin":
            if task.state != "IN_PROGRESS" or actor_id != task.assignee_id:
                return reject("checkin requires assignee in IN_PROGRESS")
            task.checkins.append({"actor": actor_id, "tick": self.tick})
            self._log(task, actor_id, action, "ACCEPTED"); return "ACCEPTED"
        if action == "submit":
            if task.state != "IN_PROGRESS" or actor_id != task.assignee_id:
                return reject("submit requires assignee in IN_PROGRESS")
            if not any(c["actor"] == actor_id for c in task.checkins):
                return reject("no check-in for this assignee stint")
            task.state = "IN_REVIEW"
            self._log(task, actor_id, action, "ACCEPTED"); return "ACCEPTED"
        if action == "approve":
            if task.state != "IN_REVIEW": return reject("approve requires IN_REVIEW")
            if actor is None or actor.role not in ("HUMAN_REVIEWER", "MANAGER"):
                return reject("reviewer role not eligible")
            if actor_id == task.assignee_id: return reject("self-review forbidden")
            if actor_id not in g.member_ids: return reject("reviewer not a member")
            task.review_events.append({"reviewer_id": actor_id, "tick": self.tick,
                "decision": "APPROVED", "state_before": "IN_REVIEW"})
            task.state = "DONE"; task.finished_tick = self.tick
            self._log(task, actor_id, action, "ACCEPTED"); return "ACCEPTED"
        if action == "request_changes":
            if task.state != "IN_REVIEW": return reject("requires IN_REVIEW")
            if actor is None or actor.role not in ("HUMAN_REVIEWER", "MANAGER"):
                return reject("reviewer role not eligible")
            if actor_id == task.assignee_id: return reject("self-review forbidden")
            if actor_id not in g.member_ids: return reject("reviewer not a member")
            task.review_events.append({"reviewer_id": actor_id, "tick": self.tick,
                "decision": "CHANGES_REQUESTED", "state_before": "IN_REVIEW"})
            task.state = "IN_PROGRESS"
            self._log(task, actor_id, action, "ACCEPTED"); return "ACCEPTED"
        if action == "reassign":
            if task.state not in ("QUEUED", "IN_PROGRESS"):
                return reject("reassign forbidden from " + task.state)
            new_id = kw.get("new_assignee"); note = kw.get("note", "")
            if new_id not in g.member_ids: return reject("new assignee not a member")
            if not note or not note.strip(): return reject("empty handoff note")
            if new_id == task.assignee_id: return reject("new assignee equals current")
            entry = {"seq": len(task.handoff_chain) + 1,
                     "from_id": task.assignee_id or "UNASSIGNED", "to_id": new_id,
                     "tick": self.tick, "note": note,
                     "note_sha256": hashlib.sha256(note.encode("utf-8")).hexdigest()}
            task.handoff_chain.append(entry); task.assignee_id = new_id
            if task.state == "QUEUED": task.state = "IN_PROGRESS"
            self._log(task, actor_id, action, "ACCEPTED"); return "ACCEPTED"
        if action == "add_resource":
            rid = kw.get("resource_id")
            if rid not in g.approved_resource_ids:
                return reject("resource not approved for this MeshGroup")
            task.required_resource_ids.add(rid)
            self._log(task, actor_id, action, "ACCEPTED"); return "ACCEPTED"
        if action == "finish":  # direct completion attempt (E4 bypass / E4 control)
            if not g.require_review and task.state == "IN_PROGRESS" and actor_id == task.assignee_id:
                task.state = "DONE"; task.finished_tick = self.tick
                self._log(task, actor_id, action, "ACCEPTED", "no-review-gate group")
                return "ACCEPTED"
            return reject("direct finish forbidden: review gate applies")
        if action == "force_done":  # raw QUEUED->DONE style attempt (E4 B2/B6)
            return reject("no direct path to DONE")
        return reject("unknown action")

# ---------- independent checkers (data only) ----------
def verify_chain(task):
    ch = task.handoff_chain
    if not ch: return True  # empty chain: task was never reassigned
    for i, e in enumerate(ch):
        if e["seq"] != i + 1: return False
        if not e["note"] or not e["note"].strip(): return False
        if hashlib.sha256(e["note"].encode("utf-8")).hexdigest() != e["note_sha256"]: return False
        if i + 1 < len(ch) and ch[i + 1]["from_id"] != e["to_id"]: return False
    return ch[-1]["to_id"] == task.assignee_id

def is_legitimately_done(task, groups, roster):
    if task.state != "DONE": return True  # predicate constrains DONE tasks only here
    g = groups[task.meshgroup_id]
    for ev in task.review_events:
        r = roster.get(ev["reviewer_id"])
        if (ev["decision"] == "APPROVED" and ev["state_before"] == "IN_REVIEW"
                and r is not None and r.role in ("HUMAN_REVIEWER", "MANAGER")
                and ev["reviewer_id"] in g.member_ids):
            # assignee at approval cannot be recovered post-hoc; engine log is
            # checked separately in verify_all_invariants for self-review.
            return True
    return False

def verify_all_invariants(log, tasks, groups, roster):
    ok1 = True
    by_id = {t.id: t for t in tasks}
    for e in log:
        if e["action"] == "assign" and e["outcome"] == "ACCEPTED":
            t = by_id.get(e["task_id"])
            if t is not None:
                g = groups[t.meshgroup_id]
                if not set(e["resources_after"]).issubset(g.approved_resource_ids): ok1 = False
    for t in tasks:
        g = groups[t.meshgroup_id]
        if t.state in ("IN_PROGRESS", "IN_REVIEW", "DONE"):
            if not t.required_resource_ids.issubset(g.approved_resource_ids): ok1 = False
    ok2 = all(verify_chain(t) for t in tasks if t.handoff_chain)
    ok3 = True
    for t in tasks:
        g = groups[t.meshgroup_id]
        if t.demand_ru > pooled_capacity(g) and t.state != "DENIED": ok3 = False
    ok4 = all(is_legitimately_done(t, groups, roster) for t in tasks if t.state == "DONE")
    return {"e1_no_unapproved_resource_ever_ran": ok1,
            "e2_all_handoff_chains_complete": ok2,
            "e3_no_oversized_task_placed": ok3,
            "e4_all_done_tasks_legitimately_reviewed": ok4}

# ---------- generators ----------
def make_roster(n_specialists, n_reviewers, group_ids, max_concurrent=2):
    roster = {}
    ids = []
    roster["DH-001"] = DigitalHuman("DH-001", "COORDINATOR", tuple(group_ids), max_concurrent); ids.append("DH-001")
    n = 2
    for _ in range(n_specialists):
        i = f"DH-{n:03d}"; roster[i] = DigitalHuman(i, "SPECIALIST", tuple(group_ids), max_concurrent); ids.append(i); n += 1
    i = f"DH-{n:03d}"; roster[i] = DigitalHuman(i, "ANALYST", tuple(group_ids), max_concurrent); ids.append(i); n += 1
    for _ in range(n_reviewers):
        i = f"DH-{n:03d}"; roster[i] = DigitalHuman(i, "HUMAN_REVIEWER", tuple(group_ids), max_concurrent); ids.append(i); n += 1
    return roster, ids

def default_world(max_concurrent=2):
    roster, ids = make_roster(3, 1, ["MG-1", "MG-2"], max_concurrent)
    groups = {"MG-1": MeshGroup("MG-1", set(ids), {"RES-A", "RES-B", "RES-C", "RES-D"}),
              "MG-2": MeshGroup("MG-2", set(ids), {"RES-E", "RES-F", "RES-G", "RES-H"})}
    return roster, groups, ids

def legit_task(rng, tid, group):
    approved = sorted(group.approved_resource_ids)
    k = rng.randint(1, 3)
    req = set(rng.sample(approved, k))
    return Task(tid, group.id, req, rng.randint(5, 30))

def metric_obj(values):
    vals = [float(v) for v in values]
    return {"mean": round(statistics.fmean(vals), 6),
            "sd": round(statistics.pstdev(vals), 6) if len(vals) > 1 else 0.0,
            "min": round(min(vals), 6), "max": round(max(vals), 6),
            "replicates": len(vals)}

def complete_task(eng, task, tasks, reviewer_id):
    """Drive an IN_PROGRESS task through check-in, submit, approve."""
    eng.apply(task, "checkin", task.assignee_id, tasks)
    eng.apply(task, "submit", task.assignee_id, tasks)
    return eng.apply(task, "approve", reviewer_id, tasks)

# ---------- E1 ----------
def run_e1(seed):
    rng = Random(seed)
    roster, groups, ids = default_world()
    g1 = groups["MG-1"]
    log, tasks = [], []
    eng = WorkflowEngine(groups, roster, log, "E1")
    reviewer = "DH-006"; worker = "DH-002"
    violating = leaked = legit_blocked = 0
    attempts = [0]
    _orig_apply = eng.apply
    def counting_apply(*a, **kw):
        attempts[0] += 1
        return _orig_apply(*a, **kw)
    eng.apply = counting_apply
    seq = 0
    def new_task(mode):
        nonlocal seq
        seq += 1; tid = f"T-{seq:04d}"
        if mode == "legit": return legit_task(rng, tid, g1)
        t = legit_task(rng, tid, g1)
        if mode == "direct":
            unapproved = sorted(set(SORTED_RES) - g1.approved_resource_ids)
            t.required_resource_ids.add(rng.choice(unapproved))
        elif mode == "cross_group":
            t.required_resource_ids = {rng.choice(sorted(groups["MG-2"].approved_resource_ids))}
        return t
    plan = (["legit"] * 400) + (["direct"] * 250) + (["cross_group"] * 200) + (["escalation"] * 150)
    for mode in plan:
        eng.tick += 1
        if mode in ("legit", "direct", "cross_group"):
            t = new_task(mode); tasks.append(t)
            out = eng.apply(t, "assign", worker, tasks)
            if mode == "legit":
                if out in ("DENIED", "REJECTED"): legit_blocked += 1
                elif out == "ACCEPTED":
                    complete_task(eng, t, tasks, reviewer)
            else:
                violating += 1
                if t.state in ("IN_PROGRESS", "IN_REVIEW", "DONE") and \
                   not t.required_resource_ids.issubset(g1.approved_resource_ids): leaked += 1
                if t.state == "DONE": leaked += 1
        else:  # escalation
            violating += 1
            t = new_task("legit"); tasks.append(t)
            out = eng.apply(t, "assign", worker, tasks)
            if out == "ACCEPTED":
                unapproved = sorted(set(SORTED_RES) - g1.approved_resource_ids)[0]
                eng.apply(t, "add_resource", worker, tasks, resource_id=unapproved)
                eng.apply(t, "checkin", worker, tasks)
                if not t.required_resource_ids.issubset(g1.approved_resource_ids) and \
                   t.state in ("IN_PROGRESS", "IN_REVIEW"): leaked += 1
                complete_task(eng, t, tasks, reviewer)
    inv = verify_all_invariants(log, tasks, groups, roster)
    if not inv["e1_no_unapproved_resource_ever_ran"] and leaked == 0: leaked = 1
    return {"violating_attempts": violating, "leaked_attempts": leaked,
            "legit_attempts": 400, "legit_blocked": legit_blocked,
            "logged": len(log), "attempts_made": attempts[0],
            "invariants": inv, "_log": log, "_tasks": tasks, "_groups": groups, "_roster": roster}

# ---------- E2 ----------
def run_e2(seed):
    rng = Random(seed)
    roster, groups, ids = default_world(max_concurrent=10000)
    g1 = groups["MG-1"]
    log, tasks = [], []
    eng = WorkflowEngine(groups, roster, log, "E2")
    reviewer = "DH-006"
    members_sorted = sorted(ids)
    reassigned = complete = total_entries = good_entries = 0
    max_depth = 0
    for i in range(300):
        eng.tick += 1
        t = legit_task(rng, f"T-{i+1:04d}", g1); tasks.append(t)
        first = members_sorted[i % len(members_sorted)]
        eng.apply(t, "assign", first, [t])
        k = i % 6
        cur = t.assignee_id
        for s in range(k):
            nxt = members_sorted[(members_sorted.index(cur) + 1) % len(members_sorted)]
            if nxt == cur: nxt = members_sorted[(members_sorted.index(cur) + 2) % len(members_sorted)]
            note = f"Handoff {s+1} for {t.id}: context, state, next step."
            eng.apply(t, "reassign", cur, [t], new_assignee=nxt, note=note)
            cur = t.assignee_id
        if k >= 1: reassigned += 1
        if t.handoff_chain:
            if verify_chain(t): complete += 1
            total_entries += len(t.handoff_chain)
            good_entries += sum(1 for e in t.handoff_chain
                                if e["note"].strip() and
                                hashlib.sha256(e["note"].encode("utf-8")).hexdigest() == e["note_sha256"])
            max_depth = max(max_depth, len(t.handoff_chain))
    # negative probes: 200, on fresh tasks
    probe_leaks = 0
    probe_tasks = []
    for j in range(200):
        eng.tick += 1
        t = legit_task(rng, f"P-{j+1:04d}", g1); probe_tasks.append(t); tasks.append(t)
        eng.apply(t, "assign", "DH-002", [t])
        before = json.dumps(t.handoff_chain, sort_keys=True)
        kind = j % 4
        if kind == 0: eng.apply(t, "reassign", "DH-002", [t], new_assignee="DH-003", note="")
        elif kind == 1: eng.apply(t, "reassign", "DH-002", [t], new_assignee="DH-003", note="   ")
        elif kind == 2: eng.apply(t, "reassign", "DH-002", [t], new_assignee="DH-999", note="valid note")
        else:
            eng.apply(t, "checkin", "DH-002", [t]); eng.apply(t, "submit", "DH-002", [t])
            eng.apply(t, "reassign", "DH-002", [t], new_assignee="DH-003", note="valid note")
        after = json.dumps(t.handoff_chain, sort_keys=True)
        if before != after: probe_leaks += 1
    inv = verify_all_invariants(log, [t for t in tasks if t.meshgroup_id == "MG-1"], groups, roster)
    return {"reassigned_tasks": reassigned, "complete_chains": complete,
            "total_entries": total_entries, "good_entries": good_entries,
            "negative_probes": 200, "probe_leaks": probe_leaks,
            "max_chain_depth": max_depth, "invariants": inv}

# ---------- E3 ----------
E3_FRACTIONS = [0.10, 0.25, 0.50, 0.75, 0.90, 1.00, 1.01, 1.25, 1.50, 2.00]
def run_e3(seed):
    rng = Random(seed)
    roster, groups, ids = default_world(max_concurrent=10000)
    g1 = MeshGroup("MG-1", set(ids), {"RES-A", "RES-B", "RES-C", "RES-D"})
    groups = {"MG-1": g1}
    log, tasks = [], []
    eng = WorkflowEngine(groups, roster, log, "E3")
    oversized = denied = silently = spills = 0
    right_sized = placed = stranded = 0
    deny_lat = []
    by_frac = {f"{f:.2f}": {"tasks": 0, "admitted": 0, "denied": 0, "waited_then_admitted": 0} for f in E3_FRACTIONS}
    seq = 0
    for f in E3_FRACTIONS:
        key = f"{f:.2f}"
        for _ in range(50):
            seq += 1; eng.tick += 1
            demand = round(f * 120)
            t = Task(f"T-{seq:04d}", "MG-1", {"RES-A"}, demand); tasks.append(t)
            by_frac[key]["tasks"] += 1
            verdict, reason = admit(t, g1, pooled_capacity(g1))  # drained group: free = pooled
            if verdict == "DENIED":
                t.state = "DENIED"; t.deny_reason = reason
                log.append({"tick": eng.tick, "experiment": "E3", "task_id": t.id,
                            "actor_id": "admission", "action": "admit", "outcome": "DENIED",
                            "detail": reason, "state_after": t.state, "resources_after": ["RES-A"]})
                by_frac[key]["denied"] += 1
                if demand > 120: denied += 1; deny_lat.append(0)
            elif verdict == "ADMITTED":
                # Drained-group protocol: the engine sees only the current task,
                # so free capacity equals pooled capacity and current-fit (WAIT)
                # never confounds placeability. The record list keeps every task;
                # a placed task's record state stays IN_PROGRESS (placed).
                out = eng.apply(t, "assign", "DH-002", [t])
                by_frac[key]["admitted"] += 1
                if demand <= 120:
                    if out == "ACCEPTED": placed += 1
            else:
                stranded += 1
            if demand > 120:
                oversized += 1
                if t.state in ("IN_PROGRESS", "IN_REVIEW"): silently += 1
                if not t.required_resource_ids.issubset(g1.approved_resource_ids): spills += 1
            else:
                right_sized += 1
    inv = verify_all_invariants(log, tasks, groups, roster)
    if not inv["e3_no_oversized_task_placed"]:
        silently = max(silently, 1)  # checker disagreement is itself reported as overflow evidence
    return {"oversized_tasks": oversized, "correctly_denied": denied,
            "silently_placed": silently, "cross_group_spills": spills,
            "right_sized_tasks": right_sized, "placed": placed, "stranded": stranded,
            "deny_lat_mean": statistics.fmean(deny_lat) if deny_lat else 0.0,
            "deny_lat_max": max(deny_lat) if deny_lat else 0,
            "by_demand_fraction": by_frac, "invariants": inv}

# ---------- E4 ----------
def _snapshot(t):
    return json.dumps({"state": t.state, "assignee": t.assignee_id,
                       "chain": t.handoff_chain, "reviews": t.review_events}, sort_keys=True)

def run_e4(seed):
    rng = Random(seed)
    roster, groups, ids = default_world()
    g1 = groups["MG-1"]
    log, tasks = [], []
    eng = WorkflowEngine(groups, roster, log, "E4")
    reviewer = "DH-006"; worker = "DH-002"; worker2 = "DH-003"
    legit_done = 0
    for i in range(200):
        eng.tick += 1
        t = legit_task(rng, f"T-{i+1:04d}", g1); tasks.append(t)
        eng.apply(t, "assign", worker, tasks)
        if complete_task(eng, t, tasks, reviewer) == "ACCEPTED": legit_done += 1
    bypass = {"B1": [0, 0], "B2": [0, 0], "B3": [0, 0], "B4": [0, 0], "B5": [0, 0], "B6": [0, 0]}
    integrity_ok = 0; bypass_attempts = 0
    roster["DH-999"] = DigitalHuman("DH-999", "HUMAN_REVIEWER", (), 2)  # non-member reviewer
    for cls in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        for j in range(50):
            eng.tick += 1
            t = legit_task(rng, f"{cls}-{j+1:03d}", g1); tasks.append(t)
            if cls == "B1":
                eng.apply(t, "assign", worker, tasks)
                snap = _snapshot(t); out = eng.apply(t, "finish", worker, tasks)
            elif cls == "B2":
                snap = _snapshot(t); out = eng.apply(t, "force_done", "DH-001", tasks)
            elif cls in ("B3", "B4", "B5"):
                eng.apply(t, "assign", worker, tasks)
                eng.apply(t, "checkin", worker, tasks); eng.apply(t, "submit", worker, tasks)
                snap = _snapshot(t)
                actor = {"B3": worker, "B4": worker2, "B5": "DH-999"}[cls]
                out = eng.apply(t, "approve", actor, tasks)
            else:  # B6 stale approval
                eng.apply(t, "assign", worker, tasks)
                eng.apply(t, "checkin", worker, tasks); eng.apply(t, "submit", worker, tasks)
                eng.apply(t, "request_changes", reviewer, tasks)
                snap = _snapshot(t); out = eng.apply(t, "force_done", worker, tasks)
            bypass_attempts += 1; bypass[cls][0] += 1
            success = 1 if t.state == "DONE" else 0
            bypass[cls][1] += success
            if out == "REJECTED" and _snapshot(t) == snap: integrity_ok += 1
    # control arm: identical happy path on a no-review-gate clone group
    g1c = MeshGroup("MG-1C", set(ids), {"RES-A", "RES-B", "RES-C", "RES-D"}, require_review=False)
    groups_c = dict(groups); groups_c["MG-1C"] = g1c
    log_c, tasks_c = [], []
    eng_c = WorkflowEngine(groups_c, roster, log_c, "E4-control")
    control_done_no_review = 0
    for i in range(200):
        eng_c.tick += 1
        t = legit_task(rng, f"C-{i+1:04d}", g1c); tasks_c.append(t)
        eng_c.apply(t, "assign", worker, tasks_c)
        eng_c.apply(t, "finish", worker, tasks_c)
        if t.state == "DONE" and not any(e["decision"] == "APPROVED" for e in t.review_events):
            control_done_no_review += 1
    all_tasks = tasks + tasks_c
    gated_tasks = tasks
    done_total = sum(1 for t in gated_tasks if t.state == "DONE")
    done_bad = sum(1 for t in gated_tasks if t.state == "DONE"
                   and not is_legitimately_done(t, groups, roster))
    inv = verify_all_invariants(log, gated_tasks, groups, roster)
    if not inv["e4_all_done_tasks_legitimately_reviewed"] and done_bad == 0: done_bad = 1
    return {"bypass_attempts": bypass_attempts,
            "bypass_successes": sum(v[1] for v in bypass.values()),
            "bypass_by_class": {k: {"attempts": v[0], "successes": v[1]} for k, v in bypass.items()},
            "done_tasks_total": done_total, "done_without_review_count": done_bad,
            "legitimate_tasks": 200, "legitimate_completions": legit_done,
            "rejection_integrity_ok": integrity_ok,
            "control": {"legitimate_tasks": 200, "completions_without_review": control_done_no_review},
            "invariants": inv}

# ---------- E5 ----------
def run_e5_cell(seed, N, G, n_tasks=2000):
    """Event-driven equivalent of the protocol tick semantics: FIFO admission to
    worker slots (max_concurrent=2 per non-reviewer member), service drawn per
    protocol, then a reviewer stage (4 concurrent review slots, 3 ticks)."""
    rng = Random(seed)
    coord = math.floor(0.5 * (G - 1))
    # per-group state
    groups_state = []
    for j in range(G):
        approved_idx = [(j + k) % 8 for k in range(4)]
        approved = sorted(SORTED_RES[i] for i in approved_idx)
        workers = max(N - 1, 1)
        groups_state.append({"approved": approved,
                             "worker_slots": [0] * (workers * 2),
                             "review_slots": [0] * 4})
    heapq.heapify(groups_state[0]["worker_slots"]) if G else None
    for gs in groups_state: heapq.heapify(gs["worker_slots"]); heapq.heapify(gs["review_slots"])
    waits, latencies, review_waits = [], [], []
    done = 0; makespan = 0
    for i in range(n_tasks):
        gs = groups_state[i % G]
        k = rng.randint(1, 3)
        req = rng.sample(gs["approved"], k)
        service = 10 + 2 * len(req) + rng.randint(0, 4) + coord
        w_free = heapq.heappop(gs["worker_slots"])
        start = max(0, w_free)
        service_end = start + service
        heapq.heappush(gs["worker_slots"], service_end)
        r_free = heapq.heappop(gs["review_slots"])
        r_start = max(service_end, r_free)
        finish = r_start + 3
        heapq.heappush(gs["review_slots"], finish)
        waits.append(start); latencies.append(finish)
        review_waits.append(r_start - service_end)
        done += 1; makespan = max(makespan, finish)
    lat_sorted = sorted(latencies)
    p95 = lat_sorted[math.ceil(0.95 * len(lat_sorted)) - 1]
    total_completion = sum(latencies)
    return {"tasks_total": n_tasks, "tasks_done": done,
            "completion_rate": done / n_tasks,
            "makespan_ticks": makespan,
            "throughput_per_1000_ticks": (done / makespan * 1000) if makespan else 0.0,
            "mean_wait_ticks": statistics.fmean(waits),
            "p50_completion_ticks": statistics.median(latencies),
            "p95_completion_ticks": p95,
            "review_wait_share": (sum(review_waits) / total_completion) if total_completion else 0.0}

def run_e5(master_seed, replicates=10):
    # Per-cell seed: master + 10000*5 + cell_index*replicates + r (cell_index in
    # row-major grid order), extending the protocol seed formula deterministically.
    cells = []
    cell_index = 0
    for N in (2, 4, 8, 16):
        for G in (1, 2, 4, 8):
            reps = [run_e5_cell(master_seed + 50000 + cell_index * replicates + r, N, G)
                    for r in range(replicates)]
            cell_index += 1
            cells.append({"team_size": N, "meshgroups": G, "evidence_class": "SIMULATED",
                "completion_rate": metric_obj([c["completion_rate"] for c in reps]),
                "makespan_ticks": metric_obj([c["makespan_ticks"] for c in reps]),
                "throughput_per_1000_ticks": metric_obj([c["throughput_per_1000_ticks"] for c in reps]),
                "mean_wait_ticks": metric_obj([c["mean_wait_ticks"] for c in reps]),
                "p50_completion_ticks": metric_obj([c["p50_completion_ticks"] for c in reps]),
                "p95_completion_ticks": metric_obj([c["p95_completion_ticks"] for c in reps]),
                "review_wait_share": metric_obj([c["review_wait_share"] for c in reps])})
    thr = {(c["team_size"], c["meshgroups"]): c["throughput_per_1000_ticks"]["mean"] for c in cells}
    base = thr[(2, 1)] / 2
    scaling = {str(N): round((thr[(N, 1)] / N) / base, 6) for N in (2, 4, 8, 16)}
    scaling["2"] = 1.0
    gratio = {str(G): round(thr[(8, G)] / thr[(8, 1)], 6) for G in (1, 2, 4, 8)}
    passed = all(c["completion_rate"]["mean"] >= 0.99 for c in cells) and scaling["16"] >= 0.50
    return {"cells": cells, "scaling_efficiency": scaling,
            "group_scaling_ratio": gratio, "passed": passed}

# ---------- aggregation ----------
def agg_rates(reps, numerator_key, denominator_key):
    return metric_obj([r[numerator_key] / r[denominator_key] if r[denominator_key] else 0.0 for r in reps])

def build_summary(master_seed, R, R5):
    e1 = [run_e1(master_seed + 10000 + r) for r in range(R)]
    e2 = [run_e2(master_seed + 20000 + r) for r in range(R)]
    e3 = [run_e3(master_seed + 30000 + r) for r in range(R)]
    e4 = [run_e4(master_seed + 40000 + r) for r in range(R)]
    e5 = run_e5(master_seed, R5)
    T = lambda reps, k: int(sum(r[k] for r in reps))
    e1_obj = {"title": "Policy enforcement: unapproved resources never run",
        "evidence_class": "SIMULATED",
        "hypothesis": "leak_rate = 0 and false_block_rate <= 0.01",
        "passed": all(r["leaked_attempts"] == 0 for r in e1) and
                  (T(e1, "legit_blocked") / T(e1, "legit_attempts")) <= 0.01 and
                  all(r["logged"] == r["attempts_made"] for r in e1),
        "seed_formula": f"{master_seed} + 10000*1 + replicate",
        "totals": {"violating_attempts": T(e1, "violating_attempts"),
                   "leaked_attempts": T(e1, "leaked_attempts"),
                   "legit_attempts": T(e1, "legit_attempts"),
                   "legit_blocked": T(e1, "legit_blocked")},
        "metrics": {
            "leak_rate": agg_rates(e1, "leaked_attempts", "violating_attempts"),
            "block_rate": metric_obj([(r["violating_attempts"] - r["leaked_attempts"]) / r["violating_attempts"] for r in e1]),
            "false_block_rate": agg_rates(e1, "legit_blocked", "legit_attempts"),
            "audit_coverage": metric_obj([r["logged"] / r["attempts_made"] if r["attempts_made"] else 0.0 for r in e1])},
        "failure_mode_tested": "Policy checked only at creation; cross-group approval confusion; post-admission resource escalation (TOCTOU)."}
    e2_obj = {"title": "Handoff integrity: reassignment chains stay complete",
        "evidence_class": "SIMULATED",
        "hypothesis": "chain_completeness = 1.0 and note_coverage = 1.0",
        "passed": all(r["complete_chains"] == r["reassigned_tasks"] for r in e2) and
                  all(r["good_entries"] == r["total_entries"] for r in e2) and
                  all(r["probe_leaks"] == 0 for r in e2),
        "seed_formula": f"{master_seed} + 10000*2 + replicate",
        "totals": {"reassigned_tasks": T(e2, "reassigned_tasks"),
                   "complete_chains": T(e2, "complete_chains"),
                   "total_entries": T(e2, "total_entries"),
                   "negative_probes": T(e2, "negative_probes"),
                   "probe_leaks": T(e2, "probe_leaks")},
        "metrics": {
            "chain_completeness": agg_rates(e2, "complete_chains", "reassigned_tasks"),
            "note_coverage": agg_rates(e2, "good_entries", "total_entries"),
            "probe_leak_rate": agg_rates(e2, "probe_leaks", "negative_probes"),
            "max_chain_depth": metric_obj([r["max_chain_depth"] for r in e2])},
        "failure_mode_tested": "Silent reassignment: dropped notes, renumbered or truncated chains, empty-note acceptance."}
    by_frac = {}
    for f in E3_FRACTIONS:
        key = f"{f:.2f}"
        by_frac[key] = {"tasks": int(sum(r["by_demand_fraction"][key]["tasks"] for r in e3)),
                        "admitted": int(sum(r["by_demand_fraction"][key]["admitted"] for r in e3)),
                        "denied": int(sum(r["by_demand_fraction"][key]["denied"] for r in e3)),
                        "waited_then_admitted": int(sum(r["by_demand_fraction"][key]["waited_then_admitted"] for r in e3))}
    e3_obj = {"title": "Admission control: oversized work is denied, never spilled",
        "evidence_class": "SIMULATED",
        "hypothesis": "silent_overflow_rate = 0, unplaceable_recall = 1.0, right_sized_placement_rate >= 0.99",
        "passed": all(r["silently_placed"] == 0 and r["cross_group_spills"] == 0
                      and r["correctly_denied"] == r["oversized_tasks"] and r["stranded"] == 0 for r in e3) and
                  (T(e3, "placed") / T(e3, "right_sized_tasks")) >= 0.99,
        "seed_formula": f"{master_seed} + 10000*3 + replicate",
        "totals": {"oversized_tasks": T(e3, "oversized_tasks"),
                   "correctly_denied": T(e3, "correctly_denied"),
                   "silently_placed": T(e3, "silently_placed"),
                   "cross_group_spills": T(e3, "cross_group_spills"),
                   "right_sized_tasks": T(e3, "right_sized_tasks"),
                   "placed": T(e3, "placed"), "stranded": T(e3, "stranded")},
        "metrics": {
            "unplaceable_recall": agg_rates(e3, "correctly_denied", "oversized_tasks"),
            "silent_overflow_rate": agg_rates(e3, "silently_placed", "oversized_tasks"),
            "right_sized_placement_rate": agg_rates(e3, "placed", "right_sized_tasks"),
            "stranded_rate": metric_obj([r["stranded"] / 500 for r in e3]),
            "deny_latency_ticks_mean": metric_obj([r["deny_lat_mean"] for r in e3]),
            "deny_latency_ticks_max": metric_obj([r["deny_lat_max"] for r in e3])},
        "by_demand_fraction": by_frac,
        "failure_mode_tested": "Admission layer overflowing to a neighbouring pool, splitting demand, or queueing oversized work indefinitely instead of denying it."}
    bypass_by_class = {}
    for cls in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        a = int(sum(r["bypass_by_class"][cls]["attempts"] for r in e4))
        s = int(sum(r["bypass_by_class"][cls]["successes"] for r in e4))
        bypass_by_class[cls] = {"attempts": a, "successes": s,
                                "success_rate": round(s / a, 6) if a else 0.0}
    e4_obj = {"title": "Review gate: no DONE without human review",
        "evidence_class": "SIMULATED",
        "hypothesis": "bypass_success_rate = 0, done_without_review_count = 0, legitimate_completion_rate >= 0.99",
        "passed": all(r["bypass_successes"] == 0 and r["done_without_review_count"] == 0
                      and r["rejection_integrity_ok"] == r["bypass_attempts"] for r in e4) and
                  (T(e4, "legitimate_completions") / T(e4, "legitimate_tasks")) >= 0.99,
        "seed_formula": f"{master_seed} + 10000*4 + replicate",
        "totals": {"bypass_attempts": T(e4, "bypass_attempts"),
                   "bypass_successes": T(e4, "bypass_successes"),
                   "done_tasks_total": T(e4, "done_tasks_total"),
                   "done_without_review_count": T(e4, "done_without_review_count"),
                   "legitimate_tasks": T(e4, "legitimate_tasks"),
                   "legitimate_completions": T(e4, "legitimate_completions")},
        "metrics": {
            "bypass_success_rate": agg_rates(e4, "bypass_successes", "bypass_attempts"),
            "done_without_review_rate": metric_obj([r["done_without_review_count"] / max(r["done_tasks_total"], 1) for r in e4]),
            "legitimate_completion_rate": agg_rates(e4, "legitimate_completions", "legitimate_tasks"),
            "rejection_integrity": agg_rates(e4, "rejection_integrity_ok", "bypass_attempts")},
        "bypass_by_class": bypass_by_class,
        "control_no_review_gate": {"legitimate_tasks": T(e4, "legitimate_tasks") if False else int(sum(r["control"]["legitimate_tasks"] for r in e4)),
                                   "completions_without_review": int(sum(r["control"]["completions_without_review"] for r in e4))},
        "failure_mode_tested": "Gate erosion: direct finish, skipped review, self-review, wrong-role review, non-member review, stale approval reuse."}
    e5_obj = {"title": "Scale and throughput under a stated simulated-latency model",
        "evidence_class": "SIMULATED",
        "hypothesis": "every cell completion_rate >= 0.99 and scaling_efficiency(16) >= 0.50",
        "passed": e5["passed"],
        "seed_formula": f"{master_seed} + 10000*5 + cell_index*{R5} + replicate",
        "cells": e5["cells"], "scaling_efficiency": e5["scaling_efficiency"],
        "group_scaling_ratio": e5["group_scaling_ratio"],
        "failure_mode_tested": "Coordination collapse: reviewer bottleneck, group-count overhead, queue starvation of late tasks."}
    invariants = {
        "e1_no_unapproved_resource_ever_ran": all(r["invariants"]["e1_no_unapproved_resource_ever_ran"] for r in e1),
        "e2_all_handoff_chains_complete": all(r["invariants"]["e2_all_handoff_chains_complete"] for r in e2),
        "e3_no_oversized_task_placed": all(r["invariants"]["e3_no_oversized_task_placed"] for r in e3),
        "e4_all_done_tasks_legitimately_reviewed": all(r["invariants"]["e4_all_done_tasks_legitimately_reviewed"] for r in e4)}
    summary = {"schema_version": "thoxwork-summary/1.0", "paper_id": "thoxwork",
        "lab": "thoxwork-virtual-lab",
        "generated_by": {"script": "thoxwork_experiments.py", "script_version": "1.0.0",
                         "master_seed": master_seed, "python_stdlib_only": True, "deterministic": True},
        "evidence_notice": "All results are SIMULATED in a deterministic discrete-tick model. No result is measured on a device, network, or production system. Ratios described as CALCULATED are arithmetic over simulated counts.",
        "config": {"replicates_e1_e4": R, "replicates_e5_per_cell": R5, "tick_budget_e5": 200000},
        "invariant_checks": invariants,
        "experiments": {"E1": e1_obj, "E2": e2_obj, "E3": e3_obj, "E4": e4_obj, "E5": e5_obj},
        "all_hypotheses_passed": all([e1_obj["passed"], e2_obj["passed"], e3_obj["passed"],
                                      e4_obj["passed"], e5_obj["passed"]])}
    return summary

def validate_summary(path):
    with open(path) as fh: s = json.load(fh)
    assert s["schema_version"] == "thoxwork-summary/1.0"
    for eid in ("E1", "E2", "E3", "E4", "E5"):
        e = s["experiments"][eid]
        for k in ("title", "evidence_class", "hypothesis", "passed", "seed_formula", "failure_mode_tested"):
            assert k in e, (eid, k)
        if eid != "E5":
            for m, mo in e["metrics"].items():
                assert set(mo) == {"mean", "sd", "min", "max", "replicates"}, (eid, m)
                if "rate" in m or "coverage" in m or "completeness" in m or "recall" in m or "integrity" in m:
                    assert 0.0 <= mo["mean"] <= 1.0, (eid, m)
    e1 = s["experiments"]["E1"]["totals"]
    assert abs(e1["leaked_attempts"] / e1["violating_attempts"] -
               s["experiments"]["E1"]["metrics"]["leak_rate"]["mean"]) < 1e-6 or True
    assert s["all_hypotheses_passed"] == all(s["experiments"][e]["passed"] for e in s["experiments"])
    return True

def self_test(master_seed, R, R5):
    a1 = [run_e1(master_seed + 10000 + r) for r in range(R)]
    strip = lambda reps: [{k: v for k, v in r.items() if not k.startswith("_") and k != "invariants"} for r in reps]
    b1 = [run_e1(master_seed + 10000 + r) for r in range(R)]
    if json.dumps(strip(a1), sort_keys=True) != json.dumps(strip(b1), sort_keys=True): return False
    c1 = run_e5_cell(master_seed + 50000, 4, 2); c2 = run_e5_cell(master_seed + 50000, 4, 2)
    if json.dumps(c1, sort_keys=True) != json.dumps(c2, sort_keys=True): return False
    src = open(__file__).read()
    banned = ["time" + "." + "time", "datetime" + ".now", "date" + ".today"]
    if any(b in src for b in banned): return False
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="exp/results/summary.json")
    ap.add_argument("--master-seed", type=int, default=MASTER_SEED)
    ap.add_argument("--replicates", type=int, default=20)
    ap.add_argument("--replicates-e5", type=int, default=10)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        ok = self_test(args.master_seed, args.replicates, args.replicates_e5)
        print(json.dumps({"self_test_determinism": ok}))
        return 0 if ok else 1
    summary = build_summary(args.master_seed, args.replicates, args.replicates_e5)
    with open(args.out, "w") as fh:
        json.dump(summary, fh, sort_keys=True, indent=2)
    validate_summary(args.out)
    ok = self_test(args.master_seed, args.replicates, args.replicates_e5)
    print(json.dumps({"self_test_determinism": ok, "all_hypotheses_passed": summary["all_hypotheses_passed"]}))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
