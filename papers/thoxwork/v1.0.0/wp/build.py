"""Build the comprehensive ThoxWork paper HTML from summary.json and the verified references.

Every number comes from exp/results/summary.json (S). Citations are [@key], numbered
by first use (wp/paperlib.py). Run:
  python3 wp/build.py && node wp/katex_render.cjs wp/paper.src.html wp/paper.html
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paperlib import (CITED, FIG, OUT, ROOT, algo, callout, cite, eq, figure, h2, h3, ieq,  # noqa: E402
                      image_grid, ol, p, ref_entry, table, ul)

S = json.loads((ROOT / "exp" / "results" / "summary.json").read_text())
VERSION = "v1.0.0"
DATE = "2026-11-04"
TITLE = "ThoxWork for the Enterprise: Governed Digital Employees, MeshGroups, Rolodex and Evidence-First Teamwork"
SHORT = "ThoxWork for the Enterprise"


def fmt(x: float, nd: int = 2) -> str:
    return f"{x:,.{nd}f}"


def pct(x: float, nd: int = 1) -> str:
    return f"{100 * x:.{nd}f}%"


# ----------------------------------------------------------------------------
# Numbers (all from summary.json)
# ----------------------------------------------------------------------------
EV = S["evidence"]; MG = S["meshgroup"]; DV = S["divergence"]; PT = S["product_tests"]; PL = S["planner"]
mat = EV["matrix"]
trials = EV["trials_per_cell"]
k1000 = EV["timing"]["n1000_keyed"]; p1000 = EV["timing"]["n1000_plain"]; k10k = EV["timing"]["n10000_keyed"]
app_k = k1000["append_us_per_record"]["median"]; ver_k = k1000["verify_us_per_record"]["median"]
app_p = p1000["append_us_per_record"]["median"]; ver_10k = k10k["verify_ms_total"]["median"]
bpr = k1000["bundle_bytes_per_record"]
mg_agree, mg_total = MG["agreement"]["agree"], MG["agreement"]["total"]
mg_js = {n: MG["timing"][f"lab_js_n{n}"]["us_per_decision"]["median"] for n in (10, 100, 1000)}
mg_py = {n: MG["timing"][f"reference_python_n{n}"]["us_per_decision"]["median"] for n in (10, 100, 1000)}
mix = MG["outcome_mix"]
dvc = DV["counts"]
dv_total = dvc["total"]
dv_ref_place = DV["reference_placements"]
dv_small = DV["reference_placements_on_too_small_node"]
dv_small_share = DV["share_of_reference_placements_on_too_small_node"]
dv_span = dvc["both_admit_pooled_needs_spanning"]
dv_site = dvc["reference_none_pooled_admits"]
pts = PT["summary"]
pl_total = PL["total"]; pl_agree = PL["agree_all"]; pl_mis = PL["mismatches"]
host = EV["host"]
HOST = f"{host['cpus']} vCPU {host['cpu_model'].strip() or host['arch']}, {host['mem_gb']} GB RAM, Linux, Node {host['node']}"

# ----------------------------------------------------------------------------
# Cover
# ----------------------------------------------------------------------------
ABSTRACT = (
    "Companies are adopting AI agents faster than they are governing them, and the open question for a buyer is no longer "
    "which model to use but which rules the work runs under. ThoxWork&trade; is THOX's third platform, the workspace where "
    "people and named Digital Employees share assignments, MeshGroups bound who may use which resources (planning is a "
    "preview today and never executes), Rolodex carries the assign, check-in and review loop, and the platform is designed so "
    "that every decision leaves a record. This comprehensive edition extends the internal THOX ThoxWork paper v1.0.0 "
    "[@thoxV1] in four ways. First, it audits the code behind the model: "
    f"{pts['repos']} THOX code bases at stated commits, {fmt(pts['rerun_passed'],0)} tests rerun for this paper with "
    f"{fmt(pts['rerun_failed'],0)} failures, and real screenshots and recordings of ThoxWork, ThoxEmployee, the Rolodex directory and "
    "validated dispatch. Second, it "
    "states the lineage honestly: the ThoxWork desktop and server shell is built on the open-source OpenWork project and the "
    "OpenCode engine, and THOX's contributions are the governance layers built on top. Third, it reconciles the record: three "
    "MeshGroup admission definitions and five assignment state machines are shown side by side with an owner, not merged. Fourth, "
    "it measures. A browser Evidence Lab re-implements the ThoxWork routing planner and agrees with the product's own "
    f"function on {fmt(pl_agree,0)} of {fmt(pl_total,0)} seeded previews; it agrees with the reference admission kit on {fmt(mg_agree,0)} of "
    f"{fmt(mg_total,0)} decisions. Comparing the two admission definitions on the same 20,000 requests, {pct(dv_small_share)} of the reference "
    "rule's placements land on a node smaller than the demand under our demand model, while the pooled rule admits "
    f"{fmt(dv_span + dv_site,0)} requests the single-node rule cannot serve. For evidence, hash links alone missed tail truncation and a "
    f"rebuilt suffix in all {trials} trials each; a session HMAC key catches the rebuild and an external head anchor catches both, at "
    f"{fmt(app_k,1)} microseconds per keyed record. Nothing here is measured on a customer deployment, and ThoxWork remains Coming Soon."
)

CONTENTS = [
    ("Executive summary", "exec"), ("1. Introduction", "intro"), ("2. Background and related work", "related"),
    ("3. System and threat model", "model"), ("4. Design", "design"), ("5. What is built", "impl"),
    ("6. The Evidence Lab", "lab"), ("7. Evaluation", "eval"), ("8. Governance mapping", "gov"),
    ("9. Discussion and limitations", "limits"), ("10. Conclusion", "concl"), ("11. Roadmap and founder decisions", "roadmap"),
    ("Appendix A. Reproducibility", "appA"), ("Appendix B. Notation", "appB"), ("Appendix C. Errata for the internal v1.0.0 paper", "appC"),
    ("Appendix D. Authorship, disclosure and publication boundary", "appD"), ("References", "refs"),
]

cover = f"""
<section class="cover">
  <div class="cover-inner">
    <div class="eyebrow"><span>THOX.ai Research &middot; Technical report, comprehensive edition {VERSION} &middot; {DATE}</span><span class="pill">Preprint, not peer reviewed</span></div>
    <h1>{TITLE}</h1>
    <p class="deck">An evidence-bounded account of THOX's third platform: what the code does today, where the records disagree, and what a browser lab and timed experiments show about the rules.</p>
    <p class="byline">THOX.ai Research &middot; Authors: Craig Ross, Chief Executive Officer, and Tommy Xaypanya, CTO and Co-Founder (corresponding author), THOX.ai LLC, Cedar Park, Texas &middot; ORCID 0009-0005-9872-3673 (Ross), 0009-0000-4425-9565 (Xaypanya)</p>
    <div class="abstract"><div class="ct">Abstract</div><p>{cite(ABSTRACT)}</p></div>
    <div class="contents"><div class="ct">Contents</div><ol>{''.join(f'<li><a href="#{a}">{t}</a></li>' for t, a in CONTENTS)}</ol></div>
    <div class="cover-foot">Your AI. Your Data. Your Rules.&trade; &middot; THOX&reg;, ThoxOS&trade;, MeshStack&trade; and ThoxWork&trade; are marks of THOX.ai LLC. OpenWork and OpenCode are the projects of their respective owners.</div>
  </div>
