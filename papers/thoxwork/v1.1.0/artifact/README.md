# ThoxWork — Research Paper v1.1.0 (Comprehensive Edition) — Artifact Package

**Paper:** Craig Ross and Tommy Xaypanya, "ThoxWork for the Enterprise:
Governed Digital Employees, MeshGroups, Rolodex and Evidence-First Teamwork."
THOX.ai Research technical report, comprehensive edition v1.1.0, 2026-11-04.
Version DOI: 10.5281/zenodo.23965052 - Concept DOI: 10.5281/zenodo.23963935
License: CC BY 4.0. Supersedes v1.0.1 (DOI 10.5281/zenodo.23963936).

## Contents
- `dist/` - the shipped trio: paper PDF, single-file paper HTML, interactive demo HTML.
- `exp/` - the evidence: `results/summary.json` is the single evidence source for
  every number in the paper (schema thoxwork-summary/1.1.0), with the underlying
  product-test, planner, admission-divergence, Evidence Lab and live-core
  acceptance records it merges, and the deterministic simulator code of the
  paper of record (`thoxwork_experiments.py`) with its own results
  (`oracle_summary_v100.json`).
- `wp/` - the build: `paper.src.html` (single source for the shipped PDF and
  HTML), `build.py` (WeasyPrint render), `surgery.py` (the v1.1.0 merge edits,
  each one asserted), and `qa/` (render QA report, page contact sheets and the
  numbers proof).
- `CITATION.cff`, `CITATION.bib` - citation metadata for this edition.

## Evidence classes
Numbers are labelled in the paper as they are labelled in the summary:
MEASURED (product test suites, Evidence Lab runs, and the live core service
acceptance replay of Section 7.7) or SIMULATED (the deterministic protocol
oracle of the paper of record; its E5 scale result is a non-collapse result,
not an efficiency claim).
