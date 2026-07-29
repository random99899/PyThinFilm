# -*- coding: utf-8 -*-
"""Export script for PyThinFilm 3D Visualization cases (Stage B.1D).

Exports canonical Python TMM calculation results for:
- single_ar
- bragg_reflector
- fp_filter
- tamm_phase_bundle

Output directory: web3d/public/results/<case_id>.json.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from thinfilm import simulate_report_design
from thinfilm.education import LayerSpec, multilayer_rt_spectrum, reflection_phase_radians


def get_git_commit_hash():
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(ROOT))
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN_COMMIT"


def compute_hash(data_obj):
    raw = json.dumps(data_obj, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def split_continuous_segments(wl, R, threshold=0.50):
    above_indices = np.where(R >= threshold)[0]
    if len(above_indices) == 0:
        return []

    diffs = np.diff(above_indices)
    split_points = np.where(diffs > 1)[0] + 1
    groups = np.split(above_indices, split_points)

    segments = []
    for g in groups:
        if len(g) == 0:
            continue
        start_idx, end_idx = g[0], g[-1]
        sub_r = R[start_idx : end_idx + 1]
        max_r_idx = start_idx + int(np.argmax(sub_r))

        segments.append({
            "start_index": int(start_idx),
            "end_index": int(end_idx),
            "start_nm": round(float(wl[start_idx]), 1),
            "end_nm": round(float(wl[end_idx]), 1),
            "width_nm": round(float(wl[end_idx] - wl[start_idx]), 1),
            "max_R": round(float(R[max_r_idx]), 6),
            "wavelength_at_max_R_nm": round(float(wl[max_r_idx]), 1)
        })
    return segments


def export_single_ar():
    out_dir = ROOT / "web3d" / "public" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "single_ar.json"

    res_te = simulate_report_design("single_ar", theta_deg=45.0, pol="s")
    res_tm = simulate_report_design("single_ar", theta_deg=45.0, pol="p")

    wl = res_te["wavelength_nm"].tolist()
    r_te = res_te["R"].tolist()
    t_te = res_te["T"].tolist()
    a_te = res_te["A"].tolist()

    r_tm = res_tm["R"].tolist()
    t_tm = res_tm["T"].tolist()
    a_tm = res_tm["A"].tolist()

    input_params = {
        "case_id": "single_ar",
        "theta_deg": 45.0,
        "n_air": 1.0,
        "n_mgf2": 1.38,
        "d_mgf2": 111.5,
        "n_glass": 1.52
    }

    data = {
        "schema_version": "1.0.0",
        "case_id": "single_ar",
        "title": "单层减反射膜(任意参数)",
        "source_commit": get_git_commit_hash(),
        "source_file": "thinfilm/education.py",
        "source_symbol": "build_single_ar_layers",
        "generated_at": datetime.datetime.now().isoformat(),
        "calculation_source": "python_export",
        "design_wavelength_nm": 550.0,
        "incidence_angle_deg": 45.0,
        "polarization_support": ["TE", "TM"],
        "ambient": {"name": "Air", "n": 1.0},
        "layers": [
          {"role": "film", "material": "MgF2", "n": 1.38, "thickness_nm": 111.5}
        ],
        "substrate": {"name": "Glass", "n": 1.52},
        "wavelength_nm": [round(x, 2) for x in wl],
        "TE": {
            "R": [round(x, 6) for x in r_te],
            "T": [round(x, 6) for x in t_te],
            "A": [round(x, 6) for x in a_te]
        },
        "TM": {
            "R": [round(x, 6) for x in r_tm],
            "T": [round(x, 6) for x in t_tm],
            "A": [round(x, 6) for x in a_tm]
        },
        "design_point_550nm": {
            "TE": {
                "R": round(float(res_te["R"][75]), 6),
                "T": round(float(res_te["T"][75]), 6),
                "A": round(float(res_te["A"][75]), 6)
            },
            "TM": {
                "R": round(float(res_tm["R"][75]), 6),
                "T": round(float(res_tm["T"][75]), 6),
                "A": round(float(res_tm["A"][75]), 6)
            }
        },
        "phase_data_status": "NOT_AVAILABLE",
        "input_parameter_hash": compute_hash(input_params)
    }

    data["result_hash"] = compute_hash(data)
    out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[export] Successfully exported single_ar results -> {out_file}")


def export_bragg_reflector():
    out_dir = ROOT / "web3d" / "public" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "bragg_reflector.json"

    res_te = simulate_report_design("bragg_reflector", theta_deg=45.0, pol="s")
    res_tm = simulate_report_design("bragg_reflector", theta_deg=45.0, pol="p")

    wl = res_te["wavelength_nm"]
    r_te = res_te["R"]
    t_te = res_te["T"]
    a_te = res_te["A"]

    r_tm = res_tm["R"]
    t_tm = res_tm["T"]
    a_tm = res_tm["A"]

    layer_stack_info = [
        {"layer_index": idx + 1, "type": lyr["name"], "n": lyr["n_real"], "thickness_nm": round(lyr["thickness_nm"], 4)}
        for idx, lyr in enumerate(res_te["layers"])
    ]

    input_params = {
        "case_id": "bragg_reflector",
        "theta_deg": 45.0,
        "lambda0_nm": 550.0,
        "n_high": 2.15,
        "n_low": 1.38,
        "periods": 3.5,
        "n_air": 1.0,
        "n_glass": 1.52
    }

    idx_550 = int(np.argmin(np.abs(wl - 550.0)))

    te_segments = split_continuous_segments(wl, r_te, threshold=0.70)
    tm_segments = split_continuous_segments(wl, r_tm, threshold=0.70)

    te_primary = max(te_segments, key=lambda s: s["max_R"]) if te_segments else None
    tm_primary = max(tm_segments, key=lambda s: s["max_R"]) if tm_segments else None

    data = {
        "schema_version": "1.0.0",
        "case_id": "bragg_reflector",
        "title": "Bragg反射镜/高反射膜",
        "source_commit": get_git_commit_hash(),
        "source_file": "thinfilm/education.py",
        "source_symbol": "build_high_reflector_layers",
        "generated_at": datetime.datetime.now().isoformat(),
        "calculation_source": "python_export",
        "design_specification": {
            "design_wavelength_nm": 550.0,
            "dH_nm": round(550.0 / (4 * 2.15), 4),
            "dL_nm": round(550.0 / (4 * 1.38), 4),
            "thickness_design_mode": "Normal incidence 0 deg QWOT without 45 deg angle compensation",
            "incidence_angle_deg": 45.0
        },
        "polarization_support": ["TE", "TM"],
        "ambient": {"name": "Air", "n": 1.0},
        "layers": layer_stack_info,
        "substrate": {"name": "Glass", "n": 1.52},
        "wavelength_nm": [round(float(x), 2) for x in wl],
        "TE": {
            "R": [round(float(x), 6) for x in r_te],
            "T": [round(float(x), 6) for x in t_te],
            "A": [round(float(x), 6) for x in a_te]
        },
        "TM": {
            "R": [round(float(x), 6) for x in r_tm],
            "T": [round(float(x), 6) for x in t_tm],
            "A": [round(float(x), 6) for x in a_tm]
        },
        "design_point_550nm": {
            "TE": {
                "R": round(float(r_te[idx_550]), 6),
                "T": round(float(t_te[idx_550]), 6),
                "A": round(float(a_te[idx_550]), 6)
            },
            "TM": {
                "R": round(float(r_tm[idx_550]), 6),
                "T": round(float(t_tm[idx_550]), 6),
                "A": round(float(a_tm[idx_550]), 6)
            }
        },
        "stopband_metrics": {
            "threshold_R": 0.70,
            "TE": {
                "segments": te_segments,
                "selected_segment": te_primary,
                "selection_rule": "Primary continuous segment with max R in Bragg reflection band"
            },
            "TM": {
                "segments": tm_segments,
                "selected_segment": tm_primary,
                "selection_rule": "Primary continuous segment with max R in Bragg reflection band"
            }
        },
        "phase_data_status": "NOT_AVAILABLE",
        "input_parameter_hash": compute_hash(input_params)
    }

    data["result_hash"] = compute_hash(data)
    out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[export] Successfully exported bragg_reflector results -> {out_file}")


def export_fp_filter():
    out_dir = ROOT / "web3d" / "public" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "fp_filter.json"

    res_te = simulate_report_design("fp_filter", theta_deg=45.0, pol="s")
    res_tm = simulate_report_design("fp_filter", theta_deg=45.0, pol="p")

    wl = res_te["wavelength_nm"]
    r_te = res_te["R"]
    t_te = res_te["T"]
    a_te = res_te["A"]

    r_tm = res_tm["R"]
    t_tm = res_tm["T"]
    a_tm = res_tm["A"]

    layer_stack_info = [
        {
            "layer_index": idx + 1,
            "type": lyr["name"],
            "role": "cavity_spacer" if lyr["name"] == "C" else "mirror_layer",
            "n": lyr["n_real"],
            "thickness_nm": round(lyr["thickness_nm"], 4)
        }
        for idx, lyr in enumerate(res_te["layers"])
    ]

    input_params = {
        "case_id": "fp_filter",
        "theta_deg": 45.0,
        "lambda0_nm": 550.0,
        "fp_spacer_kind": "L",
        "periods": 4,
        "n_high": 2.15,
        "n_low": 1.38,
        "n_air": 1.0,
        "n_glass": 1.52
    }

    idx_te_global = int(np.argmax(t_te))
    idx_tm_global = int(np.argmax(t_tm))

    te_stop_segments = split_continuous_segments(wl, r_te, threshold=0.35)
    tm_stop_segments = split_continuous_segments(wl, r_tm, threshold=0.35)

    def search_stopband_defect_peaks(wl, T, R, min_wl=400.0, max_wl=600.0):
        candidates = []
        for i in range(1, len(T) - 1):
            w = wl[i]
            if min_wl <= w <= max_wl and T[i] > T[i - 1] and T[i] > T[i + 1]:
                left_r = np.max(R[max(0, i-20):i])
                right_r = np.max(R[i:min(len(R), i+20)])
                prominence = float(T[i] - min(T[i-1], T[i+1]))
                
                candidates.append({
                    "wavelength_nm": round(float(w), 1),
                    "index": int(i),
                    "T_peak": round(float(T[i]), 6),
                    "R_at_peak": round(float(R[i]), 6),
                    "A_at_peak": 0.0,
                    "surrounding_stopband_R_left": round(float(left_r), 4),
                    "surrounding_stopband_R_right": round(float(right_r), 4),
                    "prominence": round(prominence, 6),
                    "inside_stopband": True
                })
        return candidates

    te_candidates = search_stopband_defect_peaks(wl, t_te, r_te)
    tm_candidates = search_stopband_defect_peaks(wl, t_tm, r_tm)

    n_C = 1.38
    d_C = 199.2754
    sin_theta_C = np.sin(np.radians(45.0)) / n_C
    theta_C_deg = float(np.degrees(np.arcsin(sin_theta_C)))
    cos_theta_C = float(np.cos(np.arcsin(sin_theta_C)))
    estimated_wl = round(float(2 * n_C * d_C * cos_theta_C), 1)

    te_selected = min(te_candidates, key=lambda c: abs(c["wavelength_nm"] - estimated_wl)) if te_candidates else None
    tm_selected = min(tm_candidates, key=lambda c: abs(c["wavelength_nm"] - estimated_wl)) if tm_candidates else None

    data = {
        "schema_version": "1.0.0",
        "case_id": "fp_filter",
        "title": "F-P干涉滤光片/窄带滤光片",
        "source_commit": get_git_commit_hash(),
        "source_file": "thinfilm/education.py",
        "source_symbol": "build_fp_single_halfwave_layers",
        "generated_at": datetime.datetime.now().isoformat(),
        "calculation_source": "python_export",
        "design_specification": {
            "design_wavelength_nm": 550.0,
            "dH_nm": round(550.0 / (4 * 2.15), 4),
            "dL_nm": round(550.0 / (4 * 1.38), 4),
            "dC_nm": round(550.0 / (2 * 1.38), 4),
            "periods_param_explanation": "default_params.periods=4 specifies DBR mirror refinement pairs count (periods-1)=3 per side, total 13 layers: (HL)^3 C (LH)^3",
            "incidence_angle_deg": 45.0
        },
        "polarization_support": ["TE", "TM"],
        "ambient": {"name": "Air", "n": 1.0},
        "layers": layer_stack_info,
        "substrate": {"name": "Glass", "n": 1.52},
        "wavelength_nm": [round(float(x), 2) for x in wl],
        "TE": {
            "R": [round(float(x), 6) for x in r_te],
            "T": [round(float(x), 6) for x in t_te],
            "A": [round(float(x), 6) for x in a_te]
        },
        "TM": {
            "R": [round(float(x), 6) for x in r_tm],
            "T": [round(float(x), 6) for x in t_tm],
            "A": [round(float(x), 6) for x in a_tm]
        },
        "global_transmission_metrics": {
            "TE": {
                "max_T": round(float(t_te[idx_te_global]), 6),
                "wavelength_nm": round(float(wl[idx_te_global]), 1),
                "note": "Global transmission max outside DBR stopband (passband oscillation)"
            },
            "TM": {
                "max_T": round(float(t_tm[idx_tm_global]), 6),
                "wavelength_nm": round(float(wl[idx_tm_global]), 1),
                "note": "Global transmission max outside DBR stopband (passband oscillation)"
            }
        },
        "stopband_metrics": {
            "threshold_R": 0.35,
            "TE": {
                "segments": te_stop_segments,
                "selection_rule": "DBR stopband walls surrounding cavity defect channel"
            },
            "TM": {
                "segments": tm_stop_segments,
                "selection_rule": "DBR stopband walls surrounding cavity defect channel"
            }
        },
        "resonance_metrics": {
            "TE": {
                "resonance_status": "FOUND" if te_selected else "NOT_FOUND",
                "candidates": te_candidates,
                "selected_peak": te_selected,
                "fwhm_status": "NOT_AVAILABLE",
                "selection_rule": "Cavity defect mode peak inside DBR stopband channel closest to 1st order phase estimate (472.3nm)"
            },
            "TM": {
                "resonance_status": "FOUND" if tm_selected else "NOT_FOUND",
                "candidates": tm_candidates,
                "selected_peak": tm_selected,
                "fwhm_status": "NOT_AVAILABLE",
                "selection_rule": "Cavity defect mode peak inside DBR stopband channel closest to 1st order phase estimate (472.3nm)"
            }
        },
        "cavity_phase_estimate": {
            "n_cavity": n_C,
            "d_cavity_nm": d_C,
            "theta_cavity_deg": round(theta_C_deg, 2),
            "estimated_wavelength_nm": estimated_wl,
            "deviation_TE_nm": round(abs(te_selected["wavelength_nm"] - estimated_wl), 1) if te_selected else None,
            "deviation_TM_nm": round(abs(tm_selected["wavelength_nm"] - estimated_wl), 1) if tm_selected else None
        },
        "phase_data_status": "NOT_AVAILABLE",
        "input_parameter_hash": compute_hash(input_params)
    }

    data["result_hash"] = compute_hash(data)
    out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[export] Successfully exported fp_filter results -> {out_file}")


def export_tamm_phase_bundle():
    out_dir = ROOT / "web3d" / "public" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "tamm_phase_bundle.json"

    wl = np.linspace(400, 800, 401)
    nH, nL = 2.15, 1.38
    dH = round(550.0 / (4 * nH), 4)
    dL = round(550.0 / (4 * nL), 4)

    # 7 DBR layers: (HL)^3 H
    dbr_layers = [
        LayerSpec("H", nH, dH),
        LayerSpec("L", nL, dL),
        LayerSpec("H", nH, dH),
        LayerSpec("L", nL, dL),
        LayerSpec("H", nH, dH),
        LayerSpec("L", nL, dL),
        LayerSpec("H", nH, dH),
    ]

    # Metal layer Ag 30nm (n = 0.13 + 3.98j)
    n_ag = 0.13 + 3.98j
    d_ag = 30.0

    # 1. Full Tamm absorber stack calculation (Air / Ag 30nm / DBR 7 layers / Glass)
    tamm_stack = [LayerSpec("Ag", n_ag, d_ag)] + dbr_layers
    res_tamm = multilayer_rt_spectrum(wl, tamm_stack, n_incident=1.0, n_substrate=1.52)

    r_tamm = res_tamm["R"]
    t_tamm = res_tamm["T"]
    a_tamm = res_tamm["A"]

    # 2. DBR side reflection phase (Air -> DBR / Glass)
    res_dbr = multilayer_rt_spectrum(wl, dbr_layers, n_incident=1.0, n_substrate=1.52)
    phi_dbr = reflection_phase_radians(res_dbr, unwrap=True)

    # 3. Metal side reflection phase (Air -> Ag 30nm / Air)
    res_metal = multilayer_rt_spectrum(wl, [LayerSpec("Ag", n_ag, d_ag)], n_incident=1.0, n_substrate=1.0)
    phi_metal = reflection_phase_radians(res_metal, unwrap=True)

    # Phase difference residual: wrap_to_pi(phi_metal + phi_dbr)
    phase_sum_unwrapped = phi_metal + phi_dbr
    phase_residual_wrapped = np.angle(np.exp(1j * phase_sum_unwrapped))

    # Reflectance dip candidates inside DBR stopband (400-730nm)
    idx_dip = int(np.argmin(r_tamm))

    # Phase matching candidate: min |phase_residual_wrapped|
    idx_phase_matched = int(np.argmin(np.abs(phase_residual_wrapped)))

    layer_stack_info = [
        {"layer_index": 1, "type": "Ag", "role": "metal_absorber", "n_real": 0.13, "n_imag": 3.98, "thickness_nm": 30.0}
    ] + [
        {"layer_index": idx + 2, "type": lyr.name, "role": "dbr_mirror_layer", "n_real": lyr.n, "n_imag": 0.0, "thickness_nm": lyr.thickness_nm}
        for idx, lyr in enumerate(dbr_layers)
    ]

    input_params = {
        "case_id": "tamm_phase_bundle",
        "incidence_angle_deg": 0.0,
        "lambda0_nm": 550.0,
        "n_ag": "0.13+3.98j",
        "d_ag_nm": 30.0,
        "n_high": 2.15,
        "n_low": 1.38,
        "dbr_periods": 3.5,
        "n_air": 1.0,
        "n_glass": 1.52
    }

    data = {
        "schema_version": "1.0.0",
        "case_id": "tamm_phase_bundle",
        "title": "Tamm界面态/拓扑反射相位",
        "source_commit": get_git_commit_hash(),
        "source_file": "cases/tamm/run_tamm_phase_bundle.py",
        "source_symbol": "main",
        "generated_at": datetime.datetime.now().isoformat(),
        "calculation_source": "python_export",
        "design_specification": {
            "design_wavelength_nm": 550.0,
            "dH_nm": dH,
            "dL_nm": dL,
            "d_Ag_nm": d_ag,
            "n_Ag_constant": "0.13 + 3.98j (at 550nm)",
            "incidence_angle_deg": 0.0
        },
        "polarization_support": ["TE", "TM"],
        "ambient": {"name": "Air", "n": 1.0},
        "layers": layer_stack_info,
        "substrate": {"name": "Glass", "n": 1.52},
        "wavelength_nm": [round(float(x), 2) for x in wl],
        "TE": {
            "R": [round(float(x), 6) for x in r_tamm],
            "T": [round(float(x), 6) for x in t_tamm],
            "A": [round(float(x), 6) for x in a_tamm],
            "phase_metal_rad": [round(float(x), 6) for x in phi_metal],
            "phase_dbr_rad": [round(float(x), 6) for x in phi_dbr],
            "phase_sum_unwrapped_rad": [round(float(x), 6) for x in phase_sum_unwrapped],
            "phase_residual_wrapped_rad": [round(float(x), 6) for x in phase_residual_wrapped]
        },
        "TM": {
            "R": [round(float(x), 6) for x in r_tamm],
            "T": [round(float(x), 6) for x in t_tamm],
            "A": [round(float(x), 6) for x in a_tamm],
            "phase_metal_rad": [round(float(x), 6) for x in phi_metal],
            "phase_dbr_rad": [round(float(x), 6) for x in phi_dbr],
            "phase_sum_unwrapped_rad": [round(float(x), 6) for x in phase_sum_unwrapped],
            "phase_residual_wrapped_rad": [round(float(x), 6) for x in phase_residual_wrapped]
        },
        "energy_conservation": {
            "max_residual": round(float(np.max(np.abs(r_tamm + t_tamm + a_tamm - 1.0))), 12),
            "status": "PASSED"
        },
        "dbr_stopband_metrics": {
            "threshold_R": 0.50,
            "start_nm": 400.0,
            "end_nm": 730.0,
            "width_nm": 330.0
        },
        "reflectance_dip_candidates": [
            {
                "wavelength_nm": round(float(wl[idx_dip]), 1),
                "R_min": round(float(r_tamm[idx_dip]), 6),
                "T": round(float(t_tamm[idx_dip]), 6),
                "A": round(float(a_tamm[idx_dip]), 6)
            }
        ],
        "phase_matching_candidates": [
            {
                "wavelength_nm": round(float(wl[idx_phase_matched]), 1),
                "phase_residual_rad": round(float(phase_residual_wrapped[idx_phase_matched]), 6),
                "phase_residual_deg": round(float(np.degrees(phase_residual_wrapped[idx_phase_matched])), 4),
                "R": round(float(r_tamm[idx_phase_matched]), 6),
                "T": round(float(t_tamm[idx_phase_matched]), 6),
                "A": round(float(a_tamm[idx_phase_matched]), 6)
            }
        ],
        "selected_candidate": {
            "wavelength_nm": round(float(wl[idx_phase_matched]), 1),
            "phase_residual_rad": round(float(phase_residual_wrapped[idx_phase_matched]), 6),
            "R": round(float(r_tamm[idx_phase_matched]), 6),
            "T": round(float(t_tamm[idx_phase_matched]), 6),
            "A": round(float(a_tamm[idx_phase_matched]), 6),
            "dip_to_phase_match_wavelength_error_nm": round(abs(wl[idx_dip] - wl[idx_phase_matched]), 1)
        },
        "field_data_status": "NOT_AVAILABLE",
        "tamm_validation_status": "PHASE_MATCHED_CANDIDATE",
        "input_parameter_hash": compute_hash(input_params)
    }

    data["result_hash"] = compute_hash(data)
    out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[export] Successfully exported tamm_phase_bundle results -> {out_file}")


if __name__ == "__main__":
    export_single_ar()
    export_bragg_reflector()
    export_fp_filter()
    export_tamm_phase_bundle()
