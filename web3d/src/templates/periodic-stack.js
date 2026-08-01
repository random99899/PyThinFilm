import * as THREE from "three";
import { SineWaveRenderer } from "../core/SineWaveRenderer.js";
import { calculateWaveAmplitudesFromSpectrum } from "../core/spectrumWaveAmp.js";
import { ResourceDisposer } from "../core/ResourceDisposer.js";
import { getVisualTheme } from "../visual/visualTheme.js";
import { mapThicknessNm, THICKNESS_MAPPING } from "../visual/thicknessMapping.js";
import {
  createLayerAppearance,
  createLayerOutline,
  setLayerInteractionState,
} from "../visual/layerAppearance.js";

const MATERIAL_COLOR_MAP = {
  SiO2: 0x60a5fa,
  TiO2: 0xf59e0b,
  MgF2: 0x34d399,
  ZrO2: 0xa855f7,
  Al2O3: 0xf43f5e,
  Air: 0x93c5fd,
};

export class PeriodicStackTemplate {
  constructor(container) {
    this.container = container;
    this.group = new THREE.Group();
    this.group.name = "PeriodicStackTemplateGroup";
    this.waveRenderer = new SineWaveRenderer();
    this.group.add(this.waveRenderer.getGroup());
    
    // Explicit Mode Flags & Amplitude Source Semantics
    this.templateMode = "DBR_PERIODIC_MODE";
    this.isGenericMultilayerMode = false;
    this.showDbrStopband = true;
    this.showPeriodCount = true;
    this.showRepresentativeInternalDbrWaves = true;
    this.waveAmplitudeSource = "SELECTED_WAVELENGTH_R_T_SCHEMATIC";
    this.animationSemantics = "TEACHING_ILLUSTRATION";

    this.caseResult = null;
    this.polarization = "TE";
    this.selectedWavelengthNm = 550;
    this.waveAmpInfo = null;
    this.prototypeEnabled = false;
    this.layerMeshes = [];
    this.hoveredLayerIndex = null;
    this.selectedLayerIndex = null;
    this.prototypeResources = [];
    this.interactionCleanup = [];
    this.prototypeOverlay = null;
    this.prototypeLayerList = null;
    this.prototypeSelectionDetail = null;
    this.prototypeHud = null;
    this.waveDirectionGroup = null;
  }

  getMaterialColor(matName, isH) {
    if (matName && MATERIAL_COLOR_MAP[matName]) {
      return MATERIAL_COLOR_MAP[matName];
    }
    return isH ? 0xf59e0b : 0x60a5fa;
  }

