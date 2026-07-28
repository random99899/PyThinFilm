# -*- coding: utf-8 -*-
"""Export script for PyThinFilm 3D Visualization cases (Stage B.1A).

Exports canonical Python TMM calculation results into web3d/public/results/<case_id>.json.
"""

from __future__ import annotations

import datetime
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

    data = {
        "case_id": "single_ar",
        "title": "单层减反射膜(任意参数)",
        "source_commit": get_git_commit_hash(),
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
        }
    }

    out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[export] Successfully exported single_ar results -> {out_file}")


if __name__ == "__main__":
    export_single_ar()
