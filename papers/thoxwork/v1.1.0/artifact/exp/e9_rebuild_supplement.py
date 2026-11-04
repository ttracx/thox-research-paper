#!/usr/bin/env python3
"""
E9 supplement - the suffix-rebuild attack.

The companion edition's detection study included an attacker who edits
one record and then honestly recomputes every later hash link (possible
because the link hash is unkeyed), but cannot recompute the HMAC tags.
This supplement adds that attack row to this edition's E9 matrix, using
the same chain builder, checks, seed family and trial count as
e9_detection_matrix.py, and merges the row into its result file.

Attack: at a seeded middle position p, change the payload, recompute
h_p from the stored previous link, then recompute every subsequent
h_j honestly. Tags are left as originally issued (the attacker has no
key), so the keyed tag check fails at p; the plain link check passes,
because every link is consistent; an anchor still matches unless the
final record was edited (it is not: p is interior).

Usage: python3 e9_rebuild_supplement.py [matrix.json]
Default: results/e9_detection_matrix.json next to the E9 script.
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from e9_detection_matrix import (  # noqa: E402
    MASTER, N_RECORDS, TRIALS, build_chain, run_checks, CHECKS_BY_CONFIG,
    canon,
)
import hashlib  # noqa: E402


def atk_rebuild(records, rng):
    pos = rng.randrange(100, N_RECORDS - 100)
    records[pos]["p"] = records[pos]["p"] + "-edited"
    prev_hex = records[pos - 1]["h"] if pos > 0 else None
    from e9_detection_matrix import GENESIS
    prev = bytes.fromhex(prev_hex) if prev_hex else GENESIS
    for j in range(pos, len(records)):
        r = records[j]
        h = hashlib.sha256(
            canon(r["i"], r["t"], r["k"], r["a"], r["p"], prev.hex())
        ).digest()
        r["h"] = h.hex()
        prev = h


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).parent / "results" / "e9_detection_matrix.json"
    )
    result = json.loads(path.read_text())
    configs = list(CHECKS_BY_CONFIG.keys())
    cell = {cfg: {"detected": 0, "trials": TRIALS,
                  "per_check_detected": {}} for cfg in configs}
    for trial in range(TRIALS):
        rng = random.Random(MASTER + 10000 * 9 + trial)
        base, anchor = build_chain(rng)
        attacked = [dict(r) for r in base]
        atk_rebuild(attacked, rng)
        for cfg in configs:
            det, per = run_checks(attacked, anchor, cfg)
            if det:
                cell[cfg]["detected"] += 1
            for cname, ok in per.items():
                if not ok:
                    d = cell[cfg]["per_check_detected"]
                    d[cname] = d.get(cname, 0) + 1
    result["matrix_detected_of_trials"]["rebuild"] = cell
    result["supplement"] = (
        "The 'rebuild' attack row was produced by "
        "e9_rebuild_supplement.py with the same builder, checks, seeds "
        "and trial count as the main E9 run."
    )
    path.write_text(json.dumps(result, indent=1))
    print({cfg: cell[cfg]["detected"] for cfg in configs})
    print("merged rebuild row into", path)


if __name__ == "__main__":
    main()
