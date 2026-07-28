# -*- coding: utf-8 -*-
"""Export script for PyThinFilm 3D Visualization cases (Stage B.1B).

Exports canonical Python TMM calculation results for single_ar and bragg_reflector into web3d/public/results/<case_id>.json.
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


def get_git_commit_hash():
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(ROOT))
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN_COMMIT"


def compute_hash(data_obj):
    raw = json.dumps(data_obj, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


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

    wl = res_te["wavelength_nm"].tolist()
    r_te = res_te["R"].tolist()
    t_te = res_te["T"].tolist()
    a_te = res_te["A"].tolist()

    r_tm = res_tm["R"].tolist()
    t_tm = res_tm["T"].tolist()
    a_tm = res_tm["A"].tolist()

    # Exact Python layers extracted from res_te['layers']
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
        "periods": 3.5, # 7 layers: H L H L H L H
        "n_air": 1.0,
        "n_glass": 1.52
    }

    idx_550 = int(np.argmin(np.abs(res_te["wavelength_nm"] - 550.0)))

    data = {
        "schema_version": "1.0.0",
        "case_id": "bragg_reflector",
        "title": "Bragg反射镜/高反射膜",
        "source_commit": get_git_commit_hash(),
        "source_file": "thinfilm/education.py",
        "source_symbol": "build_high_reflector_layers",
        "generated_at": datetime.datetime.now().isoformat(),
        "calculation_source": "python_export",
        "design_wavelength_nm": 550.0,
        "incidence_angle_deg": 45.0,
        "polarization_support": ["TE", "TM"],
        "ambient": {"name": "Air", "n": 1.0},
        "layers": layer_stack_info,
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
                "R": round(float(res_te["R"][idx_550]), 6),
                "T": round(float(res_te["T"][idx_550]), 6),
                "A": round(float(res_te["A"][idx_550]), 6)
            },
            "TM": {
                "R": round(float(res_tm["R"][idx_550]), 6),
                "T": round(float(res_tm["T"][idx_550]), 6),
                "A": round(float(res_tm["A"][idx_550]), 6)
            }
        },
        "phase_data_status": "NOT_AVAILABLE",
        "input_parameter_hash": compute_hash(input_params)
    }

    data["result_hash"] = compute_hash(data)
    out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[export] Successfully exported bragg_reflector results -> {out_file}")


if __name__ == "__main__":
    export_single_ar()
    export_bragg_reflector()
