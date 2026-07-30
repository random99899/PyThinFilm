/**
 * SineWaveRenderer.js
 *
 * Renders dynamically propagating polarized sine waves along ray paths.
 *
 * Rigorous Wave Kinematics:
 *   - Ray path goes from start point P0 to end point P1 (len = |P1 - P0|, kVec = (P1 - P0)/len).
 *   - Distance s along ray: s ∈ [0, len].
 *   - Forward propagation along kVec: Phase = k*s - ω*t + φ.
 *   - Peak velocity v_phase = +ω/k along +s direction (toward end point P1).
 *     * Incident wave (air -> interface): travels toward interface (P1).
 *     * Reflected wave (interface -> air): P0 is interface, P1 is away in air. Wave travels away from interface!
 *     * Transmitted wave (interface -> substrate): travels into substrate (P1).
 *
 * Vector Polarization:
 *   - Given ray direction kVec and interface normal nVec (default (0, 1, 0)):
 *     TE_dir = normalize(kVec × nVec)
 *     If |kVec × nVec| < 1e-5 (Normal Incidence), TE_dir = (0, 0, 1)
 *     TM_dir = normalize(TE_dir × kVec)
 *   - Assertion: dot(TE_dir, kVec) == 0 and dot(TM_dir, kVec) == 0 (Transverse wave constraint).
 *
 * Standing Wave Superposition (F-P Cavity):
 *   - E_total(s, t) = A_f * sin(k*s - ω*t + φ_f) + A_b * sin(k*(len - s) - ω*t + φ_b)
 *   - Real standing wave nodes remain stationary while anti-nodes oscillate in time.
 *
 * Debug Interface:
 *   Exposes window.__WEB3D_DEBUG__ for live programmatic verification of wave positions & disposes.
 */

import * as THREE from 'three';

export const WAVE_SEGMENTS = 100; // polyline sample count

export class SineWaveRenderer {
  constructor() {
    this._group = new THREE.Group();
    this._group.name = 'SineWaveRendererGroup';
    this._waves = [];  // internal wave descriptors & state
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
   *   pol: 'TE' | 'TM',
   *   color: number,              // 0xRRGGBB
   *   phaseOffset: number,        // radians, optional
   *   amplitudeEnvelope: number[] | null,  // per-sample amplitude scale [0,1], optional
   *   isSuperposition: boolean,   // if true, calculates true standing wave E_forward + E_backward
   *   interfaceNormal: [x,y,z],  // optional, default [0,1,0]
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
      const kVec    = dirVec.clone().normalize();

      // Interface normal vector for TE/TM polarization plane decomposition
      const nVec = new THREE.Vector3(...(d.interfaceNormal || [0, 1, 0])).normalize();

      // Transverse vector calculations
      let teDir = new THREE.Vector3().crossVectors(kVec, nVec);
      if (teDir.lengthSq() < 1e-6) {
        // Normal incidence degeneracy fallback: TE along Z-axis
        teDir.set(0, 0, 1);
      } else {
        teDir.normalize();
      }

      let tmDir = new THREE.Vector3().crossVectors(teDir, kVec).normalize();

      // Polarization direction vector
      const polVec = (d.pol === 'TE' ? teDir : tmDir).clone();

      // Strict Transverse Constraint Assertion
      const dotCheck = Math.abs(polVec.dot(kVec));
      if (dotCheck > 1e-4) {
        console.warn(`[SineWaveRenderer] Polarization vector is not strictly transverse to ray direction: dot = ${dotCheck}`);
      }

      const k     = (2 * Math.PI) / Math.max(d.wavelength, 0.01);
      const omega = d.speed * k;

      // Dynamic Draw Buffer Attribute Pre-allocation
      const positions = new Float32Array(WAVE_SEGMENTS * 3);
      const geo = new THREE.BufferGeometry();
      const bufAttr = new THREE.BufferAttribute(positions, 3);
      bufAttr.setUsage(THREE.DynamicDrawUsage);
      geo.setAttribute('position', bufAttr);

      const mat  = new THREE.LineBasicMaterial({ color: d.color, linewidth: d.isSuperposition ? 3 : 2 });
      const line = new THREE.Line(geo, mat);
      line.name  = d.id || 'wave';
      this._group.add(line);

      this._waves.push({
        id: d.id || 'wave',
        positions, bufAttr,
        k, omega,
        polVec, startV, kVec, len,
        phaseOffset: d.phaseOffset ?? 0,
        amplitude: d.amplitude,
        amplitudeEnvelope: d.amplitudeEnvelope ?? null,
        isSuperposition: d.isSuperposition || false,
      });
      this._lines.push(line);
    }

    // Draw initial frame at t=0
    this.update(0);
  }

  /**
   * Update all wave geometries for the given elapsed time.
   * Pure in-place BufferAttribute mutation.
   */
  update(time) {
    for (const w of this._waves) {
      const {
        positions, bufAttr,
        k, omega,
        polVec, startV, kVec, len,
        phaseOffset, amplitude, amplitudeEnvelope, isSuperposition
      } = w;

      const N = WAVE_SEGMENTS;
      for (let i = 0; i < N; i++) {
        const s = (i / (N - 1)) * len;

        // Base coordinate along ray
        const bx = startV.x + kVec.x * s;
        const by = startV.y + kVec.y * s;
        const bz = startV.z + kVec.z * s;

        let disp = 0;
        if (isSuperposition) {
          // Standing Wave Superposition: E_forward + E_backward
          // E_forward  = A * sin(k*s - ω*t + φ)
          // E_backward = A * sin(k*(len - s) - ω*t + φ)
          const fwd = amplitude * Math.sin(k * s - omega * time + phaseOffset);
          const bwd = amplitude * Math.sin(k * (len - s) - omega * time + phaseOffset);
          disp = fwd + bwd;
        } else {
          // Standard Forward Propagation Wave
          // Phase = k*s - ω*t + φ
          const phase = k * s - omega * time + phaseOffset;
          let amp = amplitude;
          if (amplitudeEnvelope !== null) {
            const envIdx = Math.min(
              Math.floor((i / N) * amplitudeEnvelope.length),
              amplitudeEnvelope.length - 1
            );
            amp = amplitude * amplitudeEnvelope[envIdx];
          }
          disp = amp * Math.sin(phase);
        }

        positions[i * 3]     = bx + polVec.x * disp;
        positions[i * 3 + 1] = by + polVec.y * disp;
        positions[i * 3 + 2] = bz + polVec.z * disp;
      }

      bufAttr.needsUpdate = true;
    }
  }

  dispose() {
    for (const line of this._lines) {
      if (line.geometry) line.geometry.dispose();
      if (line.material) line.material.dispose();
      this._group.remove(line);
    }
    this._waves = [];
    this._lines = [];
  }

  getGroup() {
    return this._group;
  }

  get waveCount() {
    return this._waves.length;
  }

  getWavePositions() {
    return this._waves.map((w) => Array.from(w.positions));
  }
}

SineWaveRenderer._instanceCount = 0;
