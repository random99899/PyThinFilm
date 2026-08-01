const lowHighReflectance = ({ r }) => {
  if (r < 0.08) return { id: "LOW_REFLECTION", label: "低反射：透射波占主导" };
  if (r >= 0.7) return { id: "RELATIVE_HIGH", label: "高反射：反射波占主导" };
  return { id: "INTERMEDIATE", label: "中等反射：反射与透射并存" };
};

const filterPassStop = ({ t }) => {
  if (t >= 0.8) return { id: "LOW_REFLECTION", label: "透射峰：透射波占主导" };
  if (t <= 0.1) return { id: "RELATIVE_HIGH", label: "阻带：反射波占主导" };
  return { id: "INTERMEDIATE", label: "滤光片边缘：反射与透射并存" };
};

const singleLayerPresets = Object.freeze([
  { id: "minimum", label: "最低反射", selector: "minR" },
  { id: "design", label: "550 nm", wavelengthNm: 550 },
  { id: "maximum", label: "相对高反", selector: "maxR" },
]);

const dbrPresets = Object.freeze([
  { id: "design", label: "550 nm", wavelengthNm: 550 },
  { id: "peak", label: "反射峰值", selector: "maxR" },
  { id: "contrast", label: "带外对照", selector: "minR" },
]);

const fpPresets = Object.freeze([
  { id: "pass", label: "透射峰值", selector: "maxT" },
  { id: "design", label: "550 nm", wavelengthNm: 550 },
  { id: "stop", label: "最深阻带", selector: "minT" },
]);

