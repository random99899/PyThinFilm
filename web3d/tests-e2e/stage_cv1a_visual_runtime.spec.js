import { test, expect } from "@playwright/test";
import { mkdirSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const OUTPUT_DIR = resolve(__dirname, "../../docs/visualization/runtime/stage_cv1a");
mkdirSync(OUTPUT_DIR, { recursive: true });

async function capture(page, name) {
  await page.waitForTimeout(180);
  await page.screenshot({ path: resolve(OUTPUT_DIR, name), fullPage: true });
}

test.describe("Stage C.V1A solar AR academic visual prototype", () => {
  test("loads, changes presets, selects layers, preserves animation and renderer lifecycle", async ({ page }) => {
    const consoleErrors = [];
    const pageErrors = [];
    page.on("console", (message) => {
      if (message.type() === "error") consoleErrors.push(message.text());
    });
    page.on("pageerror", (error) => pageErrors.push(error.message));

    await page.goto("/?case=app_solar_cell_ar");
    await page.waitForSelector("canvas", { timeout: 15000 });
    await page.waitForFunction(() => window.__WEB3D_DEBUG__?.currentCaseConfig?.id === "app_solar_cell_ar");

    const initial = await page.evaluate(() => ({
      caseId: window.__WEB3D_DEBUG__.currentCaseConfig.id,
      rendererCount: window.__WEB3D_DEBUG__.rendererInstanceCount,
      waveCount: window.__WEB3D_DEBUG__.activeWaveCount,
      preset: window.__WEB3D_DEBUG__.currentCameraPreset,
      layerCount: window.__WEB3D_DEBUG__.app.currentTemplateInstance.layerMeshes.length,
      animationTime: window.__WEB3D_DEBUG__.animationState.time,
    }));
    expect(initial).toMatchObject({
      caseId: "app_solar_cell_ar",
      rendererCount: 1,
      waveCount: 3,
      preset: "ISOMETRIC_SECTION",
      layerCount: 3,
    });

    await capture(page, "solar_default.png");
    await capture(page, "solar_te.png");

    await page.locator("#btn-view-side").click();
    expect(await page.evaluate(() => window.__WEB3D_DEBUG__.currentCameraPreset)).toBe("SIDE_SECTION");
    await capture(page, "solar_side.png");

    await page.locator("#btn-view-optical").click();
    expect(await page.evaluate(() => window.__WEB3D_DEBUG__.currentCameraPreset)).toBe("OPTICAL_PATH");
    await capture(page, "solar_optical_path.png");

    await page.locator("#btn-reset-view").click();
    expect(await page.evaluate(() => window.__WEB3D_DEBUG__.currentCameraPreset)).toBe("ISOMETRIC_SECTION");
    await page.waitForTimeout(120);

    const layerPositions = await page.evaluate(() => window.__WEB3D_DEBUG__.getLayerScreenPositions());
    expect(layerPositions).toHaveLength(3);
    await page.mouse.click(layerPositions[1].x, layerPositions[1].y);
    expect(await page.evaluate(() => window.__WEB3D_DEBUG__.selectedLayerIndex)).toBe(1);
    await expect(page.locator('[data-role="selection-detail"]')).toContainText("TiO2");

    const canvasBox = await page.locator("canvas").boundingBox();
    await page.mouse.click(canvasBox.x + 8, canvasBox.y + canvasBox.height - 8);
    expect(await page.evaluate(() => window.__WEB3D_DEBUG__.selectedLayerIndex)).toBeNull();

    const beforeAnimation = await page.evaluate(() => window.__WEB3D_DEBUG__.animationState.time);
    await page.waitForTimeout(220);
    const afterAnimation = await page.evaluate(() => window.__WEB3D_DEBUG__.animationState.time);
    expect(afterAnimation).toBeGreaterThan(beforeAnimation);

    await page.locator("#btn-play-pause").click();
    const pausedAt = await page.evaluate(() => window.__WEB3D_DEBUG__.animationState.time);
    await page.waitForTimeout(180);
    const pausedAfter = await page.evaluate(() => window.__WEB3D_DEBUG__.animationState.time);
    expect(pausedAfter).toBeCloseTo(pausedAt, 5);
    await page.locator("#btn-play-pause").click();

    await page.locator("#btn-toggle-pol").click();
    await expect(page.locator('[data-role="wave-hud"]')).toContainText("TM");
    await capture(page, "solar_tm.png");

    await page.evaluate(() => window.__WEB3D_DEBUG__.app.loadCase("app_wdm_filter"));
    await page.waitForFunction(() => window.__WEB3D_DEBUG__.currentCaseConfig.id === "app_wdm_filter");
    await page.evaluate(() => window.__WEB3D_DEBUG__.app.loadCase("app_solar_cell_ar"));
    await page.waitForFunction(() => window.__WEB3D_DEBUG__.currentCaseConfig.id === "app_solar_cell_ar");
    const switched = await page.evaluate(() => ({
      rendererCount: window.__WEB3D_DEBUG__.rendererInstanceCount,
      forceContextLossCount: window.__WEB3D_DEBUG__.forceContextLossCount,
      selectedLayerIndex: window.__WEB3D_DEBUG__.selectedLayerIndex,
    }));
    expect(switched.rendererCount).toBe(1);
    expect(switched.forceContextLossCount).toBe(0);
    expect(switched.selectedLayerIndex).toBeNull();
    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
  });
});
