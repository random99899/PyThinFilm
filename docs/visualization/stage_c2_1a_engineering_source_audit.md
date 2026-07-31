# Stage C.2.1A 五个工程应用案例权威来源与结构审计报告

> **审计基线**: `examples/applications/` 源码解算器及入口函数  
> **审计状态**: `SOURCE_AUDIT_PASSED`  
> **模板适配结论**: 5 个工程案例**全部复用已有 3D 模板**（无需创建 `engineering-device` 新模板）  
> **状态锁定规则**: 保持 `migration_status = PENDING_ENGINE_MIGRATION`（不进行前端绑定修改与状态改写）

---

## 1. 案例权威来源定位与调用链

| Case ID | 展示名称 | 正式源文件 | 权威入口函数 | 依赖项 | 物理模型 |
|---|---|---|---|---|---|
| `app_solar_cell_ar` | 太阳能电池三层增透膜 | `examples/applications/solar_cell_ar.py` | `run_solar_cell_ar` | `thinfilm.education` | TMM + 常数折射率 |
| `app_wdm_filter` | WDM 光通信密集波分复用滤光片 | `examples/applications/wdm_filter.py` | `run_wdm_filter` | `thinfilm.education` | TMM 1550nm C波段 |
| `app_laser_mirror` | 1064nm 激光高反镜 | `examples/applications/laser_mirror.py` | `run_laser_mirror` | `thinfilm.education` | TMM 1064nm DBR |
| `app_phone_lens_ar` | 手机镜头多层增透膜 | `examples/applications/phone_lens_ar.py` | `run_phone_lens_ar` | `thinfilm.education` | TMM 可见光平坦增透 |
| `app_smart_window` | 智能调温窗 Low-E 膜 | `examples/applications/smart_window.py` | `run_smart_window` | `thinfilm.education` | TMM + 金属 Ag 复折射率 |

---

## 2. 详细结构与物理输入哈希 (`physics_input_hash`)

### 2.1 `app_solar_cell_ar` (太阳能电池增透膜)
- **膜层结构**: `Air / MgF2(99.64nm) / TiO2(59.78nm) / SiO2(94.18nm) / Si(n=3.5)`
- **层数**: 3 层
- **材料折射率模型**: `CONSTANT_REAL_INDEX` (\(n_{\text{MgF2}}=1.38, n_{\text{TiO2}}=2.30, n_{\text{SiO2}}=1.46, n_{\text{Si}}=3.5+0.0j\))
- **`physics_input_hash`**: `80fe4bb33515695d`
- **能量守恒**: \(R + T + A \equiv 1.0\) (无吸收，\(A=0\))

### 2.2 `app_wdm_filter` (WDM 通信滤光片)
- **膜层结构**: `Air / (TiO2/SiO2)^4 2L (SiO2/TiO2)^4 / Glass(n=1.46)`
- **层数**: 8 层 DBR + 腔体（对应 17 层等效光学薄膜）
- **材料折射率模型**: `CONSTANT_REAL_INDEX` (\(n_{\text{TiO2}}=2.30, n_{\text{SiO2}}=1.46\))
- **`physics_input_hash`**: `9c916c228ca666fa`
- **能量守恒**: \(R + T + A \equiv 1.0\)

### 2.3 `app_laser_mirror` (1064nm 激光高反镜)
- **膜层结构**: `Air / (TiO2/SiO2)^8 H / Glass(n=1.46)`
- **层数**: 16 层膜
- **材料折射率模型**: `CONSTANT_REAL_INDEX` (\(n_{\text{TiO2}}=2.30, n_{\text{SiO2}}=1.46\))
- **`physics_input_hash`**: `de5ec15fa2aefd57`
- **能量守恒**: \(R + T + A \equiv 1.0\)

### 2.4 `app_phone_lens_ar` (手机镜头多层 AR)
- **膜层结构**: `Air / MgF2(99.64nm) / ZrO2(65.48nm) / SiO2(94.18nm) / LaSFN9 Glass(n=1.80)`
- **层数**: 3 层
- **材料折射率模型**: `CONSTANT_REAL_INDEX` (\(n_{\text{MgF2}}=1.38, n_{\text{ZrO2}}=2.10, n_{\text{SiO2}}=1.46\))
- **`physics_input_hash`**: `1f46a9e793960f8a`
- **能量守恒**: \(R + T + A \equiv 1.0\)

### 2.5 `app_smart_window` (智能调温窗 Low-E)
- **膜层结构**: `Air / WO3(80nm) / NiO(50nm) / Ag(15nm) / Glass(n=1.52)`
- **层数**: 3 层
- **材料折射率模型**: `CONSTANT_COMPLEX_INDEX` (\(n_{\text{WO3}}=2.10, n_{\text{NiO}}=2.00, \tilde{n}_{\text{Ag}}=0.05 + 3.20j\))
- **`physics_input_hash`**: `1c1084bad123ae7b`
- **能量守恒**: \(R + T + A \equiv 1.0\) (薄 Ag 吸收消光，\(A > 0\))

---

## 3. 模板适配判断与降级结论

> **关键决策**: 所有 5 个工程应用案例均可**直接复用已有 Web3D 模板**，无需为 Stage C.2 新增 `engineering-device` 模板。

1. **`app_solar_cell_ar`**: 3 层常规 AR 膜 $\to$ 适配复用 **`periodic-stack`**；
2. **`app_wdm_filter`**: 1550nm 缺陷腔结构 $\to$ 适配复用 **`defect-cavity`**；
3. **`app_laser_mirror`**: 1064nm DBR 周期高反堆栈 $\to$ 适配复用 **`periodic-stack`**；
4. **`app_phone_lens_ar`**: 3 层常规镜头 AR 膜 $\to$ 适配复用 **`periodic-stack`**；
5. **`app_smart_window`**: 包含金属 Ag 层与 NIR 吸收/反射权衡 $\to$ 适配复用 **`metal-dbr-interface`**。

---

## 4. 动态正弦波适配边界

- **`app_solar_cell_ar`**, **`app_phone_lens_ar`**, **`app_laser_mirror`**: `FORWARD_RAY_PROPAGATION`（光线沿光路推进，振幅按 \(R/T\) 示意）；
- **`app_wdm_filter`**: `FORWARD_BACKWARD_WAVE_ILLUSTRATION`（缺陷腔内提供前/后向波等振幅驻波示意）；
- **`app_smart_window`**: `FORWARD_RAY_PROPAGATION`（在 Ag 金属界面处展示透射衰减及吸收比率）。
