import * as THREE from "three";

export class SingleInterfaceTemplate {
  constructor(container) {
    this.container = container;
    this.group = new THREE.Group();
    this.group.name = "SingleInterfaceTemplateGroup";
  }

  build(caseResult, options = {}) {
    this.dispose();

    const isExploded = options.isExploded || false;
    const polarization = options.polarization || "TE";

    // 1. Build Layer Stack Mesh: Air / MgF2 (111.5nm) / Glass (1.52)
    const layers = [
      { name: "Air", thickness: 0.5, color: 0x93c5fd, opacity: 0.15 },
      { name: "MgF2", thickness: 0.8, color: 0xa7f3d0, opacity: 0.7 },
      { name: "Glass Substrate", thickness: 1.5, color: 0x38bdf8, opacity: 0.85 },
    ];

    let currentY = 0;
    const width = 6;
    const depth = 4;

    layers.forEach((layer) => {
      const geo = new THREE.BoxGeometry(width, layer.thickness, depth);
      const mat = new THREE.MeshStandardMaterial({
        color: layer.color,
        transparent: true,
        opacity: layer.opacity,
        roughness: 0.2,
      });
      const mesh = new THREE.Mesh(geo, mat);

      const gap = isExploded ? 0.5 : 0.02;
      mesh.position.y = currentY - layer.thickness / 2;
      this.group.add(mesh);

      currentY -= layer.thickness + gap;
    });

    // 2. Build 45 deg Rays (Incident, Reflected, Transmitted)
    const angleRad = (45 * Math.PI) / 180;
    
    // Incident ray
    const incGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-4 * Math.sin(angleRad), 4 * Math.cos(angleRad), 0),
      new THREE.Vector3(0, 0, 0),
    ]);
    const incLine = new THREE.Line(incGeo, new THREE.LineBasicMaterial({ color: 0xef4444, linewidth: 2 }));
    this.group.add(incLine);

    // Reflected ray
    const refGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(4 * Math.sin(angleRad), 4 * Math.cos(angleRad), 0),
    ]);
    const refLine = new THREE.Line(refGeo, new THREE.LineBasicMaterial({ color: 0x3b82f6, linewidth: 2 }));
    this.group.add(refLine);

    // Transmitted ray
    const transGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(3 * Math.sin(angleRad * 0.7), -3 * Math.cos(angleRad * 0.7), 0),
    ]);
    const transLine = new THREE.Line(transGeo, new THREE.LineBasicMaterial({ color: 0x10b981, linewidth: 2 }));
    this.group.add(transLine);

    // 3. Build Polarization Vector Arrow
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
