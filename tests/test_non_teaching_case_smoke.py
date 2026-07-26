# -*- coding: utf-8 -*-
"""Automated smoke tests for engineering applications and non-teaching case runners."""

from __future__ import annotations

import os
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.applications import (
    run_solar_cell_ar,
    run_wdm_filter,
    run_laser_mirror,
    run_phone_lens_ar,
    run_smart_window,
)


class TestEngineeringApplicationsSmoke:
    """Test suite for the 5 TMM-only engineering application cases."""

    def test_solar_cell_ar(self):
        res = run_solar_cell_ar()
        assert "wavelengths_nm" in res
        assert "R" in res
        assert "T" in res
        assert "A" in res
        assert len(res["R"]) == len(res["wavelengths_nm"])
        assert "metrics" in res
        assert "structure" in res

    def test_wdm_filter(self):
        res = run_wdm_filter()
        assert "wavelengths_nm" in res
        assert "R" in res
        assert "T" in res
        assert len(res["R"]) == len(res["wavelengths_nm"])
        assert "metrics" in res
        assert "fwhm_nm" in res["metrics"]

    def test_laser_mirror(self):
        res = run_laser_mirror()
        assert "wavelengths_nm" in res
        assert "R" in res
        assert len(res["R"]) == len(res["wavelengths_nm"])
        assert "metrics" in res
        assert "R_at_1064nm" in res["metrics"]

    def test_phone_lens_ar(self):
        res = run_phone_lens_ar()
        assert "wavelengths_nm" in res
        assert "R" in res
        assert len(res["R"]) == len(res["wavelengths_nm"])
        assert "metrics" in res

    def test_smart_window(self):
        res = run_smart_window()
        assert "wavelengths_nm" in res
        assert "R" in res
        assert "T" in res
        assert "A" in res
        assert len(res["R"]) == len(res["wavelengths_nm"])
        assert "metrics" in res
        assert "SHGC" in res["metrics"]
