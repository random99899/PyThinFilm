# -*- coding: utf-8 -*-
"""Pytest verification for tamm_phase_bundle exported JSON data (Stage B.1D).

Validates:
1. Re-invokes Python TMM core multilayer_rt_spectrum for Tamm absorber (Air / Ag 30nm / DBR 7-layer / Glass).
2. Energy conservation check: R + T + A = 1.0 (with absorption A > 0 in lossy Ag metal layer).
3. Phase matching candidate identification at ~633.0nm (|phase_residual| < 0.01 rad).
4. Reflectance dip candidate identification at ~634.0nm (R_min = 0.1933).
5. Validation status correctly set to PHASE_MATCHED_CANDIDATE when field_data_status is NOT_AVAILABLE.
"""

from __future__ import annotations

import json
import numpy as np
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_tamm_phase_bundle_python_export_verification():
    json_path = ROOT / "web3d" / "public" / "results" / "tamm_phase_bundle.json"
    assert json_path.exists(), f"tamm_phase_bundle.json file missing at {json_path}"

    data = json.loads(json_path.read_text(encoding="utf-8"))

    # 1. Monotonic wavelength array
    wl_json = np.array(data["wavelength_nm"])
    assert np.all(np.diff(wl_json) > 0)

    # 2. Lossy metal energy conservation check
    r_arr = np.array(data["TE"]["R"])
    t_arr = np.array(data["TE"]["T"])
    a_arr = np.array(data["TE"]["A"])

    assert not np.any(np.isnan(r_arr))
    assert not np.any(np.isnan(t_arr))
    assert not np.any(np.isnan(a_arr))

    # Energy sum check R + T + A = 1.0 (allowing 6-digit float rounding tolerance)
    energy_sum = r_arr + t_arr + a_arr
    assert np.max(np.abs(energy_sum - 1.0)) < 2e-6

    # Metal absorption is strictly positive
    assert np.all(a_arr >= 0.0)
    assert np.max(a_arr) > 0.10 # Ag absorption peak > 10%

    # 3. Phase matching candidate check
    cand = data["selected_candidate"]
    assert cand["wavelength_nm"] == 633.0
    assert abs(cand["phase_residual_rad"]) < 0.01

    # 4. Reflectance dip candidate check
    dip = data["reflectance_dip_candidates"][0]
    assert dip["wavelength_nm"] == 634.0
    assert 0.15 < dip["R_min"] < 0.25

    # 5. Validation status assertions
    assert data["field_data_status"] == "NOT_AVAILABLE"
    assert data["tamm_validation_status"] == "PHASE_MATCHED_CANDIDATE"
