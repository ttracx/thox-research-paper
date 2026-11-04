#!/usr/bin/env python3
"""
Fold this edition's new runs (E8, E9) into exp/results/summary-v110.json.

The v1.0.x oracle summary (exp/results/summary.json in the paper
workdir) is the frozen evidence source for E1 to E5.  This script
asserts its SHA-256 before and after the merge and never writes it.

Usage: python3 merge_summary_v110.py
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORACLE = (HERE.parents[2] / "thoxwork-paper-20261104" / "exp" / "results"
          / "summary.json")
ORACLE_SHA = ("f7c72f64b9b8c6f2e1663fbb014374858b2251f2aeaa7d989393a6"
              "cdb071dd79")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    before = sha(ORACLE)
    assert before == ORACLE_SHA, f"oracle hash drift: {before}"
    e8 = json.loads((HERE / "results" / "e8_divergence.json").read_text())
    e9 = json.loads(
        (HERE / "results" / "e9_detection_matrix.json").read_text())
    out = {
        "meta": {
            "paper": "ThoxWork v1.1.0",
            "schema": "thoxwork-summary-v110/1.0",
            "note": "New evidence runs for edition v1.1.0 only. The "
                    "E1-E5 oracle summary is a separate frozen file; "
                    "its SHA-256 is asserted by this merge.",
            "oracle_summary": "thoxwork-paper-20261104/exp/results/"
                              "summary.json",
            "oracle_summary_sha256": before,
        },
        "E8": e8,
        "E9": e9,
    }
    target = HERE / "results" / "summary-v110.json"
    target.write_text(json.dumps(out, indent=1))
    after = sha(ORACLE)
    assert after == ORACLE_SHA, f"oracle hash changed: {after}"
    print("wrote", target)
    print("oracle intact:", after)


if __name__ == "__main__":
    main()
