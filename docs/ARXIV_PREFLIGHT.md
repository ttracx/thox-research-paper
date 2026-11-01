# arXiv submission preparation

The canonical [Preflight Checklist for New Submissions](../skills/thox-research-paper/references/arxiv-preflight.md) is required for every new submission. It covers TeX source, a clean upload folder, missing files/references and archival safety, including source comments.

Use the [secure account workflow](../skills/thox-research-paper/references/arxiv-account-workflow.md) for authenticated operations. This repository contains no account credentials, authenticated session or deployed publishing adapter.

## Check a staged package

```sh
python skills/thox-research-paper/scripts/arxiv_preflight.py /path/to/clean-upload --source-format tex --main main.tex
python -m unittest discover -s tests -v
```

A passing static check does not approve or submit a paper. Inspect every required source and rendered PDF, including arXiv's generated output, and verify publication authority for the exact artifact. Keep unpublished manuscripts, reports, account state and release records outside this public repository.
