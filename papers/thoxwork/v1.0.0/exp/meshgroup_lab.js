/*
 * Experiment E2 (lab side): agreement and timing of the lab MeshGroup admission
 * module against the THOX reference policy outcomes.
 *
 * Reads exp/results/meshgroup_cases.json and meshgroup_timing_cases.json (written
 * by exp/meshgroup_reference.py), runs lab/src/meshgroup.js on every request,
 * compares outcomes one by one, then times 1000-request batches at 10, 100 and
 * 1000 nodes (one warm-up, 30 repetitions). Output: exp/results/meshgroup_lab.json.
 *
 * Usage: node exp/meshgroup_lab.js
 */
"use strict";
const fs = require("fs");
const path = require("path");
const os = require("os");
const M = require(path.join(__dirname, "..", "lab", "src", "meshgroup.js"));

const R = path.join(__dirname, "results");
const cases = JSON.parse(fs.readFileSync(path.join(R, "meshgroup_cases.json"), "utf8"));
const timingCases = JSON.parse(fs.readFileSync(path.join(R, "meshgroup_timing_cases.json"), "utf8"));

let total = 0, agree = 0;
const mismatches = [];
const byOutcome = {};
for (let si = 0; si < cases.scenarios.length; si++) {
  const sc = cases.scenarios[si];
  M.validatePolicy(sc.policy);
  sc.requests.forEach((req, ri) => {
    const got = M.outcome(M.decide(req, sc.nodes, sc.policy));
    const want = sc.reference_outcomes[ri];
    total++;
    const cls = want.startsWith("NODE:") ? "PLACE" : want;
    byOutcome[cls] = (byOutcome[cls] || 0) + 1;
    if (got === want) agree++;
    else if (mismatches.length < 25) mismatches.push({ scenario: si, request: ri, want, got });
  });
}

// Explanations: how often each exclusion reason fires across all admitted requests.
const exclusionCounts = {};
for (const sc of cases.scenarios) {
  for (const req of sc.requests) {
    const d = M.decide(req, sc.nodes, sc.policy);
    if (d.excluded) for (const e of d.excluded) exclusionCounts[e.reason] = (exclusionCounts[e.reason] || 0) + 1;
  }
}

const timing = [];
for (const n of ["10", "100", "1000"]) {
  const sc = timingCases[n];
  const run = () => { let sink = 0; for (const req of sc.requests) sink += M.decide(req, sc.nodes, sc.policy).verdict.length; return sink; };
  run();
  for (let rep = 0; rep < 30; rep++) {
    const t0 = process.hrtime.bigint();
    run();
    const dt = Number(process.hrtime.bigint() - t0) / 1e6;
    timing.push({ impl: "lab-js", n_nodes: Number(n), rep, batch: sc.requests.length, batch_ms: dt, us_per_decision: (dt * 1000) / sc.requests.length });
  }
}

const out = {
  experiment: "E2 MeshGroup admission agreement and timing", seed: cases.seed,
  host: { platform: process.platform, arch: process.arch, node: process.version, cpus: os.cpus().length, cpu_model: os.cpus()[0] ? os.cpus()[0].model : "" },
  agreement: { total, agree, rate: agree / total, by_reference_outcome: byOutcome, mismatches },
  exclusion_reason_counts: exclusionCounts, timing,
};
fs.writeFileSync(path.join(R, "meshgroup_lab.json"), JSON.stringify(out, null, 1));
console.log(`agreement ${agree}/${total}`, JSON.stringify(byOutcome));
if (mismatches.length) console.log("first mismatches", JSON.stringify(mismatches.slice(0, 5)));
