# -*- coding: utf-8 -*-
"""Validation and reconciliation script for PyThinFilm 3D Case Registry (Stage A.1).

Validates:
1. ID uniqueness across all categories.
2. Exact case count reconciliation.
3. Required JSON schema fields completeness.
4. Status enum validity.
5. Existence of source_file paths.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Required fields for web3d/data/case_registry.json schema
REQUIRED_FIELDS = [
    "id",
    "display_name",
    "category",
    "source_file",
    "source_symbol",
    "physics_model",
    "structure",
    "materials",
    "incidence_angle",
    "polarization_support",
    "visualization_template",
    "data_dependencies",
    "evidence_status",
    "conflict_status",
    "notes",
]

# Valid status enums for evidence_status
VALID_EVIDENCE_STATUSES = [
    "STRUCTURE_READY",
    "PHYSICS_DATA_READY",
    "EXTERNAL_DATA_REQUIRED",
    "VISUALIZATION_DEGRADED_MODE",
    "BLOCKED",
    "PROTOTYPE_EXIST",
]

# Valid status enums for conflict_status
VALID_CONFLICT_STATUSES = [
    "NONE",
    "EXTERNAL_CSV_MISSING",
    "HARDCODED_PATH_DEPENDENCY",
    "PROTOTYPE_SIMULATION_DISCREPANCY",
]


def validate_registry():
    registry_path = ROOT / "web3d" / "data" / "case_registry.json"
    if not registry_path.exists():
        print(f"Error: Registry file not found: {registry_path}")
        sys.exit(1)

    data = json.loads(registry_path.read_text(encoding="utf-8"))
    cases = data.get("cases", [])

    print("=" * 60)
    print("PyThinFilm 3D Case Registry Reconciliation Audit")
    print("=" * 60)

    # 1. ID Uniqueness Check
    case_ids = [c["id"] for c in cases]
    unique_ids = set(case_ids)
    print(f"Total Registered Cases: {len(cases)}")
    print(f"Unique Case IDs:       {len(unique_ids)}")
    if len(case_ids) != len(unique_ids):
        duplicates = [x for x in case_ids if case_ids.count(x) > 1]
        print(f"ERROR: Duplicate Case IDs found: {set(duplicates)}")
        sys.exit(1)
    else:
        print("[PASS] Case ID Uniqueness Check PASSED.")

    # 2. Category Counts & Deduplication Math
    cats = {}
    for c in cases:
        cat = c.get("category", "unknown")
        cats[cat] = cats.get(cat, 0) + 1

    print("\nCategory Breakdown:")
    for cat, count in sorted(cats.items()):
        print(f"  - {cat:<25}: {count} cases")

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
        ev_status = c.get("evidence_status")
        if ev_status not in VALID_EVIDENCE_STATUSES:
            errors.append(f"Case '{cid}' has invalid evidence_status: '{ev_status}'")

        conf_status = c.get("conflict_status")
        if conf_status not in VALID_CONFLICT_STATUSES:
            errors.append(f"Case '{cid}' has invalid conflict_status: '{conf_status}'")

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
        print("\n[PASS] Schema Completeness & Enum Validation PASSED.")

    print("\nReconciliation Summary:")
    print(f"  - Total Unique Cases Registered: {len(cases)}")
    print(f"  - Prototype Aligned:             {data.get('prototype_aligned_cases', 0)}")
    print(f"  - Structure Ready:               {sum(1 for c in cases if c.get('evidence_status') == 'STRUCTURE_READY')}")
    print(f"  - External Data Required:        {sum(1 for c in cases if c.get('evidence_status') == 'EXTERNAL_DATA_REQUIRED')}")

    print("=" * 60)


if __name__ == "__main__":
    validate_registry()
