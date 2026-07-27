import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

export class CameraManager {
  constructor(container) {
    this.container = container;
    const aspect = container.clientWidth / container.clientHeight || 1.0;
    
    this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
    this.camera.position.set(0, 4, 12);

    this.controls = null;
  }

  initControls(rendererDomElement) {
    if (this.controls) {
      this.controls.dispose();
    }
    this.controls = new OrbitControls(this.camera, rendererDomElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.target.set(0, 0, 0);
    this.controls.update();
  }

  onResize() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    if (width > 0 && height > 0) {
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
    }
  }

  resetView() {
    this.camera.position.set(0, 4, 12);
    if (this.controls) {
      this.controls.target.set(0, 0, 0);
      this.controls.update();
    }
  }

  getCamera() {
    return this.camera;
  }

  getControls() {
    return this.controls;
  }

  dispose() {
    if (this.controls) {
      this.controls.dispose();
      this.controls = null;
    }
  }
}
