# Quickstart — ThoxWork paper (v1.1.0 folder)

```bash
git clone https://github.com/ttracx/thox-research-paper.git
cd thox-research-paper/papers/thoxwork/v1.1.0
```

Read the paper:

```bash
open paper/THOX_ThoxWork_Research_Paper_v1.1.0.pdf        # macOS
xdg-open paper/THOX_ThoxWork_Research_Paper_v1.1.0.pdf    # Linux
```

Run the interactive demo (single file, offline):

```bash
open paper/ThoxWork_Demo_v1.2.0.html
```

Reproduce the evidence (Python 3, standard library only):

```bash
python3 artifact/exp/thoxwork_experiments.py
sha256sum artifact/exp/results/summary.json
# f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6cdb071dd79
```

Reproduce this edition's new evidence (E8, E9) the same way:

```bash
python3 artifact/exp/e8_divergence.py
python3 artifact/exp/e9_detection_matrix.py
# merged evidence source: artifact/exp/results/summary-v110.json
# 37496b599d5055e8045dfee79eff7b3ff9b1add86fa41b2b49a5b3bc941363ad
```

That is the whole quickstart: paper, demo, evidence.
