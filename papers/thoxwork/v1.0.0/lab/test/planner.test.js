/*
 * Unit tests for the Evidence Lab MeshGroup routing planner (lab/src/planner.js).
 * Run from the paper root: node --test lab/test/planner.test.js
 *
 * Copyright 2026 THOX.ai LLC. Licensed under the Apache License, Version 2.0.
 */
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("path");
const P = require(path.join(__dirname, "..", "src", "planner.js"));

const NOW_MS = Date.UTC(2026, 10, 4, 12, 0, 0);
const NOW = new Date(NOW_MS);
const iso = (deltaMs) => new Date(NOW_MS + deltaMs).toISOString();
const open = () => ({ crossSite: true, remoteAccess: true, relay: false });

function node(id, siteId, extra) {
  return Object.assign({
    id, name: "Node " + id, organizationId: "org", siteId, poolIds: ["code"],
    online: true, modelReady: true, sharingConsent: true, peerVerified: true, encrypted: true, usesRelay: false,
    lastObservedAt: iso(0), dataClasses: ["public", "internal", "restricted"],
  }, extra || {});
}

/** Valid baseline: an employee at HQ asks the engineering group for a coding model. */
function fixture() {
  return {
    directory: {
      schemaVersion: "1.0.0",
      organization: { id: "org", name: "Example org", policy: open() },
      principals: [
        { id: "lead", name: "Team lead", organizationId: "org", kind: "human", active: true, sponsorId: null },
        { id: "nova", name: "Nova", organizationId: "org", kind: "digital_employee", active: true, sponsorId: "lead" },
        { id: "other", name: "Other lead", organizationId: "org", kind: "human", active: true, sponsorId: null },
      ],
      sites: [
        { id: "hq", name: "HQ", organizationId: "org", active: true, gatewayReady: true },
        { id: "branch", name: "Branch", organizationId: "org", active: true, gatewayReady: true },
      ],
      workspaces: [{ id: "eng", name: "Engineering", organizationId: "org", homeSiteId: "hq", dataClass: "internal", policy: open() }],
      pools: [
        { id: "code", name: "Coding", organizationId: "org", tasks: ["coding", "chat"] },
        { id: "research", name: "Research", organizationId: "org", tasks: ["research"] },
      ],
      nodes: [node("hq-a", "hq"), node("br-a", "branch")],
      groups: [
        {
          id: "eng-team", name: "Engineering", organizationId: "org",
          members: [{ principalId: "lead", actions: ["infer", "workspace.read"] }, { principalId: "nova", actions: ["infer", "workspace.read", "tool.propose"] }],
          workspaceIds: ["eng"], poolIds: ["code", "research"], nodeIds: ["hq-a", "br-a"], policy: open(),
        },
        {
          id: "ops-team", name: "Operations", organizationId: "org",
          members: [{ principalId: "other", actions: ["infer", "workspace.read"] }],
          workspaceIds: ["eng"], poolIds: ["code"], nodeIds: ["hq-a"], policy: open(),
        },
      ],
    },
    request: {
      organizationId: "org", groupId: "eng-team", principalId: "nova", workspaceId: "eng", poolId: "code",
      task: "coding", payloadClass: "internal", sourceSiteId: "hq", sourceNodeId: null, meshOptIn: true,
    },
  };
}

const run = (i, now) => P.preview(i, now === undefined ? NOW : now);
const cand = (r, id) => r.candidates.find((c) => c.nodeId === id);
const reasonsOf = (r, id) => cand(r, id).denyReasons;
const nodeOf = (i, id) => i.directory.nodes.find((n) => n.id === id);

// ------------------------------------------------------------------ baseline and preview-only contract
test("baseline selects the same-site node and states preview-only flags", () => {
  const r = run(fixture());
  assert.equal(r.status, "eligible_for_planning");
  assert.equal(r.reason, "eligible_for_planning");
  assert.equal(r.outcome, "eligible");
  assert.equal(r.selectedNodeId, "hq-a");
  assert.equal(r.locality, "same_site");
  assert.deepEqual(r.ranking, ["hq-a", "br-a"]);
  assert.deepEqual(r.candidates.map((c) => [c.nodeId, c.locality, c.eligible, c.denyReasons.length]), [["hq-a", "same_site", true, 0], ["br-a", "private_cross_site", true, 0]]);
  for (const x of [r, run(Object.assign(fixture(), {}))]) {
    assert.equal(x.previewOnly, true); assert.equal(x.executionEnabled, false);
    assert.equal(x.authorizationIssued, false); assert.equal(x.cloudFallback, false);
  }
});

