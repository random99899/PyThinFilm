import { describe, expect, it } from "vitest";
import { getMaterialAppearance } from "../src/visual/materialPalette.js";

describe("Stage C.V1A material palette", () => {
  it("keeps known material colors stable across calls", () => {
    for (const name of ["SiO2", "TiO2", "MgF2", "Si", "Ag"]) {
      expect(getMaterialAppearance(name)).toEqual(getMaterialAppearance(name));
    }
  });

  it("uses a deterministic low-saturation fallback instead of randomness", () => {
    const first = getMaterialAppearance("Unlisted-Dielectric-X");
    const second = getMaterialAppearance("Unlisted-Dielectric-X");
    const other = getMaterialAppearance("Unlisted-Dielectric-Y");
    expect(first.color).toBe(second.color);
    expect(first.color).not.toBe(other.color);
    expect(first.isFallback).toBe(true);
    expect(first.metalness).toBe(0);
  });

  it("reserves metalness for declared metals", () => {
    expect(getMaterialAppearance("SiO2").metalness).toBe(0);
    expect(getMaterialAppearance("TiO2").metalness).toBe(0);
    expect(getMaterialAppearance("Ag").metalness).toBeGreaterThan(0);
  });

  it("maps engineering H/L/C aliases to stable physical material colors", () => {
    expect(getMaterialAppearance("H").color).toBe(getMaterialAppearance("TiO2").color);
    expect(getMaterialAppearance("L").color).toBe(getMaterialAppearance("SiO2").color);
    expect(getMaterialAppearance("C").color).toBe(getMaterialAppearance("SiO2").color);
  });
});
