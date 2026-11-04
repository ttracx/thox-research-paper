/*
 * Unit tests for the ThoxWork Evidence Lab core modules.
 * Run: node --test lab/test/
 */
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("path");
const crypto = require("crypto");
const E = require(path.join(__dirname, "..", "src", "evidence.js"));
const M = require(path.join(__dirname, "..", "src", "meshgroup.js"));
const G = require(path.join(__dirname, "..", "src", "governance.js"));

const clock = () => { let n = 0; return () => new Date(Date.UTC(2026, 10, 4) + 1000 * n++).toISOString(); };

test("SHA-256 and HMAC known-answer tests pass", () => {
  const r = E.selfTest();
  assert.equal(r.ok, true);
  assert.equal(r.passed, r.total);
});

test("SHA-256 and HMAC match Node crypto on random inputs", () => {
  for (let n = 0; n < 300; n++) {
    const msg = crypto.randomBytes(n);
    const key = crypto.randomBytes(n % 130);
    assert.equal(E.sha256(msg), crypto.createHash("sha256").update(msg).digest("hex"));
    assert.equal(E.hmacSha256(key, msg), crypto.createHmac("sha256", key).update(msg).digest("hex"));
  }
});

test("canonical JSON sorts keys and rejects non-finite numbers", () => {
  assert.equal(E.canonical({ b: 1, a: [true, null, "x"] }), '{"a":[true,null,"x"],"b":1}');
  assert.throws(() => E.canonical({ a: Infinity }), TypeError);
});

test("evidence chain verifies and locates an edit", () => {
  const c = new E.EvidenceChain({ key: "k", clock: clock() });
  for (let i = 0; i < 10; i++) c.append("note", "tester", { i });
  assert.equal(c.verify().ok, true);
  const recs = JSON.parse(JSON.stringify(c.records));
  recs[6].payload.i = 600;
  const v = E.EvidenceChain.verify(recs, "k");
  assert.equal(v.ok, false);
  assert.equal(v.firstBad, 6);
});

test("keyed chain detects a suffix rebuilt without the key", () => {
  const c = new E.EvidenceChain({ key: "k", clock: clock() });
  for (let i = 0; i < 5; i++) c.append("note", "tester", { i });
  const recs = JSON.parse(JSON.stringify(c.records));
  recs[2].payload.i = 99;
  for (let i = 2; i < recs.length; i++) {
    recs[i].prev = i === 0 ? E.GENESIS : recs[i - 1].hash;
    recs[i].hash = E.sha256(E.canonical({ seq: recs[i].seq, ts: recs[i].ts, kind: recs[i].kind, actor: recs[i].actor, payload: recs[i].payload, prev: recs[i].prev }));
  }
  assert.equal(E.EvidenceChain.verify(recs, null).ok, true, "unkeyed verification cannot see a rebuilt suffix");
  assert.equal(E.EvidenceChain.verify(recs, "k").firstBad, 2, "the HMAC tag exposes it");
});

test("bundle round-trips and never carries the key", () => {
  const c = new E.EvidenceChain({ key: "secret-key", clock: clock() });
  c.append("session.open", "human:lead", { scenario: "unit" });
  const b = c.exportBundle({ lab: "test" });
  assert.equal(JSON.stringify(b).includes("secret-key"), false);
  assert.equal(E.EvidenceChain.fromBundle(b, "secret-key").verify().ok, true);
  assert.throws(() => c.append("not.a.kind", "x", {}), RangeError);
});

const POLICY = {
  tenant: "acme", cross_site_enabled: false,
  groups: { finance: { classification_max: 2, allowed_sites: ["hq", "branch"] } },
  sites: { hq: { authenticated: true }, branch: { authenticated: true } },
};
const NODES = [
  { id: "a", tenant: "acme", group: "finance", site: "hq", ram_free_gb: 8, models: ["m1"], authenticated: true, healthy: true },
  { id: "b", tenant: "acme", group: "finance", site: "hq", ram_free_gb: 16, models: ["m1"], authenticated: true, healthy: false },
  { id: "c", tenant: "acme", group: "finance", site: "branch", ram_free_gb: 32, models: ["m1"], authenticated: true, healthy: true },
  { id: "d", tenant: "acme", group: "finance", site: "hq", ram_free_gb: 8, models: ["m1"], authenticated: true, healthy: true },
];
const REQ = { tenant: "acme", group: "finance", source_site: "hq", model: "m1", classification: 1, cross_site_consent: false };

