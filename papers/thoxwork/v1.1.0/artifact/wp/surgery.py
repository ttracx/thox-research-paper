#!/usr/bin/env python3
"""Merge Claude's comprehensive ThoxWork edition + Sadie's paper of record +
M1 live-core evidence into v1.1.0 source HTML (Template v1.0 design)."""
import re, sys
from pathlib import Path

W = Path('/home/hatch/workspace/thoxwork-v110')
V = Path('/home/hatch/workspace/thoxwork-publication-20261104/v110')
claude = Path('/home/hatch/workspace/user/files/THOX_ThoxWork_Enterprise_Paper_v1.0.0.html').read_text(encoding='utf-8', errors='ignore')
body = (W / 'claude_body.html').read_text(encoding='utf-8')
template = Path('/home/hatch/workspace/standards/THOX_Research_Paper_Template_v1.0/paper.src.html').read_text(encoding='utf-8')

fails = []
def rep(old, new, n=1, label=''):
    global body
    c = body.count(old)
    if c != n:
        fails.append(f"{label}: expected {n} occurrence(s), found {c} :: {old[:80]!r}")
        return
    body = body.replace(old, new)

# ---------- content edits ----------
rep('data-version="v1.0.0"', 'data-version="v1.1.0"', label='body version')
rep('Technical report, comprehensive edition v1.0.0', 'Technical report, comprehensive edition v1.1.0', label='eyebrow')

rep('This comprehensive edition extends the internal THOX ThoxWork paper v1.0.0 <span class="cite">[1]</span> in four ways. First, it audits the code behind the model: 10 THOX code bases at stated commits, 3,747 tests rerun for this paper with 3 failures,',
    'This comprehensive edition, v1.1.0, supersedes the published v1.0.1 edition of the ThoxWork paper <span class="cite">[1]</span> and extends it in five ways. First, it audits the code behind the model: 10 THOX code bases at stated commits, 3,747 tests passed when the suites were rerun for this paper, with 3 failures,',
    label='abstract opening')

rep('Nothing here is measured on a customer deployment, and ThoxWork remains Coming Soon.',
    'Fifth, it replays the protocol experiments of the paper of record against the live ThoxWork core service, the platform&#8217;s own server implementation of the model: 0 of 12,000 policy violations leaked, handoff chains were complete on all 5,000 reassigned tasks, the admission boundary held at exactly 120 of 121 resource units, no review-gate bypass succeeded in 6,000 attempts, and 50 parallel assignments admitted exactly to pooled capacity with zero over-admission, with three independent judges agreeing on all 102 workspaces (Section 7.7). Nothing here is measured on a customer deployment, and ThoxWork remains Coming Soon.',
    label='abstract fifth')

rep('<li><a href="#appC">Appendix C. Errata for the internal v1.0.0 paper</a></li>', '', label='contents appC')
rep('Appendix D. Authorship, disclosure and publication boundary</a>', 'Appendix D. Document control, authorship and publication boundary</a>', label='contents appD')

# KPI: add the live-core card after the tail-truncation card
kpi_anchor = '<div class="kt">measured</div></div></div><div class="callout green">'
new_kpi = ('<div class="kt">measured</div></div>'
           '<div class="kpi"><div class="kv">0 / 12,000</div><div class="kl">policy violations leaked when the protocol experiments were replayed against the live ThoxWork core service, the admission boundary held at exactly 120 of 121 resource units (Section 7.7)</div><div class="kt">measured</div></div>'
           '</div><div class="callout green">')
rep(kpi_anchor, new_kpi, label='kpi add')

rep('Second, the record needs one admission rule. The paper of record states a pooled-capacity rule, the reference kit places whole requests on one node without a capacity check, and the product planner orders by locality without either; Section 4.4 shows the three side by side and Section 11 asks for a ruling.',
    'Second, the record needed one admission rule, and the ruling has been made. The paper of record states a pooled-capacity rule, the reference kit places whole requests on one node without a capacity check, and the product planner orders by locality without either; Section 4.4 shows the three side by side, and the pooled rule now governs: it is implemented in the ThoxWork core service and measured against the live API in Section 7.7, with the ruling recorded in Section 11.',
    label='exec implications')