test("denied and no-node results also carry the preview-only flags and a null selection", () => {
  const a = fixture(); a.request.organizationId = "foreign";
  const b = fixture(); b.request.meshOptIn = false;
  for (const r of [run(a), run(b)]) {
    assert.equal(r.previewOnly, true); assert.equal(r.executionEnabled, false);
    assert.equal(r.authorizationIssued, false); assert.equal(r.cloudFallback, false);
    assert.equal(r.selectedNodeId, null); assert.equal(r.locality, null); assert.equal(r.outcome, "denied");
  }
});

test("pure: input is not modified and repeated calls give identical results", () => {
  const i = fixture();
  const before = JSON.stringify(i);
  const r1 = run(i), r2 = run(i);
  assert.equal(JSON.stringify(i), before);
  assert.deepEqual(r1, r2);
  assert.deepEqual(run(i, NOW_MS), r1, "epoch milliseconds and Date give the same result");
});

test("now is required and must be a valid time", () => {
  assert.throws(() => P.preview(fixture()), TypeError);
  assert.throws(() => P.preview(fixture(), new Date(NaN)), TypeError);
  assert.throws(() => P.preview(fixture(), "2026-11-04T12:00:00Z"), TypeError);
  assert.throws(() => P.preview(fixture(), Infinity), TypeError);
});

// ------------------------------------------------------------------ early denials
const EARLY = [
  ["organization_mismatch", (i) => { i.request.organizationId = "foreign"; }],
  ["resource_unavailable", (i) => { i.request.groupId = "missing"; }],
  ["resource_unavailable", (i) => { i.request.principalId = "missing"; }],
  ["resource_unavailable", (i) => { i.request.workspaceId = "missing"; }],
  ["resource_unavailable", (i) => { i.request.poolId = "missing"; }],
  ["principal_revoked", (i) => { i.directory.principals[1].active = false; }],
  ["group_access_denied", (i) => { i.request.groupId = "ops-team"; }],
  ["group_access_denied", (i) => { i.directory.groups[0].members[1].actions = ["infer"]; }],
  ["group_access_denied", (i) => { i.directory.groups[0].members[1].actions = ["workspace.read", "tool.propose"]; }],
  ["sponsor_access_denied", (i) => { i.directory.principals[0].active = false; }],
  ["resource_not_bound", (i) => { i.directory.groups[0].workspaceIds = []; }],
  ["resource_not_bound", (i) => { i.request.poolId = "research"; i.directory.groups[0].poolIds = ["code"]; }],
  ["task_not_supported", (i) => { i.request.task = "embedding"; }],
  ["source_site_unavailable", (i) => { i.request.sourceSiteId = "nowhere"; }],
  ["source_site_unavailable", (i) => { i.directory.sites[0].active = false; }],
  ["source_context_invalid", (i) => { i.request.sourceNodeId = "ghost"; }],
  ["source_context_invalid", (i) => { i.request.sourceNodeId = "br-a"; }],
  ["source_context_invalid", (i) => { i.request.sourceSiteId = null; i.request.sourceNodeId = "hq-a"; }],
];
EARLY.forEach(([reason, mutate], k) => test("early denial " + (k + 1) + ": " + reason, () => {
  const i = fixture(); mutate(i);
  const r = run(i);
  assert.equal(r.status, "denied");
  assert.equal(r.reason, reason);
  assert.deepEqual(r.candidates, []);
  assert.deepEqual(r.ranking, []);
}));

test("every documented early denial code is exercised", () => {
  assert.deepEqual([...new Set(EARLY.map((e) => e[0]))].sort(), [...P.EARLY_DENIALS].sort());
});

