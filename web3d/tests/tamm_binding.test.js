import { describe, it, expect } from "vitest";
import { validateCaseConfig } from "../src/data/caseConfigValidator.js";

describe("Stage B.1D: Tamm Phase Bundle Case Config & Result Binding Tests", () => {
  it("should validate tamm_phase_bundle case configuration", () => {
    const tammConfig = {
      id: "tamm_phase_bundle",
      display_name: "Tamm 界面态/拓扑反射相位",
      category: "research_extension",
      visualization_template: "metal-dbr-interface",
    };
    expect(validateCaseConfig(tammConfig).valid).toBe(true);
  });
});
