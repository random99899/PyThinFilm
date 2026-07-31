import { describe, it, expect } from "vitest";
import { MetalDbrInterfaceTemplate } from "../src/templates/metal-dbr-interface.js";
import { readFileSync } from "fs";
import { resolve } from "path";

const PUBLIC = resolve(__dirname, "../public");

function loadJson(name) {
  const p = resolve(PUBLIC, "results", `${name}.json`);
  return JSON.parse(readFileSync(p, "utf-8"));
}

describe("Tamm Python Field Profile Binding & Fallback Tests", () => {
  it("binds Python field profile from tamm_phase_bundle.json when available", () => {
    const data = loadJson("tamm_phase_bundle");
    const template = new MetalDbrInterfaceTemplate(null);
    template.build(data, { polarization: "TE" });

    expect(template.fieldEnvelopeSource).toBe("PYTHON_FIELD_PROFILE");
    expect(template.fieldEnvelope.length).toBeGreaterThan(0);
    expect(template.fieldEnvelope.every(Number.isFinite)).toBe(true);

    // Assert overall field profile maximum is significantly greater than deep DBR tail minimum
    const maxPeak = Math.max(...template.fieldEnvelope);
    const tailValue = template.fieldEnvelope[template.fieldEnvelope.length - 1];
    expect(maxPeak).toBeGreaterThan(tailValue);
  });

  it("gracefully falls back to ANALYTIC_VISUAL_ENVELOPE when python field profile is absent", () => {
    const template = new MetalDbrInterfaceTemplate(null);
    // Passing null or JSON without field_profile_candidate
    template.build(null, { polarization: "TM" });

    expect(template.fieldEnvelopeSource).toBe("ANALYTIC_VISUAL_ENVELOPE");
    expect(template.fieldEnvelope.length).toBeGreaterThan(0);
    expect(template.fieldEnvelope.every(Number.isFinite)).toBe(true);
  });
});
