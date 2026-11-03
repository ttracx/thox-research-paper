"""Memory budget (review equation 3) for the ThoxOS-Kernel family on the class floors (calculated).

    M_weights,resident + M_KV + M_runtime + M_OS + M_reserve <= M_available

Inputs:
  - GGUF file sizes from the public model cards (Q4_K_M and Q8_0), read from the
    Hugging Face listings on 2026-11-03. Treated as a lower bound on resident
    weight bytes (mmap can leave weights partly unresident; this budget assumes
    fully resident weights).
  - KV geometry from each card's config.json: Qwen3.5 hybrid layers, one full
    attention layer in four; per-token KV = 2 x n_full x n_kv_heads x head_dim x 2 B (bf16).
    Linear-attention state is fixed per layer:
    n_value_heads x key_dim x value_dim x 4 B (fp32 per config), an estimate
    from config, not a measured buffer.
  - Class floors from the ThoxOS whitepaper: E2 2 GB, P4 4 GB, P6 6 GB; host
    tiers 16, 32, 64 GB (illustrative hosts).
  - M_runtime + M_OS + M_reserve swept as a single reserve: 0.6, 1.0, 1.5 GB (assumptions).

Output: fit or no fit per (model, quantization, class, context, reserve), and
the largest context that fits. Nothing here is a measurement.
"""
from __future__ import annotations

import json
from pathlib import Path

RESULTS = Path(__file__).with_name("results") / "memory.json"
GB = 10 ** 9
MiB = 2 ** 20

MODELS = {
    "ThoxOS-Kernel-0.8B": {"layers": 24, "full": 6, "kv_heads": 2, "head_dim": 256, "lin_layers": 18, "lin_v_heads": 16,
                           "Q4_K_M": 529_297_056, "Q8_0": 811_843_232, "card_role": "ThoxAir / ThoxKey triage student"},
    "ThoxOS-Kernel-4B": {"layers": 32, "full": 8, "kv_heads": 4, "head_dim": 256, "lin_layers": 24, "lin_v_heads": 32,
                         "Q4_K_M": 2_708_804_128, "Q8_0": 4_482_402_848, "card_role": "ThoxMini / ThoxClip resident student (baseline)"},
    "ThoxOS-Kernel-27B": {"layers": 64, "full": 16, "kv_heads": 4, "head_dim": 256, "lin_layers": 48, "lin_v_heads": 48,
                          "Q4_K_M": 16_547_400_192, "Q8_0": 28_595_763_712, "card_role": "host-tier teacher"},
}
CLASSES = {"E2 (Air, 2 GB)": 2 * GB, "P4 (Mini, 4 GB)": 4 * GB, "P6 (Clip, 6 GB)": 6 * GB,
           "Host 16 GB": 16 * GB, "Host 32 GB": 32 * GB, "Host 64 GB": 64 * GB}
CONTEXTS = [2048, 8192, 32768, 131072]
RESERVES_GB = [0.6, 1.0, 1.5]


def kv_per_token(m: dict) -> int:
    return 2 * m["full"] * m["kv_heads"] * m["head_dim"] * 2


def linear_state(m: dict) -> int:
    return m["lin_layers"] * m["lin_v_heads"] * 128 * 128 * 4


def main() -> int:
    rows = []
    maxctx = []
    for name, m in MODELS.items():
        for q in ["Q4_K_M", "Q8_0"]:
            for cls, avail in CLASSES.items():
                for res in RESERVES_GB:
                    for ctx in CONTEXTS:
                        need = m[q] + kv_per_token(m) * ctx + linear_state(m) + res * GB
                        rows.append({"model": name, "quant": q, "class": cls, "reserve_gb": res, "context": ctx,
                                     "need_bytes": need, "available_bytes": avail, "fits": need <= avail})
                    # largest context that fits (continuous)
                    free = avail - m[q] - linear_state(m) - res * GB
                    maxctx.append({"model": name, "quant": q, "class": cls, "reserve_gb": res,
                                   "max_context_tokens": int(free // kv_per_token(m)) if free > 0 else 0})
    out = {"evidence_label": "calculated from public card file sizes, card config geometry, class floors and stated reserves; not a measurement",
           "models": {k: {**v, "kv_bytes_per_token": kv_per_token(v), "linear_state_bytes": linear_state(v)} for k, v in MODELS.items()},
           "classes": CLASSES, "contexts": CONTEXTS, "reserves_gb": RESERVES_GB, "rows": rows, "max_context": maxctx}
    RESULTS.write_text(json.dumps(out, indent=2))
    for r in maxctx:
        if r["reserve_gb"] == 1.0 and r["quant"] == "Q4_K_M":
            print(f"{r['model']:20s} {r['class']:18s} max ctx {r['max_context_tokens']:>8,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
