# -*- coding: utf-8 -*-
"""Unit tests for Stage C.2.1A Engineering Application Source Audit.

Validates:
1. 5 engineering application case functions execute cleanly.
2. Returned structure and metrics contain expected fields.
3. R + T + A = 1.0 physical energy conservation tolerance.
4. Manifest file generation and valid enum values.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import numpy as np

from examples.applications.solar_cell_ar import run_solar_cell_ar
from examples.applications.wdm_filter import run_wdm_filter
from examples.applications.laser_mirror import run_laser_mirror
from examples.applications.phone_lens_ar import run_phone_lens_ar
from examples.applications.smart_window import run_smart_window

ROOT = Path(__file__).resolve().parent.parent


class TestEngineeringSourceAudit:
    @pytest.mark.parametrize("runner_fn, case_id", [
        (run_solar_cell_ar, "app_solar_cell_ar"),
        (run_wdm_filter, "app_wdm_filter"),
        (run_laser_mirror, "app_laser_mirror"),
        (run_phone_lens_ar, "app_phone_lens_ar"),
        (run_smart_window, "app_smart_window"),
    ])
    def test_engineering_case_execution_and_energy_conservation(self, runner_fn, case_id):
        res = runner_fn()
        assert "R" in res and "T" in res and "A" in res
        assert "metrics" in res and "structure" in res

        R, T, A = res["R"], res["T"], res["A"]
        total_energy = R + T + A
        max_err = np.max(np.abs(total_energy - 1.0))
        assert max_err < 1e-5, f"Energy conservation error {max_err} for {case_id}"

    def test_manifest_file_completeness_and_enum_validity(self):
        manifest_path = ROOT / "docs" / "visualization" / "data" / "stage_c2_1a_engineering_manifest.json"
        assert manifest_path.exists()

        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        cases = data.get("cases", [])
        assert len(cases) == 5

        expected_ids = {"app_solar_cell_ar", "app_wdm_filter", "app_laser_mirror", "app_phone_lens_ar", "app_smart_window"}
        actual_ids = {c["case_id"] for c in cases}
        assert actual_ids == expected_ids

        for c in cases:
            assert c["audit_status"] == "SOURCE_AUDIT_PASSED"
            assert c["template_requirement"] == "REUSE_EXISTING"
            assert c["candidate_template"] in ["periodic-stack", "defect-cavity", "metal-dbr-interface"]
            assert len(c["formal_metrics"]) > 0
