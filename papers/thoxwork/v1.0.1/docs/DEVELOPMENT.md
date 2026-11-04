# Development — ThoxWork paper (v1.0.1 folder)

This folder changes only when the paper changes. It follows the
THOX Research Paper Process v1.0 and the THOX Repository Creation
Standard v1.0.

## Edition rules

- A new edition is a new version everywhere at once: Zenodo new
  version, this folder's `paper/` files, the Hugging Face
  whitepapers dataset folder, and the thox.ai paper page. Never edit a
  shipped edition's bytes in place; versioned filenames are permanent.
- `artifact/exp/results/summary.json` is the single evidence source.
  If the suite changes, the summary is regenerated, its SHA-256 is
  updated in the README and artifact README in the same commit, and
  the change is called out in the folder's HANDOFF.md.
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
   `NOTICE.md`; hashes recomputed.
5. Folder committed with the PDF, HTML edition, and demo in `paper/`
   and `MANIFEST.sha256` regenerated over the whole folder.
6. Association pass in the same pass: HF dataset folder, website page,
   pipeline registry and manifest updated with the DOI.
