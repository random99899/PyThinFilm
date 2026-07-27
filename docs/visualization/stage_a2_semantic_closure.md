# PyThinFilm 全案例 3D 动态可视化 — Stage A.2 语义收口与物理案例映射报告

本报告响应《Stage A.2 最终语义修正》指令，完成对 3D 案例注册表、校验器与归档文档的语义收口，精确划分了案例条目类型（`entry_kind`）、物理案例映射（`physical_case_id`）与 4 维独立状态评估，补齐了计算来源与动画语义属性。

---

## 一、 实体类型与物理案例映射演算 (Entry Kind & Physical Case Mapping)

经过对 `thinfilm/education.py:L280-295` 的代码证据查验，确认 `narrowband_filter` 拥有独立设置参数（`periods = 5`，即两侧各 5 周期 DBR 高阶反射镜，不同于 `fp_filter` 的 4 周期），属于独立的物理案例，而非单纯别名。

因此，注册表映射关系如下：
* **`guided_grating_demo`**：`entry_kind` = `"runner"`, `physical_case_id` = `"guided_grating_emt"`；
* **其余 40 项案例**（包含 `narrowband_filter`）：`entry_kind` = `"case"`, `physical_case_id` = `<自身 ID>`。

### 精确数据统计指标
1. `registry_entry_count` = **41**
2. `physical_case_count` = **40**
3. `alias_entry_count` = **0**
4. `runner_entry_count` = **1**
5. `visualization_target_count` = **40**

---

## 二、 多维状态统计拆解 (Detailed Status Metrics)

取消把多个维度混为单一状态的旧模式，在注册表中为所有 41 项条目提供 4 个独立状态维度：

1. **`geometry_ready_count`** = **40**
2. **`geometry_mismatch_count`** = **1**（`fp_filter_3d` 原型：原型采用 3 周期 `Air/(LH)^3 D (HL)^3/Glass` 几何，而 Python 官方 `fp_filter` 使用 4 周期 `Air/(HL)^4 2L (LH)^4/Glass`）
3. **`physics_data_ready_count`** = **34**
4. **`illustrative_only_count`** = **1**（`tamm_state_3d` 原型：未绑定 Python 导出结果 json 前为教学示意模式）
5. **`ready_for_migration_count`** = **2**（`single_ar_3d`, `bragg_reflector_3d`）
6. **`prototype_only_count`** = **2**（`fp_filter_3d`, `tamm_state_3d`）
7. **`external_data_required_count`** = **6**（依赖桌面外部 CSV 数据脚本）
8. **`blocked_count`** = **0**

---

## 三、 四个已有 Three.js 原型的计算来源与动画语义审查

针对 `C:\Users\L2791\Downloads\visualizations` 目录下的 4 个原型进行多维属性归纳：

| 原型 ID / 案例 ID | 计算来源 (`calculation_source`) | Python 对照 (`python_reference_comparison`) | 动画语义 (`animation_semantics`) | 几何状态 | 物理数据状态 | 迁移状态 | 冲突状态 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `single_ar_3d` (`single_ar`) | `frontend_reimplementation` | `PASSED` | `PHYSICS_DRIVEN` | `GEOMETRY_READY` | `PHYSICS_DATA_READY` | `READY_FOR_MIGRATION` | `NONE` |
| `bragg_reflector_3d` (`bragg_reflector`) | `frontend_reimplementation` | `PASSED` | `PHYSICS_DRIVEN` | `GEOMETRY_READY` | `PHYSICS_DATA_READY` | `READY_FOR_MIGRATION` | `NONE` |
| `fp_filter_3d` (`fp_filter`) | `frontend_reimplementation` | `PASSED` | `PHYSICS_DRIVEN` | `GEOMETRY_MISMATCH` | `PHYSICS_DATA_READY` | `PROTOTYPE_ONLY` | `PROTOTYPE_GEOMETRY_MISMATCH` |
| `tamm_state_3d` (`tamm_phase_bundle`) | `illustrative_only` | `NOT_RUN` | `TEACHING_ILLUSTRATION` | `GEOMETRY_READY` | `ILLUSTRATIVE_ONLY` | `PROTOTYPE_ONLY` | `NONE` |

---

## 四、 自动化校验与回归测试执行日志

1. **注册表校验脚本 (`scripts/validate_case_registry.py`)**：
   ```text
   =================================================================
   PyThinFilm 3D Case Registry Semantic Closure Audit (Stage A.2)
   =================================================================
   Registry Entry Count:          41
   Unique Entry IDs:              41
   Physical Case Count:           40
   Alias Entry Count:             0
   Runner Entry Count:            1
   Visualization Target Count:    40
   [PASS] Entry Count Assertions PASSED (41 entries, 40 physical cases, 0 alias, 1 runner, 40 targets).

   Detailed Status Metrics Breakdown:
     - geometry_ready_count:        40
     - geometry_mismatch_count:     1
     - physics_data_ready_count:    34
     - illustrative_only_count:     1
     - ready_for_migration_count:   2
     - prototype_only_count:        2
     - external_data_required_count:6
     - blocked_count:               0

   [PASS] All Schema, Field Completeness & Status Enum Checks PASSED.
   =================================================================
   ```

2. **JSON 语法规范校验**：
   `py -m json.tool web3d/data/case_registry.json > $null` $\to$ **Exit Code 0**

3. **Pytest 全量回归测试**：
   `py -m pytest tests/ -q` $\to$ **`334 passed, 0 failed in 5.62s`**

---

## 五、 Git 提交信息

* **Git Branch**：`national/v1.1-dev`
* **Stage A.2 提交号**：待提交固化
* **Commit Message**：`fix(web3d): close Stage A registry semantics and physical-case mapping`
