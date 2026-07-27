# PyThinFilm 全案例 3D 可视化注册表与设计文档 (Stage A)

本文档记录 PyThinFilm 代码库中全部 **39 项有效案例** 的 3D 可视化注册表、4 项已有 Three.js 原型对齐情况、8 大可复用物理渲染模板映射以及参数冲突与边界审查结果。

---

## 一、 统计概览

* **全量有效案例总数**：**39 项**
* **已有 3D 原型对齐**：**4 项** (`single_ar`, `bragg_reflector`, `fp_filter`, `tamm_phase_bundle`)
* **3D 可视化就绪案例 (READY)**：**29 项**
* **需确认冲突案例 (CONFLICT_REQUIRES_CONFIRMATION)**：**6 项**（依赖外部桌面 CSV 数据的扩展分析脚本）

---

## 二、 4 项已有 3D 原型与案例 ID 映射

来自原 `visualizations/` 目录的 4 个独立 Vite/Three.js 原型已与仓库核心 `case_id` 完成精确对齐：

1. **Prototype 1 (`single_ar_3d`)** $\to$ `case_id: "single_ar"`
   * **物理机制**：单层增透膜，薄膜界面反射相消干涉；
   * **功能映射**：立体视角、剖面视角、膜层展开、斜入射、TE/TM 偏振电场矢量、导纳轨迹图。
2. **Prototype 2 (`bragg_reflector_3d`)** $\to$ `case_id: "bragg_reflector"`
   * **物理机制**：分布式布拉格反射镜 (DBR)，周期性高低折射率界面同相反射叠加形成带隙；
   * **功能映射**：周期层数 $N$ 调整、带隙随着周期数增加扩展、多界面同相反射指示。
3. **Prototype 3 (`fp_filter_3d`)** $\to$ `case_id: "fp_filter"`
   * **物理机制**：Fabry–Pérot 腔窄带透射滤光片，两侧 DBR 结合中央 $2L$ 半波缺陷腔形成强共振选频透射；
   * **功能映射**：腔内光场多次往返相长干涉、极窄透射峰展示。
4. **Prototype 4 (`tamm_state_3d`)** $\to$ `case_id: "tamm_phase_bundle"`
   * **物理机制**：Tamm 界面态，金属层 ($30\text{ nm Ag}$) 与 DBR 界面反射相位匹配 ($\phi_{\text{DBR}} + \phi_{\text{metal}} \equiv 0$)；
   * **功能映射**：金属/DBR 接触面强界面局域电场、两端呈指数/带隙衰减。

---

## 三、 8 大可复用物理渲染模板 (Physical Templates)

为了避免为每个案例复制代码，前端 3D 系统采用“**一个统一渲染器 + 八大物理模板 + JSON 驱动**”的统一架构：

1. **`single-interface` (单界面/少层干涉模板)**：
   * 适用于单层、双层、三层及镜头增透膜。
   * 支持斜入射折射、第一/第二界面反射叠加、TE/TM 电场动画。
2. **`periodic-stack` (周期多层膜模板)**：
   * 适用于 DBR、QW 膜堆、高反镜及 Rugate 褶皱滤光片。
   * 支持周期层展开、多界面反射相长叠加示意、带隙随着周期数收敛。
3. **`defect-cavity` (缺陷腔模板)**：
   * 适用于 F-P 单半波、双半波及窄带通信滤光片。
   * 支持腔内多次往返谐振光路、高 Q 值透射峰与腔内场积累。
4. **`metal-dbr-interface` (金属/DBR 界面模板)**：
   * 适用于 Tamm 界面态偏振筛选、相位聚焦与共振吸收。
   * 支持金属侧趋肤深度衰减、DBR 侧带隙衰减及界面相位匹配点标识。
5. **`absorber-stack` (吸收与有损介质模板)**：
   * 适用于多层吸收表面、有损干涉结构。
   * 支持层内坡印廷矢量与能量吸收衰减示意。
6. **`spectral-weighting` (光谱加权与选择性辐射模板)**：
   * 适用于 PDRC 被动辐射制冷。
   * 支持 3D 膜系结构与 2D 太阳光谱/大气红外窗口加权曲线联动。
