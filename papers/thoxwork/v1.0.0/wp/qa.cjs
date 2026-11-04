// QA for the paper HTML: open at 1280 and 390 px in light and dark color schemes; record horizontal
// scroll and console errors; screenshot each. The Evidence Lab has its own QA (wp/qa_lab.py) and the
// PDF contact sheet is wp/qa_pdf.py.
// Usage: node wp/qa.cjs
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const PAPER = "file://" + path.join(ROOT, "wp", "paper.html");

(async () => {
  const browser = await chromium.launch({ executablePath: "/usr/bin/google-chrome", args: ["--no-sandbox"] });
  const report = [];
  for (const width of [1280, 390]) {
    for (const scheme of ["light", "dark"]) {
      const ctx = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: scheme, deviceScaleFactor: 1 });
      const page = await ctx.newPage();
      const errors = [];
      page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
      page.on("pageerror", (e) => errors.push(String(e)));
      await page.goto(PAPER, { waitUntil: "load" });
      await page.evaluate(() => document.fonts.ready);
      const sw = await page.evaluate(() => document.documentElement.scrollWidth);
      const cw = await page.evaluate(() => document.documentElement.clientWidth);
      const broken = await page.evaluate(() => Array.from(document.images).filter((i) => !i.complete || i.naturalWidth === 0).length);
      await page.screenshot({ path: path.join(ROOT, "wp", "qa", `paper-${width}-${scheme}.png`), fullPage: false });
      report.push({ width, scheme, scrollWidth: sw, clientWidth: cw, hscroll: sw > cw, brokenImages: broken, errors });
      await ctx.close();
    }
  }
  await browser.close();
  fs.writeFileSync(path.join(ROOT, "wp", "qa", "qa_report.json"), JSON.stringify(report, null, 2));
  for (const r of report) console.log(`paper ${r.width} ${r.scheme} hscroll=${r.hscroll} brokenImages=${r.brokenImages} errors=${r.errors.length}`);
})();
