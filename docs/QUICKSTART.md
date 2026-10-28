# Quickstart

## Install the skill

```bash
git clone https://github.com/ttracx/thox-research-paper.git
# Copy SKILL.md into your agent skills directory, e.g.
# ~/.claude/skills/thox-research-paper/SKILL.md
```

Or with the skills CLI:

```bash
npx skills add https://github.com/ttracx/thox-research-paper --skill thox-research-paper
```

## Run your first paper

1. Ask the agent for a THOX research paper and name the topic, the claims,
   and the target (arXiv, a conference style, or internal whitepaper).
2. The skill captures requirements first: contributions, methods, results
   or data availability, figures needed, and the Thox-ai models, datasets,
   or Spaces to link.
3. Review the generated outline before full drafting on any large paper.
4. Drafting produces LaTeX (or Markdown intermediate) with figures as
   TikZ/Mermaid/matplotlib sources kept beside the paper for reproduction.
5. Submission steps stay separate and authenticated: the skill prepares the
   arXiv package and the Hugging Face Papers submission, and an authorized
   THOX.ai principal performs the actual upload or claim.

See docs/USER_GUIDE.md for the full workflow and its gates.