export const ENGINEERING_CASE_CONFIGS = Object.freeze({
  quarter_wave_single_layer: Object.freeze({
    caseId: "quarter_wave_single_layer", slug: "quarter-wave-single-layer", title: "1/4 波长单层减反射膜",
    kicker: "PyThinFilm · 独立教学案例", expectedLayerCount: 1, sceneName: "StandaloneQuarterWaveSingleLayerScene",
    presets: singleLayerPresets, classify: lowHighReflectance,
    caveat: "最低反射、设计波长与相对高反均来自当前正式 TE/TM 光谱。",
  }),
  half_wave_single_layer: Object.freeze({
    caseId: "half_wave_single_layer", slug: "half-wave-single-layer", title: "1/2 波长单层相位膜",
    kicker: "PyThinFilm · 独立教学案例", expectedLayerCount: 1, sceneName: "StandaloneHalfWaveSingleLayerScene",
    presets: singleLayerPresets, classify: lowHighReflectance,
    caveat: "半波层的教学重点是相位等效；外部 R/T 波形不能替代膜内相位分析。",
  }),
  single_ar: Object.freeze({
    caseId: "single_ar", slug: "single-ar", title: "单层减反射膜",
    kicker: "PyThinFilm · 独立教学案例", expectedLayerCount: 1, sceneName: "StandaloneSingleArScene",
    presets: singleLayerPresets, classify: lowHighReflectance,
    caveat: "反射抑制结论依据正式 R；正弦波仅用于辅助比较。",
  }),
  high_reflector: Object.freeze({
    caseId: "high_reflector", slug: "high-reflector", title: "高反射膜",
    kicker: "PyThinFilm · 独立教学案例", expectedLayerCount: 7, sceneName: "StandaloneHighReflectorScene",
    presets: dbrPresets, classify: lowHighReflectance,
    caveat: "反射带和带外对照来自同一正式光谱，不改变七层正式结构。",
  }),
  quarter_wave_stack: Object.freeze({
    caseId: "quarter_wave_stack", slug: "quarter-wave-stack", title: "1/4 波长 QW 膜堆",
    kicker: "PyThinFilm · 独立教学案例", expectedLayerCount: 7, sceneName: "StandaloneQuarterWaveStackScene",
    presets: dbrPresets, classify: lowHighReflectance,
    caveat: "QW 膜堆通过正式 R/T 展示反射带；屏幕层厚采用视觉映射。",
  }),
  bragg_reflector: Object.freeze({
    caseId: "bragg_reflector", slug: "bragg-reflector", title: "布拉格反射镜（DBR）",
    kicker: "PyThinFilm · 独立教学案例", expectedLayerCount: 7, sceneName: "StandaloneBraggReflectorScene",
    presets: dbrPresets, classify: lowHighReflectance,
    caveat: "550 nm、反射峰与带外点均读取正式光谱；TE/TM 分裂保持原数据。",
  }),
  fp_single_halfwave: Object.freeze({
    caseId: "fp_single_halfwave", slug: "fp-single-halfwave", title: "单半波型 F-P 滤光片",
    kicker: "PyThinFilm · 独立教学案例", expectedLayerCount: 13, sceneName: "StandaloneFpSingleHalfwaveScene",
    presets: fpPresets, classify: filterPassStop,
    caveat: "透射峰和阻带来自正式光谱；示意波不表示腔内定量驻波场。",
  }),
  fp_filter: Object.freeze({
    caseId: "fp_filter", slug: "fp-filter", title: "F-P 腔窄带透射滤光片",
    kicker: "PyThinFilm · 独立教学案例", expectedLayerCount: 13, sceneName: "StandaloneFpFilterScene",
    presets: Object.freeze([
      { id: "resonance", label: "缺陷模", path: ["resonance_metrics", "$POL", "selected_peak", "wavelength_nm"] },
      { id: "design", label: "550 nm", wavelengthNm: 550 },
      { id: "stop", label: "最深阻带", selector: "minT" },
    ]),
    classify: filterPassStop,
    caveat: "缺陷模优先使用正式 resonance_metrics；不把全光谱最大透射误称为腔内缺陷模。",
  }),
  narrowband_filter: Object.freeze({
    caseId: "narrowband_filter", slug: "narrowband-filter", title: "窄带透射滤光片",
    kicker: "PyThinFilm · 独立教学案例", expectedLayerCount: 17, sceneName: "StandaloneNarrowbandFilterScene",
    presets: fpPresets, classify: filterPassStop,
    caveat: "透射峰与最深阻带用于对比窄带滤光行为；保留十七层正式结构。",
  }),
  tamm_phase_bundle: Object.freeze({
    caseId: "tamm_phase_bundle", slug: "tamm-phase-bundle", title: "Tamm 反射相位相干匹配束",
    kicker: "PyThinFilm · 独立研究案例", expectedLayerCount: 8, sceneName: "StandaloneTammPhaseBundleScene",
    presets: Object.freeze([
      { id: "candidate", label: "候选点", path: ["selected_candidate", "wavelength_nm"] },
      { id: "maximum", label: "反射峰值", selector: "maxR" },
      { id: "minimum", label: "反射谷值", selector: "minR" },
    ]),
    classify({ r, a }) {
      if (a >= 0.1) return { id: "INTERMEDIATE", label: "有损候选点：吸收不可忽略" };
      return lowHighReflectance({ r });
    },
    caveat: "候选点读取正式 selected_candidate；当前固定复折射率和相位参考面限制继续有效。",
  }),
  app_wdm_filter: Object.freeze({
    caseId: "app_wdm_filter",
    slug: "wdm-filter",
    title: "WDM 窄带滤光片",
    kicker: "PyThinFilm · 独立工程应用",
    expectedLayerCount: 17,
    sceneName: "StandaloneWdmFilterScene",
    presets: Object.freeze([
      { id: "primary", label: "通带峰值", metric: "peak_wavelength_nm" },
      { id: "target", label: "1550 nm", wavelengthNm: 1550 },
      { id: "contrast", label: "最深阻带", selector: "minT" },
    ]),
    classify({ r, t }) {
      if (t >= 0.8) return { id: "LOW_REFLECTION", label: "通带：透射波占主导" };
      if (t <= 0.1) return { id: "RELATIVE_HIGH", label: "阻带：反射波占主导" };
      return { id: "INTERMEDIATE", label: "通带边缘：反射与透射并存" };
    },
    caveat: "通带与阻带均来自当前正式光谱；正弦波只表达对应 R/T 的教学示意振幅。",
  }),
  app_laser_mirror: Object.freeze({
    caseId: "app_laser_mirror",
    slug: "laser-mirror",
    title: "1064 nm 激光高反镜",
    kicker: "PyThinFilm · 独立工程应用",
    expectedLayerCount: 17,
    sceneName: "StandaloneLaserMirrorScene",
    presets: Object.freeze([
      { id: "primary", label: "1064 nm", wavelengthNm: 1064 },
      { id: "peak", label: "反射峰值", selector: "maxR" },
      { id: "contrast", label: "低反射对照", selector: "minR" },
    ]),
    classify({ r }) {
      if (r >= 0.99) return { id: "RELATIVE_HIGH", label: "高反射带：透射波被显著抑制" };
      if (r <= 0.1) return { id: "LOW_REFLECTION", label: "带外对照：反射较低" };
      return { id: "INTERMEDIATE", label: "带边：反射与透射并存" };
    },
    caveat: "高反射结论依据正式 R 数值；零功率或近零透射波按既有阈值抑制或标记放大。",
  }),
  app_phone_lens_ar: Object.freeze({
    caseId: "app_phone_lens_ar",
    slug: "phone-lens-ar",
    title: "手机镜头三层减反膜",
    kicker: "PyThinFilm · 独立工程应用",
    expectedLayerCount: 3,
    sceneName: "StandalonePhoneLensArScene",
    presets: Object.freeze([
      { id: "blue", label: "蓝光 450", wavelengthNm: 450 },
      { id: "green", label: "绿光 550", wavelengthNm: 550 },
      { id: "red", label: "红光 650", wavelengthNm: 650 },
    ]),
    classify({ r }) {
      if (r < 0.05) return { id: "LOW_REFLECTION", label: "低反射点：透射波占主导" };
      if (r >= 0.15) return { id: "RELATIVE_HIGH", label: "可见光反射偏高：反射波不可忽略" };
      return { id: "INTERMEDIATE", label: "中等反射：透射占主导但反射可见" };
    },
    caveat: "蓝、绿、红三个波长用于检查可见光颜色一致性；不得由单点波形替代全波段指标。",
  }),
});

export function getEngineeringCaseConfig(caseId) {
  const config = ENGINEERING_CASE_CONFIGS[caseId];
  if (!config) throw new Error(`未声明独立工程案例：${caseId}`);
  return config;
}