test("early denials apply in the documented order when several hold", () => {
  const all = (i) => {
    i.request.task = "embedding"; i.request.sourceSiteId = "nowhere"; i.request.sourceNodeId = "ghost";
    i.directory.groups[0].workspaceIds = []; i.directory.principals[0].active = false;
    i.directory.groups[0].members[1].actions = ["infer"]; i.directory.principals[1].active = false;
    i.request.groupId = "eng-team";
  };
  const peel = [
    ["principal_revoked", (i) => { i.directory.principals[1].active = true; }],
    ["group_access_denied", (i) => { i.directory.groups[0].members[1].actions = ["infer", "workspace.read"]; }],
    ["sponsor_access_denied", (i) => { i.directory.principals[0].active = true; }],
    ["resource_not_bound", (i) => { i.directory.groups[0].workspaceIds = ["eng"]; }],
    ["task_not_supported", (i) => { i.request.task = "coding"; }],
    ["source_site_unavailable", (i) => { i.request.sourceSiteId = "hq"; }],
    ["source_context_invalid", (i) => { i.request.sourceNodeId = null; }],
  ];
  const i = fixture(); all(i);
  const j = JSON.parse(JSON.stringify(i)); j.request.organizationId = "foreign"; j.request.groupId = "missing";
  assert.equal(run(j).reason, "organization_mismatch");
  j.request.organizationId = "org";
  assert.equal(run(j).reason, "resource_unavailable");
  for (const [expected, fix] of peel) { assert.equal(run(i).reason, expected); fix(i); }
  assert.equal(run(i).status, "eligible_for_planning");
});

// ------------------------------------------------------------------ sponsor rule
test("sponsor rule: the sponsor must hold infer and workspace.read in the same group", () => {
  const a = fixture(); a.directory.groups[0].members = [a.directory.groups[0].members[1]];
  assert.equal(run(a).reason, "sponsor_access_denied", "sponsor not a member");
  const b = fixture(); b.directory.groups[0].members[0].actions = ["infer", "tool.propose"];
  assert.equal(run(b).reason, "sponsor_access_denied", "sponsor lacks workspace.read");
  const c = fixture(); c.directory.groups[0].members[0].actions = ["workspace.read"];
  assert.equal(run(c).reason, "sponsor_access_denied", "sponsor lacks infer");
  const d = fixture(); d.directory.groups[0].members[0].actions = [];
  d.directory.groups[1].members.push({ principalId: "lead", actions: ["infer", "workspace.read"] });
  assert.equal(run(d).reason, "sponsor_access_denied", "access in another group is not unioned in");
});

test("sponsor rule applies to digital employees only; a human needs no sponsor", () => {
  const i = fixture(); i.request.principalId = "lead";
  assert.equal(run(i).status, "eligible_for_planning");
  const j = fixture(); j.request.principalId = "lead"; j.directory.groups[0].members[1].actions = [];
  assert.equal(run(j).status, "eligible_for_planning", "a non-member employee does not block its human sponsor");
});

// ------------------------------------------------------------------ effective data class
test("data class is the stricter of workspace and payload", () => {
  const cases = [
    ["public", "public", "public"], ["public", "internal", "internal"], ["public", "restricted", "restricted"],
    ["internal", "public", "internal"], ["internal", "restricted", "restricted"],
    ["restricted", "public", "restricted"], ["restricted", "internal", "restricted"], ["restricted", "restricted", "restricted"],
  ];
  for (const [ws, payload, want] of cases) {
    const i = fixture(); i.directory.workspaces[0].dataClass = ws; i.request.payloadClass = payload;
    assert.equal(run(i).effectiveDataClass, want, ws + " workspace, " + payload + " payload");
    assert.equal(P.stricterDataClass(ws, payload), want);
  }
});

test("a public payload cannot downgrade a restricted workspace", () => {
  const i = fixture(); i.directory.workspaces[0].dataClass = "restricted"; i.request.payloadClass = "public";
  i.directory.nodes.forEach((n) => { n.dataClasses = ["public", "internal"]; });
  const r = run(i);
  assert.equal(r.status, "no_eligible_node");
  assert.ok(r.candidates.every((c) => c.denyReasons.indexOf("data_class_denied") !== -1));
});

test("an unknown workspace leaves the payload class in force and is denied early", () => {
  const i = fixture(); i.request.workspaceId = "missing"; i.request.payloadClass = "public";
  const r = run(i);
  assert.equal(r.effectiveDataClass, "public");
  assert.equal(r.reason, "resource_unavailable");
});

