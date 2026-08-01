import { describe, it, expect } from "vitest";
import { PeriodicStackTemplate } from "../src/templates/periodic-stack.js";
import { readFileSync } from "fs";
import { resolve } from "path";

const PUBLIC = resolve(__dirname, "../public");

function loadJson(name) {
  const p = resolve(PUBLIC, "results", `${name}.json`);
  return JSON.parse(readFileSync(p, "utf-8"));
}

describe("PeriodicStackTemplate GENERIC_MULTILAYER_MODE Tests", () => {
  it("enables GENERIC_MULTILAYER_MODE for app_solar_cell_ar (3 distinct materials)", () => {
    const data = loadJson("app_solar_cell_ar");
    const template = new PeriodicStackTemplate(null);
    template.build(data, { polarization: "TE" });

    expect(template.isGenericMultilayerMode).toBe(true);
  });

  it("enables GENERIC_MULTILAYER_MODE for app_phone_lens_ar (SiO2, ZrO2, MgF2)", () => {
    const data = loadJson("app_phone_lens_ar");
    const template = new PeriodicStackTemplate(null);
    template.build(data, { polarization: "TM" });

    expect(template.isGenericMultilayerMode).toBe(true);
  });

  it("remains in periodic DBR mode for high_reflector (HL alternating)", () => {
    const data = loadJson("high_reflector");
    const template = new PeriodicStackTemplate(null);
    template.build(data, { polarization: "TE" });

    expect(template.isGenericMultilayerMode).toBe(false);
  });
});
