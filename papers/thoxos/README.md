# ThoxOS / ThoxInux research draft

**Revision:** 0.2.0-review

**Evidence cutoff:** November 1, 2026, America/Chicago

**Status:** Internally reviewed architecture and validation-status draft. Not submitted to arXiv. Submission readiness is not established.

**DOI:** [10.5281/zenodo.23876230](https://doi.org/10.5281/zenodo.23876230) (Zenodo record, deposited November 1, 2026: PDF, LaTeX source, bibliography and evidence ledger; CC BY 4.0)

## What this revision establishes

This revision corrects the supplied Grok manuscript against current ThoxInux sources. It identifies the Ginux-derived x86-64 foundation, separates current work from the older Linux/Core design, preserves proprietary portfolio boundaries, and connects technical claims to exact sources. It defines experiments for kernel/workload compatibility, resident agents, offline operation, update recovery, model behavior, and hardware feasibility.

The source reports bounded engineering-preview evidence. Historical component tests, repository-reported VM runs, publisher-reported model scores, and proposed experiments remain separate. A working integrated ThoxOS/AgentOS/model/device system is not established by this manuscript.

## Authors

| Author | Affiliation / role | ORCID |
| --- | --- | --- |
| Craig Ross | THOX.ai LLC, Chief Executive Officer | [0009-0005-9872-3673](https://orcid.org/0009-0005-9872-3673) |
| Tommy Xaypanya | THOX.ai LLC, Chief Technology Officer and Co-Founder | [0009-0000-4425-9565](https://orcid.org/0009-0000-4425-9565) |

The user supplied these identities. No claim of account authentication or exact-version coauthor consent is made. AI assistance is disclosed in the manuscript.

## Contents

| File | Purpose |
| --- | --- |
| `main.tex` | Corrected canonical manuscript |
| `references.bib` | Verified source references and immutable repository/model-card links |
| `main.pdf` | PDF generated from this revision |
| `Makefile` | Local PDFLaTeX/BibTeX build, with shell escape disabled |
| `evidence-ledger.json` | Claim-level sources, evidence classes, conditions, and limitations |
| `ARXIV_STATUS.md` | Submission status and remaining gates |
| `README_HANDOFF.md` | Reproduction instructions and scoped continuation work |
| `reference_whitepaper_v0.1.0.md` | Unmodified, historical October 31 Linux-plan source; not the current manuscript |
| `HISTORICAL_REFERENCE.md` | Provenance, recovered-figure record, and limits of the historical source |
| `figures/` | Six recovered SVGs belonging only to the historical reference |

## Build

Requirements: PDFLaTeX, BibTeX, latexmk, and the standard packages declared at the top of `main.tex`. No package download, model inference, OS boot, or network access is needed by this build.

```sh
make pdf
```

The build runs without shell escape, stops on TeX errors, writes intermediates under `build/`, and copies the PDF to `main.pdf`. Review the log for unresolved references and layout warnings, then inspect every final page. A successful document build does not demonstrate OS or model functionality.

## Critical evidence boundaries

- v0.9.0 Payload U has repository-reported bounded lifecycle runs under QEMU TCG and KVM. Those runs do not prove hardware qualification or complete AgentOS integration.
- v0.9.1 has controlled build-reproducibility evidence and was not separately lifecycle-run in the inspected record.
- The 17-attempt resident-agent failure belongs to the legacy edition Ginux guest EFI `21d12d86631df7947a9bd7389b664106676c6f97a18e44d38d9ddb906b00f7b4`. It is not a reproduced failure on unified Payload U or v0.9.1. A complete resident loop on those payloads remains unestablished.
- The current foundation is x86-64. An ARM64 scoping document is not an implemented or validated Arm port.
- GATE49 scores carry model-specific scoring and serving restrictions. The student gate runs used merged safetensors and do not establish GGUF or device equivalence.
- MeshStack, ThoxWork, and ThoxKey firmware are excluded from the ThoxInux open-source rights grant. This draft does not change their licensing.

## Rights and publication

No repository license or portfolio ownership decision is changed by this revision. The historical whitepaper explicitly carries **CC BY 4.0**, with THOX.ai LLC attribution and a separate trademark notice. Its recovered figures retain that provenance. The repository's software license does not erase those document-specific notices.

Public repository publication, arXiv submission, Hugging Face paper indexing, Daily Papers selection, and external peer-reviewed acceptance are separate actions and states. None is established by the local review package. Preserve the repository's existing hold on unpublished manuscripts until the owner approves the exact public-source publication.

## Related models and systems

The kernel models evaluated in this draft are published as:

- ThoxOS-Kernel-0.8B: https://huggingface.co/Thox-ai/ThoxOS-Kernel-0.8B and https://ollama.com/Thox-ai/thoxos-kernel-0.8b
- ThoxOS-Kernel-4B: https://huggingface.co/Thox-ai/ThoxOS-Kernel-4B and https://ollama.com/Thox-ai/thoxos-kernel-4b
- ThoxOS-Kernel-27B: https://huggingface.co/Thox-ai/ThoxOS-Kernel-27B and https://ollama.com/Thox-ai/thoxos-kernel-27b (card only; the 27B weights are not public)

The systems this draft covers are open source at:

- ThoxOS Core: https://github.com/Thox-ai/thoxos-core
- linux-thox (THOX Linux kernel): https://github.com/Thox-ai/linux-thox
- Thox Kernel Lab: https://github.com/Thox-ai/thox-kernel-lab
- ThoxOS images: https://github.com/Thox-ai/thoxos-images
- ThoxInux: https://github.com/Thox-ai/thoxinux