test("MeshGroup admission denies tenant, group and classification", () => {
  assert.equal(M.outcome(M.decide(Object.assign({}, REQ, { tenant: "other" }), NODES, POLICY)), "DENY:tenant mismatch");
  assert.equal(M.outcome(M.decide(Object.assign({}, REQ, { group: "legal" }), NODES, POLICY)), "DENY:unknown group");
  assert.equal(M.outcome(M.decide(Object.assign({}, REQ, { classification: 3 }), NODES, POLICY)), "DENY:classification exceeds group policy");
});

test("MeshGroup admission is default-deny across sites and breaks ties by inventory order", () => {
  const d = M.decide(REQ, NODES, POLICY);
  assert.equal(d.verdict, "PLACE");
  assert.equal(d.node, "a", "a and d tie at 8 GB; the earlier node wins; c is cross-site");
  assert.ok(d.excluded.some((e) => e.node === "c" && e.reason === M.EXCLUDE.CROSS_SITE));
  assert.ok(d.excluded.some((e) => e.node === "b" && e.reason === M.EXCLUDE.UNHEALTHY));
  const consentOnly = M.decide(Object.assign({}, REQ, { cross_site_consent: true }), NODES, POLICY);
  assert.equal(consentOnly.node, "a", "consent without policy enablement does not open the other site");
  const both = M.decide(Object.assign({}, REQ, { cross_site_consent: true }), NODES, Object.assign({}, POLICY, { cross_site_enabled: true }));
  assert.equal(both.node, "c");
});

test("MeshGroup policy validation names the bad field", () => {
  assert.throws(() => M.validatePolicy({ tenant: "x", cross_site_enabled: "no", groups: {}, sites: {} }), /cross_site_enabled/);
});

const RULES = { deploymentDeny: ["desk.exec"], tenantDeny: ["mcp.call"], sizeCap: 1000 };

test("gateway fails closed in the documented order", () => {
  const chain = new E.EvidenceChain({ clock: clock() });
  const emp = { id: "de:mira", workspaces: ["ops"] };
  assert.equal(G.requestAction(chain, emp, "memory.write", "release cadence: weekly", "ops", RULES).rule, "default_allow");
  assert.equal(G.gateAction(emp, "desk.exec", "ls", "ops", RULES).rule, "deployment_deny");
  assert.equal(G.gateAction(emp, "format.disk", "", "ops", RULES).rule, "unknown_action");
  assert.equal(G.gateAction(emp, "mcp.call", "", "ops", RULES).rule, "deny_actions");
  assert.equal(G.gateAction(emp, "message", "hi", "finance", RULES).rule, "channel_membership");
  assert.equal(G.gateAction(emp, "message", "here is my API_KEY=abc", "ops", RULES).rule, "secret_leak");
  assert.equal(G.gateAction(emp, "message", "x".repeat(1001), "ops", RULES).rule, "size_limit");
  const tenantWiden = Object.assign({}, RULES, { tenantDeny: [] });
  assert.equal(G.gateAction(emp, "desk.exec", "ls", "ops", tenantWiden).rule, "deployment_deny", "tenant policy cannot widen the ceiling");
  assert.equal(chain.verify().ok, true);
});

test("assignment lifecycle has 7 states and 18 legal edges", () => {
  assert.equal(G.STATES.length, 7);
  assert.equal(G.EDGE_COUNT, 18);
  const chain = new E.EvidenceChain({ clock: clock() });
  const a = { id: "asg-1", state: "queued" };
  assert.equal(G.transition(chain, a, "completed", "x"), false);
  assert.equal(G.transition(chain, a, "running", "x"), true);
  assert.equal(G.transition(chain, a, "completed", "x"), true);
  assert.equal(G.transition(chain, a, "running", "x"), false, "completed is terminal");
});

