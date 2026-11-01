# Secure arXiv Account and Publishing Workflow

This package contains workflow instructions and an offline preflight checker. It does not provision a credential vault, login adapter, submission API, scheduler or persistent publishing service. A connected, authorized execution tool is required for live account actions. Never describe instructions alone as connected access or working auto-publication.

## Authentication boundary

Use the official entry point: https://arxiv.org/user/. Inspect available tools and the actual live sign-in flow before any account action. Use an already authenticated, user-controlled session or a supported secure credential-injection mechanism. Confirm the authenticated identity from the account page. A public login page or successful HTTP response is not proof of authentication.

Keep passwords, cookies, session tokens, recovery codes and private browser profiles out of plugin source, GitHub, issue bodies, logs, screenshots, prompts sent to general research/scraping services, manuscript bundles and downloadable artifacts. Store credentials only in an approved vault or operating-system credential store. Reference the actual configured secret identifier, never a fictional connection. Do not persist a password pasted into chat. Recommend rotation without repeating it. Do not change the password or recovery settings without a specific instruction.

If secure login cannot be completed, report `AUTH_NOT_CONNECTED`, name the actual missing runtime capability, and continue offline preparation. Do not retry credentials blindly, solve CAPTCHAs, evade access restrictions or weaken transport/retention safeguards. Stop for user-controlled MFA, CAPTCHA, or required identity/endorsement steps.

## Automated-submission permission

The official [third-party submission policy](https://info.arxiv.org/help/third_party_submission.html) documents an automated SWORD interface for permitted proxies and instructs prospective users to contact arXiv support for permission. A normal username/password does not establish SWORD access. Verify the account's actual permission, current service contract and approved testing arrangements before configuring such an adapter. Do not probe write endpoints or test with a dummy live publication. Browser login and automated-interface permission are separate gates.

## Authorized operations

1. **Inspect and set up:** read the authenticated profile, existing submissions, account notices and category eligibility. Compare account identity and affiliation with verified human principals. Do not invent an author identity, email verification, ORCID linkage or endorsement. A synthetic agent is not an author or the legal account holder.
2. **Prepare:** apply the [mandatory preflight](arxiv-preflight.md), create a clean source inventory and preserve the exact hashes, build evidence, metadata and source/PDF reviews in private storage. No upload of the working repository.
3. **Upload a draft:** use a live supported browser/API action only after inspecting its actual contract and checking authorization. Do not guess submission API endpoints, selectors or OAuth scopes. Reading the public metadata API does not establish publishing access.
4. **Validate the server result:** inspect the uploaded file list, compiler output and every page of the generated PDF. Fix missing references or files and rerun preflight after any change.
5. **Submit:** verify the current rules, account eligibility and limits, authorship consent, license/rights, archival acknowledgement, and valid publication authorization for the exact artifact. Reuse an existing valid approval rather than requesting it again. A general automation-setup request does not identify a final manuscript or license. Never accept new legal terms or make rights assertions without actual authority.
6. **Manage:** retain the provider's submission identifier and receipt. Read status and handle authorized corrections, replacements and journal/DOI metadata against the existing record rather than creating duplicates. Withdrawal, account-security changes and changes of rights require explicit applicable authority.

If a submission response is ambiguous or times out, inspect the account for the existing submission before retrying. A retry must not create a duplicate archival record. Use a single writer per account submission and retain a private action log without secrets.

## States and evidence

`AUTH_NOT_CONNECTED` -> `AUTH_VERIFIED` -> `PREFLIGHT_BLOCKED` or `READY_FOR_UPLOAD` -> `DRAFT_UPLOADED` -> `SERVER_PREVIEW_REVIEWED` -> `SUBMITTED` -> `ANNOUNCED`, `HELD` or `DECLINED`.

Transitions require observed evidence, not a state string alone. Record account alias (not credentials), source inventory hash, exact artifact/metadata approval, latest policy check, current-account eligibility, action, timestamp and provider receipt. Do not commit real account or submission records to the public repository.

The public repository can hold code, generic templates and tests. Private research, credentials, session state and release decisions remain outside it. No public-source authorization is inferred for unpublished manuscripts.

## Official sources to refresh

- Submission process and source rules: https://info.arxiv.org/help/submit/index.html
- TeX preparation: https://info.arxiv.org/help/submit_tex.html
- Moderation and current submission limits: https://info.arxiv.org/help/moderation/index.html#submission-rate
- Third-party submission rules: https://info.arxiv.org/help/third_party_submission.html
- Withdrawal and archival status: https://info.arxiv.org/help/withdraw.html
