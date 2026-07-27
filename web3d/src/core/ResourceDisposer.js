import * as THREE from "three";

export class ResourceDisposer {
  static disposeObject(obj) {
    if (!obj) return;

    // Traverse hierarchy to dispose geometries, materials, textures
    obj.traverse((child) => {
      if (child.isMesh || child.isLine || child.isPoints) {
        if (child.geometry) {
          child.geometry.dispose();
        }
        if (child.material) {
          if (Array.isArray(child.material)) {
            child.material.forEach((mat) => this.disposeMaterial(mat));
          } else {
            this.disposeMaterial(child.material);
          }
        }
      }
    });

    if (obj.parent) {
      obj.parent.remove(obj);
    }
  }

  static disposeMaterial(mat) {
    if (!mat) return;

    // Dispose all potential texture maps
    const textureKeys = [
      "map", "alphaMap", "aoMap", "bumpMap", "displacementMap",
      "emissiveMap", "envMap", "lightMap", "metalnessMap",
      "normalMap", "roughnessMap"
    ];

    textureKeys.forEach((key) => {
      if (mat[key] && typeof mat[key].dispose === "function") {
        mat[key].dispose();
      }
    });

    mat.dispose();
  }

  static disposeScene(scene) {
    if (!scene) return;
    while (scene.children.length > 0) {
      this.disposeObject(scene.children[0]);
    }
  }
}
