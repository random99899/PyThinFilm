export const EVIDENCE_CASE_CONFIGS = Object.freeze({
  tamm_interface_priority: { slug: "tamm-interface-priority", title: "Tamm 界面态优先极化筛选", kicker: "外部数据证据 · Tamm" },
  tamm_phase_candidates: { slug: "tamm-phase-candidates", title: "Tamm 相位匹配候选点搜寻", kicker: "外部数据证据 · Tamm" },
  tamm_phase_focus: { slug: "tamm-phase-focus", title: "Tamm 相位聚焦与吸收增强", kicker: "外部数据证据 · Tamm" },
  tamm_reflection_phase_screen: { slug: "tamm-reflection-phase-screen", title: "Tamm 界面反射相位多波长筛选", kicker: "外部数据证据 · Tamm" },
  tamm_interface_window_bundle: { slug: "tamm-interface-window-bundle", title: "Tamm 界面窗口束", kicker: "外部数据证据 · 局域统计" },
  tamm_interface_window_scan: { slug: "tamm-interface-window-scan", title: "Tamm 界面窗口扫描", kicker: "外部数据证据 · 稳健性扫描" },
  absorbing_baseline_template: { slug: "absorbing-baseline-template", title: "吸收表面基线模板", kicker: "输入契约 · 模板" },
  absorbing_surface_bundle: { slug: "absorbing-surface-bundle", title: "吸收表面综合计算束", kicker: "外部数据证据 · 吸收表面" },
  absorbing_surface_gain: { slug: "absorbing-surface-gain", title: "吸收表面增益模型", kicker: "外部数据证据 · 基准对比" },
  absorbing_surface_gain_trend: { slug: "absorbing-surface-gain-trend", title: "吸收表面增益趋势", kicker: "外部数据证据 · 参数趋势" },
  advanced_ar_bundle: { slug: "advanced-ar-bundle", title: "高级增透膜计算束", kicker: "外部数据证据 · Python—COMSOL 验证" },
  porous_double_ar_topic_bundle: { slug: "porous-double-ar-topic", title: "多孔双层增透专题", kicker: "外部数据证据 · 专题验证" },
});

export function getEvidenceCaseConfig(caseId) {
  const config = EVIDENCE_CASE_CONFIGS[caseId];
  if (!config) throw new Error(`未声明外部证据案例：${caseId}`);
  return Object.freeze({ caseId, ...config });
}
