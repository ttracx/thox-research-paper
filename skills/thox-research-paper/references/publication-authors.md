# THOX publication authors

The user has directed that both human principals be included by default in all THOX publications created or revised by this workflow. Load `publication-authors.json` at the start of each relevant task and session. Do not ask the user to repeat these details.

| Author | Position | Affiliation | ORCID |
|---|---|---|---|
| Tommy Xaypanya | Chief Technology Officer and Co-Founder | THOX.ai LLC | https://orcid.org/0009-0000-4425-9565 |
| Craig Ross | Chief Executive Officer (CEO) | THOX.ai LLC | Not supplied; do not invent |

These are user-provided identity and role details, not independent verification of employment, ORCID ownership or account authentication. The ORCID page could not be fetched during the 1.2.0 update. Keep the supplied identifier unchanged. Do not derive Craig's ORCID or either author's email from a name or a plugin developer field.

## Apply consistently

Include both authors in the title page/byline, editable manuscript, PDF metadata where supported, Markdown/HTML exports, submission metadata, author biographies and publication-specific citation metadata. Use the organization as the scholarly affiliation. Include job titles in an author biography or a venue-compatible title block, rather than forcing corporate titles into a venue format that does not accept them. Respect blinded-review requirements by storing the identities in the private submission record and restoring them only at the appropriate non-blind stage.

Preserve approved project-specific author order and additional verified coauthors. Without a project-specific order, retain the repository's existing Craig Ross, Tommy Xaypanya order. Do not choose a corresponding author or invent contribution statements. A corporate role is not itself evidence of a scientific contribution. Before submission, verify each author's contribution, consent and the venue's authorship requirements. Reuse existing valid records rather than asking again. If a requirement is unresolved, retain the requested draft author list and flag the specific publication gate; do not invent consent or silently remove an author.

The default applies going forward and to authorized revisions. It does not authorize replacing already-announced papers or changing third-party publications. Synthetic contributors receive truthful assistance disclosures and appropriate acknowledgments, not human authorship.

## Keep accounts out of publication artifacts

Load the optional `operator-account.json` only from the private installed plugin or an authorized private store. It is operational configuration, not author metadata. Never place account usernames, passwords, cookies or authenticated-session details into manuscript text, source archives, public citation files or public repositories. The public source distribution deliberately omits the configured operator account file.

Use `scripts/research_context.py authors --format json|markdown|tex` to emit public author metadata. This helper reads only the public author profile and does not authenticate accounts.
