# 非教学案例与拓展研究总账 (Non-Teaching Case Registry)

本文档记录 PyThinFilm 平台在教学案例之外的 **22 项工程应用、真实材料效应及拓展研究案例** 的全量清单、代码入口、求解模型、运行状态与国赛展示层级划定。

---

## 统计概览

* **案例总数**：22 项
* **独立运行通过 (PASS)**：19 项
* **需外部 CSV 数据 (EXTERNAL_DATA_REQUIRED)**：3 项
* **运行失败 (FAIL)**：0 项

---

## 全量非教学案例档案表

| 序号 | 案例 ID | 中文名称 | 分类 | 代码入口 | 运行命令 | 求解模型 | 默认结构/参数摘要 | 输出文件 | 当前状态 | 国赛展示层级 |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **1** | `app_solar_cell_ar` | 太阳能电池三层增透膜 | 工程应用 | `examples.applications.solar_cell_ar:run_solar_cell_ar` | `py -m examples.applications.solar_cell_ar` | TMM + 实测色散 | $\text{Air} / \text{MgF}_2 / \text{TiO}_2 / \text{SiO}_2 / \text{Si}$ | `spectrum.png, metrics.json, spectrum.csv` | **PASS** | 说明书工程案例 |
| **2** | `app_wdm_filter` | WDM 光通信密集波分复用滤光片 | 工程应用 | `examples.applications.wdm_filter:run_wdm_filter` | `py -m examples.applications.wdm_filter` | TMM | 1550nm 窄带 F-P 腔 $(HL)^4 2L (LH)^4$ | `spectrum.png, metrics.json, spectrum.csv` | **PASS** | 说明书工程案例 |
| **3** | `app_laser_mirror` | 1064nm 激光高反镜 | 工程应用 | `examples.applications.laser_mirror:run_laser_mirror` | `py -m examples.applications.laser_mirror` | TMM | 1064nm 周期 DBR $(HL)^{10}$ ($TiO_2/SiO_2$) | `spectrum.png, metrics.json, spectrum.csv` | **PASS** | 说明书工程案例 |
| **4** | `app_phone_lens_ar` | 手机镜头多层增透膜 | 工程应用 | `examples.applications.phone_lens_ar:run_phone_lens_ar` | `py -m examples.applications.phone_lens_ar` | TMM + 实测色散 | 450-650nm 宽带可调增透膜系 | `spectrum.png, metrics.json, spectrum.csv` | **PASS** | 说明书工程案例 |
| **5** | `app_smart_window` | 智能调温窗 Low-E 膜 | 工程应用 | `examples.applications.smart_window:run_smart_window` | `py -m examples.applications.smart_window` | TMM | $WO_3 / NiO / Ag$ 隔热电致变色结构 | `spectrum.png, metrics.json, spectrum.csv` | **PASS** | 说明书工程案例 |
| **6** | `mat_library_demo` | 真实材料库与色散插值演示 | 材料效应 | `cases/materials/run_material_library_demo.py` | `py cases/materials/run_material_library_demo.py` | TMM + Real (n,k) | $SiO_2, TiO_2, Si, Ag, Au$ 实测 $(n,k)$ | `overview.png, manifest.json` | **PASS** | 附录材料库 |
| **7** | `tamm_interface_priority` | Tamm 界面态优先极化筛选 | 拓展研究 | `cases/tamm/run_tamm_interface_priority.py` | `py cases/tamm/run_tamm_interface_priority.py` | TMM (极化差) | 30nm $Ag / (TiO_2/SiO_2)^N$ DBR | `v1.png, v1.json, v1.txt` | **PASS** | 附录拓展 |
| **8** | `tamm_phase_bundle` | Tamm 反射相位相干匹配束 | 拓展研究 | `cases/tamm/run_tamm_phase_bundle.py` | `py cases/tamm/run_tamm_phase_bundle.py` | TMM 相位算子 | $\phi_{\text{DBR}} + \phi_{\text{metal}} \equiv 0$ | `dw_phase_v1.png, csv, json` | **PASS** | 附录拓展 |
| **9** | `tamm_phase_candidates` | Tamm 相位匹配候选点搜寻 | 拓展研究 | `cases/tamm/run_tamm_phase_candidates.py` | `py cases/tamm/run_tamm_phase_candidates.py` | TMM 相位算子 | 谐振极大值波长点搜寻 | `v1.csv, v1.json, v1.txt` | **PASS** | 附录拓展 |
| **10** | `tamm_phase_focus` | Tamm 相位聚焦与吸收增强 | 拓展研究 | `cases/tamm/run_tamm_phase_focus.py` | `py cases/tamm/run_tamm_phase_focus.py` | TMM + 吸收损耗 | $A_{\text{tamm}} \approx 98.2\%$ 窄带共振吸收 | `focus_v1.png, csv, json` | **PASS** | 附录拓展 |
| **11** | `tamm_reflection_phase_screen` | Tamm 界面反射相位多波长筛选 | 拓展研究 | `cases/tamm/run_tamm_reflection_phase_screen.py` | `py cases/tamm/run_tamm_reflection_phase_screen.py` | TMM 多波长相位 | 400-800nm 相位漂移矩阵 | `v1.png, v1.csv, v1.json` | **PASS** | 附录拓展 |
| **12** | `tamm_interface_window_bundle` | Tamm 界面窗口束 | 拓展研究 | `cases/tamm/run_tamm_interface_window_bundle.py` | `py cases/tamm/run_tamm_interface_window_bundle.py` | TMM + 外部数据 | 外部 2D 扫描数据整合 | 依赖外部数据 | **EXTERNAL** | 保留但不主展示 |
| **13** | `tamm_interface_window_scan` | Tamm 界面窗口扫描 | 拓展研究 | `cases/tamm/run_tamm_interface_window_scan.py` | `py cases/tamm/run_tamm_interface_window_scan.py` | TMM + 外部数据 | 界面粗糙度参数窗扫描 | 依赖外部数据 | **EXTERNAL** | 保留但不主展示 |
| **14** | `pdrc_cooling_bundle` | PDRC 被动辐射制冷评估束 | 拓展研究 | `cases/pdrc/run_pdrc_cooling_bundle.py` | `py cases/pdrc/run_pdrc_cooling_bundle.py` | TMM + 太阳/大气加权 | 太阳波段高反 + 大气窗口(8-13$\mu$m)高发射 | `spectrum.png, metrics.csv, summary.json` | **PASS** | 附录拓展 |
| **15** | `absorbing_baseline_template` | 吸收表面基线模板 | 拓展研究 | `cases/absorbing_surface/run_absorbing_surface_baseline_template.py` | `py cases/absorbing_surface/run_absorbing_surface_baseline_template.py` | TMM 基线 | 平面多层吸收结构基线 | `template.json, template.txt` | **PASS** | 附录拓展 |
| **16** | `absorbing_surface_bundle` | 吸收表面综合计算束 | 拓展研究 | `cases/absorbing_surface/run_absorbing_surface_bundle.py` | `py cases/absorbing_surface/run_absorbing_surface_bundle.py` | TMM 吸收局域 | 吸收光谱与透射比对 | `overview.png, v1_summary.json` | **PASS** | 附录拓展 |
| **17** | `absorbing_surface_gain` | 吸收表面增益模型 | 拓展研究 | `cases/absorbing_surface/run_absorbing_surface_gain.py` | `py cases/absorbing_surface/run_absorbing_surface_gain.py` | TMM + 外部数据 | 粗糙表面 vs 平面基准增益 | 依赖外部数据 | **EXTERNAL** | 保留但不主展示 |
| **18** | `absorbing_surface_gain_trend` | 吸收表面增益趋势 | 拓展研究 | `cases/absorbing_surface/run_absorbing_surface_gain_trend.py` | `py cases/absorbing_surface/run_absorbing_surface_gain_trend.py` | TMM + 外部数据 | 粗糙度参数与增益趋势 | `gain_trend_v1.json` | **PASS** | 附录拓展 |
| **19** | `rugate_80layer_table` | 80层 Rugate 褶皱滤光片列表 | 拓展研究 | `cases/advanced_ar/run_rugate_80layer_table.py` | `py cases/advanced_ar/run_rugate_80layer_table.py` | TMM 连续离散化 | 80 层正弦调制折射率表 | `comsol_layers.json, csv` | **PASS** | 附录拓展 |
| **20** | `advanced_ar_bundle` | 高级增透膜计算束 | 拓展研究 | `cases/advanced_ar/run_advanced_ar_bundle.py` | `py cases/advanced_ar/run_advanced_ar_bundle.py` | TMM + 外部数据 | 单层/多孔/蛾眼对比束 | `topic_overview.png, manifest.json` | **PASS** | 附录拓展 |
| **21** | `porous_double_ar_topic_bundle` | 多孔双层增透专题 | 拓展研究 | `cases/advanced_ar/run_porous_double_ar_topic_bundle.py` | `py cases/advanced_ar/run_porous_double_ar_topic_bundle.py` | TMM + 外部数据 | 多孔双层灵敏度计算束 | `sensitivity_overview.png` | **PASS** | 附录拓展 |
| **22** | `guided_grating_demo` | 亚波长光栅 EMT 与 COMSOL 对照 | 拓展研究 | `cases/guided_grating/run_guided_grating_demo.py` | `py cases/guided_grating/run_guided_grating_demo.py` | EMT / COMSOL CSV IO | 零级 EMT + COMSOL CSV 指标提取 | `summary.json, spectrum.csv, RTA.png` | **PASS** | **S (主展示 3)** |

---

## 统一出图与数据治理规则

所有非教学案例在脚本执行时均遵循以下工程保障：
1. **无桌面交互依赖**：环境变量指定 `MPLBACKEND=Agg`；
2. **确定性输出目录**：结果统一输出至 `outputs/<case_id>/` 或系统指定的输出目录 `thinfilm_outputs/`；
3. **数据-图像双存**：生成 PNG 图像的同时，同步保存结构化 `spectrum.csv` 或 `summary.json`；
4. **资源显示显式关闭**：每次绘图完成后显式调用 `plt.close("all")` 释放内存。
