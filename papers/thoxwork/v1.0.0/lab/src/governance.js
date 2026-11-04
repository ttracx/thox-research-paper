/*
 * THOX ThoxWork Evidence Lab: Digital Employee governance.
 *
 * Re-implements, at the level of their documented rules, the governance controls
 * reviewed in THOX's Digital Employee stack, and writes every decision to the
 * evidence chain:
 *   1. Action gateway (fail closed). Order: deployment ceiling, unknown action,
 *      tenant deny list, channel membership (workspaces stand in for channels), payload secret markers, payload
 *      size cap, then allow. Tenant policy can never widen the deployment ceiling.
 *   2. Approval gate for assignments. Approval is required before any external
 *      effect when any of four reasons holds: the caller kept the external-effect
 *      gate on (the default), a responsibility requires human approval, the
 *      sensitivity is confidential or restricted, or the effective autonomy
 *      (the lower of employee and role autonomy) is zero. Only a person may
 *      decide, the person must hold the role the request names, and a decision
 *      is final.
 *   3. Assignment lifecycle: seven states and eighteen legal transitions; every
 *      other move is refused and recorded.
 *   4. Handoffs: each handoff carries the SHA-256 of its body (as built); the lab
 *      additionally chains each handoff to the previous one (proposed), so a
 *      reviewer can detect a skipped, reordered or edited step.
 *   5. Memory: a semantic fact that collides with an earlier one on the same
 *      subject is kept and cross-tagged; nothing is merged or dropped.
 *
 * The lab produces deterministic demonstration text and never calls a model or
 * an external system. Copyright 2026 THOX.ai LLC. Apache License, Version 2.0.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("./evidence.js"));
  else root.ThoxGovernance = factory(root.ThoxEvidence);
})(typeof self !== "undefined" ? self : this, function (E) {
  "use strict";
  if (!E || typeof E.sha256 !== "function") throw new Error("ThoxGovernance needs ThoxEvidence loaded first");

  // ------------------------------------------------------------------ action gateway
  const KNOWN_ACTIONS = ["message", "delegate", "desk.read", "desk.write", "desk.list", "desk.exec", "sandbox.exec",
    "memory.read", "memory.write", "routine.run", "handoff.create", "mcp.list", "mcp.call"];
  const SECRET_MARKERS = ["api_key", "secret_key", "password=", "private key", "bearer "];

  /**
   * Evaluate one action. rules: { deploymentDeny: [], tenantDeny: [], sizeCap: number }.
   * Returns { allowed, rule } where rule names the first rule that decided.
   */
  function gateAction(employee, action, payload, workspace, rules) {
    const r = rules || {};
    const body = typeof payload === "string" ? payload : JSON.stringify(payload || "");
    if ((r.deploymentDeny || []).indexOf(action) !== -1) return { allowed: false, rule: "deployment_deny" };
    if (KNOWN_ACTIONS.indexOf(action) === -1) return { allowed: false, rule: "unknown_action" };
    if ((r.tenantDeny || []).indexOf(action) !== -1) return { allowed: false, rule: "deny_actions" };
    if (workspace && (employee.workspaces || []).indexOf(workspace) === -1) return { allowed: false, rule: "channel_membership" };
    const lower = body.toLowerCase();
    if (SECRET_MARKERS.some((m) => lower.indexOf(m) !== -1)) return { allowed: false, rule: "secret_leak" };
    if (new TextEncoder().encode(body).length > (r.sizeCap || 256000)) return { allowed: false, rule: "size_limit" };
    return { allowed: true, rule: "default_allow" };
  }

  /** Route an action through the gateway and record the decision and its effect. */
  function requestAction(chain, employee, action, payload, workspace, rules) {
    const v = gateAction(employee, action, payload, workspace, rules);
    chain.append("policy.decision", "gateway", { employee: employee.id, action, workspace: workspace || null, allowed: v.allowed, rule: v.rule });
    if (v.allowed) chain.append("action.execute", employee.id, { action, mode: "simulated" });
    else chain.append("action.blocked", employee.id, { action, rule: v.rule });
    return v;
  }

  // ------------------------------------------------------------------ assignment lifecycle
  const STATES = ["queued", "running", "awaitingApproval", "blocked", "completed", "failed", "cancelled"];
  const TRANSITIONS = {
    queued: ["running", "blocked", "failed", "cancelled"],
    running: ["awaitingApproval", "blocked", "completed", "failed", "cancelled"],
    awaitingApproval: ["running", "blocked", "failed", "cancelled"],
    blocked: ["queued", "running", "failed", "cancelled"],
    completed: [],
    failed: ["queued"],
    cancelled: [],
  };
  const EDGE_COUNT = Object.values(TRANSITIONS).reduce((a, t) => a + t.length, 0);

  /** Attempt a transition; records the attempt either way and returns true if applied. */
  function transition(chain, assignment, to, actor) {
    if (STATES.indexOf(to) === -1) throw new RangeError("unknown assignment state: " + to);
    const from = assignment.state;
    const ok = TRANSITIONS[from].indexOf(to) !== -1;
    chain.append("lifecycle.transition", actor, { assignment: assignment.id, from, to, result: ok ? "applied" : "refused" });
    if (ok) { assignment.state = to; assignment.version = (assignment.version || 0) + 1; }
    return ok;
  }

  // ------------------------------------------------------------------ approval gate
  const SENSITIVITY = ["public", "internal", "confidential", "restricted"];
  const AGENT_PREFIXES = ["emp_", "agent:", "asg_", "svc:", "de:"];

  /** Reasons approval is required for this assignment; empty means no approval needed. */
  function approvalReasons(a) {
    const reasons = [];
    if (a.externalEffectGate !== false) reasons.push("external effect gate on");
    if ((a.responsibilities || []).some((r) => r.requiresHumanApproval)) reasons.push("responsibility requires a person");
    if (SENSITIVITY.indexOf(a.sensitivity) >= 2) reasons.push("sensitivity " + a.sensitivity);
    if (Math.min(a.employeeAutonomy, a.roleAutonomy) === 0) reasons.push("effective autonomy 0");
    return reasons;
  }

  class ApprovalDesk {
    /** roleFor(sensitivity) names the approver role the organization requires. */
    constructor(chain, roleFor) { this.chain = chain; this.roleFor = roleFor; this.items = []; }

    /** Run an assignment to the point of external effect; hold it if approval is required. */
    submit(assignment) {
      if (assignment.state === "queued") transition(this.chain, assignment, "running", assignment.employee);
      const reasons = approvalReasons(assignment);
      if (!reasons.length) {
        transition(this.chain, assignment, "completed", assignment.employee);
        return { status: "completed", reasons };
      }
      transition(this.chain, assignment, "awaitingApproval", assignment.employee);
      const item = { id: "apr-" + (this.items.length + 1), assignment, requiredRole: this.roleFor(assignment.sensitivity), reasons, decision: null };
      this.items.push(item);
      this.chain.append("approval.request", assignment.employee, { approval: item.id, assignment: assignment.id, action: assignment.action, reasons, required_role: item.requiredRole });
      return { status: "awaitingApproval", approval: item.id, reasons, requiredRole: item.requiredRole };
    }

    /** A decision by subject holding roles; approve resumes the assignment, reject blocks it. */
    decide(approvalId, subject, roles, approve, note) {
      const item = this.items.find((i) => i.id === approvalId);
      if (!item) throw new RangeError("unknown approval " + approvalId);
      const refuse = (reason) => { this.chain.append("approval.decision", subject || "unknown", { approval: approvalId, result: "refused", reason }); return { ok: false, reason }; };
      if (item.decision) return refuse("already decided");
      if (typeof subject !== "string" || !subject || AGENT_PREFIXES.some((p) => subject.indexOf(p) === 0)) return refuse("approver must be a person");
      if ((roles || []).indexOf(item.requiredRole) === -1) return refuse("approver lacks role " + item.requiredRole);
      item.decision = { by: subject, approve: !!approve, note: note || "" };
      this.chain.append("approval.decision", subject, { approval: approvalId, result: approve ? "approved" : "rejected", role: item.requiredRole, note: note || "" });
      const a = item.assignment;
      transition(this.chain, a, approve ? "running" : "blocked", subject);
      if (approve) {
        this.chain.append("action.execute", a.employee, { action: a.action, mode: "simulated", approval: approvalId });
        transition(this.chain, a, "completed", a.employee);
      }
      return { ok: true, status: approve ? "completed" : "blocked" };
    }

    pending() { return this.items.filter((i) => !i.decision); }
  }

  // ------------------------------------------------------------------ handoffs
  /** Deterministic demonstration text for one step; no model is called. */
  function demoStepText(member, brief, stepIndex, total, prevHash) {
    return [
      "Demonstration output. Deterministic lab sample; no model or external action.",
      member.name + " (" + member.role + "), step " + (stepIndex + 1) + " of " + total + ".",
      "Brief: " + brief,
      stepIndex === 0 ? "First step: scope the work and list open questions." : "Builds on handoff " + prevHash.slice(0, 12) + ".",
      "Checklist: confirm assumptions; name the evidence still needed; mark claims that need review.",
    ].join("\n");
  }

  /**
   * Run an ordered task. Each handoff carries body_sha256 (as built) and a chained
   * hash committing to the brief, the member and the previous handoff (proposed).
   */
  function runOrderedTask(chain, team, brief, opts) {
    if (!Array.isArray(team) || team.length === 0) throw new TypeError("team must be a non-empty array");
    if (typeof brief !== "string" || !brief.trim()) throw new TypeError("brief must be a non-empty string");
    const o = opts || {};
    const taskId = o.taskId || "task-" + E.sha256(brief).slice(0, 8);
    let prev = E.GENESIS;
    const handoffs = [];
    team.forEach((m, i) => {
      if (m.status === "offline") throw new Error(m.name + " is offline");
      const text = (o.textFor || demoStepText)(m, brief, i, team.length, prev);
      const bodySha = E.sha256(text);
      const hash = E.sha256(E.canonical({ task: taskId, step: i, member: m.id, brief_sha256: E.sha256(brief), body_sha256: bodySha, prev }));
      handoffs.push({ task: taskId, step: i, member: m.id, name: m.name, role: m.role, text, body_sha256: bodySha, prev, hash });
      chain.append("handoff", m.id, { task: taskId, step: i, body_sha256: bodySha, hash, prev });
      prev = hash;
    });
    chain.append("approval.request", "workspace", { approval: "review-" + taskId, action: "accept-task-output", reasons: ["review required before Done"] });
    return { taskId, handoffs, head: prev, status: "awaiting_review" };
  }

  /** Body-hash check only, as built: detects an edited body unless the hash was also rewritten. */
  function verifyBodies(handoffs) {
    for (let i = 0; i < handoffs.length; i++) if (!E.safeEqual(E.sha256(handoffs[i].text), handoffs[i].body_sha256)) return i;
    return -1;
  }

  /** Chained check (proposed): also detects a skipped, reordered or rewritten step. */
  function verifyHandoffs(handoffs, brief) {
    let prev = E.GENESIS;
    for (let i = 0; i < handoffs.length; i++) {
      const h = handoffs[i];
      if (h.step !== i || h.prev !== prev) return i;
      const bodySha = E.sha256(h.text);
      if (!E.safeEqual(bodySha, h.body_sha256)) return i;
      const want = E.sha256(E.canonical({ task: h.task, step: i, member: h.member, brief_sha256: E.sha256(brief), body_sha256: bodySha, prev }));
      if (!E.safeEqual(want, h.hash)) return i;
      prev = h.hash;
    }
    return -1;
  }

  // ------------------------------------------------------------------ memory contradictions
  /** Split "subject: value" style text at the first ':', '=', '->' or is/are/was/were. */
  function subjectOf(text) {
    const t = String(text).trim();
    const m = t.match(/^(.+?)\s*(?::|=|->|\bis\b|\bare\b|\bwas\b|\bwere\b)\s*(.+)$/i);
    if (!m) return null;
    const norm = (s) => s.toLowerCase().replace(/\s+/g, " ").replace(/\.$/, "").trim();
    return { subject: norm(m[1]), value: norm(m[2]) };
  }

  /** Store a semantic fact; a collision on the same subject is kept and cross-tagged, never merged. */
  function rememberFact(chain, store, employeeId, text) {
    const sv = subjectOf(text);
    const rec = { id: "fact-" + (store.length + 1), employee: employeeId, text, subject: sv ? sv.subject : null, value: sv ? sv.value : null, contradicts: [] };
    if (sv) {
      const clash = store.filter((f) => f.employee === employeeId && f.subject === sv.subject && f.value !== sv.value);
      rec.contradicts = clash.map((f) => f.id);
      clash.forEach((f) => { f.contradicts = f.contradicts.concat([rec.id]); });
    }
    store.push(rec);
    if (rec.contradicts.length) chain.append("memory.contradiction", employeeId, { fact: rec.id, collides_with: rec.contradicts, subject: rec.subject });
    return rec;
  }

  return { KNOWN_ACTIONS, gateAction, requestAction, STATES, TRANSITIONS, EDGE_COUNT, transition, approvalReasons, ApprovalDesk,
    runOrderedTask, verifyBodies, verifyHandoffs, subjectOf, rememberFact, demoStepText };
});
