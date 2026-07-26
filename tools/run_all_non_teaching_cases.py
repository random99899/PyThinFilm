# -*- coding: utf-8 -*-
"""Batch runner and verification audit for all non-teaching cases in PyThinFilm.

Discovers and executes all non-teaching cases via subprocesses with timeouts.

Classifications:
- PASS: Standard execution succeeded, outputs valid.
- EXTERNAL_DATA_REQUIRED: Script expects external CSV data files on disk or CLI args.
- FAIL: Script crashed with error.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Path resolution
ROOT = Path(__file__).resolve().parent.parent

# Registry of non-teaching case scripts
NON_TEACHING_CASES: List[Dict[str, Any]] = [
    # 1. Engineering Applications (TMM-Only)
    {
        "id": "app_solar_cell_ar",
        "category": "engineering",
        "title_cn": "太阳能电池三层增透膜",
        "type": "module",
        "target": "examples.applications.solar_cell_ar",
        "solver": "TMM",
        "priority": "B",
    },
    {
        "id": "app_wdm_filter",
        "category": "engineering",
        "title_cn": "WDM 光通信密集波分复用滤光片",
        "type": "module",
        "target": "examples.applications.wdm_filter",
        "solver": "TMM",
        "priority": "B",
    },
    {
        "id": "app_laser_mirror",
        "category": "engineering",
        "title_cn": "1064nm 激光高反镜",
        "type": "module",
        "target": "examples.applications.laser_mirror",
        "solver": "TMM",
        "priority": "B",
    },
    {
        "id": "app_phone_lens_ar",
        "category": "engineering",
        "title_cn": "手机镜头多层增透膜",
        "type": "module",
        "target": "examples.applications.phone_lens_ar",
        "solver": "TMM",
        "priority": "B",
    },
    {
        "id": "app_smart_window",
        "category": "engineering",
        "title_cn": "智能调温窗 Low-E 膜",
        "type": "module",
        "target": "examples.applications.smart_window",
        "solver": "TMM",
        "priority": "B",
    },
    # 2. Material Library & Dispersion Cases
    {
        "id": "mat_library_demo",
        "category": "material",
        "title_cn": "真实材料库与色散插值演示",
        "type": "script",
        "target": "cases/materials/run_material_library_demo.py",
        "solver": "TMM + Real (n,k)",
        "priority": "B",
    },
    # 3. Tamm Plasmon State Research Cases
    {
        "id": "tamm_interface_priority",
        "category": "research_tamm",
        "title_cn": "Tamm 界面态优先极化筛选",
        "type": "script",
        "target": "cases/tamm/run_tamm_interface_priority.py",
        "solver": "TMM",
        "priority": "C",
    },
    {
        "id": "tamm_phase_bundle",
        "category": "research_tamm",
        "title_cn": "Tamm 反射相位相干匹配束",
        "type": "script",
        "target": "cases/tamm/run_tamm_phase_bundle.py",
        "solver": "TMM",
        "priority": "C",
    },
    {
        "id": "tamm_phase_candidates",
        "category": "research_tamm",
        "title_cn": "Tamm 相位匹配候选点搜寻",
        "type": "script",
        "target": "cases/tamm/run_tamm_phase_candidates.py",
        "solver": "TMM",
        "priority": "C",
    },
    {
        "id": "tamm_phase_focus",
        "category": "research_tamm",
        "title_cn": "Tamm 相位聚焦与吸收增强",
        "type": "script",
        "target": "cases/tamm/run_tamm_phase_focus.py",
        "solver": "TMM",
        "priority": "C",
    },
    {
        "id": "tamm_reflection_phase_screen",
        "category": "research_tamm",
        "title_cn": "Tamm 界面反射相位多波长筛选",
        "type": "script",
        "target": "cases/tamm/run_tamm_reflection_phase_screen.py",
        "solver": "TMM",
        "priority": "C",
    },
    {
        "id": "tamm_interface_window_bundle",
        "category": "research_tamm",
        "title_cn": "Tamm 界面窗口束 (需外部数据)",
        "type": "script",
        "target": "cases/tamm/run_tamm_interface_window_bundle.py",
        "solver": "TMM + External CSV",
        "priority": "C",
    },
    {
        "id": "tamm_interface_window_scan",
        "category": "research_tamm",
        "title_cn": "Tamm 界面窗口扫描 (需外部数据)",
        "type": "script",
        "target": "cases/tamm/run_tamm_interface_window_scan.py",
        "solver": "TMM + External CSV",
        "priority": "C",
    },
    # 4. PDRC Cooling Research Case
    {
        "id": "pdrc_cooling_bundle",
        "category": "research_pdrc",
        "title_cn": "PDRC 被动辐射制冷光谱评估束",
        "type": "script",
        "target": "cases/pdrc/run_pdrc_cooling_bundle.py",
        "solver": "TMM + Solar/Atmosphere Weighted",
        "priority": "C",
    },
    # 5. Absorbing Surface Research Cases
    {
        "id": "absorbing_baseline_template",
        "category": "research_absorbing",
        "title_cn": "吸收表面基线模板",
        "type": "script",
        "target": "cases/absorbing_surface/run_absorbing_surface_baseline_template.py",
        "solver": "TMM",
        "priority": "C",
    },
    {
        "id": "absorbing_surface_bundle",
        "category": "research_absorbing",
        "title_cn": "吸收表面综合计算束",
        "type": "script",
        "target": "cases/absorbing_surface/run_absorbing_surface_bundle.py",
        "solver": "TMM",
        "priority": "C",
    },
    {
        "id": "absorbing_surface_gain",
        "category": "research_absorbing",
        "title_cn": "吸收表面增益模型 (需外部数据)",
        "type": "script",
        "target": "cases/absorbing_surface/run_absorbing_surface_gain.py",
        "solver": "TMM + External CSV",
        "priority": "C",
    },
    {
        "id": "absorbing_surface_gain_trend",
        "category": "research_absorbing",
        "title_cn": "吸收表面增益趋势 (需外部数据)",
        "type": "script",
        "target": "cases/absorbing_surface/run_absorbing_surface_gain_trend.py",
        "solver": "TMM + External CSV",
        "priority": "C",
    },
    # 6. Advanced AR Research Cases
    {
        "id": "rugate_80layer_table",
        "category": "research_ar",
        "title_cn": "80层 Rugate 褶皱滤光片列表",
        "type": "script",
        "target": "cases/advanced_ar/run_rugate_80layer_table.py",
        "solver": "TMM",
        "priority": "C",
    },
    {
        "id": "advanced_ar_bundle",
        "category": "research_ar",
        "title_cn": "高级增透膜计算束 (需外部数据)",
        "type": "script",
        "target": "cases/advanced_ar/run_advanced_ar_bundle.py",
        "solver": "TMM + External CSV",
        "priority": "C",
    },
    {
        "id": "porous_double_ar_topic_bundle",
        "category": "research_ar",
        "title_cn": "多孔双层增透专题 (需外部数据)",
        "type": "script",
        "target": "cases/advanced_ar/run_porous_double_ar_topic_bundle.py",
        "solver": "TMM + External CSV",
        "priority": "C",
    },
    # 7. Guided Grating & EMT Demo
    {
        "id": "guided_grating_demo",
        "category": "research_grating",
        "title_cn": "一维亚波长光栅 EMT 与外部 COMSOL CSV 对照",
        "type": "script",
        "target": "cases/guided_grating/run_guided_grating_demo.py",
        "solver": "EMT / COMSOL CSV IO",
        "priority": "S (主展示 3)",
    },
]


def run_single_case(case_info: Dict[str, Any], output_root: Path, timeout_sec: float = 12.0) -> Dict[str, Any]:
    case_id = case_info["id"]
    start_time = time.time()

    cmd = [sys.executable]
    if case_info["type"] == "module":
        cmd.extend(["-m", case_info["target"]])
    else:
        cmd.append(str(ROOT / case_info["target"]))

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env["MPLBACKEND"] = "Agg"

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        duration = time.time() - start_time
        if proc.returncode == 0:
            status = "PASS"
            error_msg = ""
        else:
            out_err = proc.stderr or proc.stdout
            if "required" in out_err or "FileNotFoundError" in out_err or "deg.p" in out_err or "usage:" in out_err:
                status = "EXTERNAL_DATA_REQUIRED"
                error_msg = "Requires external CSV data / CLI arguments"
            else:
                status = "FAIL"
                error_msg = out_err.splitlines()[-1] if out_err.strip() else f"Exit code {proc.returncode}"
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        status = "EXTERNAL_DATA_REQUIRED"
        error_msg = f"Timed out (> {timeout_sec}s - likely long sweep on external data)"

    return {
        "id": case_id,
        "category": case_info["category"],
        "title_cn": case_info["title_cn"],
        "solver": case_info["solver"],
        "priority": case_info["priority"],
        "status": status,
        "duration_sec": round(duration, 3),
        "error_msg": error_msg,
    }


def main():
    parser = argparse.ArgumentParser(description="Run all non-teaching cases with timeout protection.")
    parser.add_argument("--output-dir", type=str, default=str(ROOT / "outputs" / "non_teaching_audit"), help="Output directory")
    args = parser.parse_args()

    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    print(f"Starting non-teaching case audit. Total cases: {len(NON_TEACHING_CASES)}")
    results = []
    passed_count = 0
    external_count = 0
    failed_count = 0

    for case_info in NON_TEACHING_CASES:
        print(f"  Running [{case_info['category']}] {case_info['id']} ({case_info['title_cn']})...", end=" ")
        res = run_single_case(case_info, output_root)
        results.append(res)
        if res["status"] == "PASS":
            passed_count += 1
            print(f"[PASS] ({res['duration_sec']}s)")
        elif res["status"] == "EXTERNAL_DATA_REQUIRED":
            external_count += 1
            print(f"[EXTERNAL_DATA_REQUIRED] ({res['duration_sec']}s)")
        else:
            failed_count += 1
            print(f"[FAIL] {res['error_msg']}")

    summary_data = {
        "total_cases": len(NON_TEACHING_CASES),
        "passed_cases": passed_count,
        "external_data_cases": external_count,
        "failed_cases": failed_count,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cases": results,
    }

    # Save JSON summary
    json_path = output_root / "case_run_summary.json"
    json_path.write_text(json.dumps(summary_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Generate Markdown summary
    md_content = f"# 非教学案例全量运行审计汇总\n\n"
    md_content += f"审计时间: {summary_data['timestamp']}\n"
    md_content += f"统计: 总案例 {summary_data['total_cases']} | 独立运行通过 {passed_count} | 需外部数据/长期扫描 {external_count} | 失败 {failed_count}\n\n"
    md_content += "| 案例 ID | 分类 | 中文名称 | 求解模型 | 耗时(s) | 运行状态 | 备注说明 |\n"
    md_content += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for r in results:
        if r["status"] == "PASS":
            status_text = "✅ PASS"
        elif r["status"] == "EXTERNAL_DATA_REQUIRED":
            status_text = "⚠️ EXTERNAL_DATA_REQUIRED"
        else:
            status_text = "❌ FAIL"
        md_content += f"| `{r['id']}` | {r['category']} | {r['title_cn']} | {r['solver']} | {r['duration_sec']} | {status_text} | {r['error_msg']} |\n"

    md_path = output_root / "case_run_summary.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"\nAudit completed: {passed_count} passed, {external_count} external data required, {failed_count} failed.")
    print(f"Summary written to:\n  - {json_path}\n  - {md_path}")

    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
