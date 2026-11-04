/*
 * Experiment E5: how often the two MeshGroup admission definitions on record
 * disagree on the same requests.
 *
 *   Reference rule  : THOX reference admission policy (single node; lab/src/meshgroup.js decide)
 *   Pooled rule     : Algorithm 1 of the ThoxWork research paper v1.0.0 (lab/src/meshgroup.js admitPooled)
 *
 * Inputs: the 200 seeded scenarios of exp/results/meshgroup_cases.json (50 nodes,
 * 100 requests each). Each request gets a seeded demand in GB, uniform on
 * [1, 1.5 x the largest free memory in the inventory]. Nothing is in use, so the
 * pooled rule's WAIT path does not fire; that path is out of scope here.
 * Output: exp/results/admission_divergence.json
 *
 * Usage: node exp/admission_divergence.js
 */
"use strict";
const fs = require("fs");
const path = require("path");
const M = require(path.join(__dirname, "..", "lab", "src", "meshgroup.js"));

const SEED = 20261104 + 5;
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const R = path.join(__dirname, "results");
const cases = JSON.parse(fs.readFileSync(path.join(R, "meshgroup_cases.json"), "utf8"));
const rnd = mulberry32(SEED);

const counts = {
  total: 0,
  both_admit_fits_one_node: 0,
  both_admit_pooled_needs_spanning: 0,
  reference_places_node_too_small: 0,
  reference_places_pooled_denies_unplaceable: 0,
  reference_denies_pooled_admits: 0,
  reference_none_pooled_admits: 0,
  both_refuse: 0,
  other: 0,
};
const detail = [];
const causes = { cross_site_only: 0, other: 0 };

for (const sc of cases.scenarios) {
  const maxFree = sc.nodes.reduce((m, n) => Math.max(m, n.ram_free_gb), 0);
  for (const req of sc.requests) {
    const demand = Math.round((1 + rnd() * (1.5 * maxFree - 1)) * 2) / 2;
    const ref = M.decide(req, sc.nodes, sc.policy);
    // The pooled rule has no tenant, classification or site-consent notion of its own;
    // apply the reference rule's request-level denials first so the comparison isolates placement.
    let pooled;
    if (ref.verdict === "DENY") pooled = { verdict: "DENIED", reason: "request-level" };
    else pooled = M.admitPooled({ required: [req.model], demand }, req.group, sc.nodes, sc.policy, 0);
    counts.total++;
    const refPlaced = ref.verdict === "PLACE";
    const chosen = refPlaced ? sc.nodes.find((n) => n.id === ref.node) : null;
    if (ref.verdict === "DENY" && pooled.verdict === "DENIED") counts.both_refuse++;
    else if (refPlaced && pooled.verdict === "ADMITTED") {
      if (chosen.ram_free_gb >= demand) counts.both_admit_fits_one_node++;
      else if (pooled.fitsOneNode) counts.reference_places_node_too_small++;
      else counts.both_admit_pooled_needs_spanning++;
    } else if (refPlaced && pooled.verdict === "DENIED") counts.reference_places_pooled_denies_unplaceable++;
    else if (ref.verdict === "NO_PLACEMENT" && pooled.verdict === "ADMITTED") {
      counts.reference_none_pooled_admits++;
      // Cause: would the reference rule place it if cross-site use were enabled and consented?
      const open = M.decide(Object.assign({}, req, { cross_site_consent: true }), sc.nodes, Object.assign({}, sc.policy, { cross_site_enabled: true }));
      if (open.verdict === "PLACE") causes.cross_site_only++; else causes.other++;
    }
    else if (ref.verdict === "NO_PLACEMENT" && pooled.verdict === "DENIED") counts.both_refuse++;
    else counts.other++;
    if (detail.length < 12 && refPlaced && chosen.ram_free_gb < demand) {
      detail.push({ group: req.group, model: req.model, demand, reference_node: ref.node, reference_node_free_gb: chosen.ram_free_gb, pooled_verdict: pooled.verdict, pooled_gb: pooled.pooled });
    }
  }
}

const admittedByReference = counts.both_admit_fits_one_node + counts.both_admit_pooled_needs_spanning + counts.reference_places_node_too_small + counts.reference_places_pooled_denies_unplaceable;
const out = {
  experiment: "E5 admission rule divergence", seed: SEED, demand_model: "uniform on [1, 1.5 x largest free GB] per scenario, rounded to 0.5 GB",
  counts,
  none_vs_pooled_causes: causes,
  shares: Object.fromEntries(Object.entries(counts).filter(([k]) => k !== "total").map(([k, v]) => [k, v / counts.total])),
  reference_placements: admittedByReference,
  reference_placements_on_too_small_node: counts.reference_places_node_too_small + counts.both_admit_pooled_needs_spanning + counts.reference_places_pooled_denies_unplaceable,
  examples: detail,
};
out.share_of_reference_placements_on_too_small_node = out.reference_placements_on_too_small_node / Math.max(1, admittedByReference);
fs.writeFileSync(path.join(R, "admission_divergence.json"), JSON.stringify(out, null, 1));
console.log(JSON.stringify(counts));
console.log("reference placements", admittedByReference, "on a node smaller than the demand", out.reference_placements_on_too_small_node, (out.share_of_reference_placements_on_too_small_node * 100).toFixed(1) + "%");
