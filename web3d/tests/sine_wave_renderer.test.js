import { describe, it, expect, beforeEach } from "vitest";
import { SineWaveRenderer } from "../src/core/SineWaveRenderer.js";

describe("SineWaveRenderer Unit Tests", () => {
  let waveRenderer;

  beforeEach(() => {
    waveRenderer = new SineWaveRenderer();
  });

  it("initializes empty group and wave state", () => {
    expect(waveRenderer.getGroup()).toBeDefined();
    expect(waveRenderer.waveCount).toBe(0);
  });

  it("builds wave geometries without error and sets up position attributes", () => {
    const descriptors = [
      {
        id: "test_wave_inc",
        start: [0, 4, 0],
        end: [0, 0, 0],
        amplitude: 0.2,
        wavelength: 0.8,
        speed: 2.0,
        travelDir: 1,
        pol: "TE",
        color: 0xef4444,
      },
    ];

    waveRenderer.build(descriptors);
    expect(waveRenderer.waveCount).toBe(1);

    const group = waveRenderer.getGroup();
    expect(group.children.length).toBe(1);
    const line = group.children[0];
    expect(line.geometry.attributes.position).toBeDefined();
    expect(line.geometry.attributes.position.count).toBe(100);
  });

  it("updates position BufferAttribute in-place over time", () => {
    const descriptors = [
      {
        id: "test_wave_inc",
        start: [0, 4, 0],
        end: [0, 0, 0],
        amplitude: 0.2,
        wavelength: 0.8,
        speed: 2.0,
        travelDir: 1,
        pol: "TE",
        color: 0xef4444,
      },
    ];

    waveRenderer.build(descriptors);
    const line = waveRenderer.getGroup().children[0];
    const posAttr = line.geometry.attributes.position;
    const initialZ0 = posAttr.getZ(10);

    waveRenderer.update(0.5); // 0.5s later
    const updatedZ0 = posAttr.getZ(10);

    expect(updatedZ0).not.toBe(initialZ0);
  });

  it("disposes geometries and materials cleanly without leaks", () => {
    const descriptors = [
      {
        id: "wave1",
        start: [-2, 2, 0],
        end: [0, 0, 0],
        amplitude: 0.2,
        wavelength: 0.5,
        speed: 1.0,
        pol: "TE",
        color: 0xff0000,
      },
    ];

    waveRenderer.build(descriptors);
    expect(waveRenderer.waveCount).toBe(1);

    waveRenderer.dispose();
    expect(waveRenderer.waveCount).toBe(0);
    expect(waveRenderer.getGroup().children.length).toBe(0);
  });
});
