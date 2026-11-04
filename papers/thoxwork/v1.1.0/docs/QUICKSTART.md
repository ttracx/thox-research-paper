# Quickstart — ThoxWork paper repository

```bash
git clone https://github.com/ttracx/thox-thoxwork-paper.git
cd thox-thoxwork-paper
```

Read the paper:

```bash
open paper/THOX_ThoxWork_Research_Paper_v1.1.0.pdf        # macOS
xdg-open paper/THOX_ThoxWork_Research_Paper_v1.1.0.pdf    # Linux
```

Run the interactive demo (single file, offline):

```bash
open paper/ThoxWork_Demo_v1.1.0.html
```

Reproduce the evidence (Python 3, standard library only):

```bash
python3 artifact/exp/thoxwork_experiments.py
sha256sum artifact/exp/results/summary.json
# f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6cdb071dd79
```

That is the whole quickstart: paper, demo, evidence.
