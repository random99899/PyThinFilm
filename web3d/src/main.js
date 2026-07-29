import { SceneManager } from "./core/SceneManager.js";
import { CameraManager } from "./core/CameraManager.js";
import { RendererLifecycle } from "./core/RendererLifecycle.js";
import { ResourceDisposer } from "./core/ResourceDisposer.js";

import { SingleInterfaceTemplate } from "./templates/single-interface.js";
import { PeriodicStackTemplate } from "./templates/periodic-stack.js";
import { DefectCavityTemplate } from "./templates/defect-cavity.js";
import { MetalDbrInterfaceTemplate } from "./templates/metal-dbr-interface.js";

import { loadCaseRegistry } from "./data/registryLoader.js";
import { validateCaseConfig } from "./data/caseConfigValidator.js";
import { loadCaseResult } from "./data/caseResultLoader.js";

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
    this.currentCaseResult = null;
    
    this.sceneManager = null;
    this.cameraManager = null;
    this.rendererLifecycle = null;

    this.currentTemplateInstance = null;
    this.currentTemplateGroup = null;

    this.isExploded = false;
    this.currentPolarization = "TE";

    this.templateMap = {
      "single-interface": SingleInterfaceTemplate,
      "periodic-stack": PeriodicStackTemplate,
      "defect-cavity": DefectCavityTemplate,
      "metal-dbr-interface": MetalDbrInterfaceTemplate,
    };
  }

  async init() {
    setupErrorBoundary();

    try {
      this.registry = await loadCaseRegistry();
      this.initEngine();
      this.initUI();
      
      // Load first case by default
      if (this.registry.cases && this.registry.cases.length > 0) {
        await this.loadCase(this.registry.cases[0].id);
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
    this.rendererLifecycle.startLoop(() => {
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
      console.log("Animation playing toggled");
    });

    document.querySelector("#btn-reset-view")?.addEventListener("click", () => {
      this.cameraManager.resetView();
    });

    document.querySelector("#btn-toggle-pol")?.addEventListener("click", () => {
      this.currentPolarization = this.currentPolarization === "TE" ? "TM" : "TE";
      this.rebuildSceneObjects();
    });

    document.querySelector("#btn-explode-layers")?.addEventListener("click", () => {
      this.isExploded = !this.isExploded;
      this.rebuildSceneObjects();
    });
  }

  async loadCase(caseId) {
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

    // Check template mapping existence
    const TemplateClass = this.templateMap[caseConfig.visualization_template];
    if (!TemplateClass) {
      showErrorModal("未接入 3D 模板", `模板 '${caseConfig.visualization_template}' 尚未接入统一 Web3D 引擎。`);
      return;
    }

    // Load case result JSON
    const resultRes = await loadCaseResult(caseId);
    if (!resultRes.available && (caseConfig.migration_status === "MIGRATION_VERIFIED" || caseConfig.migration_status === "MIGRATED")) {
      showErrorModal("数据缺失", `案例 '${caseId}' 缺失 Python 计算导出 JSON 文件 (${resultRes.reason})。`);
      return;
    }

    this.disposeCurrentObjects();

    this.currentCaseConfig = caseConfig;
    this.currentCaseResult = resultRes.data;

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
    if (this.currentTemplateInstance) {
      this.currentTemplateInstance.dispose();
      this.currentTemplateInstance = null;
    }
    if (this.currentTemplateGroup) {
      ResourceDisposer.disposeObject(this.currentTemplateGroup);
      scene.remove(this.currentTemplateGroup);
      this.currentTemplateGroup = null;
    }
  }

  rebuildSceneObjects() {
    this.disposeCurrentObjects();

    if (!this.currentCaseConfig) return;

    const TemplateClass = this.templateMap[this.currentCaseConfig.visualization_template];
    if (!TemplateClass) return;

    const scene = this.sceneManager.getScene();

    this.currentTemplateInstance = new TemplateClass(this.container);
    this.currentTemplateGroup = this.currentTemplateInstance.build(this.currentCaseResult, {
      isExploded: this.isExploded,
      polarization: this.currentPolarization,
    });

    scene.add(this.currentTemplateGroup);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const app = new App();
  app.init();
});
