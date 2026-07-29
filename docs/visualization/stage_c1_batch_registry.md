# PyThinFilm 全案例 3D 动态可视化 — Stage C.1 第一批 6 个教学案例注册表与模板映射报告

本报告记录对 **Stage C.1 第一批 6 个教学案例** 的结构提取、模板映射与注册表升级。

---

## 一、 6 个教学案例模板映射与来源表

| 案例 ID | 正式 Python 来源入口 (`thinfilm/education.py`) | 3D 模板组件 (`web3d/src/templates/`) | 膜层结构 | 偏振支持 |
| :--- | :--- | :--- | :--- | :--- |
| **`quarter_wave_single_layer`** | `build_quarter_wave_single_layer_layers` | `single-interface` | Air / MgF2 99.64nm / Glass | TE, TM |
| **`half_wave_single_layer`** | `build_half_wave_single_layer_layers` | `single-interface` | Air / SiO2 199.28nm / Glass | TE, TM |
| **`high_reflector`** | `build_high_reflector_layers` | `periodic-stack` | Air / (HL)^3 H 7层 / Glass | TE, TM |
| **`quarter_wave_stack`** | `build_quarter_wave_stack_layers` | `periodic-stack` | Air / (HL)^3 H 7层 / Glass | TE, TM |
| **`fp_single_halfwave`** | `build_fp_single_halfwave_layers` | `defect-cavity` | Air / (HL)^3 C (LH)^3 13层 / Glass | TE, TM |
| **`narrowband_filter`** | `build_narrowband_filter_layers` | `defect-cavity` | Air / (HL)^4 C (LH)^4 17层 / Glass | TE, TM |

---

## 二、 注册表状态全量升级

全量 6 个案例在 `web3d/data/case_registry.json` 中均统一升级为：

```json
{
  "geometry_status": "GEOMETRY_VERIFIED",
  "physics_data_status": "PHYSICS_DATA_AVAILABLE",
  "python_export_status": "VERIFIED",
  "frontend_binding_status": "PASSED",
  "python_reference_comparison": "NOT_APPLICABLE",
  "migration_status": "MIGRATION_VERIFIED",
  "calculation_source": "python_export",
  "animation_semantics": "TEACHING_ILLUSTRATION",
  "conflict_status": "NONE"
}
```
