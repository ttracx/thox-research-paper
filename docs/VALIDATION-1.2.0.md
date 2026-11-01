# THOX Research Team 1.2.0 validation and handoff

Date: 2026-11-01. Scope: private plugin and source-package update, not a research paper or remote Studio deployment.

## Implemented

Automatic natural-language routing descriptions and implicit-invocation metadata for the existing paper skill and a new Research Studio router. Shared publication authors include Craig Ross, Chief Executive Officer, and Tommy Xaypanya, Chief Technology Officer and Co-Founder, THOX.ai LLC. Tommy's ORCID is user-provided; Craig's ORCID and a corresponding-author designation remain unset. The optional arXiv account alias and private service locators are present only in the private plugin overlay, never in public source or author exports.

The bundled standard-library helper emits public author blocks (JSON, Markdown and a venue-adaptable LaTeX snippet), creates private checkpoint JSON, and validates checkpoint structure. It does not persist data or perform network calls. Existing arXiv static checks and publication gates are retained. A self-contained official-paper baseline permits useful drafting if a separately installed research standard is not exposed, without falsely claiming the missing standard was loaded.

## Executed validation

`python -m unittest discover -s tests -v`: 62 tests passed locally (27 retained preflight tests and 35 new author/profile/checkpoint/package-configuration tests). The CLI create/read/validate round trip used only synthetic local data. Public-author exports include both authors and exclude operational fields through an allowlist. Additional packaging checks verify relative reference targets, manifest identity/version and separation of private configuration from the public source archive.

These checks are not independent scientific review, host selection tests, live connector tests, PDF/TeX rendering, ORCID ownership verification or arXiv account authentication. The structural checkpoint validator never certifies publication readiness. The user-supplied ORCID URL could not be fetched during this update; the exact supplied identifier is retained without claiming independent verification.

## Connector boundary and next implementation step

Only plugin-side connector routing was updated. No separate authenticated Research Studio tool was exposed; the previously reported Studio source repository could not be read using either available GitHub connection, and the connected browser required its originating browser context. The plugin has no invented MCP endpoint and no new local-only runtime requirement.

When the actual editable Studio source or authenticated connector becomes available, inspect its real schemas, apply these shared authors to its generation records, and verify a private project create/read/resume round trip with real provider receipts. Do not substitute the separate marketing Research Loop or Publishing Desk. Until then, research and drafting use available tools with an explicit `STUDIO_NOT_CONNECTED` state and portable private handoffs.

The plugin update and source push have separate receipts. A source commit does not deploy a site or alter an existing conversation's loaded tools. No credentials, manuscript submissions, publication approvals or account-permission changes were made in this release. No existing archived publication was modified.
