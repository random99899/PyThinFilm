# Stage C.V1J F-P 视觉原型人工检查

打开 `/apps/fp-filter/` 后检查：

## 首屏

- [ ] 一眼可辨认入射侧 DBR、中央缺陷腔和基底侧 DBR；
- [ ] 第 7 层标签与实际结构位置对应；
- [ ] “结构标注，不代表场强”常驻可见；
- [ ] 正式波长、偏振及 R/T/A 保持可见。

## 阅读解释

- [ ] 五步教学内容与冻结版本一致；
- [ ] 缺陷模与全谱最大透射点仍明确区分；
- [ ] 抽屉文字没有遮挡底部导航；
- [ ] 公式保持默认折叠。

## 观察模型

- [ ] 点击“观察模型”后抽屉缩为状态条；
- [ ] 当前步骤、波长、偏振和选中层不变；
- [ ] 点击“阅读解释”后回到同一步；
- [ ] 相机不跳动，Canvas 与 Renderer 仍各为 1。

## 视觉边界

- [ ] 缺陷腔描边没有被误解为场增强；
- [ ] 没有光晕、bloom、粒子或定量场强暗示；
- [ ] 动态正弦线仍明确属于教学示意；
- [ ] 结构分组按钮只选择正式层，不修改结构。

## 自动证据

```text
docs/visualization/runtime/stage_cv1j/fp_reading.png
docs/visualization/runtime/stage_cv1j/fp_model_focus.png
```

当前状态：`PENDING MANUAL ACCEPTANCE`
