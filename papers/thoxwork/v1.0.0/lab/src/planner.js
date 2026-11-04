/*
 * THOX ThoxWork Evidence Lab: MeshGroup routing planner (preview only).
 *
 * A clean re-implementation, written from the documented rules, of the
 * ThoxWork MeshGroups routing preview. Given a MeshGroup directory and one
 * request, it reports which node the planner would choose and why every other
 * candidate is refused. It never executes, dispatches, authorizes or falls back
 * to hosted processing, and every result states so in four fixed fields.
 *
 * Rules, in the order they apply:
 *   0. Effective data class: the stricter of the workspace class and the payload
 *      class (public < internal < restricted). A public payload cannot
 *      downgrade a restricted workspace. With an unknown workspace the payload
 *      class stands and the request is denied in step 1.
 *   1. Early denials, first match wins, no candidates listed:
 *        organization_mismatch    request organization differs from the directory
 *        resource_unavailable     unknown group, principal, workspace or pool
 *        principal_revoked        principal inactive
 *        group_access_denied      principal lacks infer AND workspace.read in this group
 *        sponsor_access_denied    a digital employee's sponsor is inactive or lacks
 *                                 infer AND workspace.read in this same group
 *        resource_not_bound       workspace or pool not bound to the group
 *        task_not_supported       pool does not offer the task
 *        source_site_unavailable  named source site unknown or inactive
 *        source_context_invalid   named source node unknown or not at the source site
 *   2. Candidates: nodes bound to the group that serve the pool, in directory order.
 *   3. Locality: device_local (the source node), else private_remote (no source
 *      site), else same_site (at the source site), else private_cross_site.
 *   4. Deny reasons per candidate, all that apply, in this fixed order:
 *        node_unavailable, model_not_ready, node_observation_stale (older than
 *        90,000 ms or more than 5,000 ms in the future), data_class_denied,
 *        cross_site_denied (target outside the workspace home site, or a
 *        cross-site locality, without crossSite in all three policies),
 *        remote_access_denied (remote locality without remoteAccess in all
 *        three policies); and for every locality except device_local:
 *        mesh_opt_in_required, node_sharing_not_authorized,
 *        private_transport_unverified, site_gateway_unavailable (cross-site or
 *        remote with a target or source gateway not ready), relay_denied.
 *   5. Selection: eligible candidates ordered by locality (device, same site,
 *      cross-site, remote), then workspace home site first, then node ID in
 *      code unit order. The first is selected; none gives no_eligible_node.
 *
 * Time is an argument, so the module is pure: identical inputs give identical
 * results and the input is never modified. Experiment E3 compares it, field by
 * field, with the product planner on seeded directories.
 *
 * Copyright 2026 THOX.ai LLC. Licensed under the Apache License, Version 2.0.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.ThoxPlanner = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const SCHEMA_VERSION = "1.0.0";
  const STALE_AFTER_MS = 90000;
  const FUTURE_TOLERANCE_MS = 5000;
  const MAX_ITEMS = 100;
  const DATA_CLASSES = ["public", "internal", "restricted"];
  const DATA_CLASS_RANK = { public: 0, internal: 1, restricted: 2 };
  const TASKS = ["chat", "coding", "research", "embedding"];
  const ACTIONS = ["infer", "workspace.read", "tool.propose"];
  const KINDS = ["human", "digital_employee"];
  const LOCALITIES = ["device_local", "same_site", "private_cross_site", "private_remote"];
  const LOCALITY_RANK = { device_local: 0, same_site: 1, private_cross_site: 2, private_remote: 3 };
  const EARLY_DENIALS = [
    "organization_mismatch", "resource_unavailable", "principal_revoked", "group_access_denied",
    "sponsor_access_denied", "resource_not_bound", "task_not_supported", "source_site_unavailable",
    "source_context_invalid",
  ];
  const CANDIDATE_REASONS = [
    "node_unavailable", "model_not_ready", "node_observation_stale", "data_class_denied",
    "cross_site_denied", "remote_access_denied", "mesh_opt_in_required", "node_sharing_not_authorized",
    "private_transport_unverified", "site_gateway_unavailable", "relay_denied",
  ];
  const STATUS = { ELIGIBLE: "eligible_for_planning", NONE: "no_eligible_node", DENIED: "denied" };

  const ID_RE = /^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,99}$/;
  const TS_RE = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?(Z|([+-])(\d{2}):(\d{2}))$/;
  const HOP = Object.prototype.hasOwnProperty;

  // ------------------------------------------------------------------ timestamps
  function isLeapYear(y) { return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0; }
  function daysInMonth(y, m) { return m === 2 ? (isLeapYear(y) ? 29 : 28) : [4, 6, 9, 11].indexOf(m) !== -1 ? 30 : 31; }

  /**
   * Parse an ISO 8601 timestamp with a required offset (Z or +hh:mm / -hh:mm),
   * minutes required, seconds and a fraction of any length optional. Returns
   * epoch milliseconds (fraction truncated to whole milliseconds) or NaN when
   * the text is not a valid timestamp of that form. Engine independent: it
   * never calls Date.parse.
   */
  function parseTimestamp(text) {
    if (typeof text !== "string") return NaN;
    const m = TS_RE.exec(text);
    if (!m) return NaN;
    const y = +m[1], mo = +m[2], d = +m[3], h = +m[4], mi = +m[5];
    const s = m[6] === undefined ? 0 : +m[6];
    const ms = m[7] === undefined ? 0 : +(m[7] + "00").slice(0, 3);
    if (mo < 1 || mo > 12 || d < 1 || d > daysInMonth(y, mo)) return NaN;
    if (h > 23 || mi > 59 || s > 59) return NaN;
    let offsetMin = 0;
    if (m[8] !== "Z") {
      const oh = +m[10], om = +m[11];
      if (oh > 23 || om > 59) return NaN;
      offsetMin = (m[9] === "+" ? 1 : -1) * (oh * 60 + om);
    }
    return ((daysFromCivil(y, mo, d) * 24 + h) * 60 + mi - offsetMin) * 60000 + s * 1000 + ms;
  }

  /** Days since 1970-01-01 for a proleptic Gregorian date (integer arithmetic, any year 0 to 9999). */
  function daysFromCivil(y, m, d) {
    const yy = m <= 2 ? y - 1 : y;
    const era = Math.floor(yy / 400);
    const yoe = yy - era * 400;
    const doy = Math.floor((153 * (m > 2 ? m - 3 : m + 9) + 2) / 5) + d - 1;
    return era * 146097 + yoe * 365 + Math.floor(yoe / 4) - Math.floor(yoe / 100) + doy - 719468;
  }

  /** Accept a Date or epoch milliseconds; anything else is a TypeError. */
  function toEpochMs(now) {
    const t = now instanceof Date ? now.getTime() : now;
    if (typeof t !== "number" || !Number.isFinite(t)) throw new TypeError("now must be a valid Date or finite epoch milliseconds");
    return t;
  }

  // ------------------------------------------------------------------ validation
  function isRecord(v) { return typeof v === "object" && v !== null && !Array.isArray(v); }

  /** Collects issues; the current path is a stack, copied only when an issue is recorded. */
  function Checker() { this.issues = []; this.path = []; }
  Checker.prototype.fail = function (message) { this.issues.push({ path: this.path.join("."), message }); return false; };
  Checker.prototype.failAt = function (path, message) { this.issues.push({ path: path.join("."), message }); return false; };
  Checker.prototype.at = function (key, check, value) {
    this.path.push(key);
    const ok = check(this, value);
    this.path.pop();
    return ok;
  };

  const V = {
    id: (c, v) => (typeof v === "string" && ID_RE.test(v)) || c.fail("invalid identifier"),
    nullableId: (c, v) => v === null || V.id(c, v),
    name: (c, v) => {
      if (typeof v !== "string") return c.fail("expected string");
      const n = v.trim().length;
      return (n >= 1 && n <= 120) || c.fail("name must be 1 to 120 characters after trimming");
    },
    bool: (c, v) => typeof v === "boolean" || c.fail("expected boolean"),
    timestamp: (c, v) => !Number.isNaN(parseTimestamp(v)) || c.fail("invalid timestamp with offset"),
    oneOf: (values) => (c, v) => values.indexOf(v) !== -1 || c.fail("expected one of " + values.join(", ")),
    literal: (value) => (c, v) => v === value || c.fail("expected " + value),
    array: (item, min, max, unique) => (c, v) => {
      if (!Array.isArray(v)) return c.fail("expected array");
      let ok = true;
      if (v.length < min) ok = c.fail("at least " + min + " entries required");
      if (v.length > max) ok = c.fail("at most " + max + " entries allowed");
      for (let i = 0; i < v.length; i++) if (!c.at(i, item, v[i])) ok = false;
      if (ok && unique && new Set(v).size !== v.length) ok = c.fail("duplicate identifiers");
      return ok;
    },
    object: (fields) => {
      const keys = Object.keys(fields);
      return (c, v) => {
        if (!isRecord(v)) return c.fail("expected object");
        let ok = true;
        for (const k in v) if (HOP.call(v, k) && !HOP.call(fields, k)) { c.path.push(k); ok = c.fail("unknown field"); c.path.pop(); }
        for (let i = 0; i < keys.length; i++) if (!c.at(keys[i], fields[keys[i]], v[keys[i]])) ok = false;
        return ok;
      };
    },
  };
  const idList = V.array(V.id, 0, MAX_ITEMS, true);
  const policyShape = V.object({ crossSite: V.bool, remoteAccess: V.bool, relay: V.bool });
  const SHAPE = {
    principal: V.object({ id: V.id, name: V.name, organizationId: V.id, kind: V.oneOf(KINDS), active: V.bool, sponsorId: V.nullableId }),
    site: V.object({ id: V.id, name: V.name, organizationId: V.id, active: V.bool, gatewayReady: V.bool }),
    workspace: V.object({ id: V.id, name: V.name, organizationId: V.id, homeSiteId: V.id, dataClass: V.oneOf(DATA_CLASSES), policy: policyShape }),
    pool: V.object({ id: V.id, name: V.name, organizationId: V.id, tasks: V.array(V.oneOf(TASKS), 1, 4, false) }),
    node: V.object({
      id: V.id, name: V.name, organizationId: V.id, siteId: V.id, poolIds: idList,
      online: V.bool, modelReady: V.bool, sharingConsent: V.bool, peerVerified: V.bool, encrypted: V.bool, usesRelay: V.bool,
      lastObservedAt: V.timestamp, dataClasses: V.array(V.oneOf(DATA_CLASSES), 1, 3, false),
    }),
  };
  SHAPE.member = V.object({ principalId: V.id, actions: V.array(V.oneOf(ACTIONS), 0, 3, false) });
  SHAPE.group = V.object({
    id: V.id, name: V.name, organizationId: V.id, members: V.array(SHAPE.member, 0, MAX_ITEMS, false),
    workspaceIds: idList, poolIds: idList, nodeIds: idList, policy: policyShape,
  });
  SHAPE.directory = V.object({
    schemaVersion: V.literal(SCHEMA_VERSION),
    organization: V.object({ id: V.id, name: V.name, policy: policyShape }),
    principals: V.array(SHAPE.principal, 0, MAX_ITEMS, false), sites: V.array(SHAPE.site, 0, MAX_ITEMS, false),
    workspaces: V.array(SHAPE.workspace, 0, MAX_ITEMS, false), pools: V.array(SHAPE.pool, 0, MAX_ITEMS, false),
    nodes: V.array(SHAPE.node, 0, MAX_ITEMS, false), groups: V.array(SHAPE.group, 0, MAX_ITEMS, false),
  });
  SHAPE.request = V.object({
    organizationId: V.id, groupId: V.id, principalId: V.id, workspaceId: V.id, poolId: V.id,
    task: V.oneOf(TASKS), payloadClass: V.oneOf(DATA_CLASSES),
    sourceSiteId: V.nullableId, sourceNodeId: V.nullableId, meshOptIn: V.bool,
  });
  const COLLECTIONS = ["principals", "sites", "workspaces", "pools", "nodes", "groups"];

  /** Cross-record rules; runs only on a directory whose shape already passed. p is the path prefix. */
  function checkReferences(c, d, p) {
    const known = {};
    for (const key of COLLECTIONS) {
      known[key] = new Set(d[key].map((v) => v.id));
      if (known[key].size !== d[key].length) c.failAt(p.concat(key), "duplicate identifiers");
      d[key].forEach((v, i) => { if (v.organizationId !== d.organization.id) c.failAt(p.concat(key, i, "organizationId"), "organization mismatch"); });
    }
    const kindOf = new Map();
    for (const v of d.principals) if (!kindOf.has(v.id)) kindOf.set(v.id, v.kind);
    d.principals.forEach((v, i) => {
      const ok = v.kind === "human" ? v.sponsorId === null : kindOf.get(v.sponsorId) === "human";
      if (!ok) c.failAt(p.concat("principals", i, "sponsorId"), "digital employees need a human sponsor; humans have none");
    });
    d.workspaces.forEach((v, i) => { if (!known.sites.has(v.homeSiteId)) c.failAt(p.concat("workspaces", i, "homeSiteId"), "unknown site"); });
    d.nodes.forEach((v, i) => {
      if (!known.sites.has(v.siteId)) c.failAt(p.concat("nodes", i, "siteId"), "unknown site");
      v.poolIds.forEach((x) => { if (!known.pools.has(x)) c.failAt(p.concat("nodes", i, "poolIds"), "unknown pool " + x); });
    });
    d.groups.forEach((g, i) => {
      if (new Set(g.members.map((m) => m.principalId)).size !== g.members.length) c.failAt(p.concat("groups", i, "members"), "duplicate members");
      g.members.forEach((m) => { if (!known.principals.has(m.principalId)) c.failAt(p.concat("groups", i, "members"), "unknown principal " + m.principalId); });
      [["workspaceIds", "workspaces"], ["poolIds", "pools"], ["nodeIds", "nodes"]].forEach((pair) => {
        g[pair[0]].forEach((x) => { if (!known[pair[1]].has(x)) c.failAt(p.concat("groups", i, pair[0]), "unknown resource " + x); });
      });
    });
  }

  /** Validate a directory alone. Returns { ok, issues: [{ path, message }] }. */
  function validateDirectory(directory) {
    const c = new Checker();
    if (c.at("directory", SHAPE.directory, directory)) checkReferences(c, directory, ["directory"]);
    return { ok: c.issues.length === 0, issues: c.issues };
  }

  /** Validate a request alone. Returns { ok, issues }. */
  function validateRequest(request) {
    const c = new Checker();
    c.at("request", SHAPE.request, request);
    return { ok: c.issues.length === 0, issues: c.issues };
  }

  /** Validate the full preview input { directory, request } with no other fields. */
  function validatePreviewInput(input) {
    const c = new Checker();
    if (!isRecord(input)) c.fail("expected { directory, request }");
    else {
      for (const k of Object.keys(input)) if (k !== "directory" && k !== "request") c.failAt([k], "unknown field");
      if (c.at("directory", SHAPE.directory, input.directory)) checkReferences(c, input.directory, ["directory"]);
      c.at("request", SHAPE.request, input.request);
    }
    return { ok: c.issues.length === 0, issues: c.issues };
  }

  // ------------------------------------------------------------------ planning
  /** The stricter of two data classes. */
  function stricterDataClass(a, b) { return DATA_CLASS_RANK[a] > DATA_CLASS_RANK[b] ? a : b; }

  /** Locality of one node for a request context. */
  function classifyLocality(nodeId, nodeSiteId, sourceSiteId, sourceNodeId) {
    if (sourceNodeId !== null && sourceNodeId === nodeId) return "device_local";
    if (sourceSiteId === null) return "private_remote";
    return nodeSiteId === sourceSiteId ? "same_site" : "private_cross_site";
  }

  function firstById(list) {
    const m = new Map();
    for (const v of list) if (!m.has(v.id)) m.set(v.id, v);
    return m;
  }

  function result(effectiveDataClass, status, reason, selected, candidates, ranking) {
    return {
      previewOnly: true, executionEnabled: false, authorizationIssued: false, cloudFallback: false,
      status, outcome: status === STATUS.ELIGIBLE ? "eligible" : "denied", reason,
      selectedNodeId: selected ? selected.nodeId : null, locality: selected ? selected.locality : null,
      effectiveDataClass, candidates, ranking,
    };
  }

  /**
   * Plan one request against a directory that has already passed validation.
   * nowMs is epoch milliseconds. Returns
   *   { previewOnly: true, executionEnabled: false, authorizationIssued: false, cloudFallback: false,
   *     status: "eligible_for_planning" | "no_eligible_node" | "denied",
   *     outcome: "eligible" | "denied", reason, selectedNodeId, locality, effectiveDataClass,
   *     candidates: [{ nodeId, locality, eligible, denyReasons }],   directory order
   *     ranking: [nodeId] }                                           eligible nodes in selection order
   * reason is eligible_for_planning, no_eligible_node or one early denial code.
   */
  function plan(d, r, nowMs) {
    const sites = firstById(d.sites);
    const nodes = firstById(d.nodes);
    const principals = firstById(d.principals);
    const w = firstById(d.workspaces).get(r.workspaceId);
    const effectiveDataClass = w ? stricterDataClass(w.dataClass, r.payloadClass) : r.payloadClass;
    const deny = (reason) => result(effectiveDataClass, STATUS.DENIED, reason, null, [], []);

    if (r.organizationId !== d.organization.id) return deny("organization_mismatch");
    const g = firstById(d.groups).get(r.groupId);
    const p = principals.get(r.principalId);
    const pool = firstById(d.pools).get(r.poolId);
    if (!g || !p || !w || !pool) return deny("resource_unavailable");
    if (!p.active) return deny("principal_revoked");
    const holdsAccess = (principalId) => {
      const m = g.members.find((x) => x.principalId === principalId);
      return !!m && m.actions.indexOf("infer") !== -1 && m.actions.indexOf("workspace.read") !== -1;
    };
    if (!holdsAccess(p.id)) return deny("group_access_denied");
    if (p.kind === "digital_employee") {
      const sponsor = p.sponsorId === null ? undefined : principals.get(p.sponsorId);
      if (!sponsor || !sponsor.active || !holdsAccess(sponsor.id)) return deny("sponsor_access_denied");
    }
    if (g.workspaceIds.indexOf(w.id) === -1 || g.poolIds.indexOf(pool.id) === -1) return deny("resource_not_bound");
    if (pool.tasks.indexOf(r.task) === -1) return deny("task_not_supported");
    const sourceSite = r.sourceSiteId === null ? undefined : sites.get(r.sourceSiteId);
    if (r.sourceSiteId !== null && (!sourceSite || !sourceSite.active)) return deny("source_site_unavailable");
    if (r.sourceNodeId !== null) {
      const src = nodes.get(r.sourceNodeId);
      if (!src || src.siteId !== r.sourceSiteId) return deny("source_context_invalid");
    }

    const policies = [d.organization.policy, g.policy, w.policy];
    const allowAll = (flag) => policies.every((x) => x[flag] === true);
    const crossSiteOk = allowAll("crossSite"), remoteOk = allowAll("remoteAccess"), relayOk = allowAll("relay");
    const bound = new Set(g.nodeIds);
    const candidates = [];
    for (const n of d.nodes) {
      if (!bound.has(n.id) || n.poolIds.indexOf(pool.id) === -1) continue;
      const locality = classifyLocality(n.id, n.siteId, r.sourceSiteId, r.sourceNodeId);
      const target = sites.get(n.siteId);
      const why = [];
      if (!n.online || !target || !target.active) why.push("node_unavailable");
      if (!n.modelReady) why.push("model_not_ready");
      // An unparseable observation counts as stale (fail closed); validation makes that case unreachable.
      const age = nowMs - parseTimestamp(n.lastObservedAt);
      if (!(age <= STALE_AFTER_MS && age >= -FUTURE_TOLERANCE_MS)) why.push("node_observation_stale");
      if (n.dataClasses.indexOf(effectiveDataClass) === -1) why.push("data_class_denied");
      if ((n.siteId !== w.homeSiteId || locality === "private_cross_site") && !crossSiteOk) why.push("cross_site_denied");
      if (locality === "private_remote" && !remoteOk) why.push("remote_access_denied");
      if (locality !== "device_local") {
        if (!r.meshOptIn) why.push("mesh_opt_in_required");
        if (!n.sharingConsent) why.push("node_sharing_not_authorized");
        if (!n.peerVerified || !n.encrypted) why.push("private_transport_unverified");
        const crossesGateway = locality === "private_cross_site" || locality === "private_remote";
        if (crossesGateway && (!target || !target.gatewayReady || (sourceSite && !sourceSite.gatewayReady))) why.push("site_gateway_unavailable");
        if (n.usesRelay && !relayOk) why.push("relay_denied");
      }
      candidates.push({ nodeId: n.id, locality, eligible: why.length === 0, denyReasons: why, homeSite: n.siteId === w.homeSiteId });
    }
    const ranked = candidates.filter((c) => c.eligible).sort(compareCandidates);
    const out = candidates.map((c) => ({ nodeId: c.nodeId, locality: c.locality, eligible: c.eligible, denyReasons: c.denyReasons }));
    const selected = ranked.length ? ranked[0] : null;
    return result(effectiveDataClass, selected ? STATUS.ELIGIBLE : STATUS.NONE, selected ? STATUS.ELIGIBLE : STATUS.NONE,
      selected, out, ranked.map((c) => c.nodeId));
  }

  /** Selection order: locality rank, then home site first, then node ID in code unit order. */
  function compareCandidates(a, b) {
    return LOCALITY_RANK[a.locality] - LOCALITY_RANK[b.locality] ||
      (a.homeSite === b.homeSite ? 0 : a.homeSite ? -1 : 1) ||
      (a.nodeId < b.nodeId ? -1 : a.nodeId > b.nodeId ? 1 : 0);
  }

  /**
   * Validate then plan. input is { directory, request }; now is a Date or epoch
   * milliseconds and is required, so the call is pure. Throws TypeError (with an
   * issues array) on invalid input. Preview only: nothing is executed.
   */
  function preview(input, now) {
    const nowMs = toEpochMs(now);
    const v = validatePreviewInput(input);
    if (!v.ok) {
      const e = new TypeError("invalid preview input: " + v.issues.slice(0, 3).map((x) => (x.path || "input") + " " + x.message).join("; "));
      e.issues = v.issues;
      throw e;
    }
    return plan(input.directory, input.request, nowMs);
  }

  return {
    preview, plan, validatePreviewInput, validateDirectory, validateRequest,
    parseTimestamp, stricterDataClass, classifyLocality,
    SCHEMA_VERSION, STALE_AFTER_MS, FUTURE_TOLERANCE_MS, DATA_CLASSES, LOCALITIES,
    EARLY_DENIALS, CANDIDATE_REASONS, STATUS,
  };
});
