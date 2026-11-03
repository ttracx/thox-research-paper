"""A/B update contract under fault injection (simulation).

Simulates the RAUC-style contract the ThoxOS design specifies: two rootfs
slots, a persistent data partition updates never touch, a signed bundle whose
signature and image hashes are checked before anything is written, a boot
attempt counter, and a first-boot health gate that marks the new slot good or
triggers automatic rollback. Faults are injected per update: bad signature,
incomplete write (power loss during install), corrupted image, health-gate
failure, power loss during the health window, and repeated boot failure.

Policies compared on identical fault streams:
    contract   signature check, A/B, attempt counter (3), health gate, data untouched
    no_sig     as contract but no signature check (accepts tampered bundles)
    no_counter as contract but no boot attempt counter (a hanging slot is retried forever)
    in_place   single slot updated in place, no rollback target

Metrics per 30-seed run of 200 updates: updates ending on a known-good slot,
updates that left the device unbootable (bricked), updates that booted a
tampered image, data partition intact, and boots spent recovering (bounded by
the attempt counter). Protocol logic only; nothing about a real device.
"""
from __future__ import annotations

import json
import random
import statistics
from pathlib import Path

import numpy as np

RESULTS = Path(__file__).with_name("results") / "update.json"
SEEDS = 30
UPDATES = 200
ATTEMPTS = 3
FAULT_P = {"bad_signature": 0.03, "incomplete_write": 0.05, "corrupt_image": 0.03,
           "health_fail": 0.06, "power_in_health": 0.04, "boot_hang": 0.04}


def run(seed: int, policy: str) -> dict:
    rng = random.Random(seed)
    stats = {"known_good_end": 0, "bricked": 0, "booted_tampered": 0, "data_damaged": 0,
             "recovery_boots": [], "rollbacks": 0, "updates": UPDATES}
    slot_good = {"A": True, "B": False}
    running = "A"
    for _ in range(UPDATES):
        faults = {k: rng.random() < p for k, p in FAULT_P.items()}
        idle = "B" if running == "A" else "A"
        target = running if policy == "in_place" else idle
        # 1 verify
        if faults["bad_signature"] or faults["corrupt_image"]:
            if policy != "no_sig":
                stats["known_good_end"] += 1  # hard reject, nothing written
                continue
        # 2 install
        if faults["incomplete_write"]:
            slot_good[target] = False
            if policy == "in_place":
                stats["bricked"] += 1
                stats["data_damaged"] += 1 if rng.random() < 0.5 else 0
                running = target
                continue
        else:
            slot_good[target] = not (faults["corrupt_image"] and policy == "no_sig") and not faults["boot_hang"]
            if policy == "no_sig" and faults["bad_signature"]:
                stats["booted_tampered"] += 1
        # 3 reboot into target with attempt counter
        boots = 0
        marked_good = False
        while True:
            boots += 1
            if slot_good[target] and not faults["health_fail"]:
                if faults["power_in_health"] and boots == 1:
                    continue  # health window interrupted, counter already decremented
                marked_good = True
                break
            if policy == "no_counter":
                if boots >= 50:
                    stats["bricked"] += 1
                    break
                continue
            if boots >= ATTEMPTS:
                break
        stats["recovery_boots"].append(boots)
        if marked_good:
            running = target
            stats["known_good_end"] += 1
        else:
            if policy == "in_place":
                stats["bricked"] += 1
            elif policy == "no_counter" and boots >= 50:
                pass
            else:
                stats["rollbacks"] += 1  # bootloader returns to the previous good slot
                stats["known_good_end"] += 1
    stats["recovery_boots_median"] = statistics.median(stats["recovery_boots"]) if stats["recovery_boots"] else 0
    stats["recovery_boots_max"] = max(stats["recovery_boots"]) if stats["recovery_boots"] else 0
    del stats["recovery_boots"]
    return stats


def summarize(rows: list[dict]) -> dict:
    out = {}
    for k in rows[0]:
        vals = [r[k] for r in rows]
        out[k] = {"median": float(np.median(vals)), "q1": float(np.percentile(vals, 25)), "q3": float(np.percentile(vals, 75))}
    return out


def main() -> int:
    configs = {p: summarize([run(s, p) for s in range(SEEDS)]) for p in ["contract", "no_sig", "no_counter", "in_place"]}
    out = {"evidence_label": "discrete simulation of the update contract under stated fault probabilities; not a device result",
           "fault_probabilities": FAULT_P, "attempts": ATTEMPTS, "updates_per_run": UPDATES, "seeds": SEEDS, "policies": configs}
    RESULTS.write_text(json.dumps(out, indent=2))
    for p, s in configs.items():
        print(f"{p:11s} good={s['known_good_end']['median']:.0f} bricked={s['bricked']['median']:.0f} tampered={s['booted_tampered']['median']:.0f} "
              f"rollbacks={s['rollbacks']['median']:.0f} maxboots={s['recovery_boots_max']['median']:.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
