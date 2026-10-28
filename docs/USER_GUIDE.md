# User Guide — thox-research-paper

## What this is

An agent skill that takes a THOX.ai research paper from a one-line brief to
a submission-ready package: requirements capture, outline, academic
authoring with technical drawings, requirements and compliance checklists,
arXiv preparation, and Hugging Face Papers indexing under the Thox-ai
organization.

## Workflow

1. **Requirements capture.** Title/topic, key contributions and claims,
   methods, results or data availability, target venue, authors and
   affiliations (default: Craig Ross, Tommy Xaypanya, THOX.ai LLC), figures
   needed, and related Thox-ai models, datasets, and Spaces to link.
2. **Outline.** Standard structure: title/authors/abstract, introduction,
   related work, method/architecture with figures, experiments/results,
   discussion/limitations, conclusion, references, and a NeurIPS-style
   reproducibility and ethics checklist. Complex papers get outline
   confirmation before drafting.
3. **Authoring with technical drawings.** Plots are generated with
   matplotlib/seaborn with the code kept for reproducibility; diagrams are
   TikZ/PGFPlots, Mermaid, or SVG. Vector formats are preferred. THOX brand
   green #05A451 is used for accents where appropriate.
4. **Requirements and compliance.** Venue checklists (arXiv, NeurIPS-style)
   are built alongside the paper, with an evidence register recording the
   identifier behind each source (job id, commit hash, repository SHA, or
   file path).
5. **Distribution preparation.** arXiv LaTeX source and packaging, Hugging
   Face Papers indexing/claim preparation, and Daily Papers submission
   preparation under Thox-ai, with links to related models, datasets, and
   Spaces.

## Hard rules

- A paper without a limitations section is unfinished.
- Submission, claiming, and any public release under the THOX.ai name are
  separate steps that follow the founder approval posture; the skill
  prepares them, an authorized principal performs them.
- Never present a drafted or packaged paper as submitted or published.
  Report the exact state reached and name the step that remains.
- Every paper gets its own repository under the THOX repository standard
  (README, LICENSE, NOTICE.md, docs/, .agents/HANDOFF.md, formal release
  per version).

## Brand

Papers align with "Your AI. Your Data. Your Rules." and emphasize
local-first, privacy-preserving, on-device AI, MagStack/MeshStack, and edge
hardware where the subject supports it.