rep('positioned in the internal paper of record in one line', 'positioned in the paper of record in one line', label='intro paper of record')
rep('licenses and 3,747 tests rerun for this paper', 'licenses and 3,747 tests passed on rerun for this paper, with 3 failures', label='intro tests')
rep('An errata register for v1.0.0 and the founder decisions the record needs (Section 11 and Appendix C).',
    'The errata for v1.0.0, reconciled into the text of this edition rather than carried as a register; a replay of the paper of record&#8217;s protocol experiments against the live core service (Section 7.7); and the decisions the record needed, with the admission ruling recorded (Section 11).',
    label='intro contributions')

rep('is a native client for iPhone, iPad and Mac that pairs with a private server and carries the same roster.',
    'is a native client for iPhone, iPad and Mac that pairs with a private server and carries the same roster as a contacts client, with the Sadie Link relay for agent contact. Its Teams and Work tabs, the ordered-task surface, exist as a built, test-covered changeset that has not landed in the shipped client; the shipped client is the contacts client, and no ordered task runs in it today.',
    label='rolodexgo 4.3')

rep('Section 7.3 measures how often the rules disagree.</p>',
    'Section 7.3 measures how often the rules disagree.</p><p><b>Ruling.</b> On 2026-11-04 the corresponding author ruled that the pooled rule of the paper of record governs (decision D1, Section 11). It is the rule implemented in the ThoxWork core service, enforced server-side at task creation and at assignment, and Section 7.7 measures that enforcement against the live API. The product planner and the reference kit are to align to it. Admission under the pooled rule is a statement about the group&#8217;s pooled capacity, not about any single node: a task admitted against the pool is admitted honestly, and if dispatch later cannot place it on one node, that shortfall is a dispatch outcome, never a retroactive admission failure.</p>',
    label='ruling 4.4')

rep('Owner of the ruling: the CTO.', 'Ruled by the CTO, 2026-11-04: the pooled rule governs (Sections 7.7 and 11).', label='table5 caption')

rep('Execution, grants, persistence, enrollment and multi-node execution are not built.',
    'Execution, grants, persistence, enrollment and multi-node execution are not built in the shell. A standalone core service built after this review snapshot persists MeshGroups with their approved resources and enforces the pooled admission rule server-side (Section 7.7); multi-node execution remains not built and is not claimed.',
    label='table6 meshgroups')

rep('and also runs as a claude.ai artifact where it can keep a team log',
    'and also runs as the hosted demo on thox.ai, where it can keep a team log', label='lab host 1')
rep('When the page runs as a claude.ai artifact it can save', 'When the page runs in its hosted form it can save', label='lab host 2')
rep('store captured files as artifact assets', 'store captured files alongside the log', label='lab host 3')

# Section 7 setup: extend the questions sentence (anchor on its tail)
m = re.search(r'and what do decisions cost \(7\.5\)\.', body)
if not m:
    fails.append('eval questions anchor not found')
else:
    body = body[:m.end()] + ' Section 7.6 reports the product evidence captured, and Section 7.7 replays the protocol experiments of the paper of record <span class="cite">[1]</span> against the live ThoxWork core service, a separate implementation measured over its HTTP API; those results are reported apart from the lab results and are labelled measured.' + body[m.end():]

