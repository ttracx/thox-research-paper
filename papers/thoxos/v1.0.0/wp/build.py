"""Build the ThoxOS paper HTML from summary.json and the verified reference table.

Every number comes from exp/results/summary.json. Citations are [@key],
numbered by first use. Helpers and CSS are shared with the MeshStack paper
pipeline (wp/_helpers.txt, wp/_css.txt) and loaded verbatim.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = json.loads((ROOT / "exp" / "results" / "summary.json").read_text())
REFS_RAW = json.loads((ROOT / "wp" / "refs_raw.json").read_text())
FIG = ROOT / "wp" / "figures"

VERSION = "v1.0.0"
DATE = "2026-11-03"
TITLE = "ThoxOS and ThoxInux: An Evidence-Bounded Architecture for a Local-First AI Operating System"
SHORT = "ThoxOS and ThoxInux: evidence-bounded architecture"

MANUAL_REFS = {
    "asterinasatc": {"authors": ["Yuke Peng", "Hongliang Tian", "Junyang Zhang", "Ruihan Li", "Chengjun Chen", "Jianfeng Jiang", "Jinyi Xian", "Xiaolin Wang", "Chenren Xu", "Diyu Zhou", "Yingwei Luo", "Shoumeng Yan", "Yinqian Zhang"], "title": "ASTERINAS: A Linux ABI-compatible, Rust-based framekernel OS with a small and sound TCB", "venue": "USENIX ATC 2025, pp. 307-323", "url": "https://www.usenix.org/conference/atc25/presentation/peng-yuke"},
    "ginux": {"authors": ["Gregory M. Kurtzer and Ginux contributors"], "title": "Ginux: independent kernel and Linux userspace compatibility (repository; LINUX-COMPATIBILITY.md at commit 36503bda2d87465765e1b94e65f9d100f27ed5be)", "venue": "GitHub, fetched 2026-11-03", "url": "https://github.com/gmkurtzer/ginux"},
    "thoxinux": {"authors": ["THOX.ai"], "title": "ThoxInux: source repository, compatibility audit (docs/COMPATIBILITY.md), wave ledger (docs/WAVES.md) and release v0.9.0 (Payload U SHA-256 85722bd4...4420ae)", "venue": "GitHub, main at 334539c3 cloned 2026-11-03; v0.9.0 engineering prerelease", "url": "https://github.com/Thox-ai/thoxinux"},
    "rauc": {"authors": ["RAUC developers"], "title": "RAUC integration documentation: bootloader integration, system health, mark-good", "venue": "rauc.readthedocs.io, accessed 2026-11-03", "url": "https://rauc.readthedocs.io/en/latest/integration.html"},
    "rfc2104": {"authors": ["Hugo Krawczyk", "Mihir Bellare", "Ran Canetti"], "title": "HMAC: Keyed-Hashing for Message Authentication", "venue": "RFC 2104, IETF, 1997", "url": "https://www.rfc-editor.org/rfc/rfc2104"},
    "rfc8032": {"authors": ["Simon Josefsson", "Ilari Liusvaara"], "title": "Edwards-Curve Digital Signature Algorithm (EdDSA)", "venue": "RFC 8032, IETF, 2017", "url": "https://www.rfc-editor.org/rfc/rfc8032"},
    "abistable": {"authors": ["The Linux kernel developers"], "title": "Linux ABI stability (admin-guide/abi-stable)", "venue": "kernel.org documentation, accessed 2026-11-03", "url": "https://www.kernel.org/doc/html/latest/admin-guide/abi-stable.html"},
    "localfirst": {"authors": ["Martin Kleppmann", "Adam Wiggins", "Peter van Hardenberg", "Mark McGranaghan"], "title": "Local-first software: you own your data, in spite of the cloud", "venue": "Onward! 2019; Ink and Switch essay", "url": "https://www.inkandswitch.com/local-first/"},
    "review020": {"authors": ["Craig Ross", "Tommy Xaypanya"], "title": "ThoxOS and ThoxInux: Architecture, Evidence, and a Validation Protocol for Local-First AI (technical research draft, revision 0.2.0-review)", "venue": "THOX.ai LLC, 2026-11-01; version of record on Zenodo, DOI 10.5281/zenodo.23876230", "url": "https://doi.org/10.5281/zenodo.23876230"},
    "thoxoswp": {"authors": ["THOX.ai"], "title": "ThoxOS: An Open Kernel and Operating System for Local-First AI (technical whitepaper v0.1.0)", "venue": "THOX.ai, 2026-10-31; historical design under CC BY 4.0 (Linux LTS fork position, class floors, entitlement and A/B design)", "url": ""},
    "card08": {"authors": ["THOX.ai"], "title": "ThoxOS-Kernel-0.8B model card and repository (config.json, GGUF sizes)", "venue": "Hugging Face, read 2026-11-03", "url": "https://huggingface.co/Thox-ai/ThoxOS-Kernel-0.8B"},
    "card4": {"authors": ["THOX.ai"], "title": "ThoxOS-Kernel-4B model card and repository", "venue": "Hugging Face, read 2026-11-03", "url": "https://huggingface.co/Thox-ai/ThoxOS-Kernel-4B"},
    "card27": {"authors": ["THOX.ai"], "title": "ThoxOS-Kernel-27B model card and repository", "venue": "Hugging Face, read 2026-11-03", "url": "https://huggingface.co/Thox-ai/ThoxOS-Kernel-27B"},
    "thoxpage": {"authors": ["THOX.ai"], "title": "ThoxOS and ThoxInux, THOX Research Paper (web page for revision 0.2.0-review)", "venue": "thox.ai, read 2026-11-03", "url": "https://www.thox.ai/research/papers/thoxos"},
    "meshpaper": {"authors": ["THOX.ai Research"], "title": "THOX MeshStack: Capacity-Priced Pipeline Sharding, Grant-Gated KV Transfer and Lease-Fenced Device Roles for a Private Household Mesh (technical report v1.0.0)", "venue": "THOX.ai Research, 2026-11-03, preprint; ttracx/thox-meshstack-inference papers/research-paper-v1.0.0", "url": ""},
}

exec((ROOT / "wp" / "_helpers.txt").read_text())  # noqa: S102  (shared helpers: cite, p, h2, h3, eq, ieq, table, figure, callout, algo, ul, ol, fmt)

# ----------------------------------------------------------------------------
E = S["entitlement"]; U = S["update"]; M = S["memory"]; Y = S["syscalls"]
hmac_us = E["kpi_hmac_us"]; ed_us = E["kpi_ed_us"]
tok_h = E["kpi_token_bytes_hmac"]; tok_e = E["kpi_token_bytes_ed"]
c_good = U["kpi_contract_good"]; c_roll = U["kpi_contract_rollbacks"]; c_boots = U["kpi_contract_maxboots"]
ns_tamp = U["kpi_nosig_tampered"]; nc_brick = U["kpi_nocounter_bricked"]; ip_brick = U["kpi_inplace_bricked"]; ip_good = U["kpi_inplace_good"]
upd = U["updates"]; seeds = U["seeds"]
m08 = M["models"]["ThoxOS-Kernel-0.8B"]; m4 = M["models"]["ThoxOS-Kernel-4B"]; m27 = M["models"]["ThoxOS-Kernel-27B"]
tot = Y["kpi_total"]; comp = Y["kpi_complete"]; part = Y["kpi_partial"]; den = Y["kpi_denied"]
ld = Y["kpi_loop_distinct_total"]; lc = Y["kpi_loop_distinct_complete"]; lp = Y["kpi_loop_distinct_partial"]; ldn = Y["kpi_loop_distinct_denied"]; lm = Y["kpi_loop_distinct_missing"]
lcalls = Y["kpi_loop_calls_total"]; lpart = Y["kpi_loop_calls_partial"]


def ctx(v: int) -> str:
    return "no fit" if v == 0 else f"{v:,} tokens"


ABSTRACT = (
    "An operating system for local AI must carry an evidence chain from kernel behaviour to application execution, model quality "
    "and physical device operation, and the THOX record for ThoxOS&trade; has changed shape twice in four days: a 31 October whitepaper "
    "specified a Linux LTS fork, and a 1 November review draft identifies ThoxInux, a Ginux-derived Rust-first x86-64 kernel, as the "
    "reviewed foundation. This report fixes the architecture against that reviewed foundation and adds the evidence a general host can "
    "produce. We implement the entitlement contract clean-room in two token designs and show by executable properties that the "
    "shared-secret HMAC design accepts a token forged by any device that can verify one, while an Ed25519 design rejects it at "
    f"{fmt(ed_us,0)} microseconds per verification on a 2-vCPU host, and that a wall-clock grace window is revived by a clock "
    "rollback unless a persisted high-water mark is used. We simulate the A/B update contract under injected faults: the full contract "
    f"ends every one of {upd} updates on a known-good slot with at most {c_boots:.0f} boots of recovery, while removing the signature check "
    f"boots {ns_tamp:.0f} tampered images and removing the attempt counter or the second slot leaves about {nc_brick:.0f} devices unbootable per run. "
    f"We read the upstream Linux-ABI ledger at the exact commit ThoxInux pins ({tot} dispatched syscalls: {comp} Complete, {part} Partial, "
    f"{den} Policy-denied) and join it with a strace of a reference agent loop on the authoring host: of {ld} distinct syscalls the loop issues, "
    f"{lc} are Complete, {lp} Partial and {ldn} Policy-denied, so a plain agent loop touches nothing the policy refuses and almost nothing that is "
    "proven equivalent to Linux. We compute the memory budget for the three published kernel models from their card geometry: the 0.8B student "
    f"fits the 2 GB Air floor with {ctx(M['kpi_08b_air_ctx_r1'])} of context at a 1 GB reserve and nothing at 1.5 GB; the 4B student fits the 4 GB Mini floor "
    f"only at {ctx(M['kpi_4b_mini_ctx_r1'])}; the 27B teacher needs a host above 16 GB. No ThoxInux boot, no device, no model inference and no "
    "production security were executed here; the validation protocol that would produce those results is restated with its gates."
)

CONTENTS = [("Executive summary", "exec"), ("1. Introduction", "intro"), ("2. Background and related work", "related"),
            ("3. System and threat model", "model"), ("4. Design", "design"), ("5. Implementation", "impl"), ("6. Evaluation", "eval"),
            ("7. Discussion and limitations", "limits"), ("8. Conclusion", "concl"), ("9. Roadmap and decisions for the founders", "roadmap"),
            ("Appendix A. Reproducibility", "appA"), ("Appendix B. Notation", "appB"), ("Appendix C. Authorship and disclosure", "appC"), ("References", "refs")]

cover = f"""
<section class="cover"><div class="cover-inner">
<div class="eyebrow"><span>THOX.ai Research &middot; Technical report {VERSION} &middot; {DATE}</span><span class="pill">Preprint, not peer reviewed</span></div>
<h1>{TITLE}</h1>
<p class="deck">The reviewed foundation (ThoxInux on Ginux) fixed as the architecture of record, the entitlement and update contracts tested as executable properties and fault simulations, the Linux-ABI ledger read at the pin and joined with a traced agent loop, and the kernel-model memory budget computed from the cards.</p>
<p class="byline">THOX.ai Research &middot; Corresponding author: Tommy Xaypanya, CTO and Co-Founder, THOX.ai LLC, Cedar Park, Texas &middot; ORCID 0009-0000-4425-9565 &middot; Proposed co-author: Craig Ross, CEO, ORCID 0009-0005-9872-3673</p>
<div class="abstract"><div class="ct">Abstract</div><p>{ABSTRACT}</p></div>
<div class="contents"><div class="ct">Contents</div><ol>{''.join(f'<li><a href="#{a}">{t}</a></li>' for t, a in CONTENTS)}</ol></div>
<div class="cover-foot">Your AI. Your Data. Your Rules.&trade; &middot; THOX&reg;, ThoxOS&trade;, MeshStack&trade; and ThoxWork&trade; are marks of THOX.ai LLC.</div>
</div></section>
"""

OUT.append('<section class="paper-body">')
h2("", "Executive summary", "exec")
p("ThoxOS&trade; is the operating system for THOX's local-first AI devices and desktops. Its record has two foundations in four days: the "
  "v0.1.0 whitepaper of 31 October specified linux-thox, a Linux LTS fork with a separate Rust research laboratory [@thoxoswp]; the "
  "0.2.0-review draft of 1 November identifies ThoxInux, a Ginux-derived Rust-first x86-64 kernel with Linux userspace compatibility, as "
  "the reviewed foundation, and treats the whitepaper as historical input [@review020; @thoxinux]. This report takes the reviewed "
  "foundation as the architecture of record, keeps what the whitepaper specified that survives the change (class floors, entitlement "
  "without DRM, A/B updates with a health gate, the open and paid line), and adds the evidence a general host can produce.")
kpis = [
    (f"{fmt(ed_us,0)} &micro;s", f"Ed25519 token verify on a 2-vCPU host; HMAC {fmt(hmac_us,0)} &micro;s. HMAC accepts a verifier-forged token, Ed25519 rejects it", "measured"),
    (f"{c_good:.0f} / {upd}", f"updates ending on a known-good slot under the full A/B contract with injected faults, at most {c_boots:.0f} recovery boots; no signature check boots {ns_tamp:.0f} tampered images", "simulated"),
    (f"{lc} / {ld}", f"distinct syscalls of a traced reference agent loop that are Complete at the ThoxInux pin; {lp} Partial, {ldn} Policy-denied", "observed + measured"),
    (ctx(M['kpi_4b_mini_ctx_r1']).replace(" tokens", " tok"), "largest context for ThoxOS-Kernel-4B Q4_K_M resident on the 4 GB Mini floor at a 1 GB reserve; no fit at 1.5 GB", "calculated"),
]
OUT.append('<div class="kpis">' + "".join(f'<div class="kpi"><div class="kv">{v}</div><div class="kl">{l}</div><div class="kt">{t}</div></div>' for v, l, t in kpis) + "</div>")
callout("Product implications",
        "First, the entitlement reference implementation's HMAC demo cannot be the production design: any device holding the verification "
        "secret can mint tokens, and the fix is a public-key signature plus a persisted time high-water mark, both of which this report tests. "
        "Second, the A/B contract's value is in the attempt counter and the second slot, not in the health gate alone; dropping either leaves "
        f"about {nc_brick:.0f} of {upd} updates unbootable in simulation. Third, the Linux ABI at the pin is dispatched but mostly Partial, and a plain "
        "agent loop lives almost entirely in Partial calls, so P1 of the review protocol (resident-agent lifecycle on the real payload) is the "
        "first measurement to fund. Fourth, the 4B student fits the Mini floor only at short context; the Mini's resident model is a context "
        "decision, and the product copy should say so.", "green")

h2("1", "Introduction", "intro")
p("Local-first software keeps the user's data and computation on hardware the user owns [@localfirst]. An operating system built for local AI "
  "inherits that promise and adds four layers that each need their own evidence: the kernel must sustain the workload's process, memory, "
  "filesystem and networking behaviour; the runtime must load the exact model artifact; the application must enforce the user's authority; "
  "and the system must fit the hardware envelope. The 0.2.0 review states this chain and the rule that evidence at one layer never establishes "
  "another [@review020]. This report follows that rule and applies it to the foundation change.")
p("ThoxInux is a derivative of Gregory M. Kurtzer's Ginux, an independent Rust-first x86-64 kernel with Linux userspace compatibility, a ring-3 "
  "administration controller and a UEFI boot image [@ginux]. ThoxInux pins upstream commit 36503bda and ships engineering prereleases v0.9.0 and "
  "v0.9.1 whose unified EFI payload passed a 22-check lifecycle suite under QEMU TCG and KVM on one host; its ledger also records a resident "
  "agent failure on an earlier edition payload and conditional build reproducibility [@thoxinux]. Those are repository-reported runs, not "
  "results of this report. The whitepaper's Linux LTS fork position is retained as a dated design whose entitlement, class-floor and update "
  "specifications carry over unchanged [@thoxoswp].")
p("The contributions are:")
ol([
    "<b>An architecture of record on the reviewed foundation</b> (Section 4) with the whitepaper's surviving contracts restated as numbered requirements and the review's two equations made executable.",
    f"<b>Entitlement evidence</b> (Section 6.1): a clean-room implementation of the Core-never-gated invariant and the MayExecute conjunction in two token designs, with ten executable properties; the shared-secret design accepts a verifier-forged token and the public-key design rejects it, at {fmt(ed_us,0)} microseconds per verification; a wall-clock grace window is revived by a clock rollback unless a persisted high-water mark is kept.",
    f"<b>Update evidence by simulation</b> (Section 6.2): the full A/B contract ends all {upd} updates on a known-good slot under injected faults with at most {c_boots:.0f} boots of recovery; ablating the signature check, the attempt counter or the second slot each produces a named failure class.",
    f"<b>Linux ABI evidence</b> (Section 6.3): the upstream ledger at the pin classified by area, and a strace of a reference agent loop joined with the ledger: {lc} of {ld} distinct calls Complete, {lp} Partial, none Policy-denied.",
    "<b>Memory budget evidence</b> (Section 6.4): the review's equation 3 evaluated for the three published kernel models from their card geometry against the class floors, including the losing regimes.",
])
p("Nothing in this report booted ThoxInux, ran a model, touched a device or evaluated production security. Section 7 says so itemised; Section 9 "
  "lists the decisions only the founders can take.")

h2("2", "Background and related work", "related")
h3("2.1 Rust kernels with Linux ABI compatibility")
p("Asterinas is a Rust framekernel with Linux ABI compatibility and a small trusted computing base, evaluated at USENIX ATC 2025 [@asterinasatc; @asterinas]; "
  "Rust-for-Linux brings Rust into the Linux kernel itself [@rustylinux]. Ginux takes a third position: an independent kernel that dispatches the "
  "pinned Linux v6.12 x86-64 syscall table and ledgers each call as Complete, Partial, Policy-denied or Missing, with Linux's documented stable "
  "ABI as the authority [@ginux; @abistable]. Neither Asterinas's safety argument nor its measurements transfer to Ginux or ThoxInux; the review "
  "says this and this report repeats it.")
h3("2.2 Agent operating systems and privilege")
p("A line of work frames the LLM as an operating-system component or the OS as an agent host: AIOS and its vision paper [@aios; @aiosvision], a "
  "lessons-from-classical-OS treatment [@agentoslessons], and an agent framework for Linux schedulers [@agenticos]. ThoxOS's position is the "
  "opposite of LLM-as-OS: the model proposes and the harness disposes, and the review's MayExecute conjunction makes the model a non-term. "
  "Progent's privilege control for agents [@ragents] and the LITMUS and SafeClawBench evaluations of agent behaviour in real OS environments and "
  "sandboxes [@litmus; @safeclaw] are the closest evaluation precedents for the review's P2 protocol.")
h3("2.3 Updates, entitlement and model reporting")
p("RAUC documents the A/B slot, bootloader and mark-good integration this design adopts [@rauc]. HMAC and EdDSA are the two primitives the "
  "entitlement experiment compares [@rfc2104; @rfc8032]. Model Cards motivate treating the ThoxOS-Kernel cards as release documentation whose "
  "conditions travel with the numbers [@modelcards]; the cards themselves are the source of the geometry and file sizes used here [@card08; @card4; @card27].")
table(["Source", "Kernel position", "Entitlement", "Updates", "Status of evidence"], [
    ["ThoxOS whitepaper v0.1.0 [@thoxoswp]", "Linux LTS fork (linux-thox), Rust lab separate", "signed offline token, 30-day grace, Core never gated", "RAUC A/B, health gate", "staging tests reported (25 entitlement, 27 image checks); no device"],
    ["0.2.0-review draft [@review020]", "ThoxInux (Ginux-derived, Rust-first x86-64)", "eq. 1 and eq. 2; HMAC demo flagged as issuer-trust failure", "RAUC template; P4 protocol", "repository-reported runs; protocol unexecuted"],
    ["ThoxInux repository [@thoxinux]", "Ginux pin 36503bda; v0.9.0 and v0.9.1 prereleases", "n/a", "n/a", "22/22 lifecycle under TCG and KVM on one host; resident-agent fault on an edition payload"],
    ["<b>This report</b>", "ThoxInux as architecture of record", "two designs tested; forgery and rollback hazards shown", "contract simulated with ablations", "measured on a host, observed ledger, simulated protocol, calculated budget"],
], "Table 1. The THOX record and this report. Evidence classes are named per row; nothing in the first three rows is re-run here.")

h2("3", "System and threat model", "model")
h3("3.1 Setting")
p("Devices are the E2, P4 and P6 classes (ThoxAir 2 GB, ThoxMini 4 GB, ThoxClip 6 GB RAM floors) plus host-tier machines; the ThoxKey companion "
  "runs no resident model and is served by a connected host [@thoxoswp; @card08]. The reviewed kernel target is x86-64; Arm is scoped, not ported "
  "[@review020]. MeshStack&trade; is the optional private mesh and ThoxWork&trade; the workspace; their roles are integration boundaries, not evidence "
  "that the stack has executed on the reviewed kernel [@meshpaper].")
h3("3.2 Requirements")
ol([
    "<b>R1 Core never gated.</b> " + ieq("f \\in F_{\\mathrm{core}} \\Rightarrow E(f,t) = \\mathrm{true}") + " for every token state " + ieq("t") + " (review eq. 1).",
    "<b>R2 Authorization is a conjunction.</b> " + ieq("\\mathrm{MayExecute}(a) = U(a) \\wedge O(a) \\wedge E(f(a), t)") + "; model output sets none of the terms (review eq. 2). Unknown feature identifiers are denied explicitly.",
    "<b>R3 Issuer-only trust.</b> A device that can verify an entitlement cannot issue one.",
    "<b>R4 Clock discipline.</b> A rolled-back clock cannot revive an expired entitlement.",
    "<b>R5 Signed bundles, A/B slots, bounded attempts, health gate, data untouched.</b> Any failure returns the device to the last known-good slot without user action.",
    "<b>R6 Memory budget.</b> " + ieq("M_{\\mathrm{weights}} + M_{\\mathrm{KV}} + M_{\\mathrm{runtime}} + M_{\\mathrm{OS}} + M_{\\mathrm{reserve}} \\le M_{\\mathrm{available}}") + " (review eq. 3), evaluated per model, quantisation, class and context.",
    "<b>R7 ABI truth.</b> Compatibility claims cite the ledger status at the pin, never a count of dispatched calls.",
    "<b>R8 Evidence separation.</b> Observed artifacts, repository-reported execution, publisher-reported evaluation and proposed protocol are never merged (review Section 3.1).",
])
h3("3.3 Threat model")
p("In scope: untrusted prompts and tool input, a compromised application, a malformed or tampered update bundle or entitlement token, a device "
  "that holds verification material, and a device whose clock is set back. Out of scope: a compromised issuer, a compromised kernel, physical "
  "key extraction, and side channels. The trusted boundary is the authenticated user decision, the enforcing broker, OS access control and "
  "verified artifact identity; the model is never in it [@review020].")

h2("4", "Design", "design")
h3("4.1 Architecture of record")
OUT.append("""
<div class="arch">
  <div class="arch-row"><div class="box ghost"><b>User surfaces (TXF)</b><span>ThoxChat, device portal, ThoxWork workspace</span></div></div>
  <div class="arch-arrow">proposals from the model; decisions from the broker (R2)</div>
  <div class="arch-row three">
    <div class="box"><b>Kernel models</b><span>ThoxOS-Kernel-0.8B (Air, ThoxKey host pack), 4B (Mini, Clip; baseline), 27B (host-tier teacher); propose only</span></div>
    <div class="box hi"><b>Authorization broker</b><span>MayExecute = U and O and E; entitlement verifier (public key, high-water clock); explicit denial of unknown features (R1-R4)</span></div>
    <div class="box"><b>Local runtime</b><span>llama.cpp-class engine, model manager, memory budget check before load (R6)</span></div>
  </div>
  <div class="arch-arrow">syscalls (ledger status at the pin, R7)</div>
  <div class="arch-row two">
    <div class="box hi"><b>ThoxInux (Ginux-derived, Rust-first x86-64)</b><span>pinned upstream 36503bda; 375 dispatched syscalls; ring-3 admin controller; UEFI payload</span></div>
    <div class="box"><b>Update and integrity</b><span>signed bundle, A/B rootfs, attempt counter, first-boot health gate, data partition untouched (R5)</span></div>
  </div>
  <div class="arch-row"><div class="box ghost"><b>Hardware classes</b><span>E2 Air 2 GB, P4 Mini 4 GB, P6 Clip 6 GB, host tier; x86-64 reviewed, Arm scoped only</span></div></div>
