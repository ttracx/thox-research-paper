# QA Report — ThoxWork Paper v1.1.0 (edition-v110)

Build date: 2026-11-04. Built per §4 of CLAUDE-PAPER-REVIEW.md.
Publication steps (Zenodo deposit, website, GitHub, HF, posting) were
NOT performed; they are a separate step after inspection.

## Deliverables

- THOX_ThoxWork_Research_Paper_v1.1.0.pdf — 45 pages, US Letter,
  SHA-256 in HASHES.md.
- THOX_ThoxWork_Research_Paper_v1.1.0.html — single file, verified
  self-contained (0 external loads, 0 file:// references, all three
  figures inlined as SVG, fonts embedded as data URIs).
- THOX_ThoxWork_Research_Paper_v1.1.0.docx — via LibreOffice
  (MS Word 2007 XML filter) from the print HTML.
- HASHES.md; exp/ (E8/E9 producers, supplement, merge, results);
  this report; VERIFIER-REPORT.md.

## Binding dispositions — compliance

- D1 reported as decided by implementation (Section 4.5 callout +
  Section 13): pooled admission stands; thoxwork-core implements
  Algorithm 1 and E11 exercised it live. The companion recommendation
  (single-node check, drop pooling) is named and not adopted, with the
  reason stated.
- Claude's divergence figures (56.3% / 4,333) appear exactly twice:
  Section 7.8's labelled port paragraph and Appendix A's reproduction
  note — both times as properties of the kit and the port, with the
  three port deviations printed. Never as measurements of Algorithm 1.
- Kit-as-rule framing corrected: Algorithm 1 governs in §§4.5, 6.2,
  7.7, 7.8; the kit is a comparator and reference implementation.
- Appendix D AI-assistance paragraph NOT adopted (boundary list only).
  The only "Claude" string in the paper is inside reference [72],
  the OpenWork project's own tagline ("alternative to Claude Cowork"),
  a bibliographic fact.
- "Cedar Park, Texas" byline NOT adopted (grep: 0 occurrences).
- Claude's title NOT adopted; the paper carries the v1.0.1 title.
- Stale pre-M1 statuses replaced: Table 6 leads with thoxwork-core
  (Live) and thoxwork-surface; MeshGroup split into shell Preview vs
  core implementation; RolodexGo correction carried verbatim in
  substance from v1.0.1.
- Gateway renumbered to Algorithm 2; measurement families renumbered
  E6–E10; E11 is the M1 live replay (Section 7.11, Table 12).
- Document control DOI line is byte-exact as specified:
  "DOI: 10.5281/zenodo.23963936 (v1.0.1); v1.1.0 DOI assigned at
  deposit under concept DOI 10.5281/zenodo.23963935". No version DOI
  was invented.
- Errata applied and verified against primary sources during the
  build: local-first fourth author = Mark McGranaghan (ACM record
  for DOI 10.1145/3359591.3359737; grep "McCarthy" = 0); Ju & Aral
  cited at arXiv v4 (2,234 participants, 11,024 ads; stale v1 figures
  2,310 / 11,138 absent); DynaFlow and CHAP titles corrected;
  SailPoint wording, WTI permutation-importance hedge, orchestration
  hedge, MCP/A2A Linux Foundation stewardship all applied.

## New evidence

- E8 and E9 were executed for this edition and independently
  re-verified (VERIFIER-REPORT.md: all counts identical, KAT 7/7,
  oracle hash exact, port study byte-identical).
- One production defect was found and fixed during the E9 build: an
  RFC 4231 test-case-2 expected value in the producer script was a
  mistyped constant (the run reported KAT 6/7). The constant was
  corrected to the RFC value, the full run was repeated (KAT 7/7),
  and the verifier's independent run also reports 7/7. The first
  run's detection matrix was unchanged by the fix, as expected —
  the defect was in a test vector, not in the chain code.