  build(caseResult, options = {}) {
    this.dispose();
    this.group.add(this.waveRenderer.getGroup());

    this.caseResult = caseResult;
    this.options = options;
    const isExploded = options.isExploded || false;
    this.polarization = options.polarization || "TE";
    if (options.selectedWavelengthNm) {
      this.selectedWavelengthNm = options.selectedWavelengthNm;
    }

    const layersData = (caseResult && caseResult.layers) ? caseResult.layers : [
      { layer_index: 1, type: "H", name: "TiO2", n: 2.15, thickness_nm: 63.95 },
      { layer_index: 2, type: "L", name: "SiO2", n: 1.38, thickness_nm: 99.64 },
      { layer_index: 3, type: "H", name: "TiO2", n: 2.15, thickness_nm: 63.95 },
    ];

    if (caseResult && caseResult.template_mode) {
      this.templateMode = caseResult.template_mode;
    } else {
      const uniqueMatNames = new Set(layersData.map((l) => l.name || l.type).filter(Boolean));
      const hasPeriodicHL = layersData.every((l) => l.type === "H" || l.type === "L");
      this.templateMode = (uniqueMatNames.size > 2 || !hasPeriodicHL)
        ? "GENERIC_MULTILAYER_MODE"
        : "DBR_PERIODIC_MODE";
    }

    this.isGenericMultilayerMode = (this.templateMode === "GENERIC_MULTILAYER_MODE");

    if (this.isGenericMultilayerMode) {
      this.showDbrStopband = false;
      this.showPeriodCount = false;
      this.showRepresentativeInternalDbrWaves = false;
    } else {
      this.showDbrStopband = true;
      this.showPeriodCount = true;
      this.showRepresentativeInternalDbrWaves = true;
    }

    this.waveAmplitudeSource = "SELECTED_WAVELENGTH_R_T_SCHEMATIC";
    this.animationSemantics = "TEACHING_ILLUSTRATION";

    if (caseResult?.case_id === "app_solar_cell_ar") {
      return this.buildSolarPrototype(layersData, isExploded, options);
    }

    let currentY = 0;
    const width = 6;
    const depth = 4;

    // Air
    const airGeo = new THREE.BoxGeometry(width, 0.4, depth);
    const airMat = new THREE.MeshStandardMaterial({ color: 0x93c5fd, transparent: true, opacity: 0.15 });
    const airMesh = new THREE.Mesh(airGeo, airMat);
    airMesh.position.y = currentY - 0.2;
    this.group.add(airMesh);
    currentY -= 0.4 + (isExploded ? 0.25 : 0.02);

    layersData.forEach((layer) => {
      const isH = layer.type === "H";
      const thicknessVisual = Math.max(0.18, (layer.thickness_nm || 80) / 220);
      const color = this.getMaterialColor(layer.name, isH);

      const geo = new THREE.BoxGeometry(width, thicknessVisual, depth);
      const mat = new THREE.MeshStandardMaterial({
        color: color,
        transparent: true,
        opacity: 0.75,
        roughness: 0.25,
      });
      const mesh = new THREE.Mesh(geo, mat);

      const gap = isExploded ? 0.25 : 0.015;
      mesh.position.y = currentY - thicknessVisual / 2;
      this.group.add(mesh);
      currentY -= thicknessVisual + gap;
    });

    // Substrate
    const subGeo = new THREE.BoxGeometry(width, 1.0, depth);
    const subMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.85 });
    const subMesh = new THREE.Mesh(subGeo, subMat);
    subMesh.position.y = currentY - 0.5;
    this.group.add(subMesh);

    // Build Waves using Selected Wavelength Spectrum R/T
    this.rebuildWaveDescriptors();

    // Polarization Helper Arrow
    const polDir = this.polarization === "TE" ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(1, 0, 0);
    const polHex = this.polarization === "TE" ? 0xf59e0b : 0xec4899;
    const arrow = new THREE.ArrowHelper(polDir, new THREE.Vector3(0, 2.2, 0), 1.5, polHex, 0.4, 0.2);
    arrow.name = "polarization_arrow";
    this.group.add(arrow);

    return this.group;
  }

  buildSolarPrototype(layersData, isExploded, options) {
    this.prototypeEnabled = true;
    const width = 6;
    const depth = 4;
    let currentY = 0;

    layersData.forEach((layer, index) => {
      const thicknessVisual = mapThicknessNm(layer.thickness_nm);
      const geometry = new THREE.BoxGeometry(width, thicknessVisual, depth);
      const appearance = createLayerAppearance(layer.name, { themeId: "ACADEMIC_LIGHT", opacity: 0.9 });
      const mesh = new THREE.Mesh(geometry, appearance.material);
      mesh.name = `solar_layer_${index + 1}_${layer.name}`;
      mesh.position.y = currentY - thicknessVisual / 2;
      mesh.userData = {
        isInteractiveLayer: true,
        layerIndex: index,
        layerNumber: index + 1,
        materialName: layer.name,
        thicknessNm: Number(layer.thickness_nm),
      };
      mesh.add(createLayerOutline(geometry, appearance.outlineColor));
      this.group.add(mesh);
      this.layerMeshes.push(mesh);
      this.prototypeResources.push(mesh);
      currentY -= thicknessVisual + (isExploded ? 0.18 : 0);
    });

    const substrateName = this.caseResult?.substrate?.name || "Si";
    const substrateGeometry = new THREE.BoxGeometry(width + 0.3, THICKNESS_MAPPING.substrateVisual, depth + 0.3);
    const substrateAppearance = createLayerAppearance(substrateName, { themeId: "ACADEMIC_LIGHT", opacity: 0.96 });
    const substrateMesh = new THREE.Mesh(substrateGeometry, substrateAppearance.material);
    substrateMesh.name = "solar_substrate";
    substrateMesh.position.y = currentY - THICKNESS_MAPPING.substrateVisual / 2;
    substrateMesh.userData = { isSubstrate: true, materialName: substrateName };
    substrateMesh.add(createLayerOutline(substrateGeometry, substrateAppearance.outlineColor));
    this.group.add(substrateMesh);
    this.prototypeResources.push(substrateMesh);

    this.rebuildWaveDescriptors();

    const theme = getVisualTheme("ACADEMIC_LIGHT");
    const polDir = this.polarization === "TE" ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(1, 0, 0);
    const polColor = this.polarization === "TE"
      ? theme.waveColors.polarizationTE
      : theme.waveColors.polarizationTM;
    const polarizationArrow = new THREE.ArrowHelper(
      polDir,
      new THREE.Vector3(-0.55, 1.25, 0),
      0.95,
      polColor,
      0.22,
      0.12
    );
    polarizationArrow.name = "polarization_arrow";
    this.group.add(polarizationArrow);
    this.prototypeResources.push(polarizationArrow);

    this.createPrototypeOverlay(layersData, substrateName);
    this.setupLayerInteraction(options.camera, options.domElement);
    return this.group;
  }

  rebuildWaveDescriptors() {
    this.waveAmpInfo = calculateWaveAmplitudesFromSpectrum(
      this.caseResult,
      this.polarization,
      this.selectedWavelengthNm
    );
    this.selectedWavelengthNm = this.waveAmpInfo.selectedWavelengthNm;

    const angleRad = (45 * Math.PI) / 180;
    const incStart = [-4 * Math.sin(angleRad), 4 * Math.cos(angleRad), 0];
    const origin = [0, 0, 0];
    const refEnd = [4 * Math.sin(angleRad), 4 * Math.cos(angleRad), 0];
    const transEnd = [1.5 * Math.sin(angleRad * 0.7), -4 * Math.cos(angleRad * 0.7), 0];

    const prototypeTheme = this.prototypeEnabled ? getVisualTheme("ACADEMIC_LIGHT") : null;
    const waveDescriptors = [
      {
        id: "incident_wave",
        start: incStart,
        end: origin,
        amplitude: 0.25,
        wavelength: 0.8,
        speed: 2.0,
        pol: this.polarization,
        color: prototypeTheme?.waveColors.incident ?? 0xef4444,
        linewidth: this.prototypeEnabled ? 1 : undefined,
        opacity: this.prototypeEnabled ? 0.88 : undefined,
      },
      {
        id: "reflected_wave",
        start: origin,
        end: refEnd,
        amplitude: this.waveAmpInfo.rAmp,
        wavelength: 0.8,
        speed: 2.0,
        pol: this.polarization,
        color: prototypeTheme?.waveColors.reflected ?? 0x3b82f6,
        linewidth: this.prototypeEnabled ? 1 : undefined,
        opacity: this.prototypeEnabled ? 0.86 : undefined,
      },
      {
        id: "transmitted_wave",
        start: origin,
        end: transEnd,
        amplitude: this.waveAmpInfo.tAmp,
        wavelength: 0.6,
        speed: 2.0,
        pol: this.polarization,
        color: prototypeTheme?.waveColors.transmitted ?? 0x10b981,
        linewidth: this.prototypeEnabled ? 1 : undefined,
        opacity: this.prototypeEnabled ? 0.86 : undefined,
      },
    ];

    this.waveRenderer.build(waveDescriptors);
    if (this.prototypeEnabled) {
      this.rebuildDirectionArrows(waveDescriptors);
      this.updatePrototypeHud();
    }
  }

  rebuildDirectionArrows(descriptors) {
    if (this.waveDirectionGroup) {
      ResourceDisposer.disposeObject(this.waveDirectionGroup);
      this.prototypeResources = this.prototypeResources.filter((item) => item !== this.waveDirectionGroup);
    }
    this.waveDirectionGroup = new THREE.Group();
    this.waveDirectionGroup.name = "solar_wave_direction_arrows";

    descriptors.forEach((descriptor) => {
      const start = new THREE.Vector3(...descriptor.start);
      const end = new THREE.Vector3(...descriptor.end);
      const direction = end.clone().sub(start);
      const length = direction.length();
      if (length <= 0) return;
      direction.normalize();
      const origin = start.clone().addScaledVector(direction, length * 0.58);
      const arrow = new THREE.ArrowHelper(direction, origin, 0.48, descriptor.color, 0.14, 0.075);
      arrow.name = `${descriptor.id}_direction`;
      this.waveDirectionGroup.add(arrow);
    });

    this.group.add(this.waveDirectionGroup);
    this.prototypeResources.push(this.waveDirectionGroup);
  }

  createPrototypeOverlay(layersData, substrateName) {
    if (!this.container?.appendChild) return;
    const overlay = document.createElement("div");
    overlay.className = "solar-prototype-overlay";
    overlay.innerHTML = `
      <div class="solar-wave-hud" data-role="wave-hud"></div>
      <div class="solar-layer-card">
        <div class="solar-layer-card__eyebrow">膜层结构 · Python 正式数据</div>
        <div class="solar-layer-card__title">Air → 3-layer AR → ${substrateName}</div>
        <div class="solar-layer-list" data-role="layer-list">
          ${layersData.map((layer, index) => `
            <div class="solar-layer-row" data-layer-index="${index}">
              <span class="solar-layer-number">${index + 1}</span>
              <span class="solar-layer-material">${layer.name}</span>
              <span class="solar-layer-thickness">${Number(layer.thickness_nm).toFixed(4)} nm</span>
            </div>
          `).join("")}
        </div>
        <div class="solar-layer-note">厚度经过视觉放大 · 层序与真实厚度未改变</div>
        <div class="solar-selection-detail" data-role="selection-detail">悬停或点击膜层查看详情</div>
      </div>
    `;
    this.container.appendChild(overlay);
    this.prototypeOverlay = overlay;
    this.prototypeLayerList = overlay.querySelector('[data-role="layer-list"]');
    this.prototypeSelectionDetail = overlay.querySelector('[data-role="selection-detail"]');
    this.prototypeHud = overlay.querySelector('[data-role="wave-hud"]');
    this.updatePrototypeHud();
  }

  updatePrototypeHud() {
    if (!this.prototypeHud) return;
    this.prototypeHud.textContent = `λ ${Number(this.selectedWavelengthNm).toFixed(1)} nm · ${this.polarization} · 教学示意波`;
  }

  setupLayerInteraction(camera, domElement) {
    if (!camera || !domElement?.addEventListener) return;
    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    const pickLayer = (event) => {
      const rect = domElement.getBoundingClientRect();
      if (!rect.width || !rect.height) return null;
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      return raycaster.intersectObjects(this.layerMeshes, false)[0]?.object || null;
    };
    const onPointerMove = (event) => {
      const mesh = pickLayer(event);
      this.setHoveredLayer(mesh ? mesh.userData.layerIndex : null);
      domElement.style.cursor = mesh ? "pointer" : "grab";
    };
    const onPointerLeave = () => {
      this.setHoveredLayer(null);
      domElement.style.cursor = "grab";
    };
    const onClick = (event) => {
      const mesh = pickLayer(event);
      if (mesh) this.setSelectedLayer(mesh.userData.layerIndex);
      else this.clearSelection();
    };

    domElement.addEventListener("pointermove", onPointerMove);
    domElement.addEventListener("pointerleave", onPointerLeave);
    domElement.addEventListener("click", onClick);
    this.interactionCleanup.push(() => domElement.removeEventListener("pointermove", onPointerMove));
    this.interactionCleanup.push(() => domElement.removeEventListener("pointerleave", onPointerLeave));
    this.interactionCleanup.push(() => domElement.removeEventListener("click", onClick));
  }

  setHoveredLayer(layerIndex) {
    this.hoveredLayerIndex = Number.isInteger(layerIndex) ? layerIndex : null;
    this.refreshLayerInteractionState();
  }

  setSelectedLayer(layerIndex) {
    this.selectedLayerIndex = Number.isInteger(layerIndex) ? layerIndex : null;
    this.refreshLayerInteractionState();
  }

  clearSelection() {
    this.selectedLayerIndex = null;
    this.refreshLayerInteractionState();
  }

  refreshLayerInteractionState() {
    this.layerMeshes.forEach((mesh, index) => {
      setLayerInteractionState(mesh, {
        hovered: index === this.hoveredLayerIndex,
        selected: index === this.selectedLayerIndex,
      });
    });
    this.prototypeLayerList?.querySelectorAll("[data-layer-index]").forEach((row) => {
      const index = Number(row.dataset.layerIndex);
      row.classList.toggle("is-hovered", index === this.hoveredLayerIndex);
      row.classList.toggle("is-selected", index === this.selectedLayerIndex);
    });

    const focusIndex = this.selectedLayerIndex ?? this.hoveredLayerIndex;
    const focusMesh = Number.isInteger(focusIndex) ? this.layerMeshes[focusIndex] : null;
    if (this.prototypeSelectionDetail) {
      this.prototypeSelectionDetail.textContent = focusMesh
        ? `第 ${focusMesh.userData.layerNumber} 层 · ${focusMesh.userData.materialName} · ${focusMesh.userData.thicknessNm.toFixed(4)} nm`
        : "悬停或点击膜层查看详情";
    }
  }

  getStructureBounds() {
    const bounds = new THREE.Box3();
    this.layerMeshes.forEach((mesh) => bounds.expandByObject(mesh));
    const substrate = this.prototypeResources.find((item) => item?.name === "solar_substrate");
    if (substrate) bounds.expandByObject(substrate);
    return bounds;
  }

  getLayerScreenPositions(camera, domElement) {
    if (!camera || !domElement) return [];
    const rect = domElement.getBoundingClientRect();
    return this.layerMeshes.map((mesh) => {
      if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
      const localPoint = new THREE.Vector3(
        0,
        0,
        mesh.geometry.boundingBox.max.z + 0.002
      );
      const projected = mesh.localToWorld(localPoint).project(camera);
      return {
        layerIndex: mesh.userData.layerIndex,
        x: rect.left + ((projected.x + 1) / 2) * rect.width,
        y: rect.top + ((1 - projected.y) / 2) * rect.height,
      };
    });
  }

  setWavelengthAndPolarization(wavelengthNm, polarization) {
    if (wavelengthNm) this.selectedWavelengthNm = wavelengthNm;
    if (polarization) this.polarization = polarization;
    this.rebuildWaveDescriptors();
  }

  updateAnimation(timeSeconds) {
    if (this.waveRenderer) {
      this.waveRenderer.update(timeSeconds);
    }
  }

  dispose() {
    this.interactionCleanup.splice(0).forEach((cleanup) => cleanup());
    this.prototypeOverlay?.remove();
    this.prototypeOverlay = null;
    this.prototypeLayerList = null;
    this.prototypeSelectionDetail = null;
    this.prototypeHud = null;
    this.prototypeResources.splice(0).forEach((resource) => ResourceDisposer.disposeObject(resource));
    this.layerMeshes = [];
    this.hoveredLayerIndex = null;
    this.selectedLayerIndex = null;
    this.waveDirectionGroup = null;
    this.prototypeEnabled = false;
    if (this.waveRenderer) {
      this.waveRenderer.dispose();
    }
    while (this.group.children.length > 0) {
      const child = this.group.children[0];
      if (child.geometry) child.geometry.dispose();
      if (child.material) {
        if (Array.isArray(child.material)) child.material.forEach((m) => m.dispose());
        else child.material.dispose();
      }
      this.group.remove(child);
    }
  }
}
