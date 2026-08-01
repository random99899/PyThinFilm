# Stage C.V1A：太阳电池减反膜 Three.js 视觉原型规范

## 1. 范围

本阶段只对 `app_solar_cell_ar` 启用学术科研风格视觉原型。其他案例继续使用原模板分支；不实施路由、WorkspaceShell、Repository、光谱页面、热力图或智能窗。

正式结构保持：

```text
Air
→ SiO2 (94.1781 nm)
→ TiO2 (59.7826 nm)
→ MgF2 (99.6377 nm)
→ Si substrate
```

空气只作为入射介质语义和标签，不绘制实体大方块。薄膜数量固定为三层，层序和真实厚度直接来自 `web3d/public/results/app_solar_cell_ar.json`。

## 2. 不变量

原型不得改变：

- Python TMM 计算和正式 JSON 数值；
- 层序、三层膜数量和基底；
- `SineWaveRenderer.update()` 的正弦传播公式；
- `stableTransverseBasis()` 的 TE/TM 偏振基；
- 当前波长与正式 R/T 光谱的振幅绑定；
- WebGLRenderer 单例、案例切换和资源释放主流程；
- `case_registry.json` 的 `migration_status`；
- 页面路由和工作区架构。

动态波仍标记为“教学示意波”，不得称为定量电场。

## 3. 公共视觉模块

| 模块 | 职责 |
|---|---|
| `visualTheme.js` | 浅色学术主题、克制灯光、波形语义色和交互强度 |
| `materialPalette.js` | 跨案例稳定材料色；未知材料使用稳定哈希色；仅声明金属具有 metalness |
| `thicknessMapping.js` | 单调、有最小可见值和最大限制的非线性厚度映射 |
| `cameraPresets.js` | `ISOMETRIC_SECTION`、`SIDE_SECTION`、`OPTICAL_PATH` 参数 |
| `layerAppearance.js` | 介质材质、细描边、悬停和选中外观 |

这些模块集中保存视觉参数，模板只组合它们。Stage C.V1A 仅由 solar 原型分支使用，暂不推广其他案例。

## 4. 色彩与材质

背景为暖白灰 `#edf0ed`，页面在 solar 案例下使用相同浅色变量。材料色采用低饱和固定色：

| 材料 | 色值 | metalness | 视觉语义 |
|---|---:|---:|---|
| SiO2 | `#b9ced8` | 0 | 冷灰蓝介质 |
| TiO2 | `#c8b79f` | 0 | 暖灰米色介质 |
| MgF2 | `#b8cbbd` | 0 | 低饱和灰绿介质 |
| Si | `#7d8994` | 0 | 深蓝灰基底 |
| Ag | `#aab0b5` | 0.72 | 仅供未来已声明金属使用 |

薄膜使用中高 roughness、低高光的 `MeshStandardMaterial`；边界由灰蓝细描边提供，不依赖强阴影。未知材料颜色由材料名稳定哈希到低饱和 HSL，禁止随机色。

## 5. 厚度映射

物理厚度到屏幕厚度采用有界幂函数：

```text
normalized = (thickness_nm / 120)^0.58
visual = clamp(0.22 + normalized × (0.64 - 0.22), 0.22, 0.64)
```

性质：

- 输入厚度越大，视觉厚度不减小；
- 最小可见厚度为 `0.22` 场景单位；
- 最大视觉厚度为 `0.64` 场景单位；
- Si 基底使用 `1.65` 场景单位，明显厚于薄膜；
- 默认层间距为零；“展开/叠合”是显式教学操作，不代表真实间隙；
- 标签始终显示正式 JSON 的真实厚度，并注明“厚度经过视觉放大”。

## 6. 相机

默认 `ISOMETRIC_SECTION`：同时显示横向膜面、侧面层序与完整基底，并给右侧标签留出空间。

辅助预设：

- `SIDE_SECTION`：近正交侧向观察层序和接触边界；
- `OPTICAL_PATH`：沿波传播平面观察入射、反射与透射路径；
- 本阶段不提供 `TOP_VIEW`。

相机以结构包围盒自动计算 target、距离、near/far 和 OrbitControls 缩放范围。重置视角总是回到当前案例默认的 `ISOMETRIC_SECTION`。

## 7. 灯光

solar 原型使用：

- `HemisphereLight`：暖白天空与冷灰地面，提供大范围柔和层次；
- 一盏 `DirectionalLight`：暖白主光，无 HDR 环境贴图；
- 弱 `AmbientLight`：避免侧面过深；
- 浅色雾仅用于远景背景统一，不制造泛光。

不启用 bloom、粒子、强阴影、高反射环境贴图或黑色科幻背景。

## 8. 动态波

波形的采样、相位、传播方向、速度、振幅和偏振基不变。solar 分支只覆盖显示参数：

| 波 | 固定语义色 | 说明 |
|---|---:|---|
| 入射 | `#a85f59` | 低饱和红 |
| 反射 | `#587a98` | 低饱和蓝 |
| 透射 | `#668d7a` | 低饱和绿 |

线宽参数设为 1、透明度约 0.86–0.88，并沿既有路径增加小型方向箭头。HUD 显示当前波长、TE/TM 和“教学示意波”。暂停、播放和 TE/TM 切换继续使用原控制逻辑。

零功率规则由既有独立提交 `1f6cf88 fix(web3d): suppress zero-power schematic waves` 保证：`power <= 1e-10` 时振幅为 0 且 `suppressedAsZero=true`；非零小功率可放大至最小可见值并标记 `exaggerated=true`。

## 9. 层交互

- raycaster 只检测三层膜 mesh，不把 Three.js 对象写入共享业务数据；
- 悬停时轻微发光和横向放大；
- 点击后保持选中，标签行同步高亮；
- 详情显示层号、材料和真实厚度；
- 点击 Canvas 空白区域取消选中；
- 案例切换或结构重建时移除事件、DOM overlay 和新增视觉资源，并清空选择。

## 10. 验收证据

真实 Chromium 截图输出到：

```text
docs/visualization/runtime/stage_cv1a/
  solar_default.png
  solar_side.png
  solar_optical_path.png
  solar_te.png
  solar_tm.png
```

视觉验收采用人工检查和行为断言，不使用截图像素完全相等。