- E9 cost figures printed in Section 7.9 are the final producer
  run's medians (append 10.0 µs, verify 10.5 µs/record, 10,000-record
  verify 197 ms, bundle ≈228 B/record); the same quantities measured
  126 ms on an earlier run — host timing variance, labelled as host
  measurements in the paper and excluded from reproduction claims.
- E6/E7 were NOT re-executed (sources THOX-internal, not in this
  edition's artifact set); their delivered result files were read and
  cross-checked. Stated in the paper (Sections 12 item 4) and in the
  verifier report. Nothing was downgraded silently.
- D2 verification: the audited thoxwork clone at the census commit
  (ab29b61) carries LICENSE and NOTICE.md with a generic third-party
  preservation paragraph; no named OpenWork/OpenCode credit was found
  in it. The paper therefore states D2 as the standing posture and
  does NOT carry the companion edition's stronger claim that named
  notices were applied in the repository on 2026-11-04.

## Blocker sweep (source HTML, final)

- Placeholders (PENDING/TODO/TBD/FLIP-): 0.
- Internal hostnames / tailnet IPs / credentials: 0 (the one generic
  word "tailnet" was rephrased to "private-network endpoint").
- Confidentiality marks: 0 (the two "confidential" hits are the
  Equation 1 data-sensitivity class names, model vocabulary).
- "1.51": one occurrence, in the superseded-figure correction in
  Table 6 (MeshStack row), as required.
- Trademark symbol: only in the exact tagline (running footer and
  closing tagline line).
- Byline: Craig Ross (CEO, ORCID 0009-0005-9872-3673) first, Tommy
  Xaypanya (CTO & Co-Founder, corresponding author, ORCID
  0009-0000-4425-9565); rendered on single lines (page 1 inspected).
- Original summary.json intact and byte-identical (merge assertion +
  independent verifier).

## Rendering inspection

Rendered pages inspected as images: page 1 (front matter, byline,
abstract, stat families) and page 24 (Figure 3 with caption, §7.4–7.5
text). Section starts mapped across all 45 pages via text extraction;
tables and figures break cleanly; no orphaned headings observed in
the map. Full-page screenshot inspection of every page was not
performed; the inspection above is the record.

## Page count — FLAGGED DEVIATION

The edition is **45 pages** against the spec's ~38-page target.
Per-section outcome vs the review's own §4 budgets: §1 ≈1.3 pp
(budget 3), §2 ≈4 (5), §§3+4 ≈8 (9 combined), §5 ≈4 (4), §6 ≈2.7
(2.5), §7 ≈7 (7), §§8–14 ≈8.5 (10.5 combined), appendices ≈2.7 (3.5),
references ≈5.5 (5–6), front matter ≈2 (unbudgeted). Nearly every
section is at or under its budget; the review's section budgets sum
to well over 38 once front matter and references are counted, so the
~38 total and the section budgets are internally inconsistent.
No mandated content was cut to chase the total. If a shorter edition
is wanted, the identified no-loss trims (captures prose §7.12,
Table 6 cell compression, one E5 figure) recover roughly 2–3 pages;
anything beyond that removes required folds.

## Sibling-tree conflict — FLAGGED

A parallel build tree existed (built earlier the same evening from
the companion edition's body). Its 38-page PDF carries the companion
edition's title, the "Cedar Park, Texas" byline, the 56.3% figure as
a headline, and the live replay as an unnumbered insertion — all
contrary to the binding dispositions. This edition was built fresh
from the v1.0.1 source and does not use that tree's paper; the tree
was left untouched and was formally marked superseded before
deposit so the two v1.1.0 artefacts are not confused. Its exp/
folder served as the delivered-artifact source for the companion
numbers (planner/kit/divergence result files), which were verified
as recorded above.

(Publication-record scrub note: this copy of the QA report replaces
one internal build path with the description above; no other text
differs from the edition's internal QA record.)