// ------------------------------------------------------------------ localities
test("locality device_local: the source node", () => {
  const i = fixture(); i.request.sourceNodeId = "hq-a";
  const r = run(i);
  assert.equal(cand(r, "hq-a").locality, "device_local");
  assert.equal(r.selectedNodeId, "hq-a"); assert.equal(r.locality, "device_local");
});

test("locality same_site and private_cross_site: relative to the source site", () => {
  const r = run(fixture());
  assert.equal(cand(r, "hq-a").locality, "same_site");
  assert.equal(cand(r, "br-a").locality, "private_cross_site");
  const i = fixture(); i.request.sourceSiteId = "branch";
  const s = run(i);
  assert.equal(cand(s, "br-a").locality, "same_site");
  assert.equal(cand(s, "hq-a").locality, "private_cross_site");
});

test("locality private_remote: no source site", () => {
  const i = fixture(); i.request.sourceSiteId = null;
  const r = run(i);
  assert.ok(r.candidates.every((c) => c.locality === "private_remote"));
  assert.equal(r.locality, "private_remote");
  assert.equal(r.selectedNodeId, "hq-a", "home site wins inside the remote locality");
  assert.equal(P.classifyLocality("x", "hq", null, null), "private_remote");
});

// ------------------------------------------------------------------ candidate selection
test("candidates are nodes bound to the group that serve the pool, in directory order", () => {
  const i = fixture();
  i.directory.nodes.push(node("hq-b", "hq", { poolIds: ["research"] }), node("hq-c", "hq"), node("hq-0", "hq"));
  i.directory.groups[0].nodeIds = ["hq-0", "hq-b", "br-a", "hq-a"];
  const r = run(i);
  assert.deepEqual(r.candidates.map((c) => c.nodeId), ["hq-a", "br-a", "hq-0"], "hq-b serves another pool, hq-c is not bound");
  const j = fixture(); j.directory.groups[0].nodeIds = [];
  const s = run(j);
  assert.equal(s.status, "no_eligible_node"); assert.deepEqual(s.candidates, []);
});

// ------------------------------------------------------------------ per-candidate deny reasons
test("node_unavailable: node offline or its site inactive", () => {
  const a = fixture(); nodeOf(a, "br-a").online = false;
  assert.deepEqual(reasonsOf(run(a), "br-a"), ["node_unavailable"]);
  const b = fixture(); b.directory.sites[1].active = false;
  assert.deepEqual(reasonsOf(run(b), "br-a"), ["node_unavailable"]);
});

test("model_not_ready", () => {
  const i = fixture(); nodeOf(i, "hq-a").modelReady = false;
  const r = run(i);
  assert.deepEqual(reasonsOf(r, "hq-a"), ["model_not_ready"]);
  assert.equal(r.selectedNodeId, "br-a");
});

test("node_observation_stale at the 90,000 ms and 5,000 ms boundaries", () => {
  const at = (delta) => { const i = fixture(); nodeOf(i, "hq-a").lastObservedAt = iso(delta); return reasonsOf(run(i), "hq-a"); };
  assert.deepEqual(at(-90000), [], "exactly 90,000 ms old is fresh");
  assert.deepEqual(at(-90001), ["node_observation_stale"]);
  assert.deepEqual(at(5000), [], "exactly 5,000 ms in the future is accepted");
  assert.deepEqual(at(5001), ["node_observation_stale"]);
  assert.deepEqual(at(-86400000), ["node_observation_stale"]);
});

test("staleness uses the passed time, timestamp offsets and millisecond truncation", () => {
  const i = fixture();
  nodeOf(i, "hq-a").lastObservedAt = "2026-11-04T13:28:30.0009+01:30"; // 11:58:30.000Z, 90,000 ms before NOW
  assert.deepEqual(reasonsOf(run(i), "hq-a"), []);
  nodeOf(i, "hq-a").lastObservedAt = "2026-11-04T11:58:29.9999Z"; // truncates to .999, 90,001 ms old
  assert.deepEqual(reasonsOf(run(i), "hq-a"), ["node_observation_stale"]);
  nodeOf(i, "hq-a").lastObservedAt = iso(0);
  assert.deepEqual(reasonsOf(run(i, NOW_MS + 90000), "hq-a"), []);
  assert.deepEqual(reasonsOf(run(i, NOW_MS + 90001), "hq-a"), ["node_observation_stale"]);
  assert.deepEqual(reasonsOf(run(i, NOW_MS - 5001), "hq-a"), ["node_observation_stale"]);
});

