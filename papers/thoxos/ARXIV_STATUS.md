# arXiv preparation status

**Manuscript:** ThoxOS and ThoxInux: Architecture, Evidence, and a Validation Protocol for Local-First AI

**Revision:** 0.2.0-review

**Decision:** Technical draft corrected and internally reviewed; **arXiv submission readiness is not established**.

**Submission performed:** No.

## Repaired in this revision

The original source fails a strict TeX build; both supplied PDFs contain clipped text. The replacement source corrects the layout, builds with a real bibliography and in-text citations, and preserves both requested human authors and ORCID identifiers. It replaces obsolete kernel framing, scopes model and system evidence, and adds methods, ablations, safety, ethics, and reproducibility sections.

The revised abstract contains 187 whitespace-delimited words and 1,527 characters before any metadata formatting. This satisfies the checked 1,920-character arXiv metadata limit and the THOX 150–250-word target. Passing these mechanical checks does not make the research contribution submission-ready.

## Remaining scientific gates

1. Establish a complete, sufficiently developed research contribution. This draft is primarily an architecture/status review and evaluation protocol. arXiv's content policy normally excludes proposals for future research; a source build cannot resolve that issue.
2. Execute the selected bounded workload study or supply a complete, independently assessable analytical contribution. Preserve exact payloads, raw runs, failures, baselines, and uncertainty.
3. Review the exact final manuscript with both human authors. Verify contributions, affiliations, consent, rights, and the chosen distribution license. The provided byline does not itself record consent to this version.
4. Recheck current source heads and model cards immediately before freezing the submission. Reconcile any material change and regenerate the PDF/source inventory.

## Remaining operational gates

- Check the actual submitting account, category endorsement, existing submissions, current-month and active-submission counts, and any account-specific restrictions. These were not inspected during this review.
- Choose the category with the authors. **cs.OS** is the strongest initial editorial fit; a cross-list is a separate judgment, not an assumed entitlement.
- Prepare a separate clean TeX upload directory and inspect every included file, including comments, for public archival safety.
- Compile that exact directory, run the offline source preflight, inspect every locally rendered page, and then inspect arXiv's own generated PDF during an authorized submission.
- Obtain or reuse valid authorization for the exact artifact, destination, and action. Do not treat a local commit, public repository access, or static preflight pass as a submission receipt.

## Official sources checked on November 1, 2026

- [Metadata and abstract requirements](https://info.arxiv.org/help/prep.html)
- [TeX source requirements](https://info.arxiv.org/help/submit_tex.html)
- [Submission overview](https://info.arxiv.org/help/submit/index.html)
- [Content types](https://info.arxiv.org/help/policies/content-types.html)
- [Moderation, AI-use disclosure, and submission rates](https://info.arxiv.org/help/moderation/index.html)
- [Identity and affiliation](https://info.arxiv.org/help/policies/identity_and_affiliation.html)
- [Hugging Face Paper Pages](https://huggingface.co/docs/hub/paper-pages)

The checked arXiv moderation policy states a maximum of two new submissions per calendar month and three active submissions, with possible individual restrictions. These are policy limits, not a verified eligibility result for an account. Hugging Face paper indexing, an authorship claim, and Daily Papers inclusion remain separate downstream steps. None implies external peer review.
