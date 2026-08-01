export const ENGINEERING_CASE_CONFIGS = Object.freeze({
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
