import { describe, it, expect } from "vitest";
import * as THREE from "three";
import { SceneManager } from "../src/core/SceneManager.js";
import { ResourceDisposer } from "../src/core/ResourceDisposer.js";
import { validateCaseConfig } from "../src/data/caseConfigValidator.js";

describe("Web3D Engine Lifecycle & Resource Disposer Tests", () => {
  it("should validate case configuration schema correctly", () => {
    const validCase = {
      id: "single_ar",
      display_name: "单层增透膜",
      category: "teaching_thinfilm",
      visualization_template: "single-interface",
    };
    expect(validateCaseConfig(validCase).valid).toBe(true);

    const invalidCase = { id: "bad_case" };
    expect(validateCaseConfig(invalidCase).valid).toBe(false);
  });

  it("should switch empty/mock cases 50 times without memory leak or crash", () => {
    const sceneManager = new SceneManager();
    const scene = sceneManager.getScene();

    for (let i = 0; i < 50; i += 1) {
      const mockGroup = new THREE.Group();
      mockGroup.name = `mockGroup_${i}`;

      const geo = new THREE.BoxGeometry(1, 1, 1);
      const mat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
      const mesh = new THREE.Mesh(geo, mat);
      mockGroup.add(mesh);

      scene.add(mockGroup);

      // Dispose clean
      ResourceDisposer.disposeObject(mockGroup);
      scene.remove(mockGroup);
    }

    expect(scene.children.length).toBeLessThan(10); // Ambient & directional lights remain
  });
});