test("data_class_denied", () => {
  const i = fixture(); nodeOf(i, "hq-a").dataClasses = ["public"];
  assert.deepEqual(reasonsOf(run(i), "hq-a"), ["data_class_denied"]);
});

test("cross_site_denied for a cross-site route when any policy forbids cross-site", () => {
  for (const where of ["organization", "group", "workspace"]) {
    const i = fixture();
    const pol = where === "organization" ? i.directory.organization.policy : where === "group" ? i.directory.groups[0].policy : i.directory.workspaces[0].policy;
    pol.crossSite = false;
    const r = run(i);
    assert.deepEqual(reasonsOf(r, "br-a"), ["cross_site_denied"], where);
    assert.deepEqual(reasonsOf(r, "hq-a"), [], where);
  }
});

test("cross_site_denied for a same-site node outside the workspace home site (residency)", () => {
  const i = fixture(); i.request.sourceSiteId = "branch"; i.directory.workspaces[0].policy.crossSite = false;
  const r = run(i);
  assert.equal(cand(r, "br-a").locality, "same_site");
  assert.deepEqual(reasonsOf(r, "br-a"), ["cross_site_denied"]);
  assert.deepEqual(reasonsOf(r, "hq-a"), ["cross_site_denied"]);
  assert.equal(r.status, "no_eligible_node");
});

test("remote_access_denied when any policy forbids remote access", () => {
  for (const where of ["organization", "group", "workspace"]) {
    const i = fixture(); i.request.sourceSiteId = null;
    const pol = where === "organization" ? i.directory.organization.policy : where === "group" ? i.directory.groups[0].policy : i.directory.workspaces[0].policy;
    pol.remoteAccess = false;
    const r = run(i);
    assert.deepEqual(reasonsOf(r, "hq-a"), ["remote_access_denied"], where);
    assert.deepEqual(reasonsOf(r, "br-a"), ["remote_access_denied"], where);
  }
});

test("mesh_opt_in_required for every non-local candidate", () => {
  const i = fixture(); i.request.meshOptIn = false;
  const r = run(i);
  assert.ok(r.candidates.every((c) => c.denyReasons.join() === "mesh_opt_in_required"));
  assert.equal(r.status, "no_eligible_node");
  assert.equal(r.cloudFallback, false);
});

test("node_sharing_not_authorized", () => {
  const i = fixture(); nodeOf(i, "hq-a").sharingConsent = false;
  assert.deepEqual(reasonsOf(run(i), "hq-a"), ["node_sharing_not_authorized"]);
});

test("private_transport_unverified: peer not verified or not encrypted", () => {
  const a = fixture(); nodeOf(a, "hq-a").peerVerified = false;
  assert.deepEqual(reasonsOf(run(a), "hq-a"), ["private_transport_unverified"]);
  const b = fixture(); nodeOf(b, "hq-a").encrypted = false;
  assert.deepEqual(reasonsOf(run(b), "hq-a"), ["private_transport_unverified"]);
});

test("site_gateway_unavailable: target or source gateway not ready on cross-site and remote routes", () => {
  const a = fixture(); a.directory.sites[1].gatewayReady = false;
  const r = run(a);
  assert.deepEqual(reasonsOf(r, "br-a"), ["site_gateway_unavailable"]);
  assert.deepEqual(reasonsOf(r, "hq-a"), [], "same-site routes need no gateway");
  const b = fixture(); b.directory.sites[0].gatewayReady = false;
  assert.deepEqual(reasonsOf(run(b), "br-a"), ["site_gateway_unavailable"], "source gateway");
  const c = fixture(); c.request.sourceSiteId = null; c.directory.sites[1].gatewayReady = false;
  const s = run(c);
  assert.deepEqual(reasonsOf(s, "br-a"), ["site_gateway_unavailable"]);
  assert.deepEqual(reasonsOf(s, "hq-a"), []);
});