</section>
"""

# ----------------------------------------------------------------------------
# Executive summary
# ----------------------------------------------------------------------------
OUT.append('<section class="paper-body">')
h2("", "Executive summary", "exec")
p("THOX builds local-first AI in three platforms: ThoxOS&trade; for ownership on each device, MeshStack&trade; for private "
  "distributed capacity [@thoxMesh], and ThoxWork for the daily work of a company. ThoxWork's thesis is that an enterprise "
  "needs an operating model for AI colleagues, not another agent framework: named Digital Employees with roles and sponsors, "
  "team-scoped access through MeshGroups, an assign, check-in and review loop through Rolodex, and a record of who did what "
  "and who approved it. The THOX ThoxWork paper v1.0.0 stated that model as five invariants and checked them in a seeded "
  "simulator [@thoxV1]. This edition asks what the code does, how the records agree, and what the rules cost.")
kpis = [
    (fmt(pts["rerun_passed"], 0), f"tests passed when {pts['rerun_suites']} suites in {pts['rerun_repos']} THOX code bases were rerun for this paper ({fmt(pts['rerun_failed'],0)} failed, causes in Section 7.1)", "measured"),
    (f"{fmt(pl_agree,0)} / {fmt(pl_total,0)}", "seeded routing previews on which the Evidence Lab planner and ThoxWork's own planner agree on status, reason, selection and every per-node denial", "measured"),
    (pct(dv_small_share), f"of reference-rule placements land on a node smaller than the request, because that rule never compares demand with capacity (illustrative demand model, {fmt(dv_ref_place,0)} placements)", "measured"),
    ("0% / 100%", f"tail truncation caught by hash links alone versus with an external head anchor, {trials} seeded trials each on 1,000-record chains", "measured"),
]
OUT.append('<div class="kpis">' + "".join(f'<div class="kpi"><div class="kv">{v}</div><div class="kl">{l}</div><div class="kt">{t}</div></div>' for v, l, t in kpis) + "</div>")
callout("Product implications",
        "First, the Digital Employee stack's governance layers, in ThoxEmployee and the Digital Employee contract, are real and "
        "tested: a fail-closed action gateway, a person-only approval gate, "
        "a seven-state assignment contract, hashed handoffs, contradiction tags that never merge, and a deterministic MeshGroup "
        "planner that is deliberately preview-only; their integration into the ThoxWork shell is in development. Second, the "
        "record needs one admission rule. The paper of record states a "
        "pooled-capacity rule, the reference kit places whole requests on one node without a capacity check, and the product "
        "planner orders by locality without either; Section 4.4 shows the three side by side and Section 11 asks for a ruling. "
        "Third, evidence must be keyed and anchored. The built hashes detect accidental change, not an insider who rewrites "
        "both a record and its hash; a session key plus a head anchor held by a second party closes that gap for a few "
        "microseconds per record. Fourth, the platform credits its foundation. The ThoxWork shell is built on OpenWork and "
        "OpenCode, and their upstream license notices travel with every distribution.",
        "green")

# ----------------------------------------------------------------------------
# 1 Introduction
# ----------------------------------------------------------------------------
h2("1", "Introduction", "intro")
p("A company that lets AI agents do real work needs answers to four questions before the agents are useful: who is doing this "
  "work, what are they allowed to touch, who approved the consequential step, and how do we know afterwards. Workplace "
  "benchmarks explain why the answers cannot be left to the agents. The best agent in TheAgentCompany completes 30 percent "
  "of tasks in a simulated software company on its own [@xu2024theagentcompany]; on OSWorld the best model reaches 12.24 "
  "percent against 72.36 percent for people [@xie2024osworld]; tau-bench finds that a strong model succeeds on under half of "
  "its tasks, with pass^8 below 25 percent in retail [@yao2025taubench]. Multi-agent systems add their own failures: MAST "
  "annotated more than 1,600 traces across seven frameworks and placed inter-agent misalignment and task verification among "
  "its three failure categories [@cemri2025mast]. A platform for agent work therefore has to ship review, scoping and records "
  "as mechanisms, not as advice.")
p("ThoxWork is THOX's answer, positioned in the internal paper of record in one line: ThoxWork organizes the work, Rolodex connects "
  "you to your Digital Employee team, MeshGroups define team access, and MeshStack connects approved resources [@thoxV1]. "
  "The terms name distinct responsibilities. A <b>Digital Employee</b> (a DigitalHuman staffed into a role, offered as "
  "ThoxEmployees) is a named, role-holding synthetic colleague with a human sponsor. <b>ThoxEmployee</b> is the local "
  "employee operating layer that runs, governs and exchanges those colleagues. <b>Rolodex</b> is the team interface: assign "
  "a task, check in, review the result. A <b>MeshGroup</b> is membership with explicit actions plus the exact workspaces, "
  "pools and nodes the members may use. <b>ThoxWork</b> holds these together as shared workspaces, assignments, policy and "
  "evidence.")
p("The THOX ThoxWork paper v1.0.0 stated the model and evaluated it in a deterministic simulator, with every result labelled "
  "simulated [@thoxV1]. It deliberately left the code out of scope. A buyer, an auditor or a peer reviewer will ask the next "
  "question: does the shipped code implement the stated rules, and where it does not, which record wins? This paper answers "
  "that question with evidence gathered for it on 2026-11-04.")
p("<b>Contributions.</b>")
ol([
    f"An evidence-bounded account of the system across {pts['repos']} repositories at stated commits: architecture, lineage, "
    f"licenses and {fmt(pts['rerun_passed'],0)} tests rerun for this paper, with real product screenshots and recordings (Section 5).",
    "A reconciled model: one vocabulary that maps five assignment state machines, three MeshGroup admission definitions and "
    "three handoff and evidence mechanisms, with every disagreement shown side by side and assigned an owner (Section 4).",
    "The ThoxWork Evidence Lab, a single-file browser instrument that runs the gateway, approval, lifecycle, handoff, "
    "admission and evidence rules, captures screenshots and recordings into a hash-chained ledger, and is checked for "
    "agreement against the product's own planner code (Section 6).",
    "Measurements: planner agreement, admission-rule divergence, evidence-chain detection limits and cost, and decision "
    "latency, each from scripts released with the paper (Section 7).",
    "A governance mapping of the mechanisms to NIST AI RMF, the NIST generative AI profile, ISO/IEC 42001, the EU AI Act, "
    "OWASP and NIST zero trust guidance, stated as alignment, not conformance (Section 8).",
    "An errata register for v1.0.0 and the founder decisions the record needs (Section 11 and Appendix C).",
])

# ----------------------------------------------------------------------------
# 2 Background and related work
# ----------------------------------------------------------------------------
h2("2", "Background and related work", "related")
p("Every property in the ThoxWork model has close prior work. The contribution, if there is one, is where the properties "
  "meet, so this section names the nearest precedent for each and states the difference.")
h3("Enterprise context")
p("Adoption is ahead of governance. McKinsey's 2025 survey of 1,993 participants in 105 nations found 62 percent of "
  "organizations at least experimenting with AI agents, 23 percent scaling an agentic system in at least one function, and "
  "no more than 10 percent scaling agents in any given function [@mckinsey-soai-2025]. A 2025 survey of 353 IT "
  "professionals found 82 percent of organizations already using AI agents and 44 percent with policies in place to secure "
  "them [@sailpoint-agents-2025]. Microsoft's 2026 Work Trend Index, with 20,000 AI-using knowledge workers in ten markets, "
  "attributes about twice as much of reported AI impact to organizational factors as to individual ones, an associational "
  "result rather than a causal one [@ms-wti-2026]. MIT CISR describes digital colleagues as agents managed like employees "
  "and reports that 75 percent of 132 surveyed organizations predicted a 25 percent average rise in revenue per employee "
  "over three years [@weill-woerner-2026]. Standards bodies are moving: NIST launched an AI Agent Standards Initiative "
  "[@nist-ai-agent-standards-2026] and an NCCoE concept paper on agent identity and authorization "
  "[@nccoe-agent-idauth-2026], and the Cloud Security Alliance proposed an Agentic Trust Framework with maturity levels from "
  "Intern to Principal [@csa-atf-blog-2026; @atf-spec-v091]. The Model Context Protocol and the Agent2Agent protocol, "
  "announced by Anthropic and Google [@anthropic-mcp-2024; @google-a2a-2025], are now stewarded under the Linux Foundation "
  "[@mcp-spec-2026-07-28; @a2a-spec-v1]; they standardize agent-to-tool and agent-to-agent traffic, not the workspace where "
  "people and agents share accountable work.")
h3("2.1 Multi-agent systems and agent workplaces")
p("Role-based multi-agent frameworks established that assigning LLM agents distinct roles and passing structured work "
  "between them improves results: CAMEL's role-playing agents [@li2023camel], MetaGPT's standard operating procedures for an "
  "assembly line of roles [@hong2024metagpt], ChatDev's chat chain across a software company [@qian2024chatdev], AutoGen's "
  "conversable agents [@wu2024autogen] and AgentVerse's dynamic expert groups [@chen2024agentverse]. Generative Agents "
  "showed persistent identities with memory and reflection [@park2023generative]. Surveys organize the field "
  "[@wang2024survey; @xi2023rise; @guo2024multiagents; @tran2025collaboration]. Magentic-One coordinates specialist agents "
  "under an orchestrator [@fourney2024magenticone]. These systems run handoffs inside one autonomous session; none records "
  "each handoff as an approvable, verifiable artifact, and none scopes resources by team. In a controlled simulation of event-driven "
  "orchestration across registries of under 10, 20 to 80 and 200 agents, both tested systems scored lower at enterprise "
  "scale, the authors suggest a larger and more confusable discovery space may contribute, and a minimal task manager cut "
  "high-priority queue latency by 14 to 75 percent [@dhanyamraju2026orch], and DynaFlow learns free-form orchestration programs that make the hand-off between stages explicit "
  "[@liu2026dynaflow].")
p("Benchmarks of agents at work include TheAgentCompany [@xu2024theagentcompany], WorkArena [@drouin2024workarena], "
  "CRMArena [@huang2025crmarena], OSWorld [@xie2024osworld] and tau-bench [@yao2025taubench]. CorpGen simulates whole "
  "corporations staffed by autonomous digital employees and is the closest use of that term in the literature, as a "
  "benchmark rather than a governed product [@jaye2026corpgen].")
h3("2.2 People in the loop")
p("Magentic-UI's action guards are the closest published analogue to an approval gate, built for one user and one task "
  "[@mozannar2025magenticui]. Feng, McDonald and Zhang define five levels of agent autonomy by the user's role, one of which "
  "is approver [@feng2025levels]; Cocoa lets plan steps be assigned to the person or the agent [@feng2026cocoa]. "
  "Collaborative Gym reports that collaborative agents beat autonomous ones with real users at 86, 74 and 66 percent win "
  "rates across three tasks [@shao2026cogym]. Field evidence points the same way: in a randomized experiment that assigned 2,234 "
  "participants to human-human and human-AI teams, human-AI teams produced 50 percent more ads per worker, and their "
  "collaboration was more task-oriented and showed more delegation [@ju2025collab]; a second preregistered experiment with "
  "1,258 participants found that pairing agent and human personalities changed output quality, which bears on how named "
  "personas are presented [@ju2025personality]. The Collaborative Human-Agent Protocol (CHAP) makes the human override a "
  "structured event with a diff, a rationale and a content hash, turns a shift handoff into a portable envelope, and makes "
  "an approval a signed decision that can be replayed [@shahid2026chap]. It is the closest specification to the ThoxWork "
  "team layer; its abstract does not describe admission of work against approved resources, which is where MeshGroups "
  "differ.")
h3("2.3 Governance, regulation and security")
p("Standards converge on a named, competent person who can stop or reverse an AI system. NIST AI 100-1 asks organizations "
  "to define roles for human-AI configurations and oversight (GOVERN 3.2) and to document oversight processes (MAP 3.5) "
  "[@nist-ai-100-1]; the generative AI profile adds governance, content provenance, pre-deployment testing and incident "
  "disclosure as considerations [@nist-ai-600-1]. ISO/IEC 42001 is a management-system standard for organizations that "
  "provide or use AI [@iso-42001]. The EU AI Act requires record-keeping (Article 12), effective human oversight including "
  "the ability to override, reverse or stop (Article 14), and deployer log retention of at least six months (Article 26(6)) "
  "for high-risk systems [@eu-ai-act]; the Digital Omnibus on AI moved the high-risk application date for Chapter III "
  "Sections 1 to 3 to 2 December 2027 [@eu-ai-omnibus]. A general workspace is not high-risk by default, but Digital "
  "Employees that allocate tasks to people or evaluate their performance would bring a deployment into Annex III scope.")
p("OWASP names excessive agency (LLM06) and prompt injection (LLM01) among the top risks for LLM applications and "
  "prescribes least privilege, human approval for high-impact actions and complete mediation outside the model "
  "[@owasp-llm-2025]; its agentic guidance and 2026 top ten add tool misuse, identity and privilege abuse, and human-agent "
  "trust exploitation [@owasp-asi-threats; @owasp-asi-top10-2026]. Indirect prompt injection turns retrieved content into "
  "instructions [@greshake2023]; AgentDojo and InjecAgent measure how often agents follow them [@debenedetti2024agentdojo; "
  "@zhan2024injecagent]. In a multi-agent workspace a handoff moves content from one agent's context into another's, so the "
  "access check has to happen again at each handoff and at each group boundary. NIST zero trust guidance grants access per "
  "session with least privilege and states that authorization to one resource does not grant another [@nist-sp-800-207]; "
  "attribute-based access control supplies the policy model [@nist-sp-800-162]. South et al. extend OAuth and OpenID "
  "Connect to delegated agent credentials [@south2025authenticated], and Chan et al. argue for agent identifiers, activity "
  "logs and infrastructure for accountability [@chan2024visibility; @chan2025infrastructure].")
h3("2.4 Provenance and tamper-evident records")
p("Secure audit logs that an attacker can neither read nor undetectably modify date to Schneier and Kelsey [@SCHNEIER99]. "
  "Crosby and Wallach showed that tree-structured logs give compact membership and consistency proofs where a plain hash "
  "chain needs a linear scan [@CROSBY09]; Certificate Transparency put those proofs into production for public logs "
  "[@RFC6962; @RFC9162]. W3C PROV defines entities, activities, agents and delegation [@W3C-PROV-DM; @W3C-PROV-O]; in-toto "
  "verifies signed per-step attestations against a declared layout [@INTOTO19]; SLSA defines build provenance "
  "[@SLSA-PROV]. For agents, PROV-AGENT extends PROV to agent interactions [@souza2025provagent], Auditable Agents defines "
  "five auditability dimensions and reports 8.3 ms median overhead for mediated, tamper-evident execution [@AUDITABLE26], and "
  "a September 2026 study shows that agents can delete their own traces, so logging must sit outside the agent's control "
  "[@TRACETAMPER26]. The primitives are SHA-256 [@FIPS180-4] and HMAC [@RFC2104]. Local-first software keeps the primary copy "
  "of data with its owner [@KLEPPMANN19], which is where THOX places workspace records.")
h3("2.5 Positioning")
POS = json.loads((ROOT / "wp" / "positioning.json").read_text())
SYM = {"yes": "yes", "partial": "partial", "no": "no", "unknown": "not stated"}
keep = ["park2023generative", "hong2024metagpt", "qian2024chatdev", "wu2024autogen", "mozannar2025magenticui", "jaye2026corpgen",
        "south2025authenticated", "souza2025provagent", "AUDITABLE26"]
rows = []
for k in keep:
    r = next(x for x in POS if x["key"] == k)
    rows.append([f"{r['system']} [@{k}]", SYM[r["persistent_role_identity"]], SYM[r["human_approval_gates"]], SYM[r["ordered_handoffs_recorded"]],
                 SYM[r["team_scoped_resources"]], SYM[r["tamper_evident_evidence"]]])
rows.append(["CHAP [@shahid2026chap]", "not stated", "yes (signed decisions)", "yes (handoff envelopes)", "not stated", "partial (content hashes)"])
rows.append(["<b>ThoxWork, built today</b>", "yes (named employees with sponsors)", "yes (person-only, role-named)", "partial (per-handoff body hash)",
             "yes, preview-only (MeshGroups)", "partial (hashes detect accidental change)"])
rows.append(["<b>ThoxWork with the lab's proposals</b>", "yes", "yes", "yes (chained, keyed)", "yes", "yes (keyed chain plus external anchor)"])
table(["System", "Persistent role identity", "Human approval gate", "Recorded ordered handoffs", "Team-scoped resources", "Tamper-evident record"], rows,
      "Table 1. Positioning against the closest prior work. Entries for other systems are judged from their abstracts only (\"not stated\" means the abstract "
      "does not say, not that the system lacks it). ThoxWork rows are judged from code reviewed for this paper (Section 5).")
p("No single prior system combines the five properties, and each property alone has precedent. The defensible claims are "
  "therefore about the seams: an approval stored in the same tamper-evident record as the action it authorizes, an access "
  "check repeated at every handoff and every group boundary, and evidence written by the workspace rather than by the agent "
  "[@TRACETAMPER26].")

# ----------------------------------------------------------------------------
# 3 System and threat model
# ----------------------------------------------------------------------------
h2("3", "System and threat model", "model")
p("<b>Actors.</b> People (members, sponsors, reviewers and approvers), Digital Employees (synthetic colleagues with a role, an "
  "autonomy level and a human sponsor), the ThoxWork workspace and its server, the ThoxEmployee runtime, and the nodes and "
  "sites that serve models. A MeshGroup binds actors to workspaces, model pools and nodes.")
p("<b>Assets.</b> Workspace data at a stated data class; the authority to cause an external effect (send, write, execute, "
  "call a tool); the record of who did what and who approved it; and node capacity owned by the organization or by "
  "individual device owners.")
p("<b>Adversaries and failure sources.</b> (A1) a Digital Employee following injected instructions from retrieved content "
  "[@greshake2023]; (A2) a member or employee reaching resources bound to another group; (A3) an insider or compromised "
  "process with write access to stored records, including one that recomputes unkeyed hashes; (A4) a stale or forged node "
  "observation that makes an unavailable or unverified node look eligible; (A5) a careless or rubber-stamp approval "
  "(automation bias, Article 14(4)(b) [@eu-ai-act]); (A6) an agent that deletes or rewrites its own trace [@TRACETAMPER26]. "
  "Out of scope: compromise of the host operating system, of the person's own credentials, and of the model weights.")
p("<b>Requirements.</b> The paper evaluates the design against eight requirements.")
REQS = [
    ("R1", "Fail closed", "An action not explicitly known and permitted is denied; a tenant cannot widen a deployment ceiling."),
    ("R2", "People decide consequential steps", "An external effect waits for a person when any approval reason holds; an agent cannot approve; each request names and records the role required to decide it; a decision is final."),
    ("R3", "Legal lifecycle", "An assignment moves only along its contract's transitions; every refused move is recorded."),
    ("R4", "Team-scoped access", "A request is planned only within its MeshGroup's bindings and the member's explicit actions; cross-site and remote use need every policy level to allow it."),
    ("R5", "Admission honesty", "Work that cannot be served is refused with a reason, never silently routed elsewhere."),
    ("R6", "Recorded handoffs", "Each change of hands leaves a written handoff that a reviewer can verify."),
    ("R7", "Tamper-evident record", "Editing, reordering, deleting, truncating or rebuilding the record is detectable by a party that did not write it."),
    ("R8", "Contradictions surface", "Conflicting facts are kept and cross-tagged, never merged or dropped."),
]
table(["Id", "Requirement", "Statement"], [[a, b, c] for a, b, c in REQS], "Table 2. Requirements used in Sections 4 to 7.")

# ----------------------------------------------------------------------------
# 4 Design
# ----------------------------------------------------------------------------
h2("4", "Design: the ThoxWork model, reconciled", "design")
p("This section states the model at the level of rules. It reconciles the paper of record [@thoxV1] with the code reviewed "
  "for this edition and keeps implementation particulars (ports, hostnames, thresholds, per-role settings and persona "
  "instructions) out of scope.")
OUT.append("""<figure id="fig1"><div class="arch">
<div class="arch-row two"><div class="box hi"><b>ThoxWork</b><span>Workspaces, assignments, policy, evidence. Desktop and web shell built on OpenWork and the OpenCode engine.</span></div><div class="box hi"><b>Rolodex</b><span>Assign, check in, review. Team directory over the Digital Employee roster.</span></div></div>
<div class="arch-arrow">authority narrows downward &middot; evidence flows upward</div>
<div class="arch-row three"><div class="box"><b>Digital Employee gateway</b><span>Server-held credentials, closed route list, owner, collaborator and viewer scopes.</span></div><div class="box"><b>ThoxEmployee</b><span>Fail-closed action gateway, operator ceiling, preview digests, audit receipts, hashed handoffs, routines, contradiction tags.</span></div><div class="box"><b>Digital Employee contract v2</b><span>Assignments, seven-state lifecycle, approval records, work receipts.</span></div></div>
<div class="arch-arrow">planning is preview-only today</div>
<div class="arch-row two"><div class="box"><b>MeshGroups</b><span>Members with explicit actions plus bound workspaces, model pools and nodes; deterministic routing preview.</span></div><div class="box dim"><b>MeshStack</b><span>Private connectivity and capacity under grant-gated, lease-fenced rules, published separately.</span></div></div>
</div><figcaption><b>Figure 1.</b> ThoxWork layers as built and as published. Dashed: a separate THOX platform cited from its own paper.</figcaption></figure>""")
h3("4.1 Digital Employees and the action gateway")
p("A Digital Employee has an identity, a role, a sponsor and an autonomy level. In ThoxEmployee every gated action passes a "
  "policy gate before it can take effect, and the gate fails closed. Algorithm 1 gives the order of evaluation as built; the "
  "first rule that decides is recorded with the decision, and an allowed effect is wrapped in receipts: a running entry "
  "before it and its outcome after. A write or execute action can be previewed first; the preview yields a digest of the request and the "
  "policy in force, and an execution that presents a digest for different content is refused.")
algo("Algorithm 1 &middot; Action gateway (fail closed, as built)", [
    "gate(actor, action, payload, channel):",
    "  1. on the deployment deny list    -> DENY deployment_deny",
    "     (tenant policy cannot widen it)",
    "  2. not a known action             -> DENY unknown_action",
    "  3. on the tenant deny list        -> DENY deny_actions",
    "  4. actor not on channel roster    -> DENY channel_membership",
    "  5. payload has a secret marker    -> DENY secret_leak",
    "  6. payload over the size cap      -> DENY size_limit",
    "  7. command execution disabled,    -> DENY exec_disabled,",
    "     empty or not allowlisted            exec_empty, exec_allowlist",
    "  8. otherwise                      -> ALLOW default_allow",
    "     (running receipt before the effect, outcome after)",
])
h3("4.2 Approval gate and assignment lifecycle")
p("Work assigned to a Digital Employee is an assignment under the Digital Employee contract. Before any external effect, the "
  "assignment requires approval when any of four reasons holds (Equation 1): the caller kept the external-effect gate on, "
  "which is the default; a responsibility of the role requires a person; the data sensitivity is confidential or restricted; "
  "or the effective autonomy, the lower of employee and role autonomy, is zero.")
eq(r"\begin{aligned}\mathrm{needs\_approval}(a) \;=\;& g_a \;\lor\; \exists r \in \mathrm{resp}(a):\, h_r \\ &\lor\; \sigma_a \in \{\mathrm{conf},\, \mathrm{restr}\} \;\lor\; \min(\alpha_{e(a)}, \alpha_{\rho(a)}) = 0\end{aligned} \tag{1}")
p("Only a person can decide. Subjects that identify an employee, agent, assignment or service are refused; each request "
  "names and records the role required to decide it, which rises with sensitivity, and the Digital Humans gateway checks that "
  "role before it accepts a decision; a second decision on the same request is refused. Approval returns the assignment to running; rejection blocks it. The contract defines seven states "
  "and eighteen legal transitions (Table 3); every other move is refused before any event is emitted, and every change "
  "increments a version used for optimistic concurrency.")
LC = [["queued", "running, blocked, failed, cancelled"], ["running", "awaitingApproval, blocked, completed, failed, cancelled"],
      ["awaitingApproval", "running (approve), blocked (reject), failed, cancelled"], ["blocked", "queued, running, failed, cancelled"],
      ["completed", "terminal"], ["failed", "queued (retry)"], ["cancelled", "terminal"]]
table(["From", "Allowed to"], LC, "Table 3. Assignment lifecycle of the Digital Employee contract: 7 states, 18 legal transitions.")
p("Five state machines describe work across the THOX repositories: the contract above, a gateway review inbox, the "
  "ThoxEmployee review workspace, the ThoxEmployee kernel's task states and Migration Studio's plan-first states. Rolodex, "
  "as described in the paper of record, presents four user states and one exception [@thoxV1]. Table 4 maps them onto the "
  "contract. One disagreement matters: the contract maps rejection to blocked, while the gateway's mapping sends it to "
  "cancelled. The contract is the authority; Section 11 asks for the gateway to align.")
MAP = [["Queued", "queued", "queued", "queued"], ["In Progress", "running", "running", "busy"],
       ["In Review", "awaitingApproval", "awaiting_approval", "(no human queue; operator-replayed preview digest)"],
       ["Done", "completed", "completed", "done"], ["Changes requested (back to In Progress)", "blocked, then running", "rejected, then queued", "blocked"],
       ["Denied (terminal, at admission)", "refused at admission; no assignment created", "not modelled", "blocked (policy refusal)"]]
table(["Rolodex (paper of record)", "Contract v2", "Review workspace", "Kernel task"], MAP,
      "Table 4. One vocabulary across the assignment state machines found in the code. The gateway inbox and Migration Studio follow the same "
      "pattern with their own names.")
h3("4.3 Rolodex, ordered handoffs and validated dispatch")
p("In the paper of record, Rolodex is the loop through which a person assigns work, checks in and reviews it [@thoxV1]. In "
  "the code, the name covers three different things, and this paper keeps them apart. The <b>Rolodex directory</b> is a "
  "web app over the nine customer-facing Digital Employees: an ID card for each, a recorded introduction, chat with one "
  "employee at a time after an explicit consent to hosted processing, and a team builder whose output is a selection "
  "marked for review that grants no tools and no permissions. It has no ordered task and no handoff. <b>RolodexGo</b> is a "
  "native client for iPhone, iPad and Mac that pairs with a private server and carries the same roster. The flow that the "
  "public site describes as building a team, running an ordered task and reviewing written handoffs is the <b>ThoxEmployee "
  "guest demo</b> on thox.ai, which reuses the ThoxEmployee workspace engine.")
p("The guest demo's engine is the clearest built example of the assign, check-in and review loop. A person composes a task "
  "for a small team (the interface allows up to three employees), always with approval required. The engine runs one step per employee in order, and "
  "each step receives every earlier handoff as context. A step can only claim the next pending position, every write is "
  "fenced by a revision check, and each run and step carries an idempotency key, so a retried or duplicated step cannot "
  "double-run or skip ahead. Each step leaves a written handoff in the audit trail, the task then waits for a person, and "
  "approve or reject is a recorded decision that performs no external action. The hosted demo adds daily call limits per "
  "session, per network address and in total, and expires a guest session after 24 hours. Table 4's first column is this "
  "loop's vocabulary.")
p("Validated dispatch is the pattern THOX uses where one answer is assembled from several workers. A request passes input "
  "guardrails, is planned, executed by workers in parallel, cross-checked and synthesized, then judged by a validator in "
  "two layers: fixed rules first, which send obviously empty or refused output back for revision without a model call, and "
  "a model judge second. A pass needs both layers to agree. If the judge's verdict cannot be read, the dispatcher withholds "
  "the answer by default. If the revision budget runs out, it returns the last answer marked as not validated. The precise "
  "claim is therefore that every answer carries its verdict and an answer the validator cannot rule on is withheld, not "
  "that nothing unvalidated is ever returned.")
h3("4.4 MeshGroups: team-scoped access and three admission definitions")
p("A MeshGroup belongs to one organization and binds members to workspaces, model pools and nodes. Each member holds "
  "explicit actions in that group (planning inference, reading the workspace, proposing tool use), and membership in another "
  "group is never added in. A Digital Employee's request also requires its human sponsor to be active and to hold the same "
  "actions in the same group, so an employee can never reach further than the person accountable for it. The ThoxWork "
  "planner evaluates a routing request in two stages. First, ordered early denials stop requests from the wrong "
  "organization, from unknown or revoked principals, without the required actions, without an accountable sponsor, against "
  "an unbound workspace or pool, for an unsupported task, or from an unknown source. Second, every node bound to the group "
  "and serving the pool is classified by locality (the requester's own device, the same site, another site, or remote) and "
  "collects deny reasons: unavailable, model not ready, stale or future-dated observation, data class not permitted, "
  "cross-site or remote use not allowed by all three policy levels (organization, group and workspace), and, for non-local "
  "nodes, no mesh opt-in, no sharing consent, unverified or unencrypted transport, no ready site gateway, or relay denied. "
  "The effective data class is the stricter of the workspace's and the payload's, so a public payload cannot downgrade a "
  "restricted workspace. Eligible nodes are ordered device first, then same site, then other sites, then remote, then home "
  "site first, then by identifier, and the first is selected. Every response states that it is a preview: no execution, no "
  "authorization, no cloud fallback.")
p("Three admission definitions exist in the THOX record, and they answer different questions (Table 5). The product planner "
  "chooses by locality and policy and does not consider capacity. The THOX reference admission kit checks tenant, data "
  "classification against the group's ceiling, node health and authentication, allowed and authenticated sites, and "
  "cross-site use only when policy enables it and the request consents; it then places the whole request on the eligible "
  "node with the most free memory, ties to the earlier node, and never compares demand with that node's capacity. The paper "
  "of record states a third rule: required resources must be a subset of the group's approved set, demand above the group's "
  "pooled capacity is denied as unplaceable, demand above free capacity waits, and there is no partial placement, splitting "
  "or borrowing from another group [@thoxV1]. Pooled capacity can exceed every single node, so the third rule admits work "
  "that only a multi-node execution could serve, which the first two rules never do and which THOX does not claim: no "
  "single request has been run across two sites. Section 7.3 measures how often the rules disagree.")
table(["Question", "Product planner (ThoxWork)", "Reference kit", "Paper of record, pooled rule"], [
    ["Unit of decision", "one routing preview", "one request", "one task"],
    ["Who may ask", "member with explicit actions; employee needs an accountable sponsor", "tenant and group match", "task's group"],
    ["Data limits", "stricter of workspace and payload class; node data classes", "classification at or below group ceiling", "not specified"],
    ["Sites", "cross-site and remote only if organization, group and workspace all allow", "allowed, authenticated sites; cross-site needs policy and consent", "not specified"],
    ["Capacity", "not considered", "not compared with demand", "demand against pooled group capacity; wait if not free"],
    ["Selection", "locality, then home site, then identifier", "most free memory, then inventory order", "admit or deny; placement unspecified"],
    ["Effect", "preview only", "returns a node", "admits to run"],
], "Table 5. The three MeshGroup admission definitions on record, shown side by side rather than merged. Owner of the ruling: the CTO.")
h3("4.5 Handoffs and evidence")
p("Two evidence mechanisms are built. ThoxEmployee's audit receipts record actor, action, target, rule and outcome before and "
  "after each effect, and its security documentation states plainly that the audit table is not a tamper-proof compliance "
  "ledger. Each handoff stores the SHA-256 of its body, and accepting a handoff whose body no longer matches is refused. "
  "Because the hash lives in the same writable row as the body, this detects accidental change, not an insider who rewrites "
  "both (adversary A3). The lab adds two proposed mechanisms and measures them. A record "
  + ieq(r"r_i") + " carries a hash that commits to its content and to the previous record, and, with a session key "
  + ieq(r"k") + " held outside the store, an HMAC tag:")
eq(r"h_i = \mathrm{SHA256}\big(\mathrm{canon}(i,\, t_i,\, \kappa_i,\, a_i,\, \pi_i,\, h_{i-1})\big), \quad h_{-1} = 0^{256}, \qquad \tau_i = \mathrm{HMAC}_k(h_i) \tag{2}")
p("where " + ieq(r"t_i, \kappa_i, a_i, \pi_i") + " are the time, kind, actor and payload and canon is JSON with sorted keys. An "
  "anchor is the pair " + ieq(r"(n, h_{n-1})") + " of record count and head hash, held by a second party (another MeshGroup "
  "member, the sponsor, or a separate store). Handoffs follow the same pattern: each handoff's chained hash commits to the "
  "task, the step, the member, the brief, the body hash and the previous handoff.")
p("<b>Proposition 1 (keyed chain).</b> Let a verifier hold " + ieq("k") + ". Any edit of a record's fields, any reorder, any "
  "deletion or insertion inside the chain, and any rebuild of the suffix after an edit, made by a party without "
  + ieq("k") + ", is detected at the first affected position, except with probability bounded by forging HMAC-SHA256. "
  "<i>Sketch.</i> An edit at " + ieq("i") + " changes " + ieq("h_i") + " under second-preimage resistance; a rebuild that "
  "restores the links must produce " + ieq(r"\tau_i") + " for the new " + ieq("h_i") + " without " + ieq("k") + ".")
p("<b>Proposition 2 (truncation).</b> No check that reads only the stored chain, keyed or not, detects removal of a suffix, "
  "because every prefix of a valid chain is itself a valid chain. Detection needs state outside the chain, such as an anchor "
  + ieq(r"(n, h_{n-1})") + " held by a second party. <i>Sketch.</i> Verification of " + ieq(r"r_0 \ldots r_{m-1}") + " uses "
  "only those records and " + ieq("k") + ", and they are unchanged by deleting " + ieq(r"r_m \ldots r_{n-1}") + ".")
p("Section 7.4 confirms both propositions empirically and states the cost. The September 2026 trace-tampering result adds "
  "the deployment rule that follows from them: the workspace, not the agent, must write the record, and the anchor must sit "
  "outside the agent's reach [@TRACETAMPER26]. Tree-structured logs would add compact proofs for audits of single events "
  "[@CROSBY09; @RFC9162]; the lab keeps a linear chain because per-team logs are small and verification is cheap at that size.")
h3("4.6 Memory that keeps contradictions")
p("ThoxEmployee stores memory in seven tiers. For semantic facts it splits a statement into subject and value at the first "
  "colon, equals sign, arrow or form of the verb to be, normalizes case and spacing, and tags a new fact that collides with "
  "an earlier fact on the same subject. Both facts are kept and cross-referenced; nothing is merged or dropped (R8). The rule "
  "is lexical: a probe during review found that \"the build is green\" and \"build: red\" are not tagged because the subjects "
  "differ, a false negative stated here as a limit.")
h3("4.7 Security argument")
p("R1 and R2 answer excessive agency and tool misuse structurally: an injected instruction (A1) can at most request an "
  "action, the gateway decides outside the model, and consequential effects wait for a person "
  "[@owasp-llm-2025; @owasp-asi-top10-2026]. Once the planner authorizes, R4 would bound the blast radius of A1 and A2 to one "
  "group, re-checked at each "
  "request, consistent with zero trust's rule that access to one resource does not grant another [@nist-sp-800-207]. The "
  "sponsor rule prevents an employee from exceeding its accountable person. Stale observations (A4) are rejected by the "
  "planner. A5 is not solved by any mechanism here; the record of what the approver saw and when is the mitigation the "
  "evidence chain supports, and reviewer capacity must be planned as a resource [@thoxV1]. A3 and A6 are what the keyed, "
  "anchored chain addresses, with the limit of Proposition 2.")

# ----------------------------------------------------------------------------
# 5 What is built
# ----------------------------------------------------------------------------
h2("5", "What is built: an evidence-bounded account", "impl")
p("Three review teams read the repositories at the commits in Table 8 on 2026-11-04, started the products with local or "
  "demonstration engines only, and captured the screens and recordings used in this paper; a test harness then reran each "
  "repository's own suites, one at a time, in isolated copies, and two further teams built the planner comparison and the "
  "experiments of Section 7. Status labels follow the paper of record [@thoxV1]: <b>Built</b> means code exists and ran here; "
  "<b>Preview</b> means built and deliberately non-executing; <b>Designed</b> means specified with partial code; "
  "<b>Not built</b> means absent. Test counts are read from the suite output by the harness of Appendix A.")
PT_BY = PT["summary"]["by_repo"]


def tests_for(repo_key: str) -> str:
    r = PT_BY.get(repo_key if "/" in repo_key or repo_key.startswith("THOX") else "ttracx/" + repo_key)
    if not r:
        return "not run"
    return (f"{fmt(r['passed'],0)} passed, {fmt(r['failed'],0)} failed" + (f", {fmt(r['skipped'],0)} skipped" if r.get("skipped") else "")
            + (" (review run, not rerun)" if r.get("log") and not r.get("run") else ""))


COMPONENTS = [
    ["ThoxWork shell (desktop, web, server)", "Built, on an upstream base", "Built on the open-source OpenWork project, running the OpenCode engine [@openwork; @opencode]. THOX restyled it and added the layers below.", tests_for("thoxwork")],
    ["MeshGroups", "Preview", "Strict schema, host-only preview endpoints, deterministic planner, settings view and end-to-end browser script. Execution, grants, persistence, enrollment and multi-node execution are not built.", "within ThoxWork"],
    ["Digital Employee gateway", "Built", "Server-held credentials, closed route list, owner, collaborator and viewer scopes, pinned contract release; the app never holds backend credentials.", "within ThoxWork"],
    ["ThoxEmployee", "Built (pre-release)", "Kernel with fail-closed gate, operator ceiling, preview digests, audit receipts, hashed handoffs, routines and contradiction tags; local review workspace; Migration Studio for bringing existing bots in. Clean-room from public behavior of OpenBot, OpenMausBot and Rakazo.", tests_for("thoxemployee")],
    ["Digital Employee contract v2", "Built", "Assignment API with the seven-state lifecycle, approval records, work receipts and event streams.", tests_for("thox-digitalhumans-backend")],
    ["Digital Humans framework (Rust)", "Built", "Gateway with approval inbox and role-checked decisions, runtime and memory crates.", tests_for("thox-digitalhumans")],
    ["Digital Humans runtime (Python)", "Built", "Fleet runtime for the THOX roster, built on the open-source Hermes Agent [@hermesagent].", tests_for("thox-digital-humans")],
    ["Rolodex directory", "Built", "Nine-card directory with recorded introductions, consent-gated chat with one employee at a time, and a team selection that is marked for review and grants no tools or permissions. No ordered task or handoff.", tests_for("thox-digitalhuman-rolodex")],
    ["ThoxEmployee guest demo", "Built (hosted adapter not run here)", "Ordered team task with written handoffs, revision-fenced steps, human approve or reject, daily limits and 24-hour expiry. Captured on the ThoxEmployee workspace engine in its offline demonstration mode.", "engine within ThoxEmployee"],
    ["RolodexGo", "Built (pre-release)", "Native client for iPhone, iPad and Mac with a React Native companion; pairs with a private server. Not captured: no macOS host was reachable.", tests_for("rolodexgo")],
    ["Validated dispatch", "Built", "Guardrails, planning, parallel workers, synthesis and a two-layer validator; unreadable verdicts withheld, budget exhaustion marked not validated.", tests_for("thoxydispatch")],
    ["MeshGroup reference admission kit", "Built (reference)", "Reference admission policy with its own tests; not wired to the ThoxWork planner (Table 5).", tests_for("thox-model-factory")],
]
table(["Component", "Status", "What exists", "Tests (Table 8)"], COMPONENTS,
      "Table 6. Components reviewed for this paper, with status labels from the paper of record. Clean-room means rebuilt from public "
      "behavior without copying source.", cls="small")

# ----------------------------------------------------------------------------
# 6 The Evidence Lab
# ----------------------------------------------------------------------------
h2("6", "The ThoxWork Evidence Lab", "lab")
p("The Evidence Lab is a single HTML file that runs in any modern browser, opens offline, and also runs as a claude.ai "
  "artifact where it can keep a team log. It exists so that a buyer, auditor or reviewer can exercise the rules before any "
  "deployment exists, and so that a person running a product trial can capture evidence in one place. It never calls a "
  "model and never takes an external action; every employee output is deterministic demonstration text, and the example "
  "organization is fictional.")
table(["Bench", "What it runs", "Grounding"], [
    ["MeshGroup admission", "The reference kit rule with per-node reasons, and the paper of record's pooled rule beside it on the same request", "Agreement with the kit, Section 7.3"],
    ["Routing planner", "A clean re-implementation of the ThoxWork planner rules", "Agreement with the product function, Section 7.2"],
    ["Approvals", "Algorithm 1 gateway, the Equation 1 approval gate with role check, and the Table 3 lifecycle", "Rules read from the ThoxEmployee kernel and the v2 contract; unit tests"],
    ["Ordered handoffs", "A team runs a brief in order; body hashes as built and chained hashes as proposed; review to Done or changes requested", "Unit tests; Proposition 1"],
    ["Tamper tests", "Five of the six E1 attacks on a copy of the live ledger, checked by hash links, by the session key and by an anchor", "Experiment E1, Section 7.4"],
    ["Captures", "Screenshots, screen recordings and PDFs hashed in the browser and written into the ledger; a self-rendered snapshot of the ledger head", "SHA-256 known-answer tests on load"],
], "Table 7. Evidence Lab benches. All logic is in four dependency-free modules shared with the experiment scripts, so the page and the measurements run the same code.")
p("The ledger is a keyed chain (Equation 2). The session key is generated in the browser and never leaves the tab; an "
  "exported bundle carries hashes and tags but not the key, and an imported bundle can be checked for hash links by anyone. "
  "When the page runs as a claude.ai artifact it can save sessions to a shared team log, write a separate anchor record for "
  "each saved session, store captured files as artifact assets and offer the bundle as a download; outside that host every "
  "feature degrades to the browser alone. The page follows the THOX design tokens (#05A451 on dark; on white, the "
  "templates' text green #047C3D, because #05A451 on white falls below WCAG AA contrast for body text; Inter and JetBrains Mono), works at 390 pixels wide without horizontal scrolling in both themes, and runs SHA-256 and HMAC "
  "known-answer tests on load (FIPS 180-4 examples and RFC 4231 cases).")

# ----------------------------------------------------------------------------
# 7 Evaluation
# ----------------------------------------------------------------------------
h2("7", "Evaluation", "eval")
p(f"<b>Setup.</b> All experiments ran on one host: {HOST}. Each timed configuration had one warm-up run and 30 measured "
  "repetitions; figures report medians, with interquartile ranges where shown. Every random input comes from a seeded generator (master "
  "seed 20261104). Experiment scripts write raw JSON; one analysis script reduces it to summary.json, from which every "
  "number in this section, the figures and the lab's measured panel are generated. The questions are: does the code pass "
  "its own tests (7.1); does the lab reproduce the product planner (7.2); how do the admission definitions differ (7.3); "
  "what does an evidence chain detect and at what cost (7.4); and what do decisions cost (7.5).")
h3("7.1 Do the components pass their own tests?")
COMPONENT = {
    "ttracx/thoxwork": "ThoxWork shell and servers",
    "ttracx/thoxemployee": "ThoxEmployee runtime",
    "ttracx/thox-digitalhumans-backend": "Digital Employee contract service",
    "ttracx/thox-digitalhumans": "Digital Humans gateway (Rust)",
    "ttracx/thox-digital-humans": "Digital Humans agent runtime (Python)",
    "ttracx/thox-digitalhuman-rolodex": "Rolodex directory",
    "ttracx/thoxydispatch": "Thoxy dispatch",
    "ttracx/thox.ai": "thox.ai website",
    "ttracx/rolodexgo": "RolodexGo",
    "ttracx/thox-model-factory": "MeshGroup reference admission kit",
}
REPO_NOTES = {
    "ttracx/thoxwork": "2 failures in one server suite, tracked internally; includes tests inherited from OpenWork; hosted enterprise and live-provider suites not run",
    "ttracx/thoxemployee": "Swift kit and Docker kernel suites not run (no macOS host, no container runtime)",
    "ttracx/thox-digitalhumans-backend": "PostgreSQL integration suite not run (no disposable database); 28 skipped for the same reason",
    "ttracx/thox-digitalhumans": "Rust workspace tests; clippy with warnings as errors and rustfmt also pass",
    "ttracx/thox-digital-humans": "Parsed from the review team's run, not rerun; suite largely inherited from Hermes Agent; failures and errors concentrated in browser-automation, SSH, chat-platform and terminal tests that need components the review host lacked",
    "ttracx/thox-digitalhuman-rolodex": "1 failure, tracked internally; browser suite replaced by captures",
    "ttracx/thoxydispatch": "Backend and web suites",
    "ttracx/thox.ai": "Claim-related subset only; hosted guest-demo check needs service credentials and was not run",
    "ttracx/rolodexgo": "TypeScript and domain suites; Swift targets not compiled",
    "ttracx/thox-model-factory": "MeshGroup reference admission kit only",
}
PT_ROWS = []
for repo, r in PT_BY.items():
    if repo.startswith("THOX Evidence Lab"):
        continue
    PT_ROWS.append([COMPONENT.get(repo, repo.replace("ttracx/", "")), ", ".join(c[:7] for c in (r.get("commits") or [])), f"{r['run']} / {r['log']} / {r['not_run']}",
                    fmt(r["passed"], 0), fmt(r["failed"], 0), fmt(r["skipped"], 0) + (f" (+{r['errors']} errors)" if r.get("errors") else ""),
                    REPO_NOTES.get(repo, "")])
table(["Component", "Commit", "Suites and checks run / log / not run", "Passed", "Failed", "Skipped", "Notes"], PT_ROWS,
      f"Table 8. Product test suites on {HOST}. 'Run' suites were executed for this table; 'log' parsed the review team's run of the "
      "same commit; subset and repeat runs are excluded from the counts. Counts are read from each tool's own summary output. "
      f"Browser end-to-end assertion groups ({pts['groups_passed']} passed) and {pts['checks_run']} scripted lint, type, format and "
      "project checks (all passed) are reported separately; a contract check that does not yet gate on its output is not counted. "
      "The run column counts suites and checks that ran for this table; the Passed column counts tests from rerun suites only, "
      "except the Python agent runtime, whose counts are parsed from the log.", cls="small")
p(f"The {pts['rerun_suites']} suites rerun for this paper passed {fmt(pts['rerun_passed'],0)} tests and failed {fmt(pts['rerun_failed'],0)}, "
  f"with {fmt(pts['rerun_skipped'],0)} skipped. Two failures are in one ThoxWork server suite and the third is in the Rolodex "
  "directory; all three are tracked internally. The Python runtime's suite, parsed from the review "
  f"team's run rather than rerun, adds {fmt(pts['log_passed'],0)} passing tests, {fmt(pts['log_failed'],0)} failures and "
  f"{fmt(pts['log_errors'],0)} errors; it is largely the Hermes Agent suite the runtime inherits, so it says more about the "
  f"upstream than about THOX's additions, and it is reported, not counted, in the headline. {['No', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten'][len(pts['not_run'])] if len(pts['not_run']) <= 10 else len(pts['not_run'])} suites did not run "
  "here because they need a macOS host, a container runtime, a disposable database, hosted credentials or a live model "
  f"provider (Table 8). The Evidence Lab's own {pts['lab_tests']} unit tests pass and are excluded from the product totals.")
h3("7.2 Does the lab reproduce the ThoxWork planner?")
plm = PL["outcome_mix"]
p(f"Experiment E3 generated {fmt(PL['directories'],0)} seeded MeshGroup directories (1 to {PL['max_nodes']} nodes and up to "
  f"{PL['max_groups']} groups each) and {fmt(pl_total,0)} routing requests, mixing allowed, denied and unservable cases. Every input "
  f"passed the product's own schema. The product planner, imported from the ThoxWork source at the reviewed commit, and the "
  f"lab's clean re-implementation then answered every request. They agreed on status, reason, selected node and every "
  f"candidate's set of deny reasons for {fmt(pl_agree,0)} of {fmt(pl_total,0)} requests, and on every compared field, including "
  f"candidate order, locality, effective data class and the order of deny reasons, for {fmt(PL['agree_strict'],0)}; "
  f"{fmt(PL['candidates_agree'],0)} of {fmt(PL['candidates_compared'],0)} per-node verdicts matched. The outcome mix was "
  f"{fmt(plm['eligible_for_planning'],0)} eligible, {fmt(plm['no_eligible_node'],0)} with no eligible node and "
  f"{fmt(plm['denied'],0)} denied before candidates were listed, covering all {PL['early_denials_seen']} early denials and "
  f"all {PL['candidate_reasons_seen']} per-node deny reasons. On {fmt(PL['invalid_total'],0)} deliberately altered inputs of "
  f"{PL['invalid_kinds']} kinds, the product schema and the lab validator gave the same accept or reject verdict "
  f"{fmt(PL['invalid_agree'],0)} times. Agreement shows that the lab runs the product's rules as implemented; "
  "as limitation 3 notes, it does not show the rules are right.")
TL_KEYS = ("product_preview_us_n100", "product_parse_us_n100", "lab_plan_us_n100", "product_validate_us_g100", "lab_validate_us_g100")
if PL.get("timing") and all(PL["timing"].get(k) is not None for k in TL_KEYS):
    tl = PL["timing"]
    p(f"Planning is cheap; validation is not free. With 100 bound nodes, a full product preview took a median "
      f"{fmt(tl['product_preview_us_n100'],0)} microseconds and parsing the request schema alone {fmt(tl['product_parse_us_n100'],0)}, so "
      f"schema validation is about {round(100 * tl['product_parse_us_n100'] / tl['product_preview_us_n100']):.0f} percent of the call (at these sizes the ratio moves by a few points between runs); the lab's plan step alone took {fmt(tl['lab_plan_us_n100'],0)} "
      f"microseconds. Validating a full 100-group directory took {fmt(tl['product_validate_us_g100']/1000,1)} ms with the product schema "
      f"and {fmt(tl['lab_validate_us_g100']/1000,1)} ms with the lab's validator. These are medians of {tl['reps']} interleaved "
      "repetitions on the host of Section 7 while it was otherwise idle (one-minute load average near 1).")
h3("7.3 How do the admission definitions differ?")
p(f"<b>Agreement with the reference kit.</b> The lab's reference-rule module and THOX's reference admission kit decided "
  f"{fmt(mg_total,0)} seeded requests (200 scenarios of 50 nodes and 100 requests, with ties in free memory made common on "
  f"purpose). They agreed on {fmt(mg_agree,0)} of {fmt(mg_total,0)}, including every tie. The outcome mix was "
  f"{fmt(mix['PLACE']['count'],0)} placed, {fmt(mix['NONE']['count'],0)} admitted with no eligible node, and "
  f"{fmt(mix['DENY:classification exceeds group policy']['count'] + mix['DENY:tenant mismatch']['count'] + mix['DENY:unknown group']['count'],0)} "
  "denied before placement (Figure 2).")
figure("fig_outcomes.svg", 2, f"Outcomes of {fmt(mg_total,0)} seeded admission requests under the reference rule; the lab module and the THOX "
       "reference kit returned the same outcome for every request.")
p("<b>Divergence between the definitions.</b> The same 20,000 requests were given a seeded demand, uniform between 1 GB and "
  "1.5 times the largest free memory in each inventory, and judged by both the reference rule and the paper of record's "
  "pooled rule (request-level denials applied first, so the comparison isolates placement). Figure 3 shows the result. Of "
  f"the reference rule's {fmt(dv_ref_place,0)} placements, {fmt(dv_small,0)} ({pct(dv_small_share)}) land on a node with less "
  "free memory than the request, because the reference rule never compares the two. The pooled rule admits "
  f"{fmt(dv_span,0)} requests only by counting memory across several nodes, which no single node could serve, and it admits "
  f"{fmt(dv_site,0)} requests that the reference rule leaves with no eligible node; for "
  f"{'all ' if DV['none_vs_pooled_causes']['cross_site_only'] == dv_site else ''}{fmt(DV['none_vs_pooled_causes']['cross_site_only'],0)} of them the reference rule would place the request if cross-site use "
  "were enabled and consented, so the gap is the pooled rule's missing notion of sites: cross-site default-deny never applies. The numbers depend on the demand model and are illustrative; "
  "the direction does not: each definition admits work the others refuse.")
figure("fig_divergence.svg", 3, "How the reference rule and the paper of record's pooled rule judge the same 20,000 requests with seeded demand. "
       "Illustrative demand model stated in the text.")
h3("7.4 What does an evidence chain detect, and at what cost?")
p(f"Six attacks were applied to copies of 1,000-record chains in {trials} seeded trials each and checked four ways: hash links "
  "alone, with the session HMAC key, with an external anchor, and with both (Figure 4). Edits to a decision or an actor, "
  "swaps and deletions inside the chain were detected in every trial by every check, and in-place edits were located at the "
  f"exact record {pct(EV['edit_position_accuracy'],0)} of the time. Cutting the tail was missed by every in-band check, keyed or not, "
  "in every trial, and caught by the anchor in every trial, as Proposition 2 predicts. Editing a record and rebuilding every "
  "later hash was missed by hash links alone in every trial and caught by the key or the anchor in every trial, as "
  "Proposition 1 predicts. The built mechanisms correspond to the first column: they detect accident, not an insider.")
figure("fig_detection.svg", 4, "Detection rate by attack and check. Red cells are attacks a check never caught; green cells are attacks it always caught.")
p(f"The cost is small at team scale (Figure 5). On this host a keyed append took a median {fmt(app_k,1)} microseconds per record "
  f"and keyed verification {fmt(ver_k,1)} microseconds per record on 1,000-record chains; an unkeyed append took {fmt(app_p,1)}. "
  f"Verifying a 10,000-record keyed chain took a median {fmt(ver_10k,0)} ms. An exported bundle costs about {fmt(bpr,0)} bytes per "
  "record. These figures are for a pure JavaScript SHA-256 written for the lab so that it runs anywhere; a native or WebCrypto "
  "implementation would be faster. For comparison only, Auditable Agents reports 8.3 ms median overhead for its full "
  "pre-execution mediation on its own hardware [@AUDITABLE26]; the two numbers measure different work.")
figure("fig_chain_cost.svg", 5, "Evidence chain cost per record by chain length, hash-only and HMAC-keyed, append and verify (medians of 30 repetitions).")
h3("7.5 What do decisions cost?")
p(f"Admission decisions are cheap at the scale of a team (Figure 6). The lab module took a median {fmt(mg_js[10],2)}, "
  f"{fmt(mg_js[100],2)} and {fmt(mg_js[1000],1)} microseconds per decision for inventories of 10, 100 and 1,000 nodes, and the "
  f"THOX reference kit in Python {fmt(mg_py[10],2)}, {fmt(mg_py[100],1)} and {fmt(mg_py[1000],1)} microseconds. Cost grows "
  "with inventory size because every node is checked. Batches include early denials, which cost almost nothing, "
  "in the proportions of Figure 2.")
figure("fig_admission_latency.svg", 6, "Admission decision cost against inventory size for the lab module and the THOX reference kit (median and interquartile range of 30 repetitions of 1,000-request batches).")
h3("7.6 Product evidence captured")
p("The review teams captured the real running products, never mockups, at 1280 by 800 and 390 by 844 pixels, and recorded "
  "screen videos of complete flows. Figure 7 shows four of them. A subset reviewed against the disclosure boundary of "
  "Appendix D ships in the reproducibility package (Appendix A) with SHA-256 hashes; captures that show local ports, "
  "device registries or generated identifiers are withheld.")
SHOTS = ROOT.parent / "evidence" / "screens"
image_grid([
    (SHOTS / "teamA-meshgroups-preview-denied-1280x800.png", "ThoxWork MeshGroups: routing preview denied for a restricted workspace"),
    (SHOTS / "teamB-workspace-approval-raised-1280x800.png", "ThoxEmployee workspace: output waits for a person's review"),
    (SHOTS / "teamB-kernel-handoff-sha256-1280x800.png", "ThoxEmployee kernel: fail-closed policy and a hashed handoff"),
    (SHOTS / "teamC-rolodex-handoff-chain-1280x800.png", "ThoxEmployee guest-demo engine: ordered team handoffs before review"),
], 7, "Screens from the real running products on 2026-11-04, local and demonstration engines only. The demonstration outputs are deterministic and labelled as such by the products themselves.")

# ----------------------------------------------------------------------------
# 8 Governance mapping
# ----------------------------------------------------------------------------
h2("8", "Governance mapping", "gov")
p("Table 9 maps the mechanisms of ThoxWork and of the Digital Employee stack beneath it (ThoxEmployee, the Digital Employee "
  "contract and the Digital Humans gateway) to the oversight, record-keeping and access requirements of Section 2.3. It states "
  "alignment with the text of each document, not conformance; no audit has been performed, the NIST framework is "
  "voluntary, and whether the EU AI Act binds a deployment depends on its use.")
table(["Requirement", "Source", "Mechanism", "Status"], [
    ["Define roles for human-AI configurations and oversight", "NIST AI 100-1 GOVERN 3.2 [@nist-ai-100-1]", "Named Digital Employees with roles and accountable human sponsors; each approval request names its required role", "Built in the Digital Employee stack"],
    ["Document oversight processes", "NIST AI 100-1 MAP 3.5 [@nist-ai-100-1]", "Approval reasons, required role and decision recorded per request", "Built in the Digital Employee stack"],
    ["Content provenance", "NIST AI 600-1 [@nist-ai-600-1]", "Hashed handoffs and receipts as built; keyed, anchored chain as proposed", "Built in part (ThoxEmployee); proposed"],
    ["Automatic recording of events", "EU AI Act Art. 12 [@eu-ai-act]", "Audit receipts around each gated effect; lifecycle events per assignment", "Built in ThoxEmployee (not tamper-evident)"],
    ["Override, reverse or stop", "EU AI Act Art. 14 [@eu-ai-act]", "Person-only approval; reject blocks; cancel is terminal; previews never execute", "Built in the Digital Employee stack"],
    ["Keep logs at least six months", "EU AI Act Art. 26(6) [@eu-ai-act]", "Local-first records owned by the organization; retention policy is the deployer's", "Deployer duty"],
    ["Management system for AI", "ISO/IEC 42001 [@iso-42001]", "Evidence the system can supply to an organization's management system", "Supporting evidence only"],
    ["Excessive agency, complete mediation", "OWASP LLM06 [@owasp-llm-2025]", "Fail-closed gateway outside the model; operator ceiling; approval for effects", "Built in ThoxEmployee"],
    ["Identity and privilege abuse; task-scoped access", "OWASP Agentic Top 10 [@owasp-asi-top10-2026]", "MeshGroup actions per member; sponsor rule; group bindings", "Preview"],
    ["Least privilege per session; no transitive access", "NIST SP 800-207 [@nist-sp-800-207]", "Group-scoped planning; cross-site and remote only if all three policy levels allow", "Preview"],
], "Table 9. Mechanisms against requirements. 'Built' names where the mechanism runs today; its integration into the ThoxWork shell is in development. 'Preview' means the ThoxWork rule is implemented and tested but the planner does not yet execute or authorize.")

# ----------------------------------------------------------------------------
# 9 Discussion and limitations
# ----------------------------------------------------------------------------
h2("9", "Discussion and limitations", "limits")
ol([
    "<b>One host, no fleet.</b> Every timing in Section 7 comes from one cloud host with the stated CPU and runtime. No THOX device, "
    "no customer deployment and no multi-node run was measured, and no figure is a device benchmark.",
    "<b>Preview is not enforcement.</b> The MeshGroup planner decides but does not authorize or execute. Its agreement with the lab shows "
    "that the rules are implemented as documented, not that a deployment enforces them.",
    "<b>Agreement is not correctness.</b> The lab planner was written from the same documented rules the product implements; a rule that is "
    "wrong in both would agree. The reference-kit comparison is against a second, independent implementation, which is stronger.",
    "<b>Illustrative demand.</b> Section 7.3's divergence counts depend on a uniform demand model chosen for illustration; the qualitative "
    "result (each definition admits work the others refuse) does not.",
    "<b>Enumerated attacks only.</b> Section 7.4 tests six attack classes. Propositions 1 and 2 bound what any in-band check can do; they do "
    "not cover a compromised verifier or a stolen session key.",
    "<b>Partial test coverage.</b> Swift, Docker-based and PostgreSQL-backed suites did not run here (Table 8), and the Python runtime's "
    "suite was parsed from a review run rather than rerun. The native ThoxWork, RolodexGo and MeshStack apps for iPhone, iPad and Mac "
    "were not built or captured because no macOS host was reachable from the review environment; that capture is scheduled for the "
    "next edition.",
    "<b>Abstract-based positioning.</b> Table 1 judges other systems from their abstracts; full texts could show more than the abstracts state.",
    "<b>Interested party.</b> The authors are THOX principals and the code reviewed is THOX's own; the review teams worked from the code and "
    "reported defects, which are tracked internally and not detailed here.",
])

# ----------------------------------------------------------------------------
# 10 Conclusion
# ----------------------------------------------------------------------------
h2("10", "Conclusion", "concl")
p("ThoxWork's case does not rest on a new model or a new agent framework. It rests on rules that sit outside the model and "
  "on records that a person can check. The code reviewed for this paper implements most of those rules today: a gateway "
  "that fails closed, an approval gate that only a person can pass, a lifecycle that refuses illegal "
  "moves, a MeshGroup planner that scopes every request to a team and its sponsor, handoffs that carry their own hashes, "
  "and memory that keeps contradictions visible. The measurements add two corrections that the record needs: the admission "
  "rule must be one rule, and the evidence must be keyed and anchored to resist an insider. The Evidence Lab lets anyone "
  "exercise those rules before trusting them.")

# ----------------------------------------------------------------------------
# 11 Roadmap and founder decisions
# ----------------------------------------------------------------------------
h2("11", "Roadmap and founder decisions", "roadmap")
p("These items need a ruling from the corresponding author. Each is stated with the option this paper recommends; none is "
  "applied by this paper.")
table(["Id", "Decision", "Recommendation"], [
    ["D1", "Which MeshGroup admission definition governs (Table 5)", "One rule with three parts: the product planner's scoping and locality, the kit's classification ceiling, and a single-node capacity check; drop pooled admission until multi-node execution exists"],
    ["D2", "Upstream credit for the ThoxWork shell", "Keep the upstream license notices beside THOX's and credit OpenWork and OpenCode in every distribution (applied in the ThoxWork repository on 2026-11-04); counsel reviews third-party license terms before any release"],
    ["D3", "Evidence chain", "Adopt the keyed, anchored chain of Equation 2 for receipts and handoffs, written by the workspace, anchored with a second party"],
    ["D4", "Assignment vocabulary", "Publish Table 4 as the mapping; align the gateway's rejection to blocked, as the contract states"],
    ["D5", "Customer-facing roster", "Pick one roster and one name for the workspace assistant across products and the website"],
    ["D6", "Reviewer capacity", "Plan reviewers per MeshGroup as a resource, as the paper of record recommends [@thoxV1]"],
], "Table 10. Founder decisions.")
p("The roadmap that follows from the evidence: make MeshGroup decisions authorize and execute behind the planner, with the "
  "keyed record written at each decision; carry the sponsor rule into the Digital Employee gateway; build and capture the "
  "native iOS and macOS clients on a macOS host; and measure approval-gate latency and approval-record completeness with "
  "people in the loop, which no verified study has done for multi-agent enterprise work. ThoxWork remains Coming Soon in "
  "THOX's product copy, with no price or date stated here.")

# ----------------------------------------------------------------------------
# Appendices
# ----------------------------------------------------------------------------
h2("A", "Reproducibility", "appA")
p(f"Host: {HOST}. Python {MG['host_py']['python']}; Node {host['node']}; matplotlib, Pillow and pypdf for figures and PDF; KaTeX, "
  "@fontsource/inter and @fontsource/jetbrains-mono for rendering; Playwright with Chrome for PDF and QA. The THOX reference "
  "admission kit and the ThoxWork planner are THOX source and are not redistributed; experiments that compare against them "
  "(E2, E3) record the THOX outcomes in their result files so the comparison can be re-checked without the source.")
algo("Commands (from the package root)", [
    "node --test lab/test/*.test.js               # lab unit tests",
    "node exp/evidence_experiments.js             # E1",
    "python3 exp/meshgroup_reference.py ...       # E2 reference side (THOX internal)",
    "node exp/meshgroup_lab.js                    # E2 lab side, agreement",
    "tsx exp/planner_agreement.ts                 # E3 (THOX internal)",
    "tsx exp/planner_timing.ts                    # E4 (THOX internal)",
    "node exp/admission_divergence.js             # E5",
    "python3 exp/product_tests.py                 # product tests (THOX internal)",
    "python3 exp/analyze.py                       # writes summary.json",
    "python3 wp/figures.py && python3 wp/build.py",
    "node wp/katex_render.cjs wp/paper.src.html wp/paper.html",
    "node wp/pdf.cjs wp/paper.html wp/cover.pdf wp/body.pdf",
    "python3 wp/merge_pdf.py && python3 wp/build_lab.py",
])
p(f"Evidence Lab known-answer tests: {EV['kat']['passed']} of {EV['kat']['total']} pass (FIPS 180-4 SHA-256 examples, RFC 4231 HMAC "
  "cases 1, 2 and 6). Seeds: master seed 20261104 for E1 to E4 (E3 and E4 derive one child seed per directory or size "
  "from it) and 20261109 for the E5 demand draw. The package also contains the reviewed subset of screenshots and "
  "recordings with their SHA-256 hashes.")
h2("B", "Notation", "appB")
table(["Symbol", "Meaning"], [
    [ieq(r"g_a, h_r, \sigma_a"), "external-effect gate of assignment a, human-approval flag of responsibility r, sensitivity of a"],
    [ieq(r"\alpha_{e(a)}, \alpha_{\rho(a)}"), "autonomy level of the employee and of the role on assignment a"],
    [ieq(r"h_i, \tau_i, k"), "hash and HMAC tag of record i, session key"],
    [ieq(r"t_i, \kappa_i, a_i, \pi_i"), "time, kind, actor and payload of record i"],
    [ieq(r"(n, h_{n-1})"), "anchor: record count and head hash held by a second party"],
])
h2("C", "Errata for the internal v1.0.0 paper", "appC")
p("The paper of record [@thoxV1] was checked against live sources and the code. These items should be corrected in its next edition; "
  "none changes its simulated results.")
table(["Item in v1.0.0", "Finding", "Source checked"], [
    ["Reference [2] title", "The paper is titled \"DynaFlow: Learning Free-Form Multi-Agent Orchestration\"", "arXiv 2610.34467 [@liu2026dynaflow]"],
    ["Reference [3] title", "The paper is titled \"Collaborative Human-Agent Protocol (CHAP)\"", "arXiv 2606.09751 [@shahid2026chap]"],
    ["Reference [12] authors", "The fourth author is Mark McGranaghan", "ACM DOI 10.1145/3359591.3359737 [@KLEPPMANN19]"],
    ["All references", "Author lists are surnames only; full lists in order are required", "arXiv API, venue pages"],
    ["Ju and Aral figures", "Current version reports 2,234 participants and 11,024 ads; v1.0.0 quotes an earlier version", "arXiv 2503.18238v4 [@ju2025collab]"],
    ["Orchestration finding", "The study says a larger discovery space may contribute; v1.0.0 states that scale dominates failure", "arXiv 2606.20058 [@dhanyamraju2026orch]"],
    ["SailPoint 44 percent", "The survey reports policies to secure agents, not policies governing them", "SailPoint release [@sailpoint-agents-2025]"],
    ["Work Trend Index", "The two-to-one figure is permutation importance for self-reported impact, associational, not variance", "Microsoft WorkLab [@ms-wti-2026]"],
    ["MCP and A2A", "Both specifications are now stewarded under the Linux Foundation", "Specification sites [@mcp-spec-2026-07-28; @a2a-spec-v1]"],
    ["Pooled admission rule vs reference kit", "The kit cited as the measured implementation uses a different rule (Table 5)", "THOX reference kit, 8 of 8 tests"],
    ["Lineage", "v1.0.0 does not mention that the ThoxWork shell is built on OpenWork and OpenCode", "Repository comparison [@openwork; @opencode]"],
], "Table 11. Errata register for the THOX ThoxWork research paper v1.0.0.")
h2("D", "Authorship, disclosure and publication boundary", "appD")
p("This preprint is issued by THOX.ai Research. The named authors are Craig Ross (Chief Executive Officer) and Tommy Xaypanya "
  "(CTO and Co-Founder, corresponding and accountable author), THOX.ai LLC, matching the roster of THOX's prior research "
  "papers and THOX's shared publication author profile. Generative AI "
  "assistance: the repository review, experiments, analysis, figures, Evidence Lab and draft text were produced by an AI "
  "system (Claude, Anthropic) operating as the THOX digital human Odette Lark, with parallel review teams, under the "
  "direction of the corresponding author; every citation was resolved live against its primary page on 2026-11-04 and every "
  "number is generated from the experiment outputs. No AI system is an author. Conflicts: the authors are THOX principals; "
  "this is an interested-party technical account.")
p("<b>Disclosure boundary.</b> The paper states rules and results. It omits internal hostnames, ports, project and database "
  "identifiers, credentials, per-role autonomy settings and approver mappings, persona instructions, model-to-base mappings "
  "beyond what THOX has published, prices, dates, customer and partner identities, and security defects that are not yet "
  "fixed, which were reported to THOX internally. Lineage and license facts are stated because the licenses require "
  "attribution.")

# ----------------------------------------------------------------------------
# References
# ----------------------------------------------------------------------------
h2("", "References", "refs")
refs_html = []
for i, key in enumerate(CITED, 1):
    r = ref_entry(key)
    authors = ", ".join(r["authors"])
    link = f' <a href="{r["url"]}">{r["url"]}</a>' if r["url"] else ""
    refs_html.append(f'<li id="ref{i}"><span class="rn">[{i}]</span> {html.escape(authors)}. <i>{html.escape(r["title"])}</i>. {html.escape(r["venue"])}.{link}</li>')
OUT.append('<ol class="refs">' + "".join(refs_html) + "</ol>")
OUT.append("</section>")

CSS = (ROOT / "wp" / "paper.css").read_text()
page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(SHORT)}</title>
<meta name="description" content="THOX.ai Research technical report, comprehensive edition {VERSION}">
<meta name="author" content="THOX.ai Research; Craig Ross; Tommy Xaypanya">
<meta name="copyright" content="Copyright 2026 THOX.ai LLC. Text and figures CC BY 4.0.">
<style>{CSS}</style></head>
<body data-version="{VERSION}">
{cover}
{''.join(OUT)}
</body></html>"""

out = ROOT / "wp" / "paper.src.html"
out.write_text(page)
print("wrote", out, "cited", len(CITED), "refs")
all_keys = set(json.loads((ROOT / "wp" / "refs.json").read_text()))
for extra in ("refs_manual.json", "refs_extra.json"):
    all_keys |= set(json.loads((ROOT / "wp" / extra).read_text()))
print("uncited keys (not listed):", sorted(k for k in all_keys if k not in CITED))
print("em dashes:", page.count("\u2014"))
