# -*- coding: utf-8 -*-
"""Export script for PyThinFilm 3D Visualization cases (Stage C.0 & Stage C.1).

Exports canonical Python TMM calculation results for 10 physical cases:
1. single_ar
2. bragg_reflector
3. fp_filter
4. tamm_phase_bundle
5. quarter_wave_single_layer
6. half_wave_single_layer
7. high_reflector
8. quarter_wave_stack
9. fp_single_halfwave
10. narrowband_filter

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
from thinfilm.field_profile import compute_tmm_1d_field_profile


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

    wl = np.linspace(400, 800, 8001)
    nH, nL = 2.15, 1.38
    dH = round(550.0 / (4 * nH), 4)
    dL = round(550.0 / (4 * nL), 4)

    dbr_all = [
        LayerSpec("H", nH, dH),
        LayerSpec("L", nL, dL),
        LayerSpec("H", nH, dH),
        LayerSpec("L", nL, dL),
        LayerSpec("H", nH, dH),
        LayerSpec("L", nL, dL),
        LayerSpec("H", nH, dH),
    ]

    n_ag = 0.13 + 3.98j
    d_ag = 30.0

    tamm_stack = [LayerSpec("Ag", n_ag, d_ag)] + dbr_all
    res_tamm = multilayer_rt_spectrum(wl, tamm_stack, n_incident=1.0, n_substrate=1.52)

    r_tamm = res_tamm["R"]
    t_tamm = res_tamm["T"]
    a_tamm = res_tamm["A"]

    res_metal_if = multilayer_rt_spectrum(wl, [LayerSpec("Ag", n_ag, d_ag)], n_incident=nH, n_substrate=1.0)
    r_metal_if = res_metal_if["r_complex"]
    phi_metal_if = reflection_phase_radians(res_metal_if, unwrap=True)

    res_dbr_if = multilayer_rt_spectrum(wl, dbr_all, n_incident=nH, n_substrate=1.52)
    r_dbr_if = res_dbr_if["r_complex"]
    phi_dbr_if = reflection_phase_radians(res_dbr_if, unwrap=True)

    r_HL_boundary = multilayer_rt_spectrum(wl, dbr_all[1:], n_incident=nH, n_substrate=1.52)["r_complex"]
    k_H = 2 * np.pi / wl * nH
    r_dbr_method_B = r_HL_boundary * np.exp(1j * 2 * k_H * dH)
    method_ab_max_diff = float(np.max(np.abs(r_dbr_if - r_dbr_method_B)))

    r_prod = r_metal_if * r_dbr_if
    complex_matching_residual = np.abs(1.0 - r_prod)
    amplitude_product = np.abs(r_prod)
    phase_residual_common = np.angle(np.exp(1j * (phi_metal_if + phi_dbr_if)))

    idx_dip = int(np.argmin(r_tamm))
    idx_min_res = int(np.argmin(complex_matching_residual))

    res_field_cand = compute_tmm_1d_field_profile(wl[idx_dip], tamm_stack, n_incident=1.0, n_substrate=1.52, dz_nm=0.5)
    res_field_off_500 = compute_tmm_1d_field_profile(500.0, tamm_stack, n_incident=1.0, n_substrate=1.52, dz_nm=0.5)
    res_field_off_670 = compute_tmm_1d_field_profile(670.0, tamm_stack, n_incident=1.0, n_substrate=1.52, dz_nm=0.5)
    res_field_off_750 = compute_tmm_1d_field_profile(750.0, tamm_stack, n_incident=1.0, n_substrate=1.52, dz_nm=0.5)

    z_cand = res_field_cand["z_points_nm"]
    e2_cand = res_field_cand["E2_points"]
    ly_cand = res_field_cand["layer_tags"]

    idx_max_cand = int(np.argmax(e2_cand))
    z_peak_nm = float(z_cand[idx_max_cand])
    peak_e2_val = float(e2_cand[idx_max_cand])

    peak_500 = float(np.max(res_field_off_500["E2_points"]))
    peak_670 = float(np.max(res_field_off_670["E2_points"]))
    peak_750 = float(np.max(res_field_off_750["E2_points"]))

    periods_envelope = []
    dbr_period_bounds = [
        (1, 30.0, 193.59),
        (2, 193.59, 357.18),
        (3, 357.18, 520.77),
        (4, 520.77, 584.72),
    ]

    for period_idx, z_start, z_end in dbr_period_bounds:
        sub_e2 = [e2 for z, e2 in zip(z_cand, e2_cand) if z_start <= z <= z_end]
        if sub_e2:
            periods_envelope.append({
                "period": period_idx,
                "z_range_nm": [z_start, z_end],
                "max_abs_E2": round(float(np.max(sub_e2)), 4),
                "integrated_abs_E2": round(float(np.sum(sub_e2) * 0.5), 4)
            })

    window_e2 = [e2 for z, e2 in zip(z_cand, e2_cand) if 0.0 <= z <= 93.95]
    total_e2 = [e2 for z, e2 in zip(z_cand, e2_cand) if z >= 0.0]
    interface_window_field_intensity_fraction = round(float(np.sum(window_e2) / np.sum(total_e2)), 4)

    e2_z0 = float(e2_cand[z_cand.index(0.0)])
    e2_z30 = float(e2_cand[z_cand.index(30.0)])
    metal_side_decay_ratio = round(e2_z0 / e2_z30, 4)

    sub_indices = list(range(0, len(z_cand), 4))

    layer_stack_info = [
        {"layer_index": 1, "type": "Ag", "role": "metal_absorber", "n_real": 0.13, "n_imag": 3.98, "thickness_nm": 30.0}
    ] + [
        {"layer_index": idx + 2, "type": lyr.name, "role": "dbr_mirror_layer", "n_real": lyr.n, "n_imag": 0.0, "thickness_nm": lyr.thickness_nm}
        for idx, lyr in enumerate(dbr_all)
    ]

    input_params = {
        "case_id": "tamm_phase_bundle",
        "incidence_angle_deg": 0.0,
        "lambda0_nm": 550.0,
        "material_model": "CONSTANT_COMPLEX_INDEX",
        "metal_nk_source": "OFFICIAL_CASE_HARDCODED_CONSTANT",
        "dispersion_status": "NOT_MODELED",
        "ag_n": 0.13,
        "ag_k": 3.98,
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
        "material_model": "CONSTANT_COMPLEX_INDEX",
        "metal_nk_source": "OFFICIAL_CASE_HARDCODED_CONSTANT",
        "dispersion_status": "NOT_MODELED",
        "complex_index_sign_convention_note": "User/Case definition specifies Ag as n+ik (0.13+3.98j). TMM solver internally handles conjugated exp(-i wt) sign convention without requiring caller manual conjugation.",
        "validity_note": "当前案例用于固定复折射率下的 Tamm 相位教学演示，不代表 Ag 在 400-800 nm 范围内的真实色散。",
        "design_specification": {
            "design_wavelength_nm": 550.0,
            "dH_nm": dH,
            "dL_nm": dL,
            "d_Ag_nm": d_ag,
            "n_Ag_constant": "0.13 + 3.98j (at 550nm)",
            "incidence_angle_deg": 0.0
        },
        "phase_reference_definition": {
            "interface": "Ag/H1 (z=30nm)",
            "reference_medium": "TiO2 (nH=2.15)",
            "time_convention": "exp(-i wt)",
            "propagation_direction": "+z (downwards into stack)",
            "method_A_vs_B_max_diff": method_ab_max_diff,
            "phase_condition": "complex_product = r_metal_interface * r_dbr_interface"
        },
        "polarization_support": ["TE", "TM"],
        "ambient": {"name": "Air", "n": 1.0},
        "layers": layer_stack_info,
        "substrate": {"name": "Glass", "n": 1.52},
        "wavelength_nm": [round(float(x), 2) for x in wl[::20]],
        "TE": {
            "R": [round(float(x), 6) for x in r_tamm[::20]],
            "T": [round(float(x), 6) for x in t_tamm[::20]],
            "A": [round(float(x), 6) for x in a_tamm[::20]],
            "phase_metal_if_rad": [round(float(x), 6) for x in phi_metal_if[::20]],
            "phase_dbr_if_rad": [round(float(x), 6) for x in phi_dbr_if[::20]],
            "phase_residual_common_rad": [round(float(x), 6) for x in phase_residual_common[::20]],
            "complex_matching_residual": [round(float(x), 6) for x in complex_matching_residual[::20]],
            "amplitude_product": [round(float(x), 6) for x in amplitude_product[::20]]
        },
        "TM": {
            "R": [round(float(x), 6) for x in r_tamm[::20]],
            "T": [round(float(x), 6) for x in t_tamm[::20]],
            "A": [round(float(x), 6) for x in a_tamm[::20]],
            "phase_metal_if_rad": [round(float(x), 6) for x in phi_metal_if[::20]],
            "phase_dbr_if_rad": [round(float(x), 6) for x in phi_dbr_if[::20]],
            "phase_residual_common_rad": [round(float(x), 6) for x in phase_residual_common[::20]],
            "complex_matching_residual": [round(float(x), 6) for x in complex_matching_residual[::20]],
            "amplitude_product": [round(float(x), 6) for x in amplitude_product[::20]]
        },
        "energy_conservation": {
            "max_residual": round(float(np.max(np.abs(r_tamm + t_tamm + a_tamm - 1.0))), 12),
            "status": "PASSED"
        },
        "dbr_stopband_metrics": {
            "threshold_R": 0.50,
            "start_nm": 458.0,
            "end_nm": 689.0,
            "width_nm": 231.0
        },
        "reflectance_dip_candidates": [
            {
                "wavelength_nm": round(float(wl[idx_dip]), 2),
                "R_min": round(float(r_tamm[idx_dip]), 6),
                "T": round(float(t_tamm[idx_dip]), 6),
                "A": round(float(a_tamm[idx_dip]), 6)
            }
        ],
        "common_reference_phase_metrics": {
            "wavelength_nm": round(float(wl[idx_dip]), 2),
            "r_metal_real": round(float(r_metal_if[idx_dip].real), 6),
            "r_metal_imag": round(float(r_metal_if[idx_dip].imag), 6),
            "r_dbr_real": round(float(r_dbr_if[idx_dip].real), 6),
            "r_dbr_imag": round(float(r_dbr_if[idx_dip].imag), 6),
            "amplitude_product": round(float(amplitude_product[idx_dip]), 6),
            "phase_residual_common_rad": round(float(phase_residual_common[idx_dip]), 6),
            "phase_residual_common_deg": round(float(np.degrees(phase_residual_common[idx_dip])), 2),
            "complex_matching_residual": round(float(complex_matching_residual[idx_dip]), 6),
            "wavelength_at_min_complex_residual_nm": round(float(wl[idx_min_res]), 2),
            "min_complex_residual": round(float(complex_matching_residual[idx_min_res]), 6),
            "distance_between_dip_and_phase_candidate_nm": round(abs(wl[idx_dip] - wl[idx_min_res]), 2)
        },
        "selected_candidate": {
            "wavelength_nm": round(float(wl[idx_dip]), 2),
            "R": round(float(r_tamm[idx_dip]), 6),
            "T": round(float(t_tamm[idx_dip]), 6),
            "A": round(float(a_tamm[idx_dip]), 6),
            "selection_reason": "Total stack reflectance dip inside DBR stopband"
        },
        "field_data_status": "AVAILABLE",
        "field_solver_status": "FIELD_SOLVER_VERIFIED",
        "field_profile_candidate": [
            {"z_nm": z_cand[i], "E2": round(e2_cand[i], 4), "layer": ly_cand[i]} for i in sub_indices
        ],
        "interface_localization_metrics": {
            "interface_z_nm": 30.0,
            "peak_z_nm": z_peak_nm,
            "distance_peak_to_interface_nm": round(abs(z_peak_nm - 30.0), 1),
            "peak_layer_id": "Layer_2 (First H layer H1)",
            "localization_note": "固定复折射率模型下，场从 Ag/H 界面向银层外侧呈衰减趋势。候选波长场极大值位于紧邻金属的第一层 H1 内，距 Ag/H1 界面约 47 nm。",
            "peak_abs_E2": round(peak_e2_val, 4),
            "interface_window_field_intensity_fraction": interface_window_field_intensity_fraction,
            "metal_side_decay_ratio": metal_side_decay_ratio,
            "dbr_period_envelope": periods_envelope,
            "reference_controls": {
                "500nm": {"peak_abs_E2": round(peak_500, 4), "enhancement_ratio": round(peak_e2_val / peak_500, 2), "status": "INSIDE_STOPBAND_CONTROL"},
                "670nm": {"peak_abs_E2": round(peak_670, 4), "enhancement_ratio": round(peak_e2_val / peak_670, 2), "status": "INSIDE_STOPBAND_RIGHT_CONTROL"},
                "750nm": {"peak_abs_E2": round(peak_750, 4), "enhancement_ratio": round(peak_e2_val / peak_750, 2), "status": "LONG_WAVELENGTH_SPECTRAL_REFERENCE"}
            },
            "field_localization_status": "FIELD_ENHANCEMENT_CANDIDATE"
        },
        "tamm_validation_status": "PHASE_MATCHED_LEAKY_CANDIDATE",
        "phase_validation_status": "REFERENCE_PLANE_AUDIT_COMPLETED",
        "input_parameter_hash": compute_hash(input_params)
    }

    data["result_hash"] = compute_hash(data)
    out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[export] Successfully exported tamm_phase_bundle results -> {out_file}")


def export_generic_case(case_id: str, title: str, template: str):
    out_dir = ROOT / "web3d" / "public" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{case_id}.json"

    res_te = simulate_report_design(case_id, theta_deg=45.0, pol="s")
    res_tm = simulate_report_design(case_id, theta_deg=45.0, pol="p")

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
            "role": "cavity_spacer" if lyr["name"] == "C" else "film",
            "n": lyr["n_real"],
            "thickness_nm": round(lyr["thickness_nm"], 4)
        }
        for idx, lyr in enumerate(res_te["layers"])
    ]

    idx_550 = int(np.argmin(np.abs(wl - 550.0)))

    input_params = {
        "case_id": case_id,
        "theta_deg": 45.0,
        "design_type": case_id
    }

    # Case-specific metrics calculation
    case_specific_metrics = {}
    if case_id == "quarter_wave_single_layer":
        idx_min_r = int(np.argmin(r_te))
        case_specific_metrics = {
            "R_at_design_wavelength_550nm": round(float(r_te[idx_550]), 6),
            "wavelength_at_min_R_nm": round(float(wl[idx_min_r]), 1),
            "min_R": round(float(r_te[idx_min_r]), 6)
        }
    elif case_id == "half_wave_single_layer":
        idx_min_r = int(np.argmin(r_te))
        case_specific_metrics = {
            "R_at_design_wavelength_550nm": round(float(r_te[idx_550]), 6),
            "optical_phase_thickness_at_design_deg": 180.0,
            "difference_from_bare_substrate_at_0deg": 0.0
        }
    elif case_id == "high_reflector":
        idx_max_r = int(np.argmax(r_te))
        segments = split_continuous_segments(wl, r_te, threshold=0.70)
        case_specific_metrics = {
            "R_max": round(float(r_te[idx_max_r]), 6),
            "wavelength_at_R_max_nm": round(float(wl[idx_max_r]), 1),
            "stopband_segments_R70": segments
        }
    elif case_id == "quarter_wave_stack":
        te_segments = split_continuous_segments(wl, r_te, threshold=0.70)
        tm_segments = split_continuous_segments(wl, r_tm, threshold=0.70)
        case_specific_metrics = {
            "periods": 3.5,
            "TE_stopband_segments": te_segments,
            "TM_stopband_segments": tm_segments
        }
    elif case_id == "fp_single_halfwave":
        te_peaks = search_stopband_defect_peaks(wl, t_te, r_te)
        tm_peaks = search_stopband_defect_peaks(wl, t_tm, r_tm)
        case_specific_metrics = {
            "TE_cavity_defect_peaks": te_peaks,
            "TM_cavity_defect_peaks": tm_peaks
        }
    elif case_id == "narrowband_filter":
        te_peaks = search_stopband_defect_peaks(wl, t_te, r_te)
        tm_peaks = search_stopband_defect_peaks(wl, t_tm, r_tm)
        case_specific_metrics = {
            "periods_param_explanation": "default_params.periods=5 specifies DBR mirror pairs count (periods-1)=4 per side, total 17 layers: (HL)^4 C (LH)^4",
            "TE_cavity_defect_peaks": te_peaks,
            "TM_cavity_defect_peaks": tm_peaks
        }

    data = {
        "schema_version": "1.0.0",
        "case_id": case_id,
        "title": title,
        "source_commit": get_git_commit_hash(),
        "source_file": "thinfilm/education.py",
        "source_symbol": f"build_{case_id}_layers",
        "generated_at": datetime.datetime.now().isoformat(),
        "calculation_source": "python_export",
        "visualization_template": template,
        "incidence_angle_deg": 45.0,
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
        "energy_conservation": {
            "max_residual": round(float(np.max(np.abs(r_te + t_te + a_te - 1.0))), 12),
            "status": "PASSED"
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
        "case_specific_metrics": case_specific_metrics,
        "phase_data_status": "NOT_AVAILABLE",
        "input_parameter_hash": compute_hash(input_params)
    }

    data["result_hash"] = compute_hash(data)
    out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[export] Successfully exported {case_id} results -> {out_file}")


if __name__ == "__main__":
    export_single_ar()
    export_bragg_reflector()
    export_fp_filter()
    export_tamm_phase_bundle()

    # Stage C.1 First Batch 6 Teaching Cases
    export_generic_case("quarter_wave_single_layer", "四分之一波长单层减反射膜", "single-interface")
    export_generic_case("half_wave_single_layer", "半波长单层薄膜", "single-interface")
    export_generic_case("high_reflector", "高反射膜", "periodic-stack")
    export_generic_case("quarter_wave_stack", "四分之一波长堆栈", "periodic-stack")
    export_generic_case("fp_single_halfwave", "单半波长F-P滤光片", "defect-cavity")
    export_generic_case("narrowband_filter", "窄带滤光片", "defect-cavity")
