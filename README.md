# thox-research-paper

Skill and documentation for end-to-end authoring, technical drawings, requirements compliance, and publishing of research papers on behalf of THOX.ai, including submission to Hugging Face Papers.

## Automatic Research Studio workflows (1.2.0)

Relevant THOX research, official-paper and continuation requests can select the installed skills implicitly. The `/thox-research-paper` entry point remains available. The new `thox-research-studio` router coordinates discovery, private checkpoints and a single manuscript integrator. See [routing and connection status](skills/thox-research-paper/references/studio-connector-routing.md).

All generated THOX publications use [the shared author profile](skills/thox-research-paper/references/publication-authors.md): Craig Ross, Chief Executive Officer, and Tommy Xaypanya, Chief Technology Officer and Co-Founder, both THOX.ai LLC. Tommy's ORCID is `0009-0000-4425-9565`. Existing author order, actual contributions and publication approvals remain applicable.

```sh
python skills/thox-research-paper/scripts/research_context.py authors --format markdown
python skills/thox-research-paper/scripts/research_context.py checkpoint --project-id mesh-study --topic "Heterogeneous edge inference"
python -m unittest discover -s tests -v
```

The helper prints data only and never logs in or submits a paper. Store checkpoints privately outside this public repository. The actual operator account alias is held only in the private plugin, not this public distribution. Remote Studio tools were not exposed during this update; plugin-side routing is not a deployed connector. See [validation](docs/VALIDATION-1.2.0.md).

## Mandatory arXiv preflight and account workflow

Version 1.1.1 adds the [Preflight Checklist for New Submissions](skills/thox-research-paper/references/arxiv-preflight.md), the [secure account workflow](skills/thox-research-paper/references/arxiv-account-workflow.md), and an [offline checker with usage instructions](docs/ARXIV_PREFLIGHT.md).

Require TeX source for TeX-authored papers, a clean upload folder, complete files/references and an archival-safety review including TeX comments. Static checks do not establish publication readiness. Review the exact source, final PDF, current account eligibility and applicable publication authority.

No account credentials, live authenticated session, SWORD permission or automatic publishing service are included. See [validation and handoff](docs/VALIDATION-1.1.1.md) for the 27 local tests and remaining operational gates. Keep unpublished papers and account records outside this public repository.

## ThoxWork for the Enterprise, technical report v1.0.0 (4 November 2026)

[papers/thoxwork/v1.0.0](papers/thoxwork/v1.0.0/README.md) holds the THOX.ai Research technical report *ThoxWork for the Enterprise: Governed Digital Employees, MeshGroups, Rolodex and Evidence-First Teamwork* by Craig Ross and Tommy Xaypanya: PDF, standalone HTML, the ThoxWork Evidence Lab (one offline HTML file), experiments, results, figures, reviewed product captures and a narrated summary video (16:9 and 9:16; the narration voice is AI-generated). Preprint, not peer reviewed; no DOI yet. A code-level account of THOX's third platform: 3,747 tests rerun across 18 suites in 9 code bases, a browser lab that matches the ThoxWork routing planner on 12,000 of 12,000 seeded previews, three MeshGroup admission definitions shown side by side, and an evidence chain that needs a key and an outside anchor to catch truncation. Nothing is measured on a THOX device or a customer deployment.

## ThoxOS / ThoxInux technical report v1.0.1 (3 November 2026)

[papers/thoxos/v1.0.1](papers/thoxos/v1.0.1/README.md) holds the THOX.ai Research technical report that builds on the 0.2.0-review draft: PDF, standalone HTML, browser demo, experiments and build pipeline. Preprint, not peer reviewed. Measured entitlement token designs, simulated A/B update contract, the Linux-ABI ledger at the ThoxInux pin joined with a traced agent loop, and the kernel-model memory budget.

## ThoxOS / ThoxInux manuscript draft

The [ThoxOS paper directory](papers/thoxos/README.md) contains revision `0.2.0-review`: editable LaTeX, a compiled PDF, verified bibliography, a claim-level evidence ledger, and the preserved historical reference with its six recovered figures. It reconciles the Ginux-derived ThoxInux foundation with the older Linux/Core design and retains model, payload, hardware, and licensing limits.

Machine-readable citation metadata: [`CITATION.cff`](CITATION.cff).

Status identifiers, stated plainly: this draft's DOI is
[10.5281/zenodo.23876230](https://doi.org/10.5281/zenodo.23876230)
(Zenodo record: https://zenodo.org/records/23876230), recorded in
`CITATION.cff`. It has **no arXiv ID**.

This is an internally reviewed technical draft. It is not an arXiv submission, an empirical validation of the full platform, or an externally peer-reviewed paper. See [validation](papers/thoxos/VALIDATION.md) and [submission status](papers/thoxos/ARXIV_STATUS.md). The existing hold on unpublished manuscripts and account material remains applicable; a local candidate or build pass does not authorize public release.

## Overview

This repository contains the `thox-research-paper` agent skill that enables complete workflows for writing, illustrating, validating, and distributing research papers under the THOX.ai brand (Hugging Face organization: Thox-ai).

**Core capabilities:**
- Requirements capture aligned with THOX values ("Your AI. Your Data. Your Rules.")
- Full paper structure and academic authoring
- Technical drawings and figures (TikZ, Mermaid, matplotlib plots)
- Requirements & compliance checklists (arXiv, NeurIPS-style)
- arXiv preparation (LaTeX source, packaging)
- Hugging Face Papers indexing, claim, and Daily Papers submission under Thox-ai
- Linking to related models, datasets, and Spaces

## Installation

### For Claude Code / Agent Skills

Place the skill in your skills directory:

```bash
# Clone or download
git clone https://github.com/ttracx/thox-research-paper.git
# Keep the full skills/ tree and its references/scripts; do not copy SKILL.md alone.
```

Alternatively, with the skills CLI (if available):

```bash
npx skills add https://github.com/ttracx/thox-research-paper --skill thox-research-paper
```

### Usage

Trigger the skill by requesting paper authoring, technical drawings for research, arXiv preparation, or Hugging Face Papers submission related to THOX.ai.

Example prompts:
- "Write a research paper on local-first edge AI for THOX.ai"
- "Generate technical drawings and LaTeX for a paper on MagStack"
- "Prepare this draft for arXiv and submit to Hugging Face Papers under Thox-ai"

The skill prepares all files and exact next steps. Actual arXiv upload and HF claims require authenticated execution and the applicable publication gates.

## Repository Structure

- `SKILL.md` — The agent skill (YAML frontmatter + instructions)
- `README.md` — This documentation
- (Future) `examples/`, `checklists/`, `templates/`

## Related

- Hugging Face org: https://huggingface.co/Thox-ai
- Papers submit: https://huggingface.co/papers/submit
- arXiv: https://arxiv.org

## License

Apache-2.0 (consistent with THOX.ai public artifacts)

---

THOX.ai LLC — Your AI. Your Data. Your Rules.
