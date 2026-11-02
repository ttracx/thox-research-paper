# Historical reference: scope and provenance

`reference_whitepaper_v0.1.0.md` is preserved **byte-for-byte** from the user-supplied package. It is a historical October 31, 2026 design paper for the older Linux/Core lane. Its architecture, licensing proposals, model-publication status, readiness wording, and authorship presentation must not be read as the current ThoxInux manuscript.

The current manuscript is `main.tex`, with the corresponding `main.pdf` and `references.bib` at revision 0.2.0-review. The historical figures are not reused as current architecture diagrams.

## Source identity

- Size: 65,885 bytes.
- SHA-256: `3c6111630440e6ead0b88fbfc47b39cbde600d9d565332381baa88d691773487`.
- Exact public Git blob: `34a8b2bdca8e59f10cabaa0a9cfb331a29f5bc9e`.
- [Public Markdown source at the reviewed revision](https://github.com/Thox-ai/thoxos-core/blob/887b8c9c47f352a577b4592c6f81a2c1570d9af3/docs/whitepaper/ThoxOS_Whitepaper_v0.1.0.md).
- [Matching public HTML source](https://github.com/Thox-ai/thoxos-core/blob/887b8c9c47f352a577b4592c6f81a2c1570d9af3/docs/whitepaper/ThoxOS_Whitepaper_v0.1.0.html).

## Restored figures

The uploaded ZIP lacked all six SVGs referenced by the Markdown. The review recovered the exact inline SVG fragments from the public HTML, without redrawing or altering their content:

1. `figures/fig1-stack.svg`
2. `figures/fig2-entitlement.svg`
3. `figures/fig3-rauc.svg`
4. `figures/fig4-kernel-tracks.svg`
5. `figures/fig5-open-paid.svg`
6. `figures/fig6-capacity.svg`

All six relative links resolve, all six files parse as XML, and no external SVG resource links were found. `HISTORICAL_FIGURES_PROVENANCE.json` preserves exact source and output hashes. These checks establish recovery and link integrity; they do not validate the historical design claims.

## Attribution and rights

The original paper credits Sadie Weaving as an openly synthetic drafter and Tommy Xaypanya as accountable human author. That historical attribution is preserved rather than silently rewritten. The current scholarly byline includes Craig Ross and Tommy Xaypanya, with synthetic contributions disclosed as AI assistance.

The reference explicitly states **CC BY 4.0, copyright 2026 THOX.ai LLC** and retains a separate trademark notice. Recovered figure provenance follows that source. Neither the root repository's software license nor this review expands rights over MeshStack, ThoxWork, ThoxKey firmware, or any third-party work. The current manuscript is a substantial revision: its kernel framing, evidence map, validation protocol, references, limitations, and presentation have changed.
