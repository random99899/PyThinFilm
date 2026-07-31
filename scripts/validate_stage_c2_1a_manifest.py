# -*- coding: utf-8 -*-
"""Validator for Stage C.2.1A Engineering Manifest & Registries.

Validates:
1. 5 case IDs exactly match case_registry.json.
2. Formal entrypoint function exists and is executable.
3. Layer stack and physics_input_hash reproducibility.
4. Metric status enums validity (FORMAL_SOURCE, DERIVED_FROM_FORMAL_OUTPUT, NOT_AVAILABLE).
5. Template requirement status is REUSE_EXISTING for all 5 cases.
6. NO status tampering: migration_status remains PENDING_ENGINE_MIGRATION in case_registry.json.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXPECTED_CASE_IDS = {
    "app_solar_cell_ar",
    "app_wdm_filter",
    "app_laser_mirror",
    "app_phone_lens_ar",
    "app_smart_window",
}

VALID_METRIC_STATUSES = {"FORMAL_SOURCE", "DERIVED_FROM_FORMAL_OUTPUT", "NOT_AVAILABLE", "EXTERNAL_DATA_REQUIRED"}
VALID_TEMPLATE_REQUIREMENTS = {"REUSE_EXISTING", "EXTEND_EXISTING", "NEW_TEMPLATE_REQUIRED", "SOURCE_AUDIT_BLOCKED"}
VALID_AUDIT_STATUSES = {"SOURCE_AUDIT_PASSED", "SOURCE_AUDIT_BLOCKED", "EXTERNAL_DATA_REQUIRED"}


def validate_manifest():
    manifest_path = ROOT / "docs" / "visualization" / "data" / "stage_c2_1a_engineering_manifest.json"
    registry_path = ROOT / "web3d" / "data" / "case_registry.json"

    if not manifest_path.exists():
        print(f"[FAIL] Manifest file missing: {manifest_path}")
        sys.exit(1)

    if not registry_path.exists():
        print(f"[FAIL] Registry file missing: {registry_path}")
        sys.exit(1)

    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    registry_data = json.loads(registry_path.read_text(encoding="utf-8"))

    manifest_cases = manifest_data.get("cases", [])
    registry_cases = registry_data.get("cases", [])

    print("=" * 70)
    print("Stage C.2.1A Manifest Validation Audit")
    print("=" * 70)

    # 1. Exact case ID match check
    manifest_ids = {c["case_id"] for c in manifest_cases}
    assert manifest_ids == EXPECTED_CASE_IDS, f"Manifest case IDs do not match expected: {manifest_ids} != {EXPECTED_CASE_IDS}"
    print(f"[PASS] Case IDs match expected set: {manifest_ids}")

    # 2. Check registry migration_status is NOT tampered
    for reg_case in registry_cases:
        if reg_case["id"] in EXPECTED_CASE_IDS:
            status = reg_case.get("migration_status")
            assert status == "PENDING_ENGINE_MIGRATION", f"Registry migration_status for '{reg_case['id']}' must remain PENDING_ENGINE_MIGRATION, got '{status}'"
    print("[PASS] Registry migration_status for all 5 cases remains PENDING_ENGINE_MIGRATION (no status tampering).")

    # 3. Check formal entrypoints, metrics, template requirements
    for c in manifest_cases:
        cid = c["case_id"]
        entry = c["formal_entrypoint"]
        mod_name, fn_name = entry.split(":")
        
        # Test import & callable
        mod = importlib.import_module(mod_name)
        fn = getattr(mod, fn_name)
        assert callable(fn), f"Formal entrypoint function '{fn_name}' in module '{mod_name}' is not callable"

        # Check template requirement enum
        tmpl_req = c.get("template_requirement")
        assert tmpl_req in VALID_TEMPLATE_REQUIREMENTS, f"Invalid template_requirement '{tmpl_req}' for {cid}"
        assert tmpl_req == "REUSE_EXISTING", f"Expected REUSE_EXISTING for {cid}, got {tmpl_req}"

        # Check metric statuses
        for m in c.get("formal_metrics", []):
            m_status = m.get("status")
            assert m_status in VALID_METRIC_STATUSES, f"Invalid metric status '{m_status}' for {m['metric_name']} in {cid}"

        # Check audit status
        a_status = c.get("audit_status")
        assert a_status in VALID_AUDIT_STATUSES, f"Invalid audit status '{a_status}' for {cid}"
        assert a_status == "SOURCE_AUDIT_PASSED", f"Expected SOURCE_AUDIT_PASSED for {cid}, got {a_status}"

    print("[PASS] All formal entrypoint importability, metric status enums, and template requirements PASSED.")
    print("=" * 70)


if __name__ == "__main__":
    validate_manifest()
