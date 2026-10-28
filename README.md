# thox-research-paper

Skill and documentation for end-to-end authoring, technical drawings, requirements compliance, and publishing of research papers on behalf of THOX.ai, including submission to Hugging Face Papers.

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
# Or copy SKILL.md into ~/.claude/skills/thox-research-paper/SKILL.md (or equivalent)
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

The skill prepares all files and exact next steps. Actual arXiv upload and HF claims require your authenticated action.

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
