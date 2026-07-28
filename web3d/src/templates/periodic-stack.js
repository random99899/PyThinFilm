import * as THREE from "three";

export class PeriodicStackTemplate {
  constructor(container) {
    this.container = container;
    this.group = new THREE.Group();
    this.group.name = "PeriodicStackTemplateGroup";
  }

  build(caseResult, options = {}) {
    this.dispose();

    const isExploded = options.isExploded || false;
    const polarization = options.polarization || "TE";

    // Extract exact layer stack from Python result JSON or fallback to official Bragg reflector stack
    const layersData = (caseResult && caseResult.layers) ? caseResult.layers : [
      { layer_index: 1, type: "H", n: 2.15, thickness_nm: 63.95 },
      { layer_index: 2, type: "L", n: 1.38, thickness_nm: 99.64 },
      { layer_index: 3, type: "H", n: 2.15, thickness_nm: 63.95 },
      { layer_index: 4, type: "L", n: 1.38, thickness_nm: 99.64 },
      { layer_index: 5, type: "H", n: 2.15, thickness_nm: 63.95 },
      { layer_index: 6, type: "L", n: 1.38, thickness_nm: 99.64 },
      { layer_index: 7, type: "H", n: 2.15, thickness_nm: 63.95 },
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
    currentY -= 0.4 + (isExploded ? 0.3 : 0.02);

    // DBR 7 Periodic Layers
    layersData.forEach((layer) => {
      const isH = layer.type === "H";
      const thicknessVisual = Math.max(0.25, (layer.thickness_nm || 80) / 180);
      const color = isH ? 0xf59e0b : 0x60a5fa; // H: TiO2 amber, L: SiO2 blue

      const geo = new THREE.BoxGeometry(width, thicknessVisual, depth);
      const mat = new THREE.MeshStandardMaterial({
        color: color,
        transparent: true,
        opacity: 0.75,
        roughness: 0.2,
      });
      const mesh = new THREE.Mesh(geo, mat);

      const gap = isExploded ? 0.35 : 0.02;
      mesh.position.y = currentY - thicknessVisual / 2;
      mesh.userData = {
        layerIndex: layer.layer_index,
        type: layer.type,
        n: layer.n,
        thickness_nm: layer.thickness_nm,
      };

      this.group.add(mesh);
      currentY -= thicknessVisual + gap;
    });

    // Glass Substrate
    const subGeo = new THREE.BoxGeometry(width, 1.2, depth);
    const subMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.85 });
    const subMesh = new THREE.Mesh(subGeo, subMat);
    subMesh.position.y = currentY - 0.6;
    this.group.add(subMesh);

    // 45 deg Rays (Incident, Reflected, Transmitted)
    const angleRad = (45 * Math.PI) / 180;
    
    const incGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-4 * Math.sin(angleRad), 4 * Math.cos(angleRad), 0),
      new THREE.Vector3(0, 0, 0),
    ]);
    const incLine = new THREE.Line(incGeo, new THREE.LineBasicMaterial({ color: 0xef4444, linewidth: 2 }));
    this.group.add(incLine);

    const refGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(4 * Math.sin(angleRad), 4 * Math.cos(angleRad), 0),
    ]);
    const refLine = new THREE.Line(refGeo, new THREE.LineBasicMaterial({ color: 0x3b82f6, linewidth: 2 }));
    this.group.add(refLine);

    const transGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(2 * Math.sin(angleRad * 0.7), -4 * Math.cos(angleRad * 0.7), 0),
    ]);
    const transLine = new THREE.Line(transGeo, new THREE.LineBasicMaterial({ color: 0x10b981, linewidth: 2 }));
    this.group.add(transLine);

    // Polarization Arrow
    const polDir = polarization === "TE" ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(1, 0, 0);
    const polHex = polarization === "TE" ? 0xf59e0b : 0xec4899;
    const arrow = new THREE.ArrowHelper(polDir, new THREE.Vector3(0, 2, 0), 1.5, polHex, 0.4, 0.2);
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
