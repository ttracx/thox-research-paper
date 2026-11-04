/*
 * Experiment E1: cost and tamper-detection behavior of the lab evidence chain.
 *
 * Runs the exact module the lab page ships (lab/src/evidence.js).
 * Timing: chain lengths 100, 1000, 10000; unkeyed and keyed; 1 warm-up run then
 * 30 measured repetitions per configuration. Detection: 6 attack classes, 500
 * seeded trials each, on 1000-record chains, with and without an external
 * head anchor (record count plus head hash held by a second party).
 * Output: exp/results/evidence.json (raw per-repetition values).
 *
 * Usage: node exp/evidence_experiments.js
 */
"use strict";
const fs = require("fs");
const path = require("path");
const os = require("os");
const E = require(path.join(__dirname, "..", "lab", "src", "evidence.js"));

const SEED = 20261104;
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const KINDS = ["policy.decision", "approval.request", "approval.decision", "action.execute", "handoff", "note"];
const ACTORS = ["human:reviewer", "de:router", "de:steward", "de:operator", "de:sentinel", "de:builder"];

function fixedClock() {
  let n = 0;
  return () => new Date(Date.UTC(2026, 10, 4, 12, 0, 0) + 1000 * n++).toISOString();
}

function buildChain(n, key, rnd) {
  const c = new E.EvidenceChain({ key, clock: fixedClock() });
  for (let i = 0; i < n; i++) {
    c.append(KINDS[Math.floor(rnd() * KINDS.length)], ACTORS[Math.floor(rnd() * ACTORS.length)], {
      step: i, group: "g" + Math.floor(rnd() * 8), verdict: rnd() < 0.8 ? "allow" : "deny", note: "r" + Math.floor(rnd() * 1e6),
    });
  }
  return c;
}

function nowMs() { const t = process.hrtime.bigint(); return Number(t) / 1e6; }

// ---------------------------------------------------------------- timing
const timing = [];
for (const n of [100, 1000, 10000]) {
  for (const keyed of [false, true]) {
    const key = keyed ? "lab-session-key-" + n : undefined;
    // warm-up
    buildChain(n, key, mulberry32(SEED)).verify();
    for (let rep = 0; rep < 30; rep++) {
      const rnd = mulberry32(SEED + rep);
      const t0 = nowMs();
      const c = buildChain(n, key, rnd);
      const t1 = nowMs();
      const v = c.verify();
      const t2 = nowMs();
      if (!v.ok) throw new Error("fresh chain failed verification");
      const bytes = Buffer.byteLength(JSON.stringify(c.exportBundle()));
      timing.push({ n, keyed, rep, append_ms: t1 - t0, verify_ms: t2 - t1, append_us_per_record: ((t1 - t0) * 1000) / n, verify_us_per_record: ((t2 - t1) * 1000) / n, bundle_bytes: bytes });
    }
  }
}

// ---------------------------------------------------------------- tamper detection
function rehashFrom(records, start, key) {
  // Attacker with write access recomputes hashes (and tags only if it holds the key) from start onward.
  for (let i = start; i < records.length; i++) {
    const r = records[i];
    r.seq = i;
    r.prev = i === 0 ? E.GENESIS : records[i - 1].hash;
    r.hash = E.sha256(E.canonical({ seq: r.seq, ts: r.ts, kind: r.kind, actor: r.actor, payload: r.payload, prev: r.prev }));
    if (key) r.tag = E.hmacSha256(key, r.hash);
  }
}

const ATTACKS = {
  edit_payload: (recs, rnd) => { const i = Math.floor(rnd() * recs.length); recs[i].payload.verdict = recs[i].payload.verdict === "allow" ? "deny" : "allow"; return i; },
  edit_actor: (recs, rnd) => { const i = Math.floor(rnd() * recs.length); recs[i].actor = "human:approver"; return i; },
  swap_adjacent: (recs, rnd) => { const i = Math.floor(rnd() * (recs.length - 1)); const t = recs[i]; recs[i] = recs[i + 1]; recs[i + 1] = t; return i; },
  delete_middle: (recs, rnd) => { const i = 1 + Math.floor(rnd() * (recs.length - 2)); recs.splice(i, 1); return i; },
  truncate_tail: (recs, rnd) => { const k = 1 + Math.floor(rnd() * 50); recs.splice(recs.length - k, k); return recs.length; },
  // Edit one record and re-chain every later record without the session key.
  rechain_suffix: (recs, rnd) => { const i = Math.floor(rnd() * recs.length); recs[i].payload.verdict = "allow"; recs[i].payload.note = "forged"; rehashFrom(recs, i, null); return i; },
};

function detect(records, key, anchor) {
  const v = E.EvidenceChain.verify(records, key);
  if (!v.ok) return { detected: true, by: "chain", at: v.firstBad };
  if (anchor) {
    if (records.length !== anchor.count) return { detected: true, by: "anchor-count", at: Math.min(records.length, anchor.count) };
    const head = records.length ? records[records.length - 1].hash : E.GENESIS;
    if (head !== anchor.head) return { detected: true, by: "anchor-head", at: records.length - 1 };
  }
  return { detected: false, by: "", at: -1 };
}

const detection = [];
const N = 1000, TRIALS = 500;
for (const [name, attack] of Object.entries(ATTACKS)) {
  for (const keyed of [false, true]) {
    for (const anchored of [false, true]) {
      let detectedCount = 0, exactPosition = 0;
      const byCounts = {};
      for (let t = 0; t < TRIALS; t++) {
        const rnd = mulberry32(SEED * 7 + t);
        const key = keyed ? "lab-session-key" : undefined;
        const c = buildChain(N, key, rnd);
        const anchor = anchored ? { count: c.records.length, head: c.head() } : null;
        const recs = JSON.parse(JSON.stringify(c.records));
        const pos = attack(recs, rnd);
        const d = detect(recs, key, anchor);
        if (d.detected) {
          detectedCount++;
          byCounts[d.by] = (byCounts[d.by] || 0) + 1;
          if (d.by === "chain" && d.at === pos) exactPosition++;
        }
      }
      detection.push({ attack: name, keyed, anchored, trials: TRIALS, detected: detectedCount, rate: detectedCount / TRIALS, chain_detected_at_exact_position: exactPosition, by: byCounts });
    }
  }
}

const kat = E.selfTest();
const out = {
  experiment: "E1 evidence chain", seed: SEED, created: new Date().toISOString(),
  host: { platform: process.platform, arch: process.arch, node: process.version, cpus: os.cpus().length, cpu_model: os.cpus()[0] ? os.cpus()[0].model : "", mem_gb: Math.round(os.totalmem() / 1e9) },
  known_answer_tests: kat, timing, detection,
};
fs.mkdirSync(path.join(__dirname, "results"), { recursive: true });
fs.writeFileSync(path.join(__dirname, "results", "evidence.json"), JSON.stringify(out, null, 1));
console.log("KAT", JSON.stringify(kat));
for (const d of detection) console.log(d.attack.padEnd(15), "keyed", String(d.keyed).padEnd(5), "anchored", String(d.anchored).padEnd(5), "rate", d.rate.toFixed(3), JSON.stringify(d.by));
