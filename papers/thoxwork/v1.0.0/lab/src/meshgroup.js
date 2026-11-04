/*
 * THOX ThoxWork Evidence Lab: MeshGroup admission.
 *
 * A MeshGroup binds people and Digital Employees to approved resources. A request
 * is admitted only when every rule below passes, and the result explains each
 * excluded node so a reviewer can see why. Decisions follow the THOX reference
 * admission policy; experiment E2 checks agreement case by case.
 *
 *   1. The request tenant equals the policy tenant.            else DENY tenant
 *   2. The request group exists in the policy.                 else DENY group
 *   3. Request classification <= the group's ceiling.          else DENY classification
 *   4. A node is eligible only if it belongs to the same tenant and group,
 *      is authenticated and healthy, serves the requested model, sits on an
 *      authenticated site that the group allows, and either shares the
 *      requester's site or cross-site use is enabled by policy AND consented
 *      to by the request (default deny across sites).
 *   5. Among eligible nodes, choose the one with the most free memory; ties go
 *      to the earliest node in the inventory. No eligible node: NO_PLACEMENT.
 *
 * Copyright 2026 THOX.ai LLC. Licensed under the Apache License, Version 2.0.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.ThoxMeshGroup = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const DENY = { TENANT: "tenant mismatch", GROUP: "unknown group", CLASSIFICATION: "classification exceeds group policy" };
  const EXCLUDE = {
    SCOPE: "outside tenant or group",
    UNAUTHENTICATED: "node not authenticated",
    UNHEALTHY: "node not healthy",
    MODEL: "model not served",
    SITE_UNKNOWN: "site not registered",
    SITE_UNAUTHENTICATED: "site not authenticated",
    SITE_NOT_ALLOWED: "site not allowed for group",
    CROSS_SITE: "cross-site needs policy and consent",
  };

  function assertString(v, name) { if (typeof v !== "string" || !v) throw new TypeError(name + " must be a non-empty string"); }

  /** Validate the policy shape before use; throws TypeError with the offending field. */
  function validatePolicy(policy) {
    if (!policy || typeof policy !== "object") throw new TypeError("policy must be an object");
    assertString(policy.tenant, "policy.tenant");
    if (typeof policy.cross_site_enabled !== "boolean") throw new TypeError("policy.cross_site_enabled must be boolean");
    if (!policy.groups || typeof policy.groups !== "object") throw new TypeError("policy.groups must be an object");
    for (const [gid, g] of Object.entries(policy.groups)) {
      if (!Number.isInteger(g.classification_max) || g.classification_max < 0) throw new TypeError("groups." + gid + ".classification_max must be a non-negative integer");
      if (!Array.isArray(g.allowed_sites)) throw new TypeError("groups." + gid + ".allowed_sites must be an array");
    }
    if (!policy.sites || typeof policy.sites !== "object") throw new TypeError("policy.sites must be an object");
    return true;
  }

  /**
   * Decide one request. Returns
   *   { verdict: "DENY", reason }                       request refused outright
   *   { verdict: "NO_PLACEMENT", excluded }             admitted, but no node qualifies
   *   { verdict: "PLACE", node, candidates, excluded }  admitted and placed
   * excluded is a list of { node, reason } in inventory order.
   */
  function decide(req, nodes, policy) {
    if (req.tenant !== policy.tenant) return { verdict: "DENY", reason: DENY.TENANT };
    const group = Object.prototype.hasOwnProperty.call(policy.groups, req.group) ? policy.groups[req.group] : null;
    // An empty group record counts as absent, matching the reference policy.
    if (!group || Object.keys(group).length === 0) return { verdict: "DENY", reason: DENY.GROUP };
    const cls = req.classification === undefined ? 0 : req.classification;
    if (cls > group.classification_max) return { verdict: "DENY", reason: DENY.CLASSIFICATION };

    const excluded = [];
    const candidates = [];
    for (const node of nodes) {
      let why = "";
      if (node.tenant !== req.tenant || node.group !== req.group) why = EXCLUDE.SCOPE;
      else if (!node.authenticated) why = EXCLUDE.UNAUTHENTICATED;
      else if (!node.healthy) why = EXCLUDE.UNHEALTHY;
      else if (node.models.indexOf(req.model) === -1) why = EXCLUDE.MODEL;
      else {
        const site = Object.prototype.hasOwnProperty.call(policy.sites, node.site) ? policy.sites[node.site] : null;
        if (!site || Object.keys(site).length === 0) why = EXCLUDE.SITE_UNKNOWN;
        else if (!site.authenticated) why = EXCLUDE.SITE_UNAUTHENTICATED;
        else if (group.allowed_sites.indexOf(node.site) === -1) why = EXCLUDE.SITE_NOT_ALLOWED;
        else if (node.site !== req.source_site && !(policy.cross_site_enabled && req.cross_site_consent === true)) why = EXCLUDE.CROSS_SITE;
      }
      if (why) excluded.push({ node: node.id, reason: why });
      else candidates.push(node);
    }
    if (!candidates.length) return { verdict: "NO_PLACEMENT", excluded };
    let best = candidates[0];
    for (let i = 1; i < candidates.length; i++) if (candidates[i].ram_free_gb > best.ram_free_gb) best = candidates[i];
    return { verdict: "PLACE", node: best.id, candidates: candidates.map((n) => n.id), excluded };
  }

  /** Collapse a decision to the comparable outcome used in agreement tests. */
  function outcome(d) {
    if (d.verdict === "DENY") return "DENY:" + d.reason;
    if (d.verdict === "NO_PLACEMENT") return "NONE";
    return "NODE:" + d.node;
  }

  /**
   * The pooled-capacity admission rule stated as Algorithm 1 in the THOX
   * ThoxWork research paper v1.0.0 (2026-11-04), kept beside the reference rule
   * above so a reviewer can compare the two records rather than merge them.
   *   1. required resources must be a subset of the group's approved set, else DENIED UNAPPROVED_RESOURCE
   *   2. demand above the group's pooled approved capacity, else DENIED UNPLACEABLE
   *   3. demand above currently free capacity: WAIT (stays queued, never placed elsewhere)
   *   4. otherwise ADMITTED
   * approved and capacity here are derived from the group's healthy, authenticated
   * nodes on authenticated, allowed sites; free equals capacity minus inUse.
   */
  function admitPooled(task, groupId, nodes, policy, inUse) {
    const group = policy.groups[groupId];
    if (!group) return { verdict: "DENIED", reason: "UNKNOWN_GROUP", approved: [], pooled: 0, free: 0 };
    const eligible = nodes.filter((n) => n.tenant === policy.tenant && n.group === groupId && n.authenticated && n.healthy &&
      policy.sites[n.site] && policy.sites[n.site].authenticated && group.allowed_sites.indexOf(n.site) !== -1);
    const approved = Array.from(new Set([].concat(...eligible.map((n) => n.models)))).sort();
    const pooled = eligible.reduce((a, n) => a + n.ram_free_gb, 0);
    const free = Math.max(0, pooled - (inUse || 0));
    const base = { approved, pooled, free, nodes: eligible.map((n) => n.id) };
    if (!task.required.every((r) => approved.indexOf(r) !== -1)) return Object.assign({ verdict: "DENIED", reason: "UNAPPROVED_RESOURCE" }, base);
    if (task.demand > pooled) return Object.assign({ verdict: "DENIED", reason: "UNPLACEABLE" }, base);
    if (task.demand > free) return Object.assign({ verdict: "WAIT", reason: "demand exceeds free capacity" }, base);
    const largest = eligible.reduce((m, n) => Math.max(m, n.ram_free_gb), 0);
    return Object.assign({ verdict: "ADMITTED", reason: "", fitsOneNode: task.demand <= largest, largestNode: largest }, base);
  }

  return { decide, outcome, validatePolicy, admitPooled, DENY, EXCLUDE };
});
