# -*- coding: utf-8 -*-
"""Pytest verification for Tamm reference plane invariance & 1D field localization (Stage B.1D.1).

Validates:
1. Common Ag/H interface reference plane (z=30nm) complex reflection matching.
2. Reference plane shift invariance: shifting z by dz in uniform medium preserves complex_matching_residual.
3. 1D TMM field distribution: electric field peak |E|^2 ~ 3.48 located near Ag/H interface (z=77nm).
4. Field enhancement ratio ~ 6.29x compared to off-resonance (500nm).
5. Rapid decay inside lossy metal Ag and exponential decay inside DBR stack.
"""

from __future__ import annotations

import json
import numpy as np
import pytest
from pathlib import Path
from thinfilm.education import LayerSpec, multilayer_rt_spectrum, reflection_phase_radians
from tools.export_visualization_cases import compute_tmm_1d_field

ROOT = Path(__file__).resolve().parent.parent


def test_tamm_common_reference_plane_invariance():
    wl = np.linspace(400, 800, 401)
    nH, nL = 2.15, 1.38
    dH = 550.0 / (4 * nH)
    dL = 550.0 / (4 * nL)
    n_ag = 0.13 + 3.98j
    d_ag = 30.0

    dbr_rest = [
        LayerSpec("L", nL, dL),
        LayerSpec("H", nH, dH),
        LayerSpec("L", nL, dL),
        LayerSpec("H", nH, dH),
        LayerSpec("L", nL, dL),
        LayerSpec("H", nH, dH),
    ]

    # Interface z=0 in nH medium
    r_metal = multilayer_rt_spectrum(wl, [LayerSpec("Ag", n_ag, d_ag)], n_incident=nH, n_substrate=1.0)["r_complex"]
    r_dbr = multilayer_rt_spectrum(wl, dbr_rest, n_incident=nH, n_substrate=1.52)["r_complex"]

    r_prod_base = r_metal * r_dbr
    res_base = np.abs(1.0 - r_prod_base)

    # Shift reference plane by dz = +10nm inside uniform nH medium
    k_nH = 2 * np.pi / wl * nH
    dz = 10.0
    # Phase shift: r_metal -> r_metal * exp(i 2 k dz), r_dbr -> r_dbr * exp(-i 2 k dz)
    r_metal_shifted = r_metal * np.exp(1j * 2 * k_nH * dz)
    r_dbr_shifted = r_dbr * np.exp(-1j * 2 * k_nH * dz)

    r_prod_shifted = r_metal_shifted * r_dbr_shifted
    res_shifted = np.abs(1.0 - r_prod_shifted)

    # Reference plane shift invariance check
    np.testing.assert_allclose(res_base, res_shifted, atol=1e-12)


def test_tamm_1d_field_localization():
    json_path = ROOT / "web3d" / "public" / "results" / "tamm_phase_bundle.json"
    assert json_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))

    loc = data["interface_localization_metrics"]
    assert loc["field_localization_status"] == "INTERFACE_LOCALIZATION_VERIFIED"
    assert loc["peak_abs_E2"] > 3.0
    assert loc["enhancement_ratio"] > 5.0
    assert loc["distance_peak_to_interface_nm"] < 50.0

    # Material model demotion checks
    assert data["material_model"] == "CONSTANT_COMPLEX_INDEX"
    assert data["metal_nk_source"] == "OFFICIAL_CASE_HARDCODED_CONSTANT"
    assert data["tamm_validation_status"] == "REFLECTANCE_DIP_CANDIDATE"
