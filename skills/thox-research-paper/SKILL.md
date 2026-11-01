---
name: thox-research-paper
description: Coordinate a THOX.ai research paper or substantive revision with a multi-agent engineering loop, primary literature from the previous 6 to 12 months, THOX formatting and independent validation. Use for /thox-research-paper and equivalent paper-generation requests.
---

# THOX Research Paper

Turn the user's actual research subject and available evidence into a rigorous THOX paper and reproducible supporting artifacts. Run the team during this conversation using available capabilities and existing authority. This is an orchestration entry point for the existing THOX research standard, not a background service or automatic publishing tool.

## Load the current THOX standard

Discover and read the installed `thox-research-publishing` skill by name. Record its package and workflow revision. Version 2.2.0 or later includes the requested team, rolling-literature and validation resources. Read its `references/team-engineering-loop.md` and `references/rolling-literature-context.md`, resolving them through the skill's actual resource provider. Do not hard-code a machine-specific directory or copy the whole policy into this entry point.

Load current `thox-brand-governance` and `thox-document-templates` for the manuscript. Resolve device, TXF, repository, document and PDF skills when the paper's subject or deliverables require them. If the current research dependency or a linked resource is unavailable, identify the missing capability, preserve useful private work, and do not claim the full workflow or formatting was validated. Do not invent access or silently replace missing policy with a remembered version.

## Execute the coordinated workflow

1. Resolve the topic, question, intended contribution, evidence, paper type, output formats and phase from the request and current project. If a necessary topic is still absent, ask for it after inspecting relevant context. Creating the plugin alone does not request a new study.
2. Complete canonical-source and cross-team review. Assign bounded literature, methods and engineering work in parallel where independent, within available concurrency. Use one owner per file and one manuscript integrator. Reserve an independent reviewer for each contribution being approved.
3. Honor an explicit user date window. Otherwise build a topic-specific corpus from the preceding six calendar months, expanding to twelve and justified adjacent CS/AI categories. Separate first-public date from revision date, retain relevant older foundations explicitly, verify full text and collect a comparison and writing-style matrix. Refresh at freeze. Do not impose a citation quota or reuse the same bibliography for every topic.
4. Connect a falsifiable hypothesis to a protocol, implementation, authorized execution, raw artifacts and claims. Iterate on actionable findings, preserve negative results and recheck corrected revisions. Use literature as cited context and structural guidance; do not describe reading as model-weight training or copy another paper's prose.
5. Independently validate claims and computations as well as writing and presentation. Run the existing research-loop structural check and artifact release audit where applicable, then complete the scientific and visual checks they cannot perform. Match the manuscript type and conclusions to the evidence actually available.
6. Freeze a consistent, versioned private bundle. Prepare publication only in the authorized phase. Read the parent skill's live arXiv checks for current formatting, originality, AI disclosure, eligibility and rate limits. Reuse any exact existing release approval; never infer submission authority from this command alone.

## Mandatory arXiv preflight and account operations

Before every new submission, read [Preflight Checklist for New Submissions](references/arxiv-preflight.md). Require TeX source for TeX-authored work, a separate clean upload directory, complete files/references, and review of every file for archival safety, including TeX comments. Do not automatically strip comments or required license notices. Use current official bibliography guidance rather than outdated blog workarounds.

Run `scripts/arxiv_preflight.py` when a Python-capable runtime and the exact staging directory are available. Its output is an offline static report, not proof of compilation, scientific validity, authentication or publication readiness. Resolve errors and warnings, complete the source and PDF reviews, and bind the review to the exact inventory hash. Keep all reports and private records outside the upload folder.

For login, account setup, uploads, replacements, submission status or publishing automation, read [Secure arXiv Account and Publishing Workflow](references/arxiv-account-workflow.md). Discover actual connected capabilities before acting. Never embed credentials or browser state in this plugin, the public repository, source bundles or logs. Do not send credentials to general research/scraping prompts. Use an authenticated user-controlled session or supported secure credential injection. Missing access is `AUTH_NOT_CONNECTED`, not a completed connection.

Automate only authorized operations on the exact reviewed artifact. Verify identity, rights, license, authorship consent, current eligibility/limits and the server-generated PDF before final submission. Reuse valid existing approval. Check for an existing submission before retrying an ambiguous result. Never claim that installing this skill itself provides a live login, submission API or always-on service.

Return the requested manuscript and supporting artifacts, their observed status, actual verification results, unresolved limitations and concrete next actions. Internal multi-agent review, preprint availability and peer-reviewed acceptance are distinct states. Do not claim a persistent team, trained model, experiment, submission or release that did not occur.
