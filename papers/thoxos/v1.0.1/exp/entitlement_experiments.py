"""Entitlement contract: Core-never-gated invariant, MayExecute, grace, and issuer trust.

Clean-room implementation of the contract the ThoxOS whitepaper and the
0.2.0 review describe, in two token designs, with property tests that fail
the script on any violation and a measured verify cost.

Contract (review equations 1 and 2):
    f in F_core  =>  E(f, t) = true for every token state t        (1)
    MayExecute(a) = U(a) and O(a) and E(f(a), t)                      (2)

Token designs compared:
    hmac     payload || HMAC-SHA256(k_issuer, payload); the verifier holds
             k_issuer. A device that can verify can also issue (the review's
             issuer-only trust failure).
    ed25519  payload || Ed25519 signature; the verifier holds only the public
             key. A device cannot issue.

Clock policy compared:
    wall     validity from the device wall clock only.
    hwm      validity from max(wall clock, persisted high-water mark of time
             seen), so a rolled-back clock cannot revive an expired token.

Grace: paid features stay allowed for 30 days after expiry.

Properties (all must pass):
    P1 valid token, paid feature, U and O true          -> allowed
    P2 expiry + 29 d                                     -> allowed (grace)
    P3 expiry + 31 d                                     -> denied
    P4 tampered payload                                  -> denied
    P5 malformed token                                   -> denied
    P6 Core feature with no / expired / invalid token    -> allowed (eq. 1)
    P7 paid feature, valid token, U false or O false     -> denied (eq. 2)
    P8 unknown feature id                                -> denied (explicit denial policy)
    P9 forged token by a device holding verifier material: accepted under hmac,
       rejected under ed25519
    P10 clock rolled back 20 d on a token expired 40 d: accepted under wall,
        rejected under hwm

Timing: verify latency per token, 30 repetitions of 1,000 verifications,
medians and quartiles; token bytes. Authoring host, Python, cryptography
library for Ed25519. No ThoxOS device, no production key custody.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

RESULTS = Path(__file__).with_name("results") / "entitlement.json"
DAY = 86400
GRACE_S = 30 * DAY
REPS = 30
BATCH = 1000

CORE = {"local-chat", "local-models", "meshstack-local", "ota-security-updates", "device-portal"}
PAID = {"meshstack-pro", "thoxroute-cloud", "fleet-console", "thoxbrain-sync"}
KNOWN = CORE | PAID


def b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def payload(account: str, features: list[str], issued: int, expires: int, nonce: bytes) -> bytes:
    return json.dumps({"v": 1, "acct": account, "feat": sorted(features), "iat": issued, "exp": expires,
                       "nonce": b64(nonce)}, separators=(",", ":"), sort_keys=True).encode()


class HmacIssuer:
    def __init__(self, secret: bytes):
        self.secret = secret

    def issue(self, p: bytes) -> str:
        return b64(p) + "." + b64(hmac.new(self.secret, p, hashlib.sha256).digest())


class HmacVerifier:
    kind = "hmac"

    def __init__(self, secret: bytes):
        self.secret = secret

    def verify(self, token: str) -> dict | None:
        try:
            p64, s64 = token.split(".")
            p = unb64(p64)
            if not hmac.compare_digest(hmac.new(self.secret, p, hashlib.sha256).digest(), unb64(s64)):
                return None
            d = json.loads(p)
            if d.get("v") != 1 or not isinstance(d.get("exp"), int):
                return None
            return d
        except Exception:  # noqa: BLE001
            return None


class EdIssuer:
    def __init__(self, key: ed25519.Ed25519PrivateKey):
        self.key = key

    def issue(self, p: bytes) -> str:
        return b64(p) + "." + b64(self.key.sign(p))


class EdVerifier:
    kind = "ed25519"

    def __init__(self, pub: ed25519.Ed25519PublicKey):
        self.pub = pub

    def verify(self, token: str) -> dict | None:
        try:
            p64, s64 = token.split(".")
            p = unb64(p64)
            self.pub.verify(unb64(s64), p)
            d = json.loads(p)
            if d.get("v") != 1 or not isinstance(d.get("exp"), int):
                return None
            return d
        except (InvalidSignature, Exception):  # noqa: BLE001
            return None


@dataclass
class Clock:
    wall: int
    hwm: int = 0  # persisted high-water mark

    def now(self, policy: str) -> int:
        if policy == "wall":
            return self.wall
        self.hwm = max(self.hwm, self.wall)
        return self.hwm


def entitled(feature: str, token: str | None, verifier, clock: Clock, policy: str) -> bool:
    """E(f, t): equation 1 makes Core unconditional; paid needs a valid token within grace."""
    if feature in CORE:
        return True
    if feature not in KNOWN:
        return False
    if token is None:
        return False
    d = verifier.verify(token)
    if d is None:
        return False
    if feature not in d["feat"]:
        return False
    return clock.now(policy) <= d["exp"] + GRACE_S


def may_execute(feature: str, user_ok: bool, os_ok: bool, token, verifier, clock, policy="hwm") -> bool:
    """Equation 2: authorization is a conjunction; the model is never a term."""
    return user_ok and os_ok and entitled(feature, token, verifier, clock, policy)


def properties(issuer, verifier, forge_fn) -> dict:
    t0 = 1_800_000_000
    nonce = os.urandom(16)
    good = issuer.issue(payload("acct-1", ["meshstack-pro"], t0, t0 + 365 * DAY, nonce))
    res = {}
    res["P1_valid_paid_allowed"] = may_execute("meshstack-pro", True, True, good, verifier, Clock(t0 + DAY))
    res["P2_grace_29d_allowed"] = may_execute("meshstack-pro", True, True, good, verifier, Clock(t0 + 365 * DAY + 29 * DAY))
    res["P3_grace_31d_denied"] = not may_execute("meshstack-pro", True, True, good, verifier, Clock(t0 + 365 * DAY + 31 * DAY))
    p64, s64 = good.split(".")
    tampered = b64(payload("acct-1", ["meshstack-pro", "fleet-console"], t0, t0 + 365 * DAY, nonce)) + "." + s64
    res["P4_tampered_denied"] = not may_execute("fleet-console", True, True, tampered, verifier, Clock(t0 + DAY))
    res["P5_malformed_denied"] = all(not may_execute("meshstack-pro", True, True, m, verifier, Clock(t0 + DAY))
                                     for m in ["", "x", "a.b", p64, p64 + ".", "..", "\x00"])
    expired = issuer.issue(payload("acct-1", ["meshstack-pro"], t0 - 400 * DAY, t0 - 100 * DAY, nonce))
    res["P6_core_unconditional"] = all(may_execute(f, True, True, tok, verifier, Clock(t0))
                                       for f in CORE for tok in [None, expired, tampered, "garbage"])
    res["P7_eq2_conjunction"] = (not may_execute("meshstack-pro", False, True, good, verifier, Clock(t0 + DAY))
                                 and not may_execute("meshstack-pro", True, False, good, verifier, Clock(t0 + DAY)))
    res["P8_unknown_denied"] = not may_execute("mystery-feature", True, True, good, verifier, Clock(t0 + DAY))
    forged = forge_fn(payload("acct-attacker", ["fleet-console"], t0, t0 + 3650 * DAY, nonce))
    res["P9_forged_accepted"] = may_execute("fleet-console", True, True, forged, verifier, Clock(t0 + DAY))
    old = issuer.issue(payload("acct-1", ["meshstack-pro"], t0 - 400 * DAY, t0 - 40 * DAY, nonce))
    clk = Clock(t0)
    clk.now("hwm")  # device has seen t0
    clk.wall = t0 - 20 * DAY  # rollback
    res["P10_rollback_wall_accepted"] = may_execute("meshstack-pro", True, True, old, verifier, clk, "wall")
    res["P10_rollback_hwm_rejected"] = not may_execute("meshstack-pro", True, True, old, verifier, clk, "hwm")
    res["token_bytes"] = len(good)
    return res


def timing(issuer, verifier) -> dict:
    t0 = 1_800_000_000
    toks = [issuer.issue(payload(f"acct-{i}", ["meshstack-pro"], t0, t0 + 365 * DAY, os.urandom(16))) for i in range(BATCH)]
    for t in toks[:50]:
        verifier.verify(t)
    runs = []
    for _ in range(REPS):
        s = time.perf_counter()
        ok = sum(1 for t in toks if verifier.verify(t) is not None)
        runs.append((time.perf_counter() - s) / BATCH * 1e6)
        assert ok == BATCH
    return {"us_per_verify_median": statistics.median(runs), "us_q1": float(np.percentile(runs, 25)),
            "us_q3": float(np.percentile(runs, 75)), "reps": REPS, "batch": BATCH}


def main() -> int:
    secret = os.urandom(32)
    hi, hv = HmacIssuer(secret), HmacVerifier(secret)
    priv = ed25519.Ed25519PrivateKey.generate()
    ei, ev = EdIssuer(priv), EdVerifier(priv.public_key())
    attacker = ed25519.Ed25519PrivateKey.generate()
    out = {
        "evidence_label": "clean-room contract implementation with exact property tests and host-measured verify cost; not a ThoxOS build",
        "grace_days": 30, "core_features": sorted(CORE), "paid_features": sorted(PAID),
        "hmac": {"properties": properties(hi, hv, lambda p: HmacIssuer(secret).issue(p)), "timing": timing(hi, hv)},
        "ed25519": {"properties": properties(ei, ev, lambda p: EdIssuer(attacker).issue(p)), "timing": timing(ei, ev)},
    }
    expect = {"hmac": {"P9_forged_accepted": True}, "ed25519": {"P9_forged_accepted": False}}
    for kind in ["hmac", "ed25519"]:
        pr = out[kind]["properties"]
        for k, v in pr.items():
            if k.startswith("P9"):
                if v != expect[kind]["P9_forged_accepted"]:
                    raise SystemExit(f"{kind} forgery expectation failed: {v}")
            elif k.startswith("P") and v is not True:
                raise SystemExit(f"{kind} property failed: {k}")
    # known-answer vector for the demo (HMAC design, fixed secret and nonce)
    kav_secret = bytes(range(32))
    kav_nonce = bytes([0x42] * 16)
    kav_payload = payload("acct-demo", ["meshstack-pro"], 1_800_000_000, 1_831_536_000, kav_nonce)
    out["known_answer"] = {"secret_hex": kav_secret.hex(), "payload": kav_payload.decode(),
                           "token": HmacIssuer(kav_secret).issue(kav_payload),
                           "allowed_at": 1_800_086_400, "grace_allowed_at": 1_831_536_000 + 29 * DAY,
                           "denied_at": 1_831_536_000 + 31 * DAY}
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(out, indent=2))
    print(json.dumps({k: out[k]["timing"] for k in ["hmac", "ed25519"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