test("relay_denied unless all three policies allow relay", () => {
  const i = fixture(); nodeOf(i, "hq-a").usesRelay = true;
  assert.deepEqual(reasonsOf(run(i), "hq-a"), ["relay_denied"]);
  i.directory.organization.policy.relay = true; i.directory.groups[0].policy.relay = true;
  assert.deepEqual(reasonsOf(run(i), "hq-a"), ["relay_denied"], "two of three is not enough");
  i.directory.workspaces[0].policy.relay = true;
  assert.deepEqual(reasonsOf(run(i), "hq-a"), []);
});

test("device_local candidates skip opt-in, sharing, transport, gateway and relay checks", () => {
  const i = fixture(); i.request.sourceNodeId = "hq-a"; i.request.meshOptIn = false;
  Object.assign(nodeOf(i, "hq-a"), { sharingConsent: false, peerVerified: false, encrypted: false, usesRelay: true });
  i.directory.sites[0].gatewayReady = false;
  const r = run(i);
  assert.deepEqual(reasonsOf(r, "hq-a"), []);
  assert.equal(r.selectedNodeId, "hq-a"); assert.equal(r.locality, "device_local");
  assert.ok(reasonsOf(r, "br-a").indexOf("mesh_opt_in_required") !== -1);
});

test("device_local still applies availability, readiness, staleness, data class and residency", () => {
  const i = fixture(); i.request.sourceNodeId = "hq-a";
  Object.assign(nodeOf(i, "hq-a"), { online: false, modelReady: false, lastObservedAt: iso(-100000), dataClasses: ["public"] });
  assert.deepEqual(reasonsOf(run(i), "hq-a"), ["node_unavailable", "model_not_ready", "node_observation_stale", "data_class_denied"]);
  const j = fixture(); j.request.sourceSiteId = "branch"; j.request.sourceNodeId = "br-a"; j.directory.groups[0].policy.crossSite = false;
  assert.deepEqual(reasonsOf(run(j), "br-a"), ["cross_site_denied"], "residency binds device-local work outside the home site");
});

test("all applicable reasons accumulate in the fixed documented order", () => {
  const i = fixture(); i.request.sourceSiteId = null; i.request.meshOptIn = false;
  i.directory.organization.policy = { crossSite: false, remoteAccess: false, relay: false };
  i.directory.sites[1].active = false; i.directory.sites[1].gatewayReady = false;
  Object.assign(nodeOf(i, "br-a"), { modelReady: false, lastObservedAt: iso(6000), dataClasses: ["public"], sharingConsent: false, encrypted: false, usesRelay: true });
  const r = run(i);
  assert.deepEqual(reasonsOf(r, "br-a"), P.CANDIDATE_REASONS);
  assert.ok(reasonsOf(r, "br-a").length === 11);
});

// ------------------------------------------------------------------ deterministic selection order
test("selection: locality outranks home site", () => {
  const i = fixture(); i.directory.workspaces[0].homeSiteId = "branch"; i.directory.groups[0].nodeIds = ["br-a", "hq-a"];
  const r = run(i);
  assert.equal(r.selectedNodeId, "hq-a", "same-site outside the home site beats cross-site at the home site");
  assert.deepEqual(r.ranking, ["hq-a", "br-a"]);
});

test("selection: device_local outranks same_site", () => {
  const i = fixture(); i.directory.nodes.push(node("hq-0", "hq")); i.directory.groups[0].nodeIds.push("hq-0");
  i.request.sourceNodeId = "hq-a";
  assert.deepEqual(run(i).ranking, ["hq-a", "hq-0", "br-a"]);
});

test("selection: within a locality the home site wins before node ID", () => {
  const i = fixture(); i.request.sourceSiteId = null;
  i.directory.nodes = [node("a-branch", "branch"), node("z-hq", "hq")];
  i.directory.groups[0].nodeIds = ["a-branch", "z-hq"]; i.directory.groups[1].nodeIds = [];
  const r = run(i);
  assert.equal(r.selectedNodeId, "z-hq");
  assert.deepEqual(r.ranking, ["z-hq", "a-branch"]);
});

