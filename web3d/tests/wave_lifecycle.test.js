import { describe, it, expect } from "vitest";
import { SingleInterfaceTemplate } from "../src/templates/single-interface.js";
import { DefectCavityTemplate } from "../src/templates/defect-cavity.js";

describe("Wave Lifecycle Teardown & Rebuild Tests", () => {
  it("disposes wave objects completely when template dispose is called", () => {
    const t = new SingleInterfaceTemplate(null);
    t.build(null, { polarization: "TE" });

    expect(t.waveRenderer.waveCount).toBe(3);

    t.dispose();

    expect(t.waveRenderer.waveCount).toBe(0);
    expect(t.group.children.length).toBe(0);
  });

  it("handles cavity standing wave build and clean disposal in defect cavity template", () => {
    const cavityTemp = new DefectCavityTemplate(null);
    cavityTemp.build(null, { polarization: "TM" });

    // Should include incident, reflected, transmitted, forward cavity, and backward cavity waves (5 total)
    expect(cavityTemp.waveRenderer.waveCount).toBe(5);

    cavityTemp.dispose();

    expect(cavityTemp.waveRenderer.waveCount).toBe(0);
    expect(cavityTemp.group.children.length).toBe(0);
  });
});