test("approval gate: four reasons, person only, role required, final decision", () => {
  const base = { externalEffectGate: false, responsibilities: [], sensitivity: "internal", employeeAutonomy: 3, roleAutonomy: 3 };
  assert.deepEqual(G.approvalReasons(base), []);
  assert.equal(G.approvalReasons(Object.assign({}, base, { externalEffectGate: true })).length, 1);
  assert.equal(G.approvalReasons(Object.assign({}, base, { sensitivity: "confidential" })).length, 1);
  assert.equal(G.approvalReasons(Object.assign({}, base, { roleAutonomy: 0 })).length, 1);
  assert.equal(G.approvalReasons(Object.assign({}, base, { responsibilities: [{ requiresHumanApproval: true }] })).length, 1);
  const chain = new E.EvidenceChain({ clock: clock() });
  const desk = new G.ApprovalDesk(chain, (s) => (s === "restricted" ? "accountable-owner" : s === "confidential" ? "data-steward" : "team-lead"));
  const free = Object.assign({ id: "asg-free", employee: "de:ava", action: "message", state: "queued" }, base);
  assert.equal(desk.submit(free).status, "completed");
  const held = Object.assign({ id: "asg-held", employee: "de:helix", action: "mcp.call", state: "queued" }, base, { sensitivity: "confidential" });
  const r = desk.submit(held);
  assert.equal(r.status, "awaitingApproval");
  assert.equal(desk.decide(r.approval, "agent:thoxy", ["data-steward"], true).reason, "approver must be a person");
  assert.equal(desk.decide(r.approval, "human:sam", ["team-lead"], true).reason, "approver lacks role data-steward");
  assert.equal(desk.decide(r.approval, "human:lee", ["data-steward"], false).status, "blocked");
  assert.equal(desk.decide(r.approval, "human:lee", ["data-steward"], true).reason, "already decided");
  assert.equal(held.state, "blocked");
  assert.equal(chain.verify().ok, true);
});

test("handoffs: body hash misses a rewritten pair, chained hash does not", () => {
  const chain = new E.EvidenceChain({ clock: clock() });
  const team = [
    { id: "de:atlas", name: "Atlas", role: "Strategy research" },
    { id: "de:mira", name: "Mira", role: "Knowledge steward" },
    { id: "de:sera", name: "Sera", role: "Compliance sentinel" },
  ];
  const brief = "Draft an onboarding plan for a 40-person team.";
  const run = G.runOrderedTask(chain, team, brief);
  assert.equal(G.verifyHandoffs(run.handoffs, brief), -1);
  const edited = JSON.parse(JSON.stringify(run.handoffs));
  edited[1].text += " (edited)";
  assert.equal(G.verifyBodies(edited), 1);
  edited[1].body_sha256 = E.sha256(edited[1].text);
  assert.equal(G.verifyBodies(edited), -1, "rewriting the body hash defeats the body-only check");
  assert.equal(G.verifyHandoffs(edited, brief), 1, "the chained hash still catches it");
  const swapped = [run.handoffs[1], run.handoffs[0], run.handoffs[2]];
  assert.equal(G.verifyHandoffs(swapped, brief), 0);
});

test("memory keeps contradicting facts side by side", () => {
  const chain = new E.EvidenceChain({ clock: clock() });
  const store = [];
  G.rememberFact(chain, store, "de:mira", "Release cadence: weekly");
  const b = G.rememberFact(chain, store, "de:mira", "release cadence is biweekly.");
  assert.equal(store.length, 2);
  assert.deepEqual(b.contradicts, ["fact-1"]);
  assert.deepEqual(store[0].contradicts, ["fact-2"]);
  G.rememberFact(chain, store, "de:mira", "the build is green");
  assert.equal(G.rememberFact(chain, store, "de:mira", "build: red").contradicts.length, 0, "subject mismatch is not tagged, as observed in the product");
  assert.equal(chain.records.filter((r) => r.kind === "memory.contradiction").length, 1);
});
