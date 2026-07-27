import { SceneManager } from "./core/SceneManager.js";
import { CameraManager } from "./core/CameraManager.js";
import { RendererLifecycle } from "./core/RendererLifecycle.js";
import { LayerStackBuilder } from "./core/LayerStackBuilder.js";
import { WavePathBuilder } from "./core/WavePathBuilder.js";
import { PolarizationRenderer } from "./core/PolarizationRenderer.js";
import { AnimationController } from "./core/AnimationController.js";
import { ResourceDisposer } from "./core/ResourceDisposer.js";

import { loadCaseRegistry } from "./data/registryLoader.js";
import { validateCaseConfig } from "./data/caseConfigValidator.js";

import { renderCaseSelector } from "./ui/caseSelector.js";
import { renderParameterPanel } from "./ui/parameterPanel.js";
import { renderEvidencePanel } from "./ui/evidencePanel.js";
import { renderStatusBadges } from "./ui/statusBadge.js";
import { setupErrorBoundary, showErrorModal } from "./ui/errorBoundary.js";

class App {
  constructor() {
    this.container = document.querySelector("#canvas-container");
    this.registry = null;
    this.currentCaseConfig = null;
    
    this.sceneManager = null;
    this.cameraManager = null;
    this.rendererLifecycle = null;
    this.animationController = new AnimationController();

    this.currentObjects = {
      layers: null,
      rays: null,
      polarization: null,
    };

    this.isExploded = false;
    this.currentPolarization = "TE";
  }

  async init() {
    setupErrorBoundary();

    try {
      this.registry = await loadCaseRegistry();
      this.initEngine();
      this.initUI();
      
      // Load first case by default
      if (this.registry.cases && this.registry.cases.length > 0) {
        this.loadCase(this.registry.cases[0].id);
      }
    } catch (err) {
      showErrorModal("引擎初始化失败", err.message);
    }
  }

  initEngine() {
    this.sceneManager = new SceneManager();
    this.cameraManager = new CameraManager(this.container);
    this.rendererLifecycle = new RendererLifecycle(this.container);

    this.cameraManager.initControls(this.rendererLifecycle.getDomElement());

    window.addEventListener("resize", () => {
      this.cameraManager.onResize();
      this.rendererLifecycle.onResize();
    });

    // Start Animation Render Loop
    this.rendererLifecycle.startLoop((timestamp) => {
      const controls = this.cameraManager.getControls();
      if (controls) controls.update();

      this.rendererLifecycle.getRenderer().render(
        this.sceneManager.getScene(),
        this.cameraManager.getCamera()
      );
    });
  }

  initUI() {
    const listContainer = document.querySelector("#case-list-container");
    if (listContainer && this.registry) {
      renderCaseSelector(listContainer, this.registry.cases, "", (selectedId) => {
        this.loadCase(selectedId);
      });
    }

    // Button Events
    document.querySelector("#btn-play-pause")?.addEventListener("click", () => {
      const isPlaying = this.animationController.togglePlayPause();
      console.log("Animation playing:", isPlaying);
    });

    document.querySelector("#btn-reset-view")?.addEventListener("click", () => {
      this.cameraManager.resetView();
    });

    document.querySelector("#btn-toggle-pol")?.addEventListener("click", () => {
      this.currentPolarization = this.currentPolarization === "TE" ? "TM" : "TE";
      if (this.currentObjects.polarization) {
        this.currentObjects.polarization.setPolarization(this.currentPolarization);
      }
    });

    document.querySelector("#btn-explode-layers")?.addEventListener("click", () => {
      this.isExploded = !this.isExploded;
      this.rebuildSceneObjects();
    });
  }

  loadCase(caseId) {
    const caseConfig = this.registry.cases.find((c) => c.id === caseId);
    if (!caseConfig) {
      showErrorModal("无效案例", `找不到 ID 为 ${caseId} 的案例配置。`);
      return;
    }

    const validation = validateCaseConfig(caseConfig);
    if (!validation.valid) {
      showErrorModal("案例配置校验失败", validation.reason);
      return;
    }

    // Clean dispose previous objects
    this.disposeCurrentObjects();

    this.currentCaseConfig = caseConfig;

    // Update UI Panels
    renderParameterPanel(document.querySelector("#parameter-panel"), caseConfig);
    renderEvidencePanel(document.querySelector("#evidence-panel"), caseConfig);
    renderStatusBadges(document.querySelector("#status-badge-container"), caseConfig);

    const listContainer = document.querySelector("#case-list-container");
    if (listContainer) {
      renderCaseSelector(listContainer, this.registry.cases, caseId, (id) => this.loadCase(id));
    }

    // Build 3D Scene Objects
    this.rebuildSceneObjects();
  }

  disposeCurrentObjects() {
    const scene = this.sceneManager.getScene();
    Object.keys(this.currentObjects).forEach((key) => {
      if (this.currentObjects[key]) {
        const obj = this.currentObjects[key].group || this.currentObjects[key];
        ResourceDisposer.disposeObject(obj);
        scene.remove(obj);
        this.currentObjects[key] = null;
      }
    });
  }

  rebuildSceneObjects() {
    this.disposeCurrentObjects();

    if (!this.currentCaseConfig) return;

    const scene = this.sceneManager.getScene();

    // 1. Build Layers
    const mockLayers = [
      { material: "Air", thickness_nm: 0 },
      { material: "SiO2", thickness_nm: 120 },
      { material: "TiO2", thickness_nm: 80 },
      { material: "Glass", thickness_nm: 500 },
    ];
    const layerBuilder = new LayerStackBuilder();
    const layersMesh = layerBuilder.buildStack(mockLayers, this.isExploded);
    scene.add(layersMesh);
    this.currentObjects.layers = layersMesh;

    // 2. Build Rays
    const waveBuilder = new WavePathBuilder();
    const raysMesh = waveBuilder.buildRays(45);
    scene.add(raysMesh);
    this.currentObjects.rays = raysMesh;

    // 3. Build Polarization Vector
    const polRenderer = new PolarizationRenderer();
    polRenderer.setPolarization(this.currentPolarization);
    const polMesh = polRenderer.getGroup();
    scene.add(polMesh);
    this.currentObjects.polarization = polRenderer;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const app = new App();
  app.init();
});