test("selection: node ID ties break in code unit order, not natural or locale order", () => {
  const i = fixture();
  const ids = ["n2", "n10", "a", "B", "n1"];
  i.directory.nodes = ids.map((id) => node(id, "hq"));
  i.directory.groups[0].nodeIds = ids.slice(); i.directory.groups[1].nodeIds = [];
  const r = run(i);
  assert.deepEqual(r.ranking, ["B", "a", "n1", "n10", "n2"]);
  assert.equal(r.selectedNodeId, "B");
  assert.deepEqual(r.candidates.map((c) => c.nodeId), ids, "candidates keep directory order");
});

test("selection: an ineligible better-ranked node is skipped", () => {
  const i = fixture(); nodeOf(i, "hq-a").online = false;
  const r = run(i);
  assert.equal(r.selectedNodeId, "br-a"); assert.equal(r.locality, "private_cross_site");
  assert.deepEqual(r.ranking, ["br-a"]);
});

test("selection is independent of directory order", () => {
  const i = fixture(); const j = fixture();
  j.directory.nodes.reverse(); j.directory.groups[0].nodeIds.reverse();
  assert.equal(run(i).selectedNodeId, run(j).selectedNodeId);
  assert.deepEqual(run(i).ranking, run(j).ranking);
});

// ------------------------------------------------------------------ validation
test("valid fixture passes validation", () => {
  const v = P.validatePreviewInput(fixture());
  assert.equal(v.ok, true, JSON.stringify(v.issues));
});

test("validation rejects invalid inputs and preview throws TypeError with issues", () => {
  const bad = [
    (i) => { i.request.execute = true; },
    (i) => { i.extra = 1; },
    (i) => { i.directory.schemaVersion = "2.0.0"; },
    (i) => { i.directory.nodes[0].lastObservedAt = "2026-11-04T12:00:00"; },
    (i) => { i.directory.nodes[0].lastObservedAt = "2026-02-29T12:00:00Z"; },
    (i) => { i.directory.nodes[0].lastObservedAt = "2026-11-04T24:00Z"; },
    (i) => { i.directory.nodes[0].lastObservedAt = "2026-11-04T12:00+0100"; },
    (i) => { i.directory.nodes[0].dataClasses = []; },
    (i) => { i.directory.nodes[0].poolIds = ["code", "code"]; },
    (i) => { i.directory.nodes[0].poolIds = ["nope"]; },
    (i) => { i.directory.nodes[0].siteId = "nope"; },
    (i) => { i.directory.nodes[1].id = "hq-a"; },
    (i) => { i.directory.principals[1].sponsorId = null; },
    (i) => { i.directory.principals[1].sponsorId = "nova"; },
    (i) => { i.directory.principals[0].sponsorId = "other"; },
    (i) => { i.directory.sites[0].organizationId = "foreign"; },
    (i) => { i.directory.groups[0].members.push({ principalId: "lead", actions: [] }); },
    (i) => { i.directory.groups[0].members[0].actions = ["infer", "workspace.read", "tool.propose", "infer"]; },
    (i) => { i.directory.groups[0].nodeIds.push("ghost"); },
    (i) => { i.directory.workspaces[0].homeSiteId = "ghost"; },
    (i) => { i.directory.pools[0].tasks = []; },
    (i) => { i.directory.pools[0].name = "   "; },
    (i) => { i.directory.pools[0].id = "-leading-dash"; },
    (i) => { i.directory.pools[0].id = "x".repeat(101); },
    (i) => { i.request.sourceNodeId = undefined; },
    (i) => { i.request.task = "image"; },
    (i) => { while (i.directory.groups.length < 101) i.directory.groups.push(Object.assign({}, i.directory.groups[1], { id: "g" + i.directory.groups.length })); },
  ];
  bad.forEach((mutate, k) => {
    const i = fixture(); mutate(i);
    assert.equal(P.validatePreviewInput(i).ok, false, "case " + k);
    assert.throws(() => run(i), (e) => e instanceof TypeError && Array.isArray(e.issues) && e.issues.length > 0, "case " + k);
  });
});

