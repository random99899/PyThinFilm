/**
 * SineWaveRenderer.js
 *
 * Renders dynamically propagating polarized sine waves along ray paths.
 * Physics:
 *   - Wave propagating from start to end: P(s,t) = base(s) + A*sin(k*s - ω*t + φ) * perpDir
 *   - TE: perpDir = (0, 0, 1)  — oscillates out of scene plane (Z axis)
 *   - TM: perpDir = perpendicular to ray direction within the XY plane
 *   - BufferAttribute is updated each frame; no geometry is re-created
 *
 * Labels for transparency:
 *   数值光谱 = Python TMM | 空间波长 = 视觉缩放 | 动画振幅 = 教学示意或 Python 场包络
 */

import * as THREE from 'three';

export const WAVE_SEGMENTS = 100; // polyline sample count

export class SineWaveRenderer {
  constructor() {
    this._group = new THREE.Group();
    this._group.name = 'SineWaveRendererGroup';
    this._waves = [];  // internal wave state
    this._lines = [];  // THREE.Line objects

    SineWaveRenderer._instanceCount += 1;
    this._id = SineWaveRenderer._instanceCount;
  }

  /**
   * Build wave geometry from an array of wave descriptors.
   * Disposes any existing waves first.
   *
   * @param {WaveDescriptor[]} descriptors
   * WaveDescriptor = {
   *   id: string,
   *   start: [x,y,z],
   *   end: [x,y,z],
   *   amplitude: number,          // visual peak displacement (scene units)
   *   wavelength: number,         // visual wavelength (scene units)
   *   speed: number,              // visual wave speed (units/s)
   *   travelDir: +1 | -1,        // +1: toward end, -1: toward start
   *   pol: 'TE' | 'TM',
   *   color: number,              // 0xRRGGBB
   *   phaseOffset: number,        // radians, optional
   *   amplitudeEnvelope: number[] | null,  // per-sample amplitude scale [0,1], optional
   * }
   */
  build(descriptors) {
    this.dispose();
    if (!descriptors || descriptors.length === 0) return;

    for (const d of descriptors) {
      const startV  = new THREE.Vector3(...d.start);
      const endV    = new THREE.Vector3(...d.end);
      const dirVec  = new THREE.Vector3().subVectors(endV, startV);
      const len     = dirVec.length();
      if (len < 1e-6) continue;
      const dirNorm = dirVec.clone().normalize();

      // Perpendicular oscillation axis based on polarization
      let perpDir;
      if (d.pol === 'TE') {
        // TE: E-field perpendicular to plane of incidence (XY plane) → Z axis
        perpDir = new THREE.Vector3(0, 0, 1);
      } else {
        // TM: E-field in plane of incidence, perpendicular to propagation direction
        //     Within XY plane: rotate dirNorm by 90°
        perpDir = new THREE.Vector3(-dirNorm.y, dirNorm.x, 0);
        if (perpDir.lengthSq() < 1e-9) {
          // Ray along Z: fall back to X
          perpDir.set(1, 0, 0);
        }
        perpDir.normalize();
      }

      const k     = (2 * Math.PI) / Math.max(d.wavelength, 0.01);
      const omega = d.speed * k;

      // Pre-allocate position buffer (reused every frame, never reallocated)
      const positions = new Float32Array(WAVE_SEGMENTS * 3);
      const geo = new THREE.BufferGeometry();
      const bufAttr = new THREE.BufferAttribute(positions, 3);
      bufAttr.setUsage(THREE.DynamicDrawUsage);
      geo.setAttribute('position', bufAttr);

      const mat  = new THREE.LineBasicMaterial({ color: d.color });
      const line = new THREE.Line(geo, mat);
      line.name  = d.id || 'wave';
      this._group.add(line);

      this._waves.push({
        positions, bufAttr,
        travelDir: d.travelDir ?? +1,
        k, omega,
        perpDir, startV, dirNorm, len,
        phaseOffset: d.phaseOffset ?? 0,
        amplitude: d.amplitude,
        amplitudeEnvelope: d.amplitudeEnvelope ?? null,
      });
      this._lines.push(line);
    }

    // Draw initial frame at t=0
    this.update(0);
  }

  /**
   * Update all wave geometries for the given elapsed time.
   * Call every animation frame with the accumulated time (seconds).
   * Only mutates BufferAttribute.array — no geometry creation.
   */
  update(time) {
    for (const w of this._waves) {
      const {
        positions, bufAttr,
        travelDir, k, omega,
        perpDir, startV, dirNorm, len,
        phaseOffset, amplitude, amplitudeEnvelope,
      } = w;

      const N = WAVE_SEGMENTS;
      for (let i = 0; i < N; i++) {
        const s = (i / (N - 1)) * len;

        // Base position along ray (no displacement)
        const bx = startV.x + dirNorm.x * s;
        const by = startV.y + dirNorm.y * s;
        const bz = startV.z + dirNorm.z * s;

        // Wave phase: +travelDir so that +1 propagates toward end, -1 toward start
        const phase = k * s - travelDir * omega * time + phaseOffset;

        // Amplitude (optionally spatially modulated by envelope)
        let amp = amplitude;
        if (amplitudeEnvelope !== null) {
          const envIdx = Math.min(
            Math.floor((i / N) * amplitudeEnvelope.length),
            amplitudeEnvelope.length - 1
          );
          amp = amplitude * amplitudeEnvelope[envIdx];
        }

        const disp = amp * Math.sin(phase);

        positions[i * 3]     = bx + perpDir.x * disp;
        positions[i * 3 + 1] = by + perpDir.y * disp;
        positions[i * 3 + 2] = bz + perpDir.z * disp;
      }

      bufAttr.needsUpdate = true;
    }
  }

  /**
   * Dispose all geometry and materials.
   * Must be called before switching cases to prevent GPU memory leaks.
   */
  dispose() {
    for (const line of this._lines) {
      if (line.geometry) line.geometry.dispose();
      if (line.material) line.material.dispose();
      this._group.remove(line);
    }
    this._waves = [];
    this._lines = [];
  }

  /** THREE.Group containing all wave lines — add to scene directly */
  getGroup() {
    return this._group;
  }

  /** Number of active wave objects (for leak detection in tests) */
  get waveCount() {
    return this._waves.length;
  }
}

SineWaveRenderer._instanceCount = 0;

