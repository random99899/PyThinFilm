import * as THREE from "three";

export class MetalDbrInterfaceTemplate {
  constructor(container) {
    this.container = container;
    this.group = new THREE.Group();
    this.group.name = "MetalDbrInterfaceTemplateGroup";
  }

  build(caseResult, options = {}) {
    this.dispose();

    const isExploded = options.isExploded || false;
    const polarization = options.polarization || "TE";

    // Extract layers from JSON
    const layersData = (caseResult && caseResult.layers) ? caseResult.layers : [
      { layer_index: 1, type: "Ag", role: "metal_absorber", n_real: 0.13, n_imag: 3.98, thickness_nm: 30.0 },
      { layer_index: 2, type: "H", role: "dbr_mirror_layer", n_real: 2.15, n_imag: 0.0, thickness_nm: 63.95 },
      { layer_index: 3, type: "L", role: "dbr_mirror_layer", n_real: 1.38, n_imag: 0.0, thickness_nm: 99.64 },
      { layer_index: 4, type: "H", role: "dbr_mirror_layer", n_real: 2.15, n_imag: 0.0, thickness_nm: 63.95 },
      { layer_index: 5, type: "L", role: "dbr_mirror_layer", n_real: 1.38, n_imag: 0.0, thickness_nm: 99.64 },
      { layer_index: 6, type: "H", role: "dbr_mirror_layer", n_real: 2.15, n_imag: 0.0, thickness_nm: 63.95 },
      { layer_index: 7, type: "L", role: "dbr_mirror_layer", n_real: 1.38, n_imag: 0.0, thickness_nm: 99.64 },
      { layer_index: 8, type: "H", role: "dbr_mirror_layer", n_real: 2.15, n_imag: 0.0, thickness_nm: 63.95 },
    ];

    let currentY = 0;
    const width = 6;
    const depth = 4;

    // Ambient Air
    const airGeo = new THREE.BoxGeometry(width, 0.4, depth);
    const airMat = new THREE.MeshStandardMaterial({ color: 0x93c5fd, transparent: true, opacity: 0.15 });
    const airMesh = new THREE.Mesh(airGeo, airMat);
    airMesh.position.y = currentY - 0.2;
    this.group.add(airMesh);
    currentY -= 0.4 + (isExploded ? 0.25 : 0.02);

    // 8 Layers
    layersData.forEach((layer) => {
      const isMetal = layer.type === "Ag";
      const isH = layer.type === "H";
      
      const thicknessVisual = isMetal ? 0.3 : Math.max(0.18, (layer.thickness_nm || 80) / 220);
      
      // Metallic Silver vs Amber vs Blue
      let color = 0x94a3b8; // Ag Silver
      if (!isMetal) color = isH ? 0xf59e0b : 0x60a5fa;

      const geo = new THREE.BoxGeometry(width, thicknessVisual, depth);
      const mat = new THREE.MeshStandardMaterial({
        color: color,
        metalness: isMetal ? 0.95 : 0.1,
        roughness: isMetal ? 0.15 : 0.3,
        transparent: true,
        opacity: isMetal ? 0.95 : 0.75,
        emissive: isMetal ? 0x475569 : 0x000000,
        emissiveIntensity: isMetal ? 0.3 : 0.0,
      });
      const mesh = new THREE.Mesh(geo, mat);

      const gap = isExploded ? 0.25 : 0.015;
      mesh.position.y = currentY - thicknessVisual / 2;
      mesh.userData = {
        layerIndex: layer.layer_index,
        type: layer.type,
        role: layer.role,
        n_real: layer.n_real,
        n_imag: layer.n_imag || 0.0,
        thickness_nm: layer.thickness_nm,
      };

      this.group.add(mesh);
      currentY -= thicknessVisual + gap;
    });

    // Substrate Glass
    const subGeo = new THREE.BoxGeometry(width, 1.0, depth);
    const subMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.85 });
    const subMesh = new THREE.Mesh(subGeo, subMat);
    subMesh.position.y = currentY - 0.5;
    this.group.add(subMesh);

    // Normal Incidence Rays (0 deg)
    const incGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 3.5, 0),
      new THREE.Vector3(0, 0, 0),
    ]);
    const incLine = new THREE.Line(incGeo, new THREE.LineBasicMaterial({ color: 0xef4444, linewidth: 2 }));
    this.group.add(incLine);

    const refGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(0, 3.5, 0),
    ]);
    const refLine = new THREE.Line(refGeo, new THREE.LineBasicMaterial({ color: 0x3b82f6, linewidth: 2 }));
    this.group.add(refLine);

    // Polarization Arrow
    const polDir = polarization === "TE" ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(1, 0, 0);
    const polHex = polarization === "TE" ? 0xf59e0b : 0xec4899;
    const arrow = new THREE.ArrowHelper(polDir, new THREE.Vector3(0, 2.2, 0), 1.5, polHex, 0.4, 0.2);
    this.group.add(arrow);

    return this.group;
  }

  dispose() {
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
