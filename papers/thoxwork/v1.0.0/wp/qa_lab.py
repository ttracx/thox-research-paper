"""QA for the Evidence Lab page: 1280 and 390 px, light and dark.

Checks horizontal scroll and console errors, reads the known-answer tests, and
drives every bench (admission, approvals, lifecycle, handoffs with tamper,
tamper matrix, snapshot capture). Writes wp/qa/lab_qa.json and screenshots
wp/qa/lab-<width>-<scheme>-<bench>.png.

Usage: python3 wp/qa_lab.py [path-to-lab.html]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
LAB = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "ThoxWork_Evidence_Lab_v1.0.0.html"
QA = ROOT / "wp" / "qa"
QA.mkdir(parents=True, exist_ok=True)


def main() -> None:
    report = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for width in (1280, 390):
            for scheme in ("dark", "light"):
                ctx = browser.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme)
                page = ctx.new_page()
                errors: list[str] = []
                page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.goto(LAB.as_uri(), wait_until="load")
                page.wait_for_timeout(300)
                kat = page.evaluate("window.__labSelfTest")
                hscroll = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
                flows = {}
                page.screenshot(path=str(QA / f"lab-{width}-{scheme}-admission.png"), full_page=False)
                # Admission: open cross-site and place on the plant node.
                page.check("#aConsent"); page.check("#aPolicy"); page.click("#aRun")
                flows["admission_cross_site"] = page.text_content("#aOut")[:80]
                # Routing planner: sponsor rule, then a device-local selection.
                page.click("#tab-planner")
                page.uncheck("#rSponsor"); page.click("#rRun")
                flows["planner_sponsor"] = page.text_content("#rOut")[:40]
                page.check("#rSponsor"); page.select_option("#rDev", "hq-laptop-07"); page.click("#rRun")
                flows["planner_device"] = page.text_content("#rOut")[:40]
                page.screenshot(path=str(QA / f"lab-{width}-{scheme}-planner.png"), full_page=False)
                # Approvals: gateway ceiling, approval gate, role check, agent refusal, lifecycle.
                page.click("#tab-approvals")
                page.select_option("#gAct", "desk.exec"); page.click("#gRun")
                flows["gateway_ceiling"] = page.text_content("#gOut")[:60]
                page.select_option("#pEmp", "de:helix"); page.select_option("#pAct", "message"); page.select_option("#pSens", "confidential"); page.click("#pRun")
                flows["approval_submit"] = page.text_content("#pOut")[:90]
                page.select_option("#pApprover", "human:lead")
                page.click("#queue tr:first-child button:has-text('Approve')")
                flows["wrong_role"] = page.text_content("#pOut")[:70]
                page.click("#queue tr:first-child button:has-text('As THOXY')")
                flows["agent_approval"] = page.text_content("#pOut")[:70]
                page.select_option("#pApprover", "human:steward")
                page.click("#queue tr:first-child button:has-text('Approve')")
                flows["human_approval"] = page.text_content("#pOut")[:70]
                page.select_option("#lTo", "running"); page.click("#lRun")
                flows["lifecycle"] = page.text_content("#lOut")[:90]
                page.screenshot(path=str(QA / f"lab-{width}-{scheme}-approvals.png"), full_page=False)
                # Handoffs: run, tamper, verify.
                page.click("#tab-handoffs"); page.click("#hRun"); page.click("#hTamper"); page.click("#hVerify")
                flows["handoff_tamper"] = page.text_content("#hOut")[:60]
                page.screenshot(path=str(QA / f"lab-{width}-{scheme}-handoffs.png"), full_page=False)
                # Tamper matrix: rebuild-hashes attack.
                page.click("#tab-tamper"); page.click("#t-rechain")
                flows["tamper_rechain"] = page.text_content("#tOut")[:120]
                page.click("#t-truncate")
                flows["tamper_truncate"] = page.text_content("#tOut")[:120]
                page.screenshot(path=str(QA / f"lab-{width}-{scheme}-tamper.png"), full_page=False)
                # Snapshot capture.
                page.click("#btnSnapshot"); page.wait_for_timeout(600)
                page.click("#tab-captures")
                flows["captures"] = page.text_content("#roCaps")
                page.screenshot(path=str(QA / f"lab-{width}-{scheme}-captures.png"), full_page=False)
                page.click("#tab-measured")
                page.screenshot(path=str(QA / f"lab-{width}-{scheme}-measured.png"), full_page=True)
                page.click("#btnVerify")
                flows["verify"] = page.text_content("#roVerify")
                hscroll_end = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
                report.append({"width": width, "scheme": scheme, "kat": kat, "hscroll": hscroll or hscroll_end, "errors": errors, "flows": flows})
                ctx.close()
        browser.close()
    (QA / "lab_qa.json").write_text(json.dumps(report, indent=1))
    for r in report:
        print(r["width"], r["scheme"], "kat", r["kat"]["passed"], "/", r["kat"]["total"], "hscroll", r["hscroll"], "errors", len(r["errors"]))
        for k, v in r["flows"].items():
            print("   ", k, "|", " ".join(str(v).split()))
        for e in r["errors"][:3]:
            print("    ERR", e[:160])


if __name__ == "__main__":
    main()
