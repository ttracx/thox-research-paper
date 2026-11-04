# Development — ThoxWork paper repository

This repository changes only when the paper changes. It follows the
THOX Research Paper Process v1.0 and the THOX Repository Creation
Standard v1.0.

## Edition rules

- A new edition is a new version everywhere at once: Zenodo new
  version, this repo's `paper/` files and release, the Hugging Face
  whitepapers dataset folder, and the thox.ai paper page. Never edit a
  shipped edition's bytes in place; versioned filenames are permanent.
- `artifact/exp/results/summary.json` is the single evidence source.
  If the suite changes, the summary is regenerated, its SHA-256 is
  updated in the README and artifact README in the same commit, and
  the change is called out in the release notes.
- The experiment suite is deterministic by design: standard library
  only, fixed master seed, no wall-clock or environment input. A run
  that does not reproduce the committed summary byte for byte is a
  defect, not a result.

## Release checklist (per edition)

1. New edition built and QA-passed under the Research Paper Process
   (blocker sweep, rendered-page inspection, independent verifier).
2. Both authors' consent to the exact bytes on record.
3. Zenodo new version deposited first; DOI recorded.
4. DOI substituted into `README.md`, `CITATION.cff`, `CITATION.bib`,
   `citation.bib`, `paper.bib`, `NOTICE.md`; hashes recomputed.
5. Release tagged `v<edition>` with the PDF, HTML edition, and demo
   attached, byte-identical to `paper/`.
6. Association pass in the same pass: HF dataset folder, website page,
   pipeline registry and manifest updated with the DOI.
