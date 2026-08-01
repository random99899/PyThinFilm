import { test, expect } from "@playwright/test";
import { mkdirSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SCREENSHOT_DIR = resolve(__dirname, "../../docs/visualization/runtime/stage_c2_1");
if (!existsSync(SCREENSHOT_DIR)) {
  mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const LOSSLESS_ENGINEERING_CASES = [
  { id: "app_solar_cell_ar", name: "太阳能电池三层增透膜", expectedLayers: 3 },
  { id: "app_wdm_filter", name: "WDM 光通信密集波分复用滤光片", expectedLayers: 17 },
  { id: "app_laser_mirror", name: "1064nm 激光高反镜", expectedLayers: 17 },
  { id: "app_phone_lens_ar", name: "手机镜头多层增透膜", expectedLayers: 3 },
];

test.describe("Stage C.2.1B-1 Lossless Engineering Cases E2E Runtime Acceptance", () => {
  for (const c of LOSSLESS_ENGINEERING_CASES) {
    test(`${c.id}: load, render 3D scene, pause/play, toggle polarization & capture screenshot`, async ({ page }) => {
      await page.goto(`/?case=${c.id}`);
      await page.waitForSelector("canvas", { timeout: 15000 });
      await page.waitForTimeout(500);

      // Check debug interface metrics
      await page.waitForFunction(() => window.__WEB3D_DEBUG__ && window.__WEB3D_DEBUG__.currentCaseConfig);
      const caseConfig = await page.evaluate(() => window.__WEB3D_DEBUG__.currentCaseConfig);
      expect(caseConfig.id).toBe(c.id);

      // Take screenshot of real browser runtime
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

      // Verify clean debug counters
      const debugInfo = await page.evaluate(() => ({
        rendererInstanceCount: window.__WEB3D_DEBUG__.rendererInstanceCount,
        forceContextLossCount: window.__WEB3D_DEBUG__.forceContextLossCount,
      }));
      expect(debugInfo.rendererInstanceCount).toBe(1);
      expect(debugInfo.forceContextLossCount).toBe(0);
    });
  }

  test("Sequential engineering case switching without context loss", async ({ page }) => {
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
