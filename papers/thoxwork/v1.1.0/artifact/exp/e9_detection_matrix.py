#!/usr/bin/env python3
"""
E9 - Audit-chain detection matrix (ThoxWork paper v1.1.0).

Independent re-implementation of the chained audit record of Section 4
(Equation 2 of the paper), written from the equation alone:

    h_i     = SHA256( canon(i, t_i, kappa_i, a_i, pi_i, h_{i-1}) )
    tau_i   = HMAC-SHA256_k( h_i )
    anchor  = ( n, h_{n-1} )          held by a second party

canon(.) here is JSON with sorted keys, separators (",", ":"), UTF-8.
The genesis link h_{-1} is SHA256("thoxwork-e9-genesis").

Configurations (2 chain schemes x anchor off/on):
    plain            hash links only
    plain+anchor     hash links + external anchor
    keyed            hash links + HMAC tags
    keyed+anchor     hash links + HMAC tags + external anchor

Checks available to a verifier of a configuration:
    link        recompute every h_i from the stored fields and the stored
                previous link; any mismatch flags the chain
    tag         (keyed only) verify every tau_i under the verifier's key
    continuity  the stored index of every record equals its position
    anchor      (anchored only) record count and final h match the anchor

A trial is "detected" when at least one check available to the
configuration flags the attacked chain.  Per-check results are recorded
as well as the suite result.

Attacks (applied to a copy of an honest chain):
    modify          change the payload of one middle record
    delete          remove one middle record
    reorder         swap two adjacent middle records
    renumber        add 1 to every stored index
    truncate        drop the last 50 records
    append-nokey    append a fabricated record; the attacker computes the
                    hash link honestly but does not hold the HMAC key, so
                    the tag is a guess
    append-withkey  append a fabricated record; the attacker holds the key
                    and produces a valid tag

Trials: 500 per attack, on chains of 1,000 records.  Record content and
attack positions come from a seeded PRNG (family seed convention of the
v1.0.x oracle: seed = 20261104 + 10000*E + rep, here E = 9), so a
re-run with the same seed reproduces every count exactly.  Timings are
host measurements and are reported separately; they are not part of the
reproducibility claim.

Also measured: keyed append cost (us/record), keyed verify cost
(us/record and full-chain ms at 1,000 and 10,000 records), and the
serialised bundle size per record.  Known-answer tests: SHA-256 per
FIPS 180-4 examples (4) and HMAC-SHA-256 per RFC 4231 cases 1, 2, 6 (3).

Usage: python3 e9_detection_matrix.py [out.json]
Default out: results/e9_detection_matrix.json next to this script.
"""

import hashlib
import hmac as hmac_mod
import json
import random
import statistics
import sys
import time
from pathlib import Path

MASTER = 20261104
N_RECORDS = 1000
TRIALS = 500
TRUNCATE_TAIL = 50
KEY = bytes.fromhex(
    "3b7f1c9a54e2d806b1a94c73f05d28e6c4179ab3d5f08e2a6c91d4b7f3058e2a"
)
GENESIS = hashlib.sha256(b"thoxwork-e9-genesis").digest()
KINDS = ["task", "handoff", "review", "checkin"]
ACTORS = ["emp-a", "emp-b", "emp-c", "svc-router", "svc-audit"]