# ---- new Section 7.7, inserted before the Governance h2 ----
sec77 = '''<h3>7.7 The live core service: the protocol experiments, measured</h3>
<p>The paper of record <span class="cite">[1]</span> evaluated its five invariants in a deterministic, seeded simulator, with every result labelled simulated. The ThoxWork core service is the platform&#8217;s own server implementation of the same model: a Rust service with a PostgreSQL system of record, MeshGroups persisted with their approved resources, pooled capacity computed inside the admission transaction and never stored, a server-enforced Rolodex state machine whose reassignment requires a written handoff, DONE reachable only through review approval, and one append-only, hash-chained event log that the database roles may insert into but never update or delete. For this edition, the simulator&#8217;s experiment generators were ported one-to-one (same seed family, master seed 20261104, 20 replicates per experiment) and driven against the live service over its HTTP API. Three judges then recomputed every invariant independently: the platform&#8217;s separate verifier service, through its API and through its command line, and a harness-side checker written against the protocol, with both hash chains recomputed.</p>
<table class=""><caption>Table 11. The protocol experiments of the paper of record, replayed against the live ThoxWork core service. Measured. The live run supersedes the simulator as evidence for E1 to E4; E5 was not run live and remains simulated (text below).</caption><thead><tr><th>Experiment</th><th>Result against the live service</th><th>Verdict</th></tr></thead><tbody>
<tr><td>E1 Policy enforcement</td><td>12,000 violating attempts: 0 leaked in every replicate. 8,000 legitimate attempts: 0 blocked (false-block rate 0.0, bar &#8804; 0.01). Audit coverage 1.0 in every replicate.</td><td>PASS</td></tr>
<tr><td>E2 Handoff integrity</td><td>5,000 reassigned tasks: chain completeness 1.0; 15,000 entries: note coverage 1.0. 4,000 negative probes (empty or whitespace notes, non-member assignee, reassignment from review): 0 leaks. Maximum chain depth 5.</td><td>PASS</td></tr>
<tr><td>E3 Admission honesty</td><td>4,000 oversized tasks: all denied UNPLACEABLE, synchronously in the create response; 0 silently placed, 0 cross-group spills, 0 stranded. 6,000 right-sized tasks: all placed. Boundary held in every replicate: a 120-resource-unit demand admitted, 121 denied.</td><td>PASS</td></tr>
<tr><td>E4 Review gate</td><td>6,000 bypass attempts across six classes (direct finish, self-review, wrong role, non-member reviewer, stale approval, skipped review): 0 successes. 4,000 of 4,000 legitimate completions; 0 done without review over 8,000 DONE tasks; rejection integrity 1.0 over 8,000 checks. Control arm with review disabled: 4,000 of 4,000 completed without review, so the measurement discriminates.</td><td>PASS</td></tr>
<tr><td>Parallel admission</td><td>50 assignments in parallel against a pooled capacity of 120 resource units at 12 units each: exactly 10 ACCEPTED, 40 WAIT, 0 denied, 0 rejected; admitted demand exactly 120 units and stable. Zero over-admission.</td><td>PASS</td></tr>
</tbody></table>
<p><b>Judges and drills.</b> The three judges agreed on all 102 judged workspaces: every invariant true, both hash chains clean, zero disagreements. Fail-closed drills passed: with the event log&#8217;s insert permission revoked on a scratch instance, assignment returned a 503 operational error and the task was unchanged; with the database severed, assignment returned 503 and nothing was admitted. The suspension and revocation drill found the one defect of the run: suspend and revoke first returned 404 for a principal present in more than one workspace, because the handler resolved the workspace from the bare identifier (no mutation occurred; the security property itself held). The fix scopes those routes by workspace and adds a token epoch, checked inside the transition transaction, that suspend, revoke and rotation increment so outstanding credentials die immediately; the drill then passed in full, and a post-fix verifier run over 121 workspaces was clean.</p>
<p><b>What this does and does not show.</b> E3 measures admission under the pooled rule of Section 4.4, the rule the ruling in Section 11 adopts: capacity is the group&#8217;s pool, computed at decision time. Live dispatch is not part of this milestone: the core&#8217;s dispatch leg reports itself unconfigured rather than simulating success, and no multi-node execution of a single request is claimed anywhere in this paper. The fifth invariant&#8217;s scale grid (E5 in <span class="cite">[1]</span>) was not run against the live service; it remains a simulated result whose falsifiable content is non-collapse (completion 1.0 in all 16 cells), not the efficiency figure, which exceeds 1.0 only as an artifact of the simulated-latency model. Throughput posture is stated plainly in the implementation record: writes serialize through one database connection behind a lock, which is what makes the sequential semantics exact under concurrency; it is a pilot posture, not a scale posture.</p>
'''
rep('</figure><h2 id="gov">', '</figure>' + sec77 + '<h2 id="gov">', label='insert 7.7')

rep('not that a deployment enforces them.</li>',
    'not that a deployment enforces them. The planner in the ThoxWork shell remains preview-only in exactly this sense; the standalone core service, however, enforces its rules server-side, and Section 7.7 measures that enforcement against the live API.</li>',
    label='limitation 2')

