const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

const outputDir = path.resolve("output", "rapport", "screenshots");
fs.mkdirSync(outputDir, { recursive: true });

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 920 }, deviceScaleFactor: 1 });
  await page.goto("http://127.0.0.1:8019/app/", { waitUntil: "networkidle" });
  await page.evaluate(() => {
    localStorage.setItem("gedJwtToken", "report-demo-token");
    localStorage.setItem("gedUserName", "Administrateur GED");
    localStorage.setItem("gedUserRole", "Administrateur");
  });
  await page.reload({ waitUntil: "networkidle" });
  await page.screenshot({ path: path.join(outputDir, "01-dashboard.png"), fullPage: true });

  await page.getByRole("button", { name: "Documents", exact: true }).click();
  await page.waitForTimeout(250);
  await page.screenshot({ path: path.join(outputDir, "02-bibliotheque.png"), fullPage: true });

  await page.getByRole("button", { name: "Recherche", exact: true }).click();
  await page.getByRole("button", { name: "Aquaculture" }).click();
  await page.waitForTimeout(300);
  await page.getByRole("button", { name: "Consulter l'apercu" }).first().click();
  await page.screenshot({ path: path.join(outputDir, "03-recherche-apercu.png"), fullPage: true });
  await page.getByRole("button", { name: "Fermer l'apercu" }).click();

  await page.getByRole("button", { name: "Assistant IA", exact: true }).click();
  await page.screenshot({ path: path.join(outputDir, "04-assistant-ia.png"), fullPage: true });

  await page.getByRole("button", { name: "Administration", exact: true }).click();
  await page.waitForTimeout(150);
  await page.screenshot({ path: path.join(outputDir, "05-administration.png"), fullPage: true });
  await browser.close();
})();
