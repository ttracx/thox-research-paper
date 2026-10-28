# Development

## Layout

- `SKILL.md` — the agent skill (frontmatter + workflow). This is the
  product; edit it deliberately and keep the frontmatter description
  accurate, because agents select the skill from that text.
- `README.md` — human-facing overview and installation.
- `docs/` — USER_GUIDE.md, QUICKSTART.md, this file, and previews/ for
  rendered paper previews and boards.
- `.agents/HANDOFF.md` — live state for the next agent; update it on every
  significant change.

## Changing the skill

1. Edit SKILL.md on a branch; keep workflow steps executable and in order.
2. Check that every external action the workflow names (arXiv upload, HF
   Papers claim/submission, public release) stays behind the founder
   approval posture stated in the skill.
3. Keep claims honest: the skill prepares submissions; it does not perform
   authenticated uploads by itself.
4. Update README.md and docs/USER_GUIDE.md when behavior changes, and note
   the change in .agents/HANDOFF.md.

## Releases

Cut a formal GitHub release per version once a change lands on main,
following the THOX Repository Creation Standard v1.0.