test("validation accepts boundary-valid inputs", () => {
  const ok = [
    (i) => { i.directory.pools[0].name = "  trimmed  "; },
    (i) => { i.directory.pools.push({ id: "x".repeat(100), name: "Long", organizationId: "org", tasks: ["chat"] }); },
    (i) => { i.directory.nodes[0].lastObservedAt = "2024-02-29T12:00Z"; },
    (i) => { i.directory.nodes[0].lastObservedAt = "2026-11-04T12:00:00.123456789-00:00"; },
    (i) => { i.directory.groups[0].members[0].actions = ["infer", "workspace.read", "infer"]; },
    (i) => { while (i.directory.groups.length < 100) i.directory.groups.push(Object.assign({}, i.directory.groups[1], { id: "g" + i.directory.groups.length })); },
  ];
  ok.forEach((mutate, k) => { const i = fixture(); mutate(i); assert.equal(P.validatePreviewInput(i).ok, true, "case " + k + " " + JSON.stringify(P.validatePreviewInput(i).issues)); });
});

test("parseTimestamp matches Date.parse on valid forms and rejects invalid ones", () => {
  const valid = ["2026-11-04T12:00Z", "2026-11-04T12:00:07Z", "2026-11-04T12:00:07.5+05:30", "2026-11-04T12:00:07.123456-08:00",
    "2000-02-29T00:00Z", "0000-01-01T00:00+01:00", "0099-12-31T23:59:59Z", "9999-12-31T23:59:59.999-23:59", "2026-11-04T12:00:00-00:00"];
  for (const s of valid) assert.equal(P.parseTimestamp(s), Date.parse(s), s);
  for (const s of ["", "2026-11-04", "2026-11-04T12Z", "2026-13-01T00:00Z", "1900-02-29T00:00Z", "2026-11-04T12:60Z", "2026-11-04T12:00:60Z",
    "2026-11-04T12:00:00.Z", "2026-11-04t12:00Z", "2026-11-04T12:00+24:00", "+02026-11-04T12:00Z", 12345, null]) {
    assert.ok(Number.isNaN(P.parseTimestamp(s)), String(s));
  }
});

test("parseTimestamp equals Date.parse on 20,000 seeded valid timestamps across years 0 to 9999", () => {
  let s = 20261104;
  const rnd = () => { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; };
  const p2 = (n) => String(n).padStart(2, "0");
  for (let k = 0; k < 20000; k++) {
    const y = Math.floor(rnd() * 10000), mo = 1 + Math.floor(rnd() * 12);
    const dim = mo === 2 ? ((y % 4 === 0 && y % 100 !== 0) || y % 400 === 0 ? 29 : 28) : [4, 6, 9, 11].indexOf(mo) !== -1 ? 30 : 31;
    const d = 1 + Math.floor(rnd() * dim);
    const t = String(y).padStart(4, "0") + "-" + p2(mo) + "-" + p2(d) + "T" + p2(Math.floor(rnd() * 24)) + ":" + p2(Math.floor(rnd() * 60)) +
      (rnd() < 0.8 ? ":" + p2(Math.floor(rnd() * 60)) + (rnd() < 0.6 ? "." + String(Math.floor(rnd() * 1e9)).padStart(1 + Math.floor(rnd() * 9), "0") : "") : "");
    const off = rnd() < 0.4 ? "Z" : (rnd() < 0.5 ? "+" : "-") + p2(Math.floor(rnd() * 24)) + ":" + p2(Math.floor(rnd() * 60));
    assert.equal(P.parseTimestamp(t + off), Date.parse(t + off), t + off);
  }
});

test("validation issues name the offending path", () => {
  const i = fixture(); i.directory.nodes[1].lastObservedAt = "yesterday"; i.request.extra = 1; i.directory.groups[0].nodeIds.push("ghost");
  const paths = P.validatePreviewInput(i).issues.map((x) => x.path);
  assert.ok(paths.indexOf("directory.nodes.1.lastObservedAt") !== -1, paths.join());
  assert.ok(paths.indexOf("request.extra") !== -1, paths.join());
  const j = fixture(); j.directory.groups[0].nodeIds.push("ghost");
  assert.deepEqual(P.validatePreviewInput(j).issues.map((x) => x.path), ["directory.groups.0.nodeIds"]);
});
