"""Record the Evidence Lab's main flows as screen video for the paper package and the announcement.

Drives the built lab page with Playwright and system Chrome at 1280x800, pausing so a
viewer can read each result, then converts the WebM to H.264 MP4 with ffmpeg.
Output: evidence/video/lab/thoxwork-evidence-lab-tour.mp4 (and the source .webm).

Usage: python3 wp/record_lab.py
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "dist" / "ThoxWork_Evidence_Lab_v1.0.0.html"
OUTDIR = ROOT.parent / "evidence" / "video" / "lab"
OUTDIR.mkdir(parents=True, exist_ok=True)


def pause(page, ms: int = 1400) -> None:
    page.wait_for_timeout(ms)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, color_scheme="dark",
                                  record_video_dir=str(OUTDIR), record_video_size={"width": 1280, "height": 800})
        page = ctx.new_page()
        page.goto(LAB.as_uri(), wait_until="load")
        pause(page, 2200)
        # MeshGroup admission: open cross-site, compare both rules.
        page.fill("#aDemand", "70")
        page.check("#aConsent"); page.check("#aPolicy"); pause(page, 600)
        page.click("#aRun"); pause(page, 1200)
        page.locator("#aCompare").scroll_into_view_if_needed(); pause(page, 2600)
        page.evaluate("window.scrollTo(0,0)"); pause(page, 600)
        # Routing planner: the sponsor rule, then a device-local selection.
        page.click("#tab-planner"); pause(page, 1200)
        page.uncheck("#rSponsor"); page.click("#rRun"); pause(page, 600)
        page.locator("#rOut").scroll_into_view_if_needed(); pause(page, 2000)
        page.check("#rSponsor"); page.select_option("#rDev", "hq-laptop-07"); page.click("#rRun"); pause(page, 600)
        page.locator("#rOut").scroll_into_view_if_needed(); pause(page, 2400)
        page.evaluate("window.scrollTo(0,0)"); pause(page, 600)
        # Approvals: gateway ceiling, gate, wrong role, agent refusal, approval.
        page.click("#tab-approvals"); pause(page, 1200)
        page.select_option("#gAct", "desk.exec"); page.click("#gRun"); pause(page, 1600)
        page.select_option("#pEmp", "de:helix"); page.select_option("#pSens", "confidential"); page.click("#pRun"); pause(page, 1800)
        page.locator("#queue").scroll_into_view_if_needed(); pause(page, 600)
        page.select_option("#pApprover", "human:lead")
        page.click("#queue tr:first-child button:has-text('Approve')"); pause(page, 1600)
        page.click("#queue tr:first-child button:has-text('As THOXY')"); pause(page, 1600)
        page.select_option("#pApprover", "human:steward")
        page.click("#queue tr:first-child button:has-text('Approve')"); pause(page, 2000)
        page.evaluate("window.scrollTo(0,0)"); pause(page, 600)
        # Ordered handoffs with an insider edit.
        page.click("#tab-handoffs"); pause(page, 1000)
        page.click("#hRun"); pause(page, 1800)
        page.click("#hTamper"); pause(page, 1200)
        page.click("#hVerify"); pause(page, 1200)
        page.locator("#hChain .hcard.broken").scroll_into_view_if_needed(); pause(page, 2600)
        page.evaluate("window.scrollTo(0,0)"); pause(page, 600)
        # Tamper tests.
        page.click("#tab-tamper"); pause(page, 1000)
        page.click("#t-rechain"); pause(page, 2400)
        page.click("#t-truncate"); pause(page, 2400)
        # Snapshot capture and verify.
        page.click("#btnSnapshot"); pause(page, 1500)
        page.click("#tab-captures"); pause(page, 2000)
        page.click("#btnVerify"); pause(page, 1800)
        page.click("#tab-measured"); pause(page, 2600)
        video_path = page.video.path()
        ctx.close()
        browser.close()
    webm = OUTDIR / "thoxwork-evidence-lab-tour.webm"
    shutil.move(video_path, webm)
    mp4 = OUTDIR / "thoxwork-evidence-lab-tour.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(webm), "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-pix_fmt", "yuv420p", str(mp4)], check=True)
    print("wrote", mp4)


if __name__ == "__main__":
    main()
