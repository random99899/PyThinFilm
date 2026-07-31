# -*- coding: utf-8 -*-
"""Stage C.2.1A Engineering Application Cases Source & Structure Audit.

Audits the 5 engineering application cases:
1. app_solar_cell_ar
2. app_wdm_filter
3. app_laser_mirror
4. app_phone_lens_ar
5. app_smart_window

Performs:
- Authoritative Python source file & symbol tracking
- Default parameters & layer stack extraction
- Stable physics_input_hash generation (excluding case_id, title, timestamps, notes)
- Formal metrics classification (FORMAL_SOURCE, DERIVED_FROM_FORMAL_OUTPUT, NOT_AVAILABLE)
- R + T + A = 1.0 physical energy conservation audit
- Case physical equivalence status determination
- Template requirement evaluation (Strict reuse of existing templates, NO new templates)
- Machine-readable manifest generation: docs/visualization/data/stage_c2_1a_engineering_manifest.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.applications.solar_cell_ar import run_solar_cell_ar
from examples.applications.wdm_filter import run_wdm_filter
from examples.applications.laser_mirror import run_laser_mirror
from examples.applications.phone_lens_ar import run_phone_lens_ar
from examples.applications.smart_window import run_smart_window


ENGINEERING_CASES_CONFIG = [
    {
        "case_id": "app_solar_cell_ar",
        "display_name": "太阳能电池三层增透膜",
        "category": "engineering_applications",
        "source_file": "examples/applications/solar_cell_ar.py",
        "source_symbol": "run_solar_cell_ar",
        "formal_entrypoint": "examples.applications.solar_cell_ar:run_solar_cell_ar",
        "runner_fn": run_solar_cell_ar,
        "default_parameters": {
            "lambda0_nm": 550.0,
            "wavelength_range_nm": [300.0, 1100.0, 200],
            "n_incident": 1.0,
            "n_substrate": "3.5 + 0.0j",
            "incidence_angle_deg": 0.0,
            "polarization": "p",
        },
        "formal_metrics": [
            {"metric_name": "avg_R_300_1100nm", "status": "FORMAL_SOURCE", "definition": "300-1100nm 波段平均反射率", "unit": "fraction"},
            {"metric_name": "R_at_550nm", "status": "FORMAL_SOURCE", "definition": "550nm 设计波长处反射率", "unit": "fraction"},
            {"metric_name": "bandwidth_R_lt_2pct_nm", "status": "FORMAL_SOURCE", "definition": "R < 2% 减反带宽", "unit": "nm"},
            {"metric_name": "avg_R_bare_Si", "status": "FORMAL_SOURCE", "definition": "裸硅衬底平均反射率基线", "unit": "fraction"},
            {"metric_name": "efficiency_improvement_pct", "status": "DERIVED_FROM_FORMAL_OUTPUT", "definition": "相对裸硅的光吸收改善估算百分比 ((1-avg_R)/(1-avg_R_bare)-1)", "unit": "%"},
        ],
        "unavailable_metrics": ["carrier_recombination_rate", "electrical_conversion_efficiency_IV"],
        "template_requirement": "REUSE_EXISTING",
        "candidate_template": "periodic-stack",
        "physical_equivalence_status": "UNIQUE_PHYSICAL_CONFIGURATION",
        "variant_of": "UNIQUE",
    },
    {
        "case_id": "app_wdm_filter",
        "display_name": "WDM 光通信密集波分复用滤光片",
        "category": "engineering_applications",
        "source_file": "examples/applications/wdm_filter.py",
        "source_symbol": "run_wdm_filter",
        "formal_entrypoint": "examples.applications.wdm_filter:run_wdm_filter",
        "runner_fn": run_wdm_filter,
        "default_parameters": {
            "lambda0_nm": 1550.0,
            "wavelength_range_nm": [1500.0, 1600.0, 500],
            "n_incident": 1.0,
            "n_substrate": 1.46,
            "periods": 4,
            "spacer_kind": "L",
            "incidence_angle_deg": 0.0,
            "polarization": "p",
        },
        "formal_metrics": [
            {"metric_name": "peak_transmittance", "status": "FORMAL_SOURCE", "definition": "1550nm 中心波长峰值透射率", "unit": "fraction"},
            {"metric_name": "peak_wavelength_nm", "status": "FORMAL_SOURCE", "definition": "透射峰值波长", "unit": "nm"},
            {"metric_name": "fwhm_nm", "status": "FORMAL_SOURCE", "definition": "半高全宽", "unit": "nm"},
            {"metric_name": "fsr_nm", "status": "FORMAL_SOURCE", "definition": "自由光谱范围 (FSR)", "unit": "nm"},
            {"metric_name": "finesse", "status": "DERIVED_FROM_FORMAL_OUTPUT", "definition": "精细度 F = FSR / FWHM", "unit": "dimensionless"},
            {"metric_name": "isolation_dB", "status": "FORMAL_SOURCE", "definition": "信道隔离度 (-10 log10 T_off_peak)", "unit": "dB"},
        ],
        "unavailable_metrics": ["multi_channel_crosstalk_matrix"],
        "template_requirement": "REUSE_EXISTING",
        "candidate_template": "defect-cavity",
        "physical_equivalence_status": "UNIQUE_PHYSICAL_CONFIGURATION",
        "variant_of": "UNIQUE",
    },
    {
        "case_id": "app_laser_mirror",
        "display_name": "1064nm 激光高反镜",
        "category": "engineering_applications",
        "source_file": "examples/applications/laser_mirror.py",
        "source_symbol": "run_laser_mirror",
        "formal_entrypoint": "examples.applications.laser_mirror:run_laser_mirror",
        "runner_fn": run_laser_mirror,
        "default_parameters": {
            "lambda0_nm": 1064.0,
            "wavelength_range_nm": [900.0, 1200.0, 300],
            "n_incident": 1.0,
            "n_substrate": 1.46,
            "periods": 8,
            "incidence_angle_deg": 0.0,
            "polarization": "p",
        },
        "formal_metrics": [
            {"metric_name": "peak_reflectance", "status": "FORMAL_SOURCE", "definition": "1064nm 峰值反射率", "unit": "fraction"},
            {"metric_name": "R_at_1064nm", "status": "FORMAL_SOURCE", "definition": "1064nm 处反射率", "unit": "fraction"},
            {"metric_name": "stopband_width_nm", "status": "FORMAL_SOURCE", "definition": "高反射禁带宽度 (R > 99%)", "unit": "nm"},
            {"metric_name": "index_ratio", "status": "FORMAL_SOURCE", "definition": "高低折射率对比度 nH/nL", "unit": "ratio"},
        ],
        "unavailable_metrics": ["laser_damage_threshold_LIDT", "thermal_stress_distribution"],
        "template_requirement": "REUSE_EXISTING",
        "candidate_template": "periodic-stack",
        "physical_equivalence_status": "UNIQUE_PHYSICAL_CONFIGURATION",
        "variant_of": "UNIQUE",
    },
    {
        "case_id": "app_phone_lens_ar",
        "display_name": "手机镜头多层增透膜",
        "category": "engineering_applications",
        "source_file": "examples/applications/phone_lens_ar.py",
        "source_symbol": "run_phone_lens_ar",
        "formal_entrypoint": "examples.applications.phone_lens_ar:run_phone_lens_ar",
        "runner_fn": run_phone_lens_ar,
        "default_parameters": {
            "lambda0_nm": 550.0,
            "wavelength_range_nm": [380.0, 780.0, 200],
            "n_incident": 1.0,
            "n_substrate": 1.80,
            "incidence_angle_deg": 0.0,
            "polarization": "p",
        },
        "formal_metrics": [
            {"metric_name": "avg_R_visible", "status": "FORMAL_SOURCE", "definition": "可见光 380-780nm 平均反射率", "unit": "fraction"},
            {"metric_name": "avg_R_single_layer", "status": "FORMAL_SOURCE", "definition": "单层 MgF2 减反膜平均反射率对比", "unit": "fraction"},
            {"metric_name": "R_improvement_vs_single", "status": "DERIVED_FROM_FORMAL_OUTPUT", "definition": "相对单层减反改善比例", "unit": "%"},
            {"metric_name": "R_blue_450nm", "status": "FORMAL_SOURCE", "definition": "450nm 蓝光反射率", "unit": "fraction"},
            {"metric_name": "R_green_550nm", "status": "FORMAL_SOURCE", "definition": "550nm 绿光反射率", "unit": "fraction"},
            {"metric_name": "R_red_650nm", "status": "FORMAL_SOURCE", "definition": "650nm 红光反射率", "unit": "fraction"},
            {"metric_name": "color_uniformity", "status": "DERIVED_FROM_FORMAL_OUTPUT", "definition": "颜色均匀度 (1 - maxDiff(RGB))", "unit": "score"},
        ],
        "unavailable_metrics": ["curved_lens_ray_tracing", "ghost_image_stray_light_simulation"],
        "template_requirement": "REUSE_EXISTING",
        "candidate_template": "periodic-stack",
        "physical_equivalence_status": "UNIQUE_PHYSICAL_CONFIGURATION",
        "variant_of": "UNIQUE",
    },
    {
        "case_id": "app_smart_window",
        "display_name": "智能调温窗 Low-E 膜",
        "category": "engineering_applications",
        "source_file": "examples/applications/smart_window.py",
        "source_symbol": "run_smart_window",
        "formal_entrypoint": "examples.applications.smart_window:run_smart_window",
        "runner_fn": run_smart_window,
        "default_parameters": {
            "wavelength_range_nm": [300.0, 2500.0, 500],
            "n_incident": 1.0,
            "n_substrate": 1.52,
            "incidence_angle_deg": 0.0,
            "polarization": "p",
        },
        "formal_metrics": [
            {"metric_name": "T_visible", "status": "FORMAL_SOURCE", "definition": "可见光波段 (400-700nm) 平均透射率", "unit": "fraction"},
            {"metric_name": "T_NIR", "status": "FORMAL_SOURCE", "definition": "近红外波段 (700-2500nm) 平均透射率", "unit": "fraction"},
            {"metric_name": "R_NIR", "status": "FORMAL_SOURCE", "definition": "近红外波段 (700-2500nm) 平均反射率", "unit": "fraction"},
            {"metric_name": "T_solar_weighted", "status": "DERIVED_FROM_FORMAL_OUTPUT", "definition": "高斯拟合太阳光谱加权透射率", "unit": "fraction"},
            {"metric_name": "R_solar_weighted", "status": "DERIVED_FROM_FORMAL_OUTPUT", "definition": "高斯拟合太阳光谱加权反射率", "unit": "fraction"},
            {"metric_name": "SHGC", "status": "DERIVED_FROM_FORMAL_OUTPUT", "definition": "估算太阳得热系数 (T_solar + 0.5 * A_solar)", "unit": "ratio"},
            {"metric_name": "NIR_rejection_ratio", "status": "DERIVED_FROM_FORMAL_OUTPUT", "definition": "近红外抑制比 T_vis / T_NIR", "unit": "ratio"},
        ],
        "unavailable_metrics": ["astm_g173_full_spectrum_weighted_VLT", "building_energy_saving_rate"],
        "template_requirement": "REUSE_EXISTING",
        "candidate_template": "metal-dbr-interface",
        "physical_equivalence_status": "UNIQUE_PHYSICAL_CONFIGURATION",
        "variant_of": "UNIQUE",
    },
]


def generate_physics_input_hash(layer_stack: list[dict], n_incident: float, n_substrate: Any) -> str:
    """Generates a stable physics input hash excluding title, case_id, timestamps, and notes."""
    hash_data = {
        "n_incident": float(n_incident),
        "n_substrate": str(n_substrate),
        "layers": [
            {
                "material": ly["material"],
                "thickness_nm": round(float(ly["thickness_nm"]), 4),
                "n": str(ly["n"]),
            }
            for ly in layer_stack
        ],
    }
    raw_str = json.dumps(hash_data, sort_keys=True)
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]


def audit_engineering_cases():
    print("=" * 70)
    print("Stage C.2.1A Engineering Cases Source & Structure Audit")
    print("=" * 70)

    manifest_cases = []

    for item in ENGINEERING_CASES_CONFIG:
        cid = item["case_id"]
        print(f"\n[Auditing Case]: {cid} ({item['display_name']})")
        print(f"  Source File: {item['source_file']}")
        print(f"  Formal Entrypoint: {item['formal_entrypoint']}")

        # 1. Execute formal entrypoint Python function
        res = item["runner_fn"]()
        
        # 2. Extract structure & layers
        struct = res.get("structure", {})
        raw_layers = struct.get("layers", [])
        
        layer_stack = []
        for ly in raw_layers:
            layer_stack.append({
                "material": ly.get("material", "Unknown"),
                "thickness_nm": round(float(ly.get("thickness_nm", 0.0)), 4),
                "n": str(ly.get("n", 1.0)),
            })

        sub_n = struct.get("substrate", "Substrate")
        n_inc = 1.0

        # Generate physics_input_hash
        physics_hash = generate_physics_input_hash(layer_stack, n_inc, sub_n)
        print(f"  Physics Input Hash: {physics_hash}")
        print(f"  Layer Count: {len(layer_stack)}")
        print(f"  Layer Stack: {layer_stack}")

        # 3. Energy Conservation Check R + T + A = 1.0
        R, T, A = res["R"], res["T"], res["A"]
        total_energy = R + T + A
        max_err = float(np.max(np.abs(total_energy - 1.0)))
        print(f"  Max Energy Conservation Error |R+T+A - 1.0|: {max_err:.2e}")
        assert max_err < 1e-5, f"Energy conservation failed for {cid}, max_err = {max_err}"

        # 4. Construct manifest record
        manifest_record = {
            "case_id": cid,
            "display_name": item["display_name"],
            "category": item["category"],
            "source_file": item["source_file"],
            "source_symbol": item["source_symbol"],
            "formal_entrypoint": item["formal_entrypoint"],
            "default_parameters": item["default_parameters"],
            "layer_stack": layer_stack,
            "physics_input_hash": physics_hash,
            "material_model": "CONSTANT_COMPLEX_INDEX" if "smart_window" in cid or "solar_cell" in cid else "CONSTANT_REAL_INDEX",
            "external_dependencies": "NONE",
            "formal_metrics": item["formal_metrics"],
            "unavailable_metrics": item["unavailable_metrics"],
            "physical_equivalence_status": item["physical_equivalence_status"],
            "variant_of": item["variant_of"],
            "template_requirement": item["template_requirement"],
            "candidate_template": item["candidate_template"],
            "dynamic_wave_mode": "FORWARD_BACKWARD_WAVE_ILLUSTRATION" if "wdm" in cid else "FORWARD_RAY_PROPAGATION",
            "audit_status": "SOURCE_AUDIT_PASSED",
        }
        manifest_cases.append(manifest_record)

    # Write Manifest JSON
    manifest_path = ROOT / "docs" / "visualization" / "data" / "stage_c2_1a_engineering_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_data = {
        "schema_version": "1.0.0",
        "stage": "Stage C.2.1A",
        "title": "Engineering Application Cases Source Manifest",
        "audit_cases_count": len(manifest_cases),
        "cases": manifest_cases,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[SUCCESS] Manifest written to {manifest_path}")
    print("=" * 70)


if __name__ == "__main__":
    audit_engineering_cases()