rep('the admission rule must be one rule, and the evidence must be keyed and anchored to resist an insider.',
    'the admission rule is now one rule, the pooled rule, implemented in the core service and measured in Section 7.7; and the evidence must be keyed and anchored to resist an insider.',
    label='conclusion')

rep('<p>These items need a ruling from the corresponding author. Each is stated with the option this paper recommends; none is applied by this paper.</p>',
    '<p>One item has been ruled on and implemented since the review (D1). The rest are stated with the option this paper recommends; none of the rest is applied by this paper.</p>',
    label='roadmap intro')
d1_forms = [
  '<td>One rule with three parts: the product planner&#8217;s scoping and locality, the kit&#8217;s classification ceiling, and a single-node capacity check; drop pooled admission until multi-node execution exists</td>',
  '<td>One rule with three parts: the product planner\u2019s scoping and locality, the kit\u2019s classification ceiling, and a single-node capacity check; drop pooled admission until multi-node execution exists</td>',
  '<td>One rule with three parts: the product planner\'s scoping and locality, the kit\'s classification ceiling, and a single-node capacity check; drop pooled admission until multi-node execution exists</td>']
for f in d1_forms:
    if f in body:
        body = body.replace(f, '<td><b>Ruled, 2026-11-04.</b> PLACEHOLDER_D1</td>'); break
else:
    fails.append('D1 cell: no known form found')
rep('PLACEHOLDER_D1',
    'The pooled rule of the paper of record governs: pooled capacity computed over the group&#8217;s approved resources, work above the pool denied UNPLACEABLE, work above free capacity waiting, no splitting and no borrowing. It is implemented in the ThoxWork core service and measured in Section 7.7; the planner&#8217;s scoping and locality ordering and the kit&#8217;s classification ceiling carry into placement under it. Admission is a pooled statement; a later dispatch shortfall is a dispatch outcome, not an admission failure.',
    label='D1 text')
rep('make MeshGroup decisions authorize and execute behind the planner, with the keyed record written at each decision;',
    'align the shell planner and the reference kit to the pooled rule the core service already enforces, and put live dispatch behind the core&#8217;s admission, with the keyed record written at each decision;',
    label='roadmap dispatch')
rep('build and capture the native iOS and macOS clients on a macOS host;',
    'finish the native client work: land the RolodexGo ordered-task changeset described in Section 4.3 and complete the macOS-host client captures begun after this review;',
    label='roadmap clients')

# ---- Appendix C out; Appendix D rewritten ----
i = body.find('<h2 id="appC">'); j = body.find('<h2 id="appD">')
if i < 0 or j < 0 or j < i:
    fails.append('appendix C/D boundaries not found')
else:
    body = body[:i] + body[j:]
appD_new = '''<h2 id="appD"><span class="num">D</span>Document control, authorship and publication boundary</h2><p>This preprint is issued by THOX.ai Research. The named authors are Craig Ross (Chief Executive Officer) and Tommy Xaypanya (CTO and Co-Founder, corresponding and accountable author), THOX.ai LLC, matching the roster of THOX&#8217;s prior research papers and THOX&#8217;s shared publication author profile. Conflicts: the authors are THOX principals; this is an interested-party technical account.</p><p><b>Document control.</b> Comprehensive edition v1.1.0, 2026-11-04. Version DOI 10.5281/zenodo.23965052; concept DOI 10.5281/zenodo.23963935. This edition supersedes v1.0.1 (version DOI 10.5281/zenodo.23963936) as the current edition of the ThoxWork paper; v1.0.0 was the internal edition of the paper of record <span class="cite">[1]</span>. Changes in this edition: the code audit, the reconciled model, the Evidence Lab and the measurements of Sections 5 to 7 are incorporated; the errata recorded against v1.0.0 (reference titles and author lists, the Ju and Aral figures, the SailPoint and Work Trend Index readings, the orchestration finding, the stewardship of MCP and A2A, and the OpenWork and OpenCode lineage) are reconciled into the text and references of this edition rather than carried as a register; the RolodexGo account is corrected in Section 4.3 (the shipped client is the contacts client with Sadie Link; its Teams and Work changeset is built and test-covered but has not landed); decision D1 is recorded as ruled, with the pooled admission rule implemented in the core service; and Section 7.7 adds the live-service replay, measured, which no earlier edition contained. The authors&#8217; shared publication profile and consent cover this edition. Every number in this edition is generated from the experiment outputs in the accompanying reproducibility package, reduced to one summary file.</p><p><b>Disclosure boundary.</b> The paper states rules and results. It omits internal hostnames, ports, project and database identifiers, credentials, per-role autonomy settings and approver mappings, persona instructions, model-to-base mappings beyond what THOX has published, prices, dates, customer and partner identities, and security defects that are not yet fixed, which were reported to THOX internally. Lineage and license facts are stated because the licenses require attribution.</p>'''
i = body.find('<h2 id="appD">'); j = body.find('<h2 id="refs">')
if i < 0 or j < 0 or j < i:
    fails.append('appendix D/refs boundaries not found')
