import * as THREE from "three";
import { SineWaveRenderer } from "../core/SineWaveRenderer.js";

const MATERIAL_COLOR_MAP = {
  SiO2: 0x60a5fa, // Blue
  TiO2: 0xf59e0b, // Amber
  MgF2: 0x34d399, // Emerald Green
  ZrO2: 0xa855f7, // Purple
  Al2O3: 0xf43f5e, // Rose Red
  Air: 0x93c5fd,  // Light Blue
};

export class PeriodicStackTemplate {
  constructor(container) {
    this.container = container;
    this.group = new THREE.Group();
    this.group.name = "PeriodicStackTemplateGroup";
    this.waveRenderer = new SineWaveRenderer();
    this.group.add(this.waveRenderer.getGroup());
    
    // Explicit Mode Flags
    this.templateMode = "DBR_PERIODIC_MODE";
    this.isGenericMultilayerMode = false;
    this.showDbrStopband = true;
    this.showPeriodCount = true;
    this.showRepresentativeInternalDbrWaves = true;
    this.waveAmplitudeSource = "DBR_DEFAULT";
    this.animationSemantics = "STANDING_WAVE_ILLUSTRATION";
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

    const isExploded = options.isExploded || false;
    const polarization = options.polarization || "TE";

    const layersData = (caseResult && caseResult.layers) ? caseResult.layers : [
      { layer_index: 1, type: "H", name: "TiO2", n: 2.15, thickness_nm: 63.95 },
      { layer_index: 2, type: "L", name: "SiO2", n: 1.38, thickness_nm: 99.64 },
      { layer_index: 3, type: "H", name: "TiO2", n: 2.15, thickness_nm: 63.95 },
    ];

    // Priority 1: Explicit template_mode from JSON or registry
    if (caseResult && caseResult.template_mode) {
      this.templateMode = caseResult.template_mode;
    } else {
      // Fallback 2: Automated heuristic detection
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
      this.waveAmplitudeSource = "R_T_SCHEMATIC";
      this.animationSemantics = "TEACHING_ILLUSTRATION";
    } else {
      this.showDbrStopband = true;
      this.showPeriodCount = true;
      this.showRepresentativeInternalDbrWaves = true;
      this.waveAmplitudeSource = "DBR_DEFAULT";
      this.animationSemantics = "STANDING_WAVE_ILLUSTRATION";
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

    // Dynamic wave amplitudes based on case R/T spectrum if in GENERIC_MULTILAYER_MODE
    let rAmp = 0.23;
    let tAmp = 0.05;
    if (this.isGenericMultilayerMode && caseResult && caseResult[polarization]) {
      const rArr = caseResult[polarization].R || [];
      const tArr = caseResult[polarization].T || [];
      const meanR = rArr.length > 0 ? (rArr.reduce((a, b) => a + b, 0) / rArr.length) : 0.2;
      const meanT = tArr.length > 0 ? (tArr.reduce((a, b) => a + b, 0) / tArr.length) : 0.8;
      
      rAmp = Math.max(0.04, Math.min(0.28, meanR * 0.30));
      tAmp = Math.max(0.04, Math.min(0.28, meanT * 0.30));
    }

    // Rays & Waves
    const angleRad = (45 * Math.PI) / 180;
    const incStart = [-4 * Math.sin(angleRad), 4 * Math.cos(angleRad), 0];
    const origin = [0, 0, 0];
    const refEnd = [4 * Math.sin(angleRad), 4 * Math.cos(angleRad), 0];
    const transEnd = [1.5 * Math.sin(angleRad * 0.7), -4 * Math.cos(angleRad * 0.7), 0];

    const waveDescriptors = [
      {
        id: "incident_wave",
        start: incStart,
        end: origin,
        amplitude: 0.25,
        wavelength: 0.8,
        speed: 2.0,
        travelDir: 1,
        pol: polarization,
        color: 0xef4444,
      },
      {
        id: "reflected_wave",
        start: origin,
        end: refEnd,
        amplitude: rAmp,
        wavelength: 0.8,
        speed: 2.0,
        travelDir: 1,
        pol: polarization,
        color: 0x3b82f6,
      },
      {
        id: "transmitted_wave",
        start: origin,
        end: transEnd,
        amplitude: tAmp,
        wavelength: 0.6,
        speed: 2.0,
        travelDir: 1,
        pol: polarization,
        color: 0x10b981,
      },
    ];

    this.waveRenderer.build(waveDescriptors);

    // Polarization Helper Arrow
    const polDir = polarization === "TE" ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(1, 0, 0);
    const polHex = polarization === "TE" ? 0xf59e0b : 0xec4899;
    const arrow = new THREE.ArrowHelper(polDir, new THREE.Vector3(0, 2.2, 0), 1.5, polHex, 0.4, 0.2);
    this.group.add(arrow);

    return this.group;
  }

  updateAnimation(timeSeconds) {
    if (this.waveRenderer) {
      this.waveRenderer.update(timeSeconds);
    }
  }

  dispose() {
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