def canon(i, t, kappa, a, pi, prev_hex):
    return json.dumps(
        {"i": i, "t": t, "k": kappa, "a": a, "p": pi, "prev": prev_hex},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")


def build_chain(rng):
    """Return (records, anchor). Records carry fields + h (hex) + tau (hex)."""
    records = []
    prev = GENESIS
    for i in range(N_RECORDS):
        t = f"2026-11-04T00:{i // 60:02d}:{i % 60:02d}Z"
        kappa = rng.choice(KINDS)
        a = rng.choice(ACTORS)
        pi = f"payload-{rng.randrange(10**6)}"
        h = hashlib.sha256(canon(i, t, kappa, a, pi, prev.hex())).digest()
        tau = hmac_mod.new(KEY, h, hashlib.sha256).hexdigest()
        records.append(
            {"i": i, "t": t, "k": kappa, "a": a, "p": pi,
             "h": h.hex(), "tau": tau}
        )
        prev = h
    anchor = {"n": len(records), "head": records[-1]["h"]}
    return records, anchor


# ---------------------------------------------------------------- checks

def check_link(records):
    prev = GENESIS
    for pos, r in enumerate(records):
        expect = hashlib.sha256(
            canon(r["i"], r["t"], r["k"], r["a"], r["p"], prev.hex())
        ).hexdigest()
        if expect != r["h"]:
            return False
        prev = bytes.fromhex(r["h"])
    return True


def check_tag(records):
    for r in records:
        expect = hmac_mod.new(
            KEY, bytes.fromhex(r["h"]), hashlib.sha256
        ).hexdigest()
        if not hmac_mod.compare_digest(expect, r["tau"]):
            return False
    return True


def check_continuity(records):
    return all(r["i"] == pos for pos, r in enumerate(records))


def check_anchor(records, anchor):
    return (
        len(records) == anchor["n"]
        and len(records) > 0
        and records[-1]["h"] == anchor["head"]
    )


CHECKS_BY_CONFIG = {
    "plain": ["link", "continuity"],
    "plain+anchor": ["link", "continuity", "anchor"],
    "keyed": ["link", "continuity", "tag"],
    "keyed+anchor": ["link", "continuity", "tag", "anchor"],
}


def run_checks(records, anchor, config):
    out = {}
    for name in CHECKS_BY_CONFIG[config]:
        if name == "link":
            out[name] = check_link(records)
        elif name == "tag":
            out[name] = check_tag(records)
        elif name == "continuity":
            out[name] = check_continuity(records)
        elif name == "anchor":
            out[name] = check_anchor(records, anchor)
    detected = any(v is False for v in out.values())
    return detected, out


# ---------------------------------------------------------------- attacks

def atk_modify(records, rng):
    pos = rng.randrange(100, N_RECORDS - 100)
    records[pos]["p"] = records[pos]["p"] + "-tampered"


def atk_delete(records, rng):
    pos = rng.randrange(100, N_RECORDS - 100)
    del records[pos]


def atk_reorder(records, rng):
    pos = rng.randrange(100, N_RECORDS - 101)
    records[pos], records[pos + 1] = records[pos + 1], records[pos]


def atk_renumber(records, rng):
    for r in records:
        r["i"] += 1


def atk_truncate(records, rng):
    del records[len(records) - TRUNCATE_TAIL:]


def _append_forged(records, with_key):
    prev_hex = records[-1]["h"]
    i = len(records)
    t = "2026-11-04T01:00:00Z"
    kappa, a, pi = "task", "emp-a", "payload-forged"
    h = hashlib.sha256(canon(i, t, kappa, a, pi, prev_hex)).digest()
    if with_key:
        tau = hmac_mod.new(KEY, h, hashlib.sha256).hexdigest()
    else:
        tau = hashlib.sha256(b"attacker-guess").hexdigest()
    records.append(
        {"i": i, "t": t, "k": kappa, "a": a, "p": pi,
         "h": h.hex(), "tau": tau}
    )


def atk_append_nokey(records, rng):
    _append_forged(records, with_key=False)


def atk_append_withkey(records, rng):
    _append_forged(records, with_key=True)


ATTACKS = {
    "modify": atk_modify,
    "delete": atk_delete,
    "reorder": atk_reorder,
    "renumber": atk_renumber,
    "truncate": atk_truncate,
    "append-nokey": atk_append_nokey,
    "append-withkey": atk_append_withkey,
}


# ---------------------------------------------------------------- KATs

def kats():
    results = []
    sha_vectors = [
        (b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        (b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
        (b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
         "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"),
        (b"a" * 1_000_000,
         "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0"),
    ]
    for msg, expect in sha_vectors:
        got = hashlib.sha256(msg).hexdigest()
        results.append({"test": f"FIPS180-4 SHA-256 len={len(msg)}",
                        "pass": got == expect})
    rfc4231 = [
        (bytes([0x0B] * 20), b"Hi There",
         "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"),
        (b"Jefe", b"what do ya want for nothing?",
         "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"),
        (bytes([0xAA] * 131),
         b"Test Using Larger Than Block-Size Key - Hash Key First",
         "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54"),
    ]
    for key, msg, expect in rfc4231:
        got = hmac_mod.new(key, msg, hashlib.sha256).hexdigest()
        results.append({"test": "RFC4231 HMAC-SHA-256", "pass": got == expect})
    return results


# ---------------------------------------------------------------- costs

def costs():
    rng = random.Random(MASTER + 90000 + 999999)
    # append cost on the keyed scheme: median per-record over a growing chain
    records, _ = build_chain(rng)
    times = []
    prev = bytes.fromhex(records[-1]["h"])
    for j in range(2000):
        i = N_RECORDS + j
        t0 = time.perf_counter_ns()
        t = f"2026-11-04T02:{j // 60 % 60:02d}:{j % 60:02d}Z"
        h = hashlib.sha256(canon(i, t, "task", "emp-a", f"payload-{j}", prev.hex())).digest()
        tau = hmac_mod.new(KEY, h, hashlib.sha256).hexdigest()
        t1 = time.perf_counter_ns()
        times.append((t1 - t0) / 1000.0)
        records.append({"i": i, "t": t, "k": "task", "a": "emp-a",
                        "p": f"payload-{j}", "h": h.hex(), "tau": tau})
        prev = h
    append_us = statistics.median(times)

    def verify_time(recs):
        t0 = time.perf_counter_ns()
        ok_link = check_link(recs)
        ok_tag = check_tag(recs)
        t1 = time.perf_counter_ns()
        assert ok_link and ok_tag
        return (t1 - t0) / 1e6  # ms

    v1000 = [verify_time(records[:1000]) for _ in range(9)]
    v10000_records, _ = (None, None)
    big_rng = random.Random(MASTER + 90000 + 888888)
    big = []
    prev = GENESIS
    for i in range(10000):
        t = f"2026-11-04T03:{i // 60 % 60:02d}:{i % 60:02d}Z"
        kappa = big_rng.choice(KINDS)
        a = big_rng.choice(ACTORS)
        pi = f"payload-{big_rng.randrange(10**6)}"
        h = hashlib.sha256(canon(i, t, kappa, a, pi, prev.hex())).digest()
        tau = hmac_mod.new(KEY, h, hashlib.sha256).hexdigest()
        big.append({"i": i, "t": t, "k": kappa, "a": a, "p": pi,
                    "h": h.hex(), "tau": tau})
        prev = h
    v10000 = [verify_time(big) for _ in range(5)]
    bundle = [len(json.dumps(r, separators=(",", ":")).encode("utf-8"))
              for r in records[:1000]]
    return {
        "append_keyed_us_per_record_median": round(append_us, 2),
        "verify_keyed_1000_ms_median": round(statistics.median(v1000), 2),
        "verify_keyed_us_per_record_median": round(
            statistics.median(v1000) * 1000 / 1000, 2),
        "verify_keyed_10000_ms_median": round(statistics.median(v10000), 1),
        "bundle_bytes_per_record_mean": round(statistics.mean(bundle), 1),
    }


# ---------------------------------------------------------------- main

def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).parent / "results" / "e9_detection_matrix.json"
    )
    configs = list(CHECKS_BY_CONFIG.keys())
    matrix = {atk: {cfg: {"detected": 0, "trials": TRIALS,
                          "per_check_detected": {}}
                    for cfg in configs} for atk in ATTACKS}
    for trial in range(TRIALS):
        rng = random.Random(MASTER + 10000 * 9 + trial)
        base, anchor = build_chain(rng)
        # sanity: the honest chain must pass every check in every config
        for cfg in configs:
            det, _ = run_checks([dict(r) for r in base], anchor, cfg)
            assert not det, f"honest chain flagged under {cfg}"
        for atk_name, atk_fn in ATTACKS.items():
            attacked = [dict(r) for r in base]
            atk_fn(attacked, rng)
            for cfg in configs:
                det, per = run_checks(attacked, anchor, cfg)
                cell = matrix[atk_name][cfg]
                if det:
                    cell["detected"] += 1
                for cname, ok in per.items():
                    if not ok:
                        d = cell["per_check_detected"]
                        d[cname] = d.get(cname, 0) + 1
    kat_results = kats()
    result = {
        "experiment": "E9 audit-chain detection matrix (v1.1.0 re-implementation)",
        "scheme": "Eq. 2: h_i = SHA256(canon(i,t,kappa,a,pi,h_{i-1})); "
                  "tau_i = HMAC-SHA256_k(h_i); anchor = (n, h_{n-1})",
        "canon": "JSON sorted keys, separators (',',':'), UTF-8",
        "records_per_chain": N_RECORDS,
        "trials_per_attack": TRIALS,
        "seed_family": "20261104 + 10000*9 + trial",
        "matrix_detected_of_trials": matrix,
        "kat": {"passed": sum(1 for k in kat_results if k["pass"]),
                "total": len(kat_results), "detail": kat_results},
        "costs_host_measured": costs(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=1))
    print(json.dumps({
        atk: {cfg: matrix[atk][cfg]["detected"] for cfg in configs}
        for atk in ATTACKS
    }, indent=1))
    print("KAT", result["kat"]["passed"], "/", result["kat"]["total"])
    print("costs", result["costs_host_measured"])
    print("wrote", out_path)


if __name__ == "__main__":
    main()
