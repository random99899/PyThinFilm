# -*- coding: utf-8 -*-
"""Validation and reconciliation script for PyThinFilm 3D Case Registry (Stage B.1C).

Validates:
1. ID uniqueness across all registered entries.
2. Exact entry, physical case, alias, runner, and visualization target counts.
3. Entry kind & physical case ID mapping invariants.
4. Schema fields completeness (22 mandatory fields).
5. 4-dimensional status enums validation.
6. Calculation source & animation semantics validation.
7. Existence of source_file paths.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUIRED_FIELDS = [
    "id",
    "display_name",
    "category",
    "entry_kind",
    "physical_case_id",
    "source_file",
    "source_symbol",
    "physics_model",
    "structure",
    "materials",
    "incidence_angle",
    "polarization_support",
    "visualization_template",
    "data_dependencies",
    "geometry_status",
    "physics_data_status",
    "migration_status",
    "conflict_status",
    "calculation_source",
    "python_reference_comparison",
    "animation_semantics",
    "notes",
]

VALID_ENTRY_KINDS = ["case", "alias", "runner"]
VALID_GEOMETRY_STATUSES = ["GEOMETRY_READY", "GEOMETRY_VERIFIED", "GEOMETRY_MISMATCH", "PENDING_GEOMETRY", "NOT_AUDITED"]
VALID_PHYSICS_DATA_STATUSES = ["PHYSICS_DATA_READY", "PHYSICS_DATA_AVAILABLE", "EXTERNAL_DATA_REQUIRED", "ILLUSTRATIVE_ONLY", "NOT_AUDITED"]
VALID_MIGRATION_STATUSES = ["MIGRATED", "MIGRATION_VERIFIED", "READY_FOR_MIGRATION", "PROTOTYPE_ONLY", "PENDING_ENGINE_MIGRATION", "BLOCKED"]
VALID_CONFLICT_STATUSES = [
    "NONE",
    "EXTERNAL_CSV_MISSING",
    "HARDCODED_PATH_DEPENDENCY",
    "PROTOTYPE_GEOMETRY_MISMATCH",
]
VALID_CALC_SOURCES = ["python_export", "frontend_reimplementation", "hardcoded", "illustrative_only"]
VALID_PYTHON_COMPARISONS = ["PASSED", "FAILED", "NOT_RUN", "NOT_APPLICABLE"]
VALID_ANIMATION_SEMANTICS = ["PHYSICS_DRIVEN", "TEACHING_ILLUSTRATION", "MIXED"]


def validate_registry():
    registry_path = ROOT / "web3d" / "data" / "case_registry.json"
    if not registry_path.exists():
        print(f"Error: Registry file not found: {registry_path}")
        sys.exit(1)

    data = json.loads(registry_path.read_text(encoding="utf-8"))
    cases = data.get("cases", [])

    print("=" * 65)
    print("PyThinFilm 3D Case Registry Evidence Audit (Stage B.1C fp_filter)")
    print("=" * 65)

    # 1. Entry Count Checks
    registry_entry_count = len(cases)
    case_ids = [c["id"] for c in cases]
    unique_ids = set(case_ids)

    if len(case_ids) != len(unique_ids):
        duplicates = [x for x in case_ids if case_ids.count(x) > 1]
        print(f"[FAIL] Duplicate Case IDs found: {set(duplicates)}")
        sys.exit(1)

    # Filter out runner entries from independent geometry & visualization scenes
    non_runner_cases = [c for c in cases if c.get("entry_kind") != "runner"]
    physical_cases = [c for c in cases if c.get("entry_kind") == "case"]
    alias_entries = [c for c in cases if c.get("entry_kind") == "alias"]
    runner_entries = [c for c in cases if c.get("entry_kind") == "runner"]

    visualization_targets = set(c["physical_case_id"] for c in cases)

    physical_case_count = len(physical_cases)
    alias_entry_count = len(alias_entries)
    runner_entry_count = len(runner_entries)
    visualization_target_count = len(visualization_targets)

    print(f"Registry Entry Count:          {registry_entry_count}")
    print(f"Unique Entry IDs:              {len(unique_ids)}")
    print(f"Physical Case Count:           {physical_case_count}")
    print(f"Alias Entry Count:             {alias_entry_count}")
    print(f"Runner Entry Count:            {runner_entry_count}")
    print(f"Visualization Target Count:    {visualization_target_count}")

    # Exact expected count assertions
    assert registry_entry_count == 41, f"Expected 41 registry entries, got {registry_entry_count}"
    assert physical_case_count == 40, f"Expected 40 physical cases, got {physical_case_count}"
    assert alias_entry_count == 0, f"Expected 0 alias entries, got {alias_entry_count}"
    assert runner_entry_count == 1, f"Expected 1 runner entry (guided_grating_demo), got {runner_entry_count}"
    assert visualization_target_count == 40, f"Expected 40 visualization targets, got {visualization_target_count}"
    print("[PASS] Entry Count Assertions PASSED (41 entries, 40 physical cases, 0 alias, 1 runner, 40 targets).")

    # 2. Status Dimension Metrics Breakdown (excluding runners from independent geometry scenes)
    geometry_verified_count = sum(1 for c in non_runner_cases if c.get("geometry_status") == "GEOMETRY_VERIFIED")
    geometry_ready_count = sum(1 for c in non_runner_cases if c.get("geometry_status") == "GEOMETRY_READY")
    geometry_mismatch_count = sum(1 for c in non_runner_cases if c.get("geometry_status") == "GEOMETRY_MISMATCH")
    geometry_not_audited_count = sum(1 for c in non_runner_cases if c.get("geometry_status") == "NOT_AUDITED")

    physics_data_available_count = sum(1 for c in cases if c.get("physics_data_status") == "PHYSICS_DATA_AVAILABLE")
    physics_data_ready_count = sum(1 for c in cases if c.get("physics_data_status") == "PHYSICS_DATA_READY")
    illustrative_only_count = sum(1 for c in cases if c.get("physics_data_status") == "ILLUSTRATIVE_ONLY")
    external_data_required_count = sum(1 for c in cases if c.get("physics_data_status") == "EXTERNAL_DATA_REQUIRED")

    migration_verified_count = sum(1 for c in cases if c.get("migration_status") == "MIGRATION_VERIFIED")
    ready_for_migration_count = sum(1 for c in cases if c.get("migration_status") == "READY_FOR_MIGRATION")
    prototype_only_count = sum(1 for c in cases if c.get("migration_status") == "PROTOTYPE_ONLY")
    pending_migration_count = sum(1 for c in cases if c.get("migration_status") == "PENDING_ENGINE_MIGRATION")

    frontend_passed_count = sum(1 for c in cases if c.get("frontend_binding_status") == "PASSED")
    python_export_verified_count = sum(1 for c in cases if c.get("python_export_status") == "VERIFIED")

    print("\nEvidence-Backed Status Metrics Breakdown:")
    print(f"  - geometry_verified_count:             {geometry_verified_count} (single_ar, bragg_reflector, fp_filter)")
    print(f"  - geometry_ready_count:                {geometry_ready_count}")
    print(f"  - geometry_mismatch_count:             {geometry_mismatch_count}")
    print(f"  - geometry_not_audited_count:          {geometry_not_audited_count}")
    print(f"  - physics_data_available_count:        {physics_data_available_count}")
    print(f"  - physics_data_ready_count:            {physics_data_ready_count}")
    print(f"  - illustrative_only_count:             {illustrative_only_count}")
    print(f"  - external_data_required_count:        {external_data_required_count}")
    print(f"  - migration_verified_count:            {migration_verified_count} (single_ar, bragg_reflector, fp_filter)")
    print(f"  - ready_for_migration_count:           {ready_for_migration_count}")
    print(f"  - prototype_only_count:                {prototype_only_count}")
    print(f"  - pending_engine_migration_count:      {pending_migration_count}")
    print(f"  - frontend_binding_passed_count:       {frontend_passed_count}")
    print(f"  - python_export_verified_count:        {python_export_verified_count}")

    # Assert exactly 3 migrated cases (single_ar, bragg_reflector, fp_filter)
    assert migration_verified_count == 3, f"Expected 3 MIGRATION_VERIFIED cases, got {migration_verified_count}"
    assert frontend_passed_count == 3, f"Expected 3 frontend_binding PASSED cases, got {frontend_passed_count}"
    assert geometry_mismatch_count == 0, f"Expected 0 GEOMETRY_MISMATCH cases after resolving fp_filter, got {geometry_mismatch_count}"

    # 3. Schema Completeness & File Existence Check
    errors = []
    missing_source_files = []

    for idx, c in enumerate(cases):
        cid = c.get("id", f"INDEX_{idx}")

        # Field completeness
        for field in REQUIRED_FIELDS:
            if field not in c or c[field] is None or str(c[field]).strip() == "":
                errors.append(f"Case '{cid}' missing required field: '{field}'")

        # Enum checks
        if c.get("entry_kind") not in VALID_ENTRY_KINDS:
            errors.append(f"Case '{cid}' invalid entry_kind: {c.get('entry_kind')}")
        if c.get("geometry_status") not in VALID_GEOMETRY_STATUSES:
            errors.append(f"Case '{cid}' invalid geometry_status: {c.get('geometry_status')}")
        if c.get("physics_data_status") not in VALID_PHYSICS_DATA_STATUSES:
            errors.append(f"Case '{cid}' invalid physics_data_status: {c.get('physics_data_status')}")
        if c.get("migration_status") not in VALID_MIGRATION_STATUSES:
            errors.append(f"Case '{cid}' invalid migration_status: {c.get('migration_status')}")
        if c.get("conflict_status") not in VALID_CONFLICT_STATUSES:
            errors.append(f"Case '{cid}' invalid conflict_status: {c.get('conflict_status')}")
        if c.get("calculation_source") not in VALID_CALC_SOURCES:
            errors.append(f"Case '{cid}' invalid calculation_source: {c.get('calculation_source')}")
        if c.get("python_reference_comparison") not in VALID_PYTHON_COMPARISONS:
            errors.append(f"Case '{cid}' invalid python_reference_comparison: {c.get('python_reference_comparison')}")
        if c.get("animation_semantics") not in VALID_ANIMATION_SEMANTICS:
            errors.append(f"Case '{cid}' invalid animation_semantics: {c.get('animation_semantics')}")

        # Source file check
        src = c.get("source_file", "").split(":")[0]
        if src and not (ROOT / src).exists():
            missing_source_files.append((cid, src))

    if missing_source_files:
        print(f"\n[WARNING] Missing Source Files ({len(missing_source_files)}):")
        for cid, src in missing_source_files:
            print(f"  - [{cid}] File not found on disk: {src}")

    if errors:
        print(f"\n[FAIL] Validation FAILED with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n[PASS] All Schema, Field Completeness & Status Enum Checks PASSED.")

    print("=" * 65)


if __name__ == "__main__":
    validate_registry()
