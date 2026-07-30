import { describe, it, expect } from "vitest";
import { SineWaveRenderer } from "../src/core/SineWaveRenderer.js";

describe("Polarization Geometry Direction Tests", () => {
  it("TE polarization oscillates strictly along Z axis (out of plane)", () => {
    const waveRenderer = new SineWaveRenderer();
    waveRenderer.build([
      {
        id: "te_wave",
        start: [0, 5, 0],
        end: [0, 0, 0],
        amplitude: 0.5,
        wavelength: 1.0,
        speed: 1.0,
        travelDir: 1,
        pol: "TE",
        color: 0xef4444,
      },
    ]);

    waveRenderer.update(0.25); // t = 0.25s -> sin(phase) != 0
    const line = waveRenderer.getGroup().children[0];
    const posAttr = line.geometry.attributes.position;

    let hasNonZeroZ = false;
    let hasXDisplacement = false;

    for (let i = 0; i < posAttr.count; i++) {
      if (Math.abs(posAttr.getZ(i)) > 0.001) hasNonZeroZ = true;
      if (Math.abs(posAttr.getX(i)) > 0.001) hasXDisplacement = true;
    }

    expect(hasNonZeroZ).toBe(true);
    expect(hasXDisplacement).toBe(false); // Ray is along Y (x=0), TE displacement must be purely along Z
  });

  it("TM polarization oscillates within XY plane (perpendicular to propagation ray)", () => {
    const waveRenderer = new SineWaveRenderer();
    // Propagation along Y axis: (0,5,0) -> (0,0,0)
    // Perpendicular direction in XY plane is X axis
    waveRenderer.build([
      {
        id: "tm_wave",
        start: [0, 5, 0],
        end: [0, 0, 0],
        amplitude: 0.5,
        wavelength: 1.0,
        speed: 1.0,
        travelDir: 1,
        pol: "TM",
        color: 0xec4899,
      },
    ]);

    waveRenderer.update(0.25);
    const line = waveRenderer.getGroup().children[0];
    const posAttr = line.geometry.attributes.position;

    let hasNonZeroX = false;
    let hasZDisplacement = false;

    for (let i = 0; i < posAttr.count; i++) {
      if (Math.abs(posAttr.getX(i)) > 0.001) hasNonZeroX = true;
      if (Math.abs(posAttr.getZ(i)) > 0.001) hasZDisplacement = true;
    }

    expect(hasNonZeroX).toBe(true);
    expect(hasZDisplacement).toBe(false); // TM displacement must be in XY plane (Z=0)
  });
});
