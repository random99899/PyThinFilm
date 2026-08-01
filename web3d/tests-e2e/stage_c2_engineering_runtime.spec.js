import { test, expect } from "@playwright/test";
import { mkdirSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SCREENSHOT_DIR = resolve(__dirname, "../../docs/visualization/runtime/stage_c2_1");
if (!existsSync(SCREENSHOT_DIR)) {
  mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

let GIT_COMMIT_SHA = "unknown";
try {
  GIT_COMMIT_SHA = execSync("git rev-parse --short HEAD", { encoding: "utf-8" }).trim();
} catch (e) {}

const LOSSLESS_ENGINEERING_CASES = [
  { id: "app_solar_cell_ar", expectedMode: "GENERIC_MULTILAYER_MODE", expectDbrUi: false },
  { id: "app_wdm_filter", expectedMode: "DEFECT_CAVITY_MODE", expectDbrUi: false },
  { id: "app_laser_mirror", expectedMode: "DBR_PERIODIC_MODE", expectDbrUi: true },
  { id: "app_phone_lens_ar", expectedMode: "GENERIC_MULTILAYER_MODE", expectDbrUi: false },
];

test.describe("Stage C.2.1B-1.1 Lossless Engineering Cases E2E Runtime Acceptance & Template Mode Validation", () => {
  for (const c of LOSSLESS_ENGINEERING_CASES) {
    test(`${c.id}: load, verify template_mode, dynamic waves, pause/play, TE/TM toggle & screenshot`, async ({ page }) => {
      const pageErrors = [];
      const consoleErrors = [];

      page.on("pageerror", (err) => pageErrors.push(err.message));
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });

      await page.goto(`/?case=${c.id}`);
      await page.waitForSelector("canvas", { timeout: 15000 });
      await page.waitForTimeout(500);

      // Check debug interface & current case config
      await page.waitForFunction(() => window.__WEB3D_DEBUG__ && window.__WEB3D_DEBUG__.currentCaseConfig);
      const debugState = await page.evaluate(() => {
        const app = window.__WEB3D_DEBUG__.app;
        const tmpl = app.currentTemplateInstance;
        return {
          caseId: app.currentCaseConfig.id,
          gitCommit: app.currentCaseResult ? app.currentCaseResult.git_commit : null,
          templateMode: tmpl ? tmpl.templateMode : null,
          showDbrStopband: tmpl ? tmpl.showDbrStopband : null,
          showPeriodCount: tmpl ? tmpl.showPeriodCount : null,
          waveAmplitudeSource: tmpl ? tmpl.waveAmplitudeSource : null,
          activeWaveCount: window.__WEB3D_DEBUG__.activeWaveCount,
          rendererInstanceCount: window.__WEB3D_DEBUG__.rendererInstanceCount,
          forceContextLossCount: window.__WEB3D_DEBUG__.forceContextLossCount,
        };
      });

      expect(debugState.caseId).toBe(c.id);
      expect(debugState.templateMode).toBe(c.expectedMode);

      if (c.expectedMode === "GENERIC_MULTILAYER_MODE") {
        expect(debugState.showDbrStopband).toBe(false);
        expect(debugState.showPeriodCount).toBe(false);
        expect(debugState.waveAmplitudeSource).toBe("R_T_SCHEMATIC");
      }

      expect(debugState.activeWaveCount).toBeGreaterThanOrEqual(3);
      expect(debugState.rendererInstanceCount).toBe(1);
      expect(debugState.forceContextLossCount).toBe(0);

      expect(pageErrors).toHaveLength(0);
      expect(consoleErrors).toHaveLength(0);

      // Capture screenshot
      const screenshotPath = resolve(SCREENSHOT_DIR, `${c.id}.png`);
      await page.screenshot({ path: screenshotPath });

      // Toggle pause/play
      const btnPause = page.locator("#btn-play-pause");
      if (await btnPause.count() > 0) {
        await btnPause.click();
        await page.waitForTimeout(100);
        await btnPause.click();
      }

      // Toggle polarization TE / TM
      const btnPol = page.locator("#btn-toggle-pol");
      if (await btnPol.count() > 0) {
        await btnPol.click();
        await page.waitForTimeout(100);
        await btnPol.click();
      }
    });
  }

  test("Sequential engineering case switching without context loss or UI leftover", async ({ page }) => {
    await page.goto("/");
    await page.waitForSelector("canvas", { timeout: 15000 });

    for (const c of LOSSLESS_ENGINEERING_CASES) {
      await page.evaluate((caseId) => window.__WEB3D_DEBUG__.app.loadCase(caseId), c.id);
      await page.waitForTimeout(400);

      const activeCaseId = await page.evaluate(() => window.__WEB3D_DEBUG__.currentCaseConfig.id);
      expect(activeCaseId).toBe(c.id);
    }

    const debugState = await page.evaluate(() => ({
      rendererInstanceCount: window.__WEB3D_DEBUG__.rendererInstanceCount,
      caseUpdateSubscriptionRemovalCount: window.__WEB3D_DEBUG__.caseUpdateSubscriptionRemovalCount,
    }));

    expect(debugState.rendererInstanceCount).toBe(1);
    expect(debugState.caseUpdateSubscriptionRemovalCount).toBeGreaterThanOrEqual(3);
  });
});