else:
    body = body[:i] + appD_new + body[j:]

rep('THOX.ai Research technical report v1.0.0 (internal edition), 2026-11-04.',
    'THOX.ai Research technical report v1.0.1, preprint, 2026-11-04; Zenodo DOI 10.5281/zenodo.23963936. https://doi.org/10.5281/zenodo.23963936',
    label='ref 1')

rep('are marks of THOX.ai LLC. OpenWork and OpenCode are the projects of their respective owners.',
    'are marks of THOX.ai LLC. OpenWork and OpenCode are the projects of their respective owners. This edition: version DOI 10.5281/zenodo.23965052; concept DOI 10.5281/zenodo.23963935.',
    label='cover foot DOI')

if fails:
    print("SURGERY FAILURES:")
    for f in fails: print(" -", f)
    sys.exit(1)

# ---------- style assembly ----------
style_full = claude[claude.find('<style>'):claude.find('</style>')]
fonts_katex = style_full[7:style_full.find('body{')]  # strip '<style>' prefix; fonts + katex css
# Replace his Inter/JetBrains @font-face blocks (woff2 instances that WeasyPrint
# misrenders) with the fleet TTFs used by every prior THOX paper build.
import base64 as _b64
fonts_katex = re.sub(r"@font-face\{font-family:'(?:Inter|JetBrains Mono)'[^}]*\}", '', fonts_katex)
fleet_faces = ''
for fam, path in (("Inter", "/home/hatch/.fonts/Inter.ttf"),
                  ("JetBrains Mono", "/home/hatch/.fonts/JetBrainsMono.ttf")):
    uri = 'data:font/ttf;base64,' + _b64.b64encode(Path(path).read_bytes()).decode()
    fleet_faces += f"@font-face{{font-family:'{fam}';src:url('{uri}');font-weight:100 900}}\n"
fonts_katex = fleet_faces + fonts_katex
theme = style_full[style_full.find('body{'):]
tstyle = template[template.find('<style>') + len('<style>'):template.find('</style>')]
extra = ''
for sel in ['.mtable', '.shots', '.shot', '.shot-l', '.mtight']:
    for m in re.finditer(re.escape(sel) + r'[^{]*\{[^}]*\}', theme):
        extra += m.group(0) + '\n'
style = fonts_katex + '\n' + tstyle + '\n' + extra

head = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>ThoxWork for the Enterprise: Governed Digital Employees, MeshGroups, Rolodex and Evidence-First Teamwork</title>\n'
        '<meta name="description" content="THOX.ai Research technical report, comprehensive edition v1.1.0">\n'
        '<meta name="author" content="THOX.ai Research; Craig Ross; Tommy Xaypanya">\n'
        '<meta name="copyright" content="Copyright 2026 THOX.ai LLC. Text and figures CC BY 4.0.">\n'
        '<style>\n' + style + '\n</style></head>\n')
doc = head + body + '\n</body></html>'
out = V / 'src' / 'paper.src.html'
out.write_text(doc, encoding='utf-8')
print("built src:", out, len(doc), "chars")
print("extra rules added:", extra.count('{'), "| template style:", len(tstyle), "| fonts+katex:", len(fonts_katex))