7. **`engineering-device` (工程器件综合模板)**：
   * 适用于太阳能电池、智能窗、手机镜头、激光镜、WDM 设备。
   * 展示真实器件结构语境与实际工程评价指标。
8. **`grating-emt` (光栅等效介质模板)**：
   * 适用于一维亚波长光栅。
   * 展示光栅周期 $\Lambda$、占空比 $f$、TE/TM 结构双折射与 0 级有效介质近似范围警告 ($\rho = \frac{n_{\text{max}}\Lambda}{\lambda_0} < 1$)。

---

## 四、 39 项案例全量注册表

| 序号 | 案例 ID | 中文名称 | 案例分类 | 结构/膜系摘要 | 设计波长 | 入射角与偏振 | 对应 3D 模板 | 状态 | 证据与来源 |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | `quarter_wave_single_layer` | 1/4波长单层减反射膜 | 经典教学 | Air / MgF2(99.6nm) / Glass | 550nm | 0°, TE/TM | `single-interface` | **READY** | `thinfilm/education.py:L60` |
| **2** | `half_wave_single_layer` | 1/2波长单层相位膜(虚设层) | 经典教学 | Air / MgF2(199.3nm) / Glass | 550nm | 0°, TE/TM | `single-interface` | **READY** | `thinfilm/education.py:L73` |
| **3** | `single_ar` | 单层减反射膜(任意参数) | 经典教学 | Air / MgF2(111.5nm) / Glass | 550nm | 0°/45°, TE/TM | `single-interface` | **PROTOTYPE_EXIST** | Prototype 1: `single_ar_3d` |
| **4** | `porous_sio2_layer` | 多孔二氧化硅减反结构 | 经典教学 | Air / Porous-SiO2(104.2nm) / Glass | 550nm | 0°, TE/TM | `single-interface` | **READY** | `thinfilm/education.py:L99` |
| **5** | `porous_double_ar` | 多孔双层减反膜 | 经典教学 | Air / Porous-SiO2 / TiO2 / Glass | 550nm | 0°, TE/TM | `single-interface` | **READY** | `thinfilm/education.py:L112` |
| **6** | `moth_eye_effective_gradient` | 蛾眼等效渐变层减反膜 | 经典教学 | Air / 5-Graded-Layers / Glass | 550nm | 0°, TE/TM | `periodic-stack` | **READY** | `thinfilm/education.py:L126` |
| **7** | `double_ar` | 双层减反射膜(任意参数) | 经典教学 | Air / SiO2 / TiO2 / Glass | 550nm | 0°, TE/TM | `single-interface` | **READY** | `thinfilm/education.py:L145` |
| **8** | `quarter_wave_double_layer` | 四分之一波长双层减反膜(V形) | 经典教学 | Air / MgF2 / ZrO2 / Glass | 550nm | 0°, TE/TM | `single-interface` | **READY** | `thinfilm/education.py:L159` |
| **9** | `triple_ar` | 三层渐变折射率减反膜 | 经典教学 | Air / MgF2 / Al2O3 / ZrO2 / Glass | 550nm | 0°, TE/TM | `single-interface` | **READY** | `thinfilm/education.py:L173` |
| **10** | `high_reflector` | 高反射膜 | 经典教学 | Air / (TiO2/SiO2)^6 / Glass | 550nm | 0°, TE/TM | `periodic-stack` | **READY** | `thinfilm/education.py:L188` |
| **11** | `quarter_wave_stack` | 1/4波长QW膜堆 | 经典教学 | Air / (TiO2/SiO2)^6 / Glass | 550nm | 0°, TE/TM | `periodic-stack` | **READY** | `thinfilm/education.py:L203` |
| **12** | `bragg_reflector` | 布拉格反射镜(DBR) | 经典教学 | Air / (TiO2/SiO2)^6 / Glass | 550nm | 0°/30°, TE/TM | `periodic-stack` | **PROTOTYPE_EXIST** | Prototype 2: `bragg_reflector_3d` |
| **13** | `fp_single_halfwave` | 单半波型 F-P 滤光片 | 经典教学 | Air / (HL)^3 2L (LH)^3 / Glass | 550nm | 0°, TE/TM | `defect-cavity` | **READY** | `thinfilm/education.py:L233` |
| **14** | `fp_filter` | F-P 腔窄带透射滤光片 | 经典教学 | Air / (HL)^4 2L (LH)^4 / Glass | 550nm | 0°/20°, TE/TM | `defect-cavity` | **PROTOTYPE_EXIST** | Prototype 3: `fp_filter_3d` |
| **15** | `fp_double_halfwave` | 双半波型 F-P 滤光片 | 经典教学 | Air / (HL)^2 2L (LH)^2 L ... / Glass | 550nm | 0°, TE/TM | `defect-cavity` | **READY** | `thinfilm/education.py:L265` |
| **16** | `rugate_filter` | Rugate 褶皱渐变折射率滤光片 | 经典教学 | Air / 80-Sinusoidal-Layers / Glass | 550nm | 0°, TE/TM | `periodic-stack` | **READY** | `thinfilm/education.py:L303` |
| **17** | `neutral_beamsplitter` | 中性分束膜 | 经典教学 | Air / Ag-TiO2-Stack / Glass | 550nm | 45°, TE/TM | `single-interface` | **READY** | `thinfilm/education.py:L325` |
| **18** | `guided_grating_emt` | 一维亚波长光栅 EMT | 经典教学 | Air / 1D-Si-Grating / Substrate | 1550nm | 0°, TE/TM | `grating-emt` | **READY** | 教学主展示 3; `guided_grating/emt.py` |
| **19** | `app_solar_cell_ar` | 太阳能电池三层增透膜 | 工程应用 | Air / MgF2 / TiO2 / SiO2 / Si | 300-1100nm | 0°, TE/TM | `engineering-device` | **READY** | `examples/applications/solar_cell_ar.py` |
| **20** | `app_wdm_filter` | WDM 光通信滤光片 | 工程应用 | Air / (HL)^4 2L (LH)^4 / Glass | 1540-1560nm | 0°, TE/TM | `engineering-device` | **READY** | `examples/applications/wdm_filter.py` |
| **21** | `app_laser_mirror` | 1064nm 激光高反镜 | 工程应用 | Air / (TiO2/SiO2)^10 / Substrate | 1064nm | 0°, TE/TM | `engineering-device` | **READY** | `examples/applications/laser_mirror.py` |
| **22** | `app_phone_lens_ar` | 手机镜头多层增透膜 | 工程应用 | Air / MgF2/TiO2/SiO2/Al2O3 / Glass | 400-700nm | 0°/30°, TE/TM | `engineering-device` | **READY** | `examples/applications/phone_lens_ar.py` |
| **23** | `app_smart_window` | 智能调温窗 Low-E 膜 | 工程应用 | Air / WO3 / NiO / Ag / Glass | 300-2500nm | 0°, TE/TM | `engineering-device` | **READY** | `examples/applications/smart_window.py` |
| **24** | `mat_library_demo` | 真实材料库与色散插值演示 | 材料效应 | Air / Real-NK-Material / Substrate | 300-1000nm | 0°, TE/TM | `single-interface` | **READY** | `cases/materials/run_material_library_demo.py` |
| **25** | `tamm_interface_priority` | Tamm 界面态优先极化筛选 | 拓展研究 | Air / 30nm Ag / DBR | 600-900nm | 0°/30°, TE/TM | `metal-dbr-interface` | **READY** | `cases/tamm/run_tamm_interface_priority.py` |
| **26** | `tamm_phase_bundle` | Tamm 反射相位相干匹配束 | 拓展研究 | Air / 30nm Ag / DBR | 600-900nm | 0°, TE/TM | `metal-dbr-interface` | **PROTOTYPE_EXIST** | Prototype 4: `tamm_state_3d` |
| **27** | `tamm_phase_candidates` | Tamm 相位匹配候选点搜寻 | 拓展研究 | Air / 30nm Ag / DBR | 600-900nm | 0°, TE/TM | `metal-dbr-interface` | **READY** | `cases/tamm/run_tamm_phase_candidates.py` |
| **28** | `tamm_phase_focus` | Tamm 相位聚焦与吸收增强 | 拓展研究 | Air / 30nm Ag / DBR | 650nm | 0°, TE/TM | `metal-dbr-interface` | **READY** | `cases/tamm/run_tamm_phase_focus.py` |
| **29** | `tamm_reflection_phase_screen` | Tamm 界面反射相位多波长筛选 | 拓展研究 | Air / 30nm Ag / DBR | 400-800nm | 0°, TE/TM | `metal-dbr-interface` | **READY** | `cases/tamm/run_tamm_reflection_phase_screen.py` |
| **30** | `tamm_interface_window_bundle` | Tamm 界面窗口束 | 拓展研究 | Air / Ag / DBR | 600-900nm | 0°, TE/TM | `metal-dbr-interface` | **CONFLICT** | 需外部桌面 E3.csv, E4.csv |
| **31** | `tamm_interface_window_scan` | Tamm 界面窗口扫描 | 拓展研究 | `Air / Ag / DBR` | 600-900nm | 0°, TE/TM | `metal-dbr-interface` | **CONFLICT** | 需外部桌面 E3.csv, E4.csv |
| **32** | `pdrc_cooling_bundle` | PDRC 被动辐射制冷评估束 | 拓展研究 | Air / TiO2/SiO2/Ag / Substrate | 300-15000nm | 0°, TE/TM | `spectral-weighting` | **READY** | `cases/pdrc/run_pdrc_cooling_bundle.py` |
| **33** | `absorbing_baseline_template` | 吸收表面基线模板 | 拓展研究 | Air / Absorbing-Layer / Substrate | 550nm | 0°, TE/TM | `absorber-stack` | **READY** | `cases/absorbing_surface/run_absorbing_surface_baseline_template.py` |
| **34** | `absorbing_surface_bundle` | 吸收表面综合计算束 | 拓展研究 | Air / Complex-Absorbing-Stack | 300-1100nm | 0°, TE/TM | `absorber-stack` | **READY** | `cases/absorbing_surface/run_absorbing_surface_bundle.py` |
| **35** | `absorbing_surface_gain` | 吸收表面增益模型 | 拓展研究 | Air / Rough-Absorber / Substrate | 550nm | 0°, TE/TM | `absorber-stack` | **CONFLICT** | 需外部 --rough-csv 文件 |
| **36** | `absorbing_surface_gain_trend` | 吸收表面增益趋势 | 拓展研究 | Air / Rough-Absorber / Substrate | 550nm | 0°, TE/TM | `absorber-stack` | **CONFLICT** | 需外部 deg.p 样本目录 |
| **37** | `rugate_80layer_table` | 80层 Rugate 褶皱滤光片列表 | 拓展研究 | Air / 80-Layers / Glass | 550nm | 0°, TE/TM | `periodic-stack` | **READY** | `cases/advanced_ar/run_rugate_80layer_table.py` |
| **38** | `advanced_ar_bundle` | 高级增透膜计算束 | 拓展研究 | Air / Multi-AR-Stack / Glass | 550nm | 0°, TE/TM | `single-interface` | **CONFLICT** | 需外部 COMSOL 对照 CSV |
| **39** | `porous_double_ar_topic_bundle` | 多孔双层增透专题 | 拓展研究 | Air / Porous-Double-AR / Glass | 550nm | 0°, TE/TM | `single-interface` | **CONFLICT** | 需外部 COMSOL 对照 CSV |

---

## 五、 冲突与缺失数据清单 (Conflict & Missing Data Report)

以下 6 项拓展研究案例由于依赖桌面或外部 COMSOL 导出文件，在无外部数据时可静默降级为 3D 结构参数静态展示或跳过数据注入，不影响 3D 渲染器的统一运行：

1. `tamm_interface_window_bundle`（依赖 `C:\Users\L2791\OneDrive\Desktop\deg.p\E3.csv` 等）
2. `tamm_interface_window_scan`（依赖 `C:\Users\L2791\OneDrive\Desktop\deg.p\E4.csv` 等）
3. `absorbing_surface_gain`（依赖 `--rough-csv` 及 `--baseline-csv` 参数）
4. `absorbing_surface_gain_trend`（依赖 `C:\Users\L2791\OneDrive\Desktop\deg.p` 路径）
5. `advanced_ar_bundle`（依赖桌面对比 CSV 文件）
6. `porous_double_ar_topic_bundle`（依赖桌面对比 CSV 文件）

**处理建议**：在 3D 前端可视化系统中，此 6 项案例直接读取对应的 Python 计算抽象结构模型进行 3D 光路与层结构渲染，2D 光谱比对数据在缺失外部文件时优雅隐藏图例对比线。