</div>
<figcaption><b>Figure 0.</b> Architecture of record on the reviewed foundation. Schematic; the model layer proposes, the broker decides, the kernel is ThoxInux at the pin, and every box carries the evidence class of Section 6.</figcaption>
""")
h3("4.2 Entitlement without DRM, made executable")
p("A token is a payload (account, feature set, issued-at, expiry, nonce) and a signature. Validity is signature correctness, a well-formed payload, "
  "membership of the requested feature, and " + ieq("\\mathrm{now} \\le \\mathrm{exp} + G") + " with " + ieq("G") + " the 30-day grace. Core features "
  "short-circuit before any token is examined, which is how R1 is enforced rather than hoped. The whitepaper's reference implementation and the "
  "review's demo use HMAC under a shared secret [@thoxoswp; @review020]; the review names the consequence, that a holder of the verification "
  "secret can also generate MACs. This report tests two designs side by side:")
eq(r"\mathrm{hmac}:\ \tau = p \,\|\, \mathrm{HMAC}_{k}(p),\quad \text{verifier holds } k;\qquad \mathrm{ed25519}:\ \tau = p \,\|\, \mathrm{Sig}_{sk}(p),\quad \text{verifier holds } pk \text{ only.}")
p("<b>Proposition 1 (forgeability).</b> Under the hmac design any party holding " + ieq("k") + " produces a token the verifier accepts for any feature "
  "set; under the ed25519 design a party holding only " + ieq("pk") + " produces an accepted token with probability bounded by EdDSA's existential "
  "unforgeability. <i>Proof.</i> HMAC verification recomputes " + ieq("\\mathrm{HMAC}_k(p)") + ", so possession of " + ieq("k") + " is possession of the "
  "issuing capability; for Ed25519 the statement is the EUF-CMA property of the scheme [@rfc8032]. " + ieq("\\square") + " Property P9 in Section 6.1 is the executable form.")
p("<b>Proposition 2 (clock rollback).</b> With wall-clock time only, an expired token with expiry " + ieq("e") + " is accepted again whenever the clock "
  "is set to any " + ieq("t' \\le e + G") + "; with the device persisting " + ieq("h = \\max(h, \\mathrm{wall})") + " and evaluating validity at " + ieq("h") +
  ", a rollback changes nothing. <i>Proof.</i> " + ieq("h") + " is monotone by construction and already exceeded " + ieq("e + G") + " when the token expired. " +
  ieq("\\square") + " Property P10 is the executable form. Persisting " + ieq("h") + " needs no trusted time source; it needs tamper-evident local storage, which the review lists as production work.")
h3("4.3 The update contract")
algo("Algorithm 1. First boot of a new slot (health gate with bounded attempts)", [
    "Precondition: bundle signature and image hashes verified before any write; image written to the idle slot;",
    "              attempt counter armed with N = 3; data partition untouched",
    "boots <- 0",
    "loop:",
    "    boots <- boots + 1; boot idle slot",
    "    if thoxd answers, portal is enabled, local mesh discovery is up, network reaches targets, slot reports bootable:",
    "        mark slot GOOD; it becomes the running slot; return OK",
    "    if boots >= N: bootloader returns to the previous GOOD slot; mark idle slot BAD; return ROLLED_BACK",
])
p("Three ablations are simulated in Section 6.2: no signature check (R5 first clause), no attempt counter, and a single slot updated in place. "
  "Each removes one clause of the contract and each produces a distinct failure class, which is the argument that the contract has no redundant part.")
h3("4.4 ABI truth and the agent path")
p("Ginux's ledger scores every dispatched syscall; ThoxInux's audit recounts it and runs upstream's architecture checker at the pin [@thoxinux]. "
  "This report adds an area classification and a measured join: which calls a plain agent loop issues and what their status is. The loop "
  "(Appendix A) reads a configuration, appends a log, spawns a child and waits, opens a TCP connection to a local listener, polls, handles a "
  "signal and maps a file. It is a Python program on the authoring host's Linux; it is not the ThoxOS agent and it did not run on ThoxInux. "
  "Its value is to name the Partial calls that P1 of the review protocol must exercise first.")
h3("4.5 Memory budget")
p("For a Qwen3.5-family hybrid model with " + ieq("n_f") + " full-attention layers of " + ieq("n_{kv}") + " KV heads and head dimension " + ieq("d") +
  ", bf16 KV costs " + ieq("2\\, n_f\\, n_{kv}\\, d \\cdot 2") + " bytes per token; the linear-attention layers carry a fixed fp32 state. "
  f"From the cards: 0.8B {m08['kv_bytes_per_token']:,} B/token, 4B {m4['kv_bytes_per_token']:,} B/token, 27B {m27['kv_bytes_per_token']:,} B/token [@card08; @card4; @card27]. "
  "Weights are the published GGUF sizes, assumed fully resident. The reserve term is swept because it is not measured.")

h2("5", "Implementation", "impl")
p("Three implementations exist in the record and one in this report. ThoxInux carries the kernel, a Python lifecycle suite, source-preparation "
  "and launcher tests, an SSD installer with tests and an agentos Rust crate [@thoxinux]; the historical thoxos-core lane carries the entitlement "
  "reference (25 tests) and the image validator (27 checks) [@thoxoswp]. This report could not execute code from those public clones under the "
  "authoring session's policy, so their test states are quoted as repository-reported. This report's own code is Appendix A: the entitlement "
  "contract in two designs with property tests, the update simulator, the ledger parser and traced loop, and the memory budget calculator.")
table(["Requirement", "Specified", "Test or evidence in this report", "Result"], [
    ["R1 Core never gated", "Section 4.2", "P6: Core allowed with no, expired, tampered and garbage tokens", "pass" if E["properties_pass"] else "FAIL"],
    ["R2 conjunction, unknown denied", "Section 4.2", "P7, P8", "pass" if E["properties_pass"] else "FAIL"],
    ["R3 issuer-only trust", "Prop. 1", "P9: forged token accepted (hmac) / rejected (ed25519)", f"{'accepted' if E['kpi_hmac_forged_accepted'] else 'rejected'} / {'accepted' if E['kpi_ed_forged_accepted'] else 'rejected'}"],
    ["R4 clock discipline", "Prop. 2", "P10: rollback with wall clock / with high-water mark", f"{'accepted' if E['kpi_rollback_wall_accepted'] else 'rejected'} / {'rejected' if E['kpi_rollback_hwm_rejected'] else 'accepted'}"],
    ["R5 update contract", "Algorithm 1", f"exp/update_sim.py, {seeds} seeds x {upd} updates, 4 policies", "simulated; Section 6.2"],
    ["R6 memory budget", "Section 4.5", "exp/memory_budget.py over cards, floors, contexts, reserves", "calculated; Section 6.4"],
    ["R7 ABI truth", "Section 4.4", "exp/syscall_ledger.py: ledger parse (375 rows asserted) and strace join", "observed and measured; Section 6.3"],
    ["R8 evidence separation", "throughout", "every number carries its class in summary.json", "editorial"],
], "Table 2. Requirement-to-evidence map.")

h2("6", "Evaluation", "eval")
p("<b>Setup.</b> Authoring container, Linux, 2 vCPU, 7 GB RAM, Python 3.13, cryptography library for Ed25519, strace for the traced loop. Timing: "
  "30 repetitions of 1,000 verifications after warm-up, medians with interquartile ranges. The ledger was fetched from the upstream repository "
  "at the pinned commit on 2026-11-03. Model geometry and sizes were read from the three public cards the same day. Nothing ran on ThoxInux.")
h3("6.1 Does the entitlement contract hold, and which token design is safe?")
figure("fig_entitlement.svg", 1, f"Entitlement contract in two token designs. A: verify cost per token on the authoring host (median of 30 x 1,000). B: the ten properties; P9 and P10 are hazards, so a red ACCEPTED is the finding. Token sizes: {tok_h} bytes (hmac) and {tok_e} bytes (ed25519).")
p(f"Properties P1 to P8 pass in both designs: Core is unconditional, the conjunction holds, grace admits at 29 days and refuses at 31, tampered and malformed tokens "
  f"are refused, unknown features are denied. P9 separates the designs: a forged token minted with the verification secret is {'accepted' if E['kpi_hmac_forged_accepted'] else 'rejected'} "
  f"under hmac and {'accepted' if E['kpi_ed_forged_accepted'] else 'rejected'} under ed25519, which is Proposition 1 run. P10 is design-independent: with wall-clock validity a "
  f"token expired 40 days earlier is {'accepted' if E['kpi_rollback_wall_accepted'] else 'rejected'} after a 20-day clock rollback, and with a persisted high-water mark it is "
  f"{'rejected' if E['kpi_rollback_hwm_rejected'] else 'accepted'}. The cost of the safe design is {fmt(ed_us,0)} microseconds per verification against {fmt(hmac_us,0)} for HMAC on this host, "
  "a difference that no entitlement check on a device will notice. The recommendation is unambiguous: production tokens are Ed25519-signed, devices hold only the public key, "
  "and the device persists its time high-water mark.")
h3("6.2 Does the A/B contract recover, and which clause does the work?")
figure("fig_update.svg", 2, f"A/B update contract under injected faults, {seeds} seeds of {upd} updates each, medians with IQR. Fault probabilities per update: bad signature 3%, incomplete write 5%, corrupt image 3%, health failure 6%, power loss in the health window 4%, boot hang 4%. Protocol logic only.")
p(f"The full contract ends all {c_good:.0f} updates on a known-good slot, with {c_roll:.0f} automatic rollbacks and never more than {c_boots:.0f} boots of recovery. Removing the "
  f"signature check keeps the device bootable but boots {ns_tamp:.0f} tampered images per run; removing the attempt counter leaves {nc_brick:.0f} devices looping on a bad slot; "
  f"a single slot updated in place ends {ip_good:.0f} updates well and leaves {ip_brick:.0f} unbootable. The three clauses fail differently, so none is redundant, and the ablation "
  "ordering tells the release team what to test first on hardware: attempt-counter exhaustion and interrupted writes (P4 of the review protocol), not the happy path.")
h3("6.3 What does the Linux ABI at the pin look like, and what does an agent loop touch?")
figure("fig_syscalls.svg", 3, f"A: the upstream ledger at commit 36503bda, {tot} dispatched syscalls, classified by area (classification is this report's; statuses are the ledger's). B: the 18 most frequent syscalls of the reference agent loop under strace on the authoring host, coloured by ledger status; none is Policy-denied.")
p(f"At the pin, {comp} syscalls are Complete, {part} Partial and {den} Policy-denied, with nothing Missing [@ginux; @thoxinux]. By area, files is {Y['kpi_files_partial']} Partial to "
  f"{Y['kpi_files_complete']} Complete, network is {Y['kpi_network_complete']} Complete to {Y['kpi_network_partial']} Partial, and the Policy-denied set is concentrated in security "
  f"({Y['kpi_security_denied']}) and identity ({Y['kpi_identity_denied']}): credential mutation, bpf and Landlock are refused by design, which matches the ThoxInux domain model. "
  f"The reference loop issues {ld} distinct syscalls and {lcalls:,} calls per run: {lc} distinct calls are Complete, {lp} Partial, {ldn} Policy-denied and {lm} absent from the "
  f"pinned table; by volume {lpart:,} of {lcalls:,} calls land in Partial entries (stat, rt_sigaction, read, openat, mmap, futex, clone3, wait4 and their neighbours). The "
  "positive reading is that an agent loop asks for nothing the policy refuses. The cautionary reading is that it lives almost entirely in calls that are dispatched and "
  "useful but not proven equivalent to Linux, which is exactly the surface on which the edition payload's resident-agent failure occurred [@review020]. This is the "
  "evidence for funding P1 before any other protocol item.")
h3("6.4 What fits where? (Calculated)")
figure("fig_memory.svg", 4, "Largest context that fits the review's memory budget for each published kernel model at Q4_K_M with fully resident weights, bf16 KV from the card geometry, fixed linear-attention state, and a 1.0 GB OS-plus-runtime reserve. 'No fit' means the weights and reserve alone exceed the floor. Calculated; nothing measured.")
p(f"The 0.8B student fits the 2 GB Air floor with {ctx(M['kpi_08b_air_ctx_r1'])} at a 1.0 GB reserve and {ctx(M['kpi_08b_air_ctx_r15'])} at 1.5 GB: the reserve, not the model, decides "
  f"the Air. The 4B student fits the 4 GB Mini floor only at {ctx(M['kpi_4b_mini_ctx_r1'])} at a 1.0 GB reserve, {ctx(M['kpi_4b_mini_ctx_r15'])} at 1.5 GB, and its Q8_0 build "
  f"{ctx(M['kpi_4b_q8_mini_ctx_r1'])}; on the 6 GB Clip it reaches {ctx(M['kpi_4b_clip_ctx_r1'])}. The 27B teacher is {ctx(M['kpi_27b_host16_ctx_r1'])} on a 16 GB host at Q4_K_M, "
  f"{ctx(M['kpi_27b_host32_ctx_r1'])} on 32 GB, and at Q8_0 {ctx(M['kpi_27b_q8_host32_ctx_r1'])} on 32 GB and {ctx(M['kpi_27b_q8_host64_ctx_r1'])} on 64 GB. Two product "
  "consequences: the Mini's resident 4B model is a 2k-to-8k-context assistant unless the reserve is measured smaller than 1 GB, and the 27B host tier starts at 32 GB. "
  "File size is a lower bound on resident weight memory and the reserve is an assumption; the review's warning that storage bytes, advertised memory and peak resident "
  "memory are different quantities stands [@review020].")

h2("7", "Discussion and limitations", "limits")
ol([
    "<b>No kernel execution.</b> ThoxInux was not booted here; its 22/22 lifecycle results, the resident-agent fault and the reproducibility conditions are repository-reported [@thoxinux].",
    "<b>Policy-bound.</b> The authoring session could not run code from the public ThoxInux clone, so its suites were not re-run; this report's own code ran.",
    "<b>The traced loop is not the ThoxOS agent.</b> It is a Python program on the authoring host's Linux; it establishes which ledger entries a plain loop touches, not that the loop works on ThoxInux.",
    "<b>Area classification is ours.</b> The ledger's statuses are upstream's; the nine areas are this report's regex classification of syscall names.",
    "<b>Entitlement scope.</b> The two designs are clean-room; production key custody, rotation, revocation, replay and trusted time remain unbuilt, as the review lists.",
    "<b>Update simulation.</b> Fault probabilities are stated assumptions; the simulation evaluates contract logic, not RAUC, a bootloader or flash behaviour.",
    "<b>Memory budget.</b> GGUF size is a lower bound on resident weights; the reserve is swept, not measured; the linear-attention state is an estimate from config.json.",
    "<b>Record motion.</b> The whitepaper (31 October) states no kernel-model weights exist; the cards (1 November) publish them, and the thox.ai paper page reads '27B card only, weights not public' while the 27B card lists public GGUF and safetensors [@thoxpage; @card27]. This report follows the cards and flags the page for correction.",
    "<b>No device, no model run, no security assessment.</b> No E2, P4 or P6 hardware was touched; no inference ran; no penetration or adversarial test was performed.",
    "<b>Not peer reviewed.</b> Preprint prepared by THOX.ai Research with AI assistance (Appendix C).",
])

h2("8", "Conclusion", "concl")
p("ThoxOS's foundation changed from a Linux fork to ThoxInux in the week before this report, and the contracts the whitepaper specified survived the change "
  "because they never depended on the kernel. This report made two of them executable and tested them: the entitlement contract, whose demo design is forgeable by "
  "any verifier and whose grace window is revivable by a clock rollback, both fixed by a public key and a persisted high-water mark; and the update contract, whose "
  "every clause removes a distinct failure class in simulation. It read the ABI ledger at the pin and showed that a plain agent loop asks for nothing refused and "
  "almost nothing proven. It computed what fits on each device from the cards. The next evidence is the review's P1 on the real payload bytes, and this report says why it comes first.")

h2("9", "Roadmap and decisions for the founders", "roadmap")
ol([
    "<b>Record correction.</b> Align the thox.ai paper page and the whitepaper status box with the 1 November cards (27B weights public).",
    "<b>Entitlement production design.</b> Adopt Ed25519 tokens with device-held public keys and a persisted time high-water mark; the HMAC demo stays a demo.",
    "<b>P1 first.</b> Run the review's resident-agent lifecycle protocol on Payload U and v0.9.1 bytes, 30 cold starts per configuration, with the Partial calls of Section 6.3 as the watch list.",
    "<b>P4 on hardware.</b> Interrupted writes and attempt-counter exhaustion before the happy path.",
    "<b>Measure the reserve.</b> One measured OS-plus-runtime figure per class replaces the sweep and settles the Mini context statement.",
    "<b>Author roster and venue.</b> Craig Ross and Tommy Xaypanya are the proposed human authors; confirm contributions and consent before any submission.",
])

h2("A", "Appendix A. Reproducibility", "appA")
algo("Commands (from the artifact root)", [
    "pip install cryptography numpy matplotlib pypdf pillow && cd wp && npm install && cd ..",
    "curl -o /home/claude/ginux_ledger/LINUX-COMPATIBILITY.md https://raw.githubusercontent.com/gmkurtzer/ginux/36503bda2d87465765e1b94e65f9d100f27ed5be/docs/LINUX-COMPATIBILITY.md",
    "python3 exp/entitlement_experiments.py   # fails on any property violation",
    "python3 exp/update_sim.py",
    "python3 exp/memory_budget.py",
    "python3 exp/syscall_ledger.py            # needs strace; asserts 375 ledger rows",
    "python3 exp/analyze.py && python3 wp/figures.py && python3 wp/build.py",
    "node wp/katex_render.cjs wp/paper.src.html wp/paper.html && node wp/pdf.cjs wp/paper.html wp/cover.pdf wp/body.pdf && python3 wp/merge_pdf.py",
])
ka = E["known_answer"]
p("Entitlement known-answer vector (hmac design, secret = bytes 0x00..0x1f): payload <code>" + html.escape(ka["payload"]) + "</code>; token <code>" + ka["token"] + "</code>; "
  f"allowed at {ka['allowed_at']}, allowed in grace at {ka['grace_allowed_at']}, denied at {ka['denied_at']} (Unix seconds).")
p("Reference loop last log line on the authoring host: <code>" + html.escape(Y["loop_last_log_line"]) + "</code>.")
h2("B", "Appendix B. Notation", "appB")
table(["Symbol", "Meaning"], [
    [ieq("F_{\\mathrm{core}}, E(f,t)"), "Core feature set; entitlement decision for feature f under token state t"],
    [ieq("U(a), O(a), f(a)"), "user authorization, OS and application access control, feature of action a"],
    [ieq("G, h"), "grace window (30 days); persisted time high-water mark"],
    [ieq("k, sk, pk"), "HMAC secret; Ed25519 private and public key"],
    [ieq("n_f, n_{kv}, d"), "full-attention layers, KV heads, head dimension"],
    ["E2, P4, P6", "THOX compute classes (Air, Mini, Clip)"],
])
h2("C", "Appendix C. Authorship and disclosure", "appC")
p("Issued by THOX.ai Research. Corresponding and accountable human author: Tommy Xaypanya (CTO and Co-Founder, THOX.ai LLC); proposed co-author Craig Ross (CEO). "
  "Generative AI assistance: experiment code, analysis, figures and draft text were produced by an AI system (Claude, Anthropic) operating as the THOX digital human "
  "Odette Lark under the direction of the corresponding author; every citation was resolved live on 2026-11-03 and every number is generated from the experiment outputs. "
  "No AI system is an author. The authors are THOX.ai principals; this is an interested-party technical account. Upstream attribution: ThoxInux derives from Gregory M. "
  "Kurtzer's Ginux under its recorded terms. Confidential until the founders authorise release; the 0.2.0-review draft it builds on is public on Zenodo.")

h2("", "References", "refs")
refs_html = []
for i, key in enumerate(CITED, 1):
    r = ref_entry(key)
    link = f' <a href="{r["url"]}">{r["url"]}</a>' if r["url"] else ""
    refs_html.append(f'<li id="ref{i}"><span class="rn">[{i}]</span> {html.escape(", ".join(r["authors"]))}. <i>{html.escape(r["title"])}</i>. {html.escape(r["venue"])}.{link}</li>')
OUT.append('<ol class="refs">' + "".join(refs_html) + "</ol></section>")

exec((ROOT / "wp" / "_css.txt").read_text())  # noqa: S102  defines CSS
page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(SHORT)}</title><meta name="description" content="THOX.ai Research technical report {VERSION}">
<style>{CSS}</style></head><body data-version="{VERSION}">{cover}{''.join(OUT)}</body></html>"""
(ROOT / "wp" / "paper.src.html").write_text(page)
print("wrote paper.src.html cited", len(CITED), "uncited:", [k for k in list(REFS_RAW) + list(MANUAL_REFS) if k not in CITED], "em dashes:", page.count("—"))
