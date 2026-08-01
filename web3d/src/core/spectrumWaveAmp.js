/**
 * spectrumWaveAmp.js
 *
 * Calculates visual sine wave amplitudes tied to the selected wavelength and polarization
 * in the R/T spectrum.
 *
 * Math Formula:
 *   A_reflected_visual = A_incident * sqrt(R_selected)
 *   A_transmitted_visual = A_incident * sqrt(T_selected)
 *
 * Exaggeration & Boundaries:
 *   Min visible amplitude = 0.04
 *   Max display limit = 0.35
 *   Flagged with VISUAL_AMPLITUDE_EXAGGERATED if clamped or scaled.
 */

export function calculateWaveAmplitudesFromSpectrum(caseResult, polarization = "TE", selectedWavelengthNm = null) {
  let wl = selectedWavelengthNm;
  if (!wl) {
    if (caseResult && caseResult.case_id) {
      if (caseResult.case_id === "app_solar_cell_ar") wl = 550;
      else if (caseResult.case_id === "app_wdm_filter") wl = caseResult.metrics?.peak_wavelength_nm || 1550;
      else if (caseResult.case_id === "app_laser_mirror") wl = 1064;
      else if (caseResult.case_id === "app_phone_lens_ar") wl = 550;
    }
  }
  if (!wl) wl = 550;

  let rSelected = 0.5;
  let tSelected = 0.5;

  const polKey = (polarization === "TM" && caseResult && caseResult.TM) ? "TM" : "TE";
  const polData = caseResult ? caseResult[polKey] : null;

  const wList = (caseResult && (caseResult.wavelength_nm || caseResult.wavelengths)) ||
                (polData && (polData.wavelength_nm || polData.wavelengths)) || [];
  const rList = polData ? polData.R : [];
  const tList = polData ? polData.T : [];

  if (wList && wList.length > 0 && rList && rList.length === wList.length && tList && tList.length === wList.length) {
    if (wl <= wList[0]) {
      rSelected = rList[0];
      tSelected = tList[0];
    } else if (wl >= wList[wList.length - 1]) {
      rSelected = rList[rList.length - 1];
      tSelected = tList[tList.length - 1];
    } else {
      let idx = 0;
      for (let i = 0; i < wList.length - 1; i++) {
        if (wl >= wList[i] && wl <= wList[i + 1]) {
          idx = i;
          break;
        }
      }
      const frac = (wl - wList[idx]) / (wList[idx + 1] - wList[idx]);
      rSelected = rList[idx] + frac * (rList[idx + 1] - rList[idx]);
      tSelected = tList[idx] + frac * (tList[idx + 1] - tList[idx]);
    }
  }

  rSelected = Math.max(0, Math.min(1, rSelected));
  tSelected = Math.max(0, Math.min(1, tSelected));

  // Visual amplitude formulation: A ∝ sqrt(R), sqrt(T)
  const baseIncidentAmp = 0.25;
  const rawRAmp = baseIncidentAmp * Math.sqrt(rSelected);
  const rawTAmp = baseIncidentAmp * Math.sqrt(tSelected);

  const minAmp = 0.04;
  const maxAmp = 0.35;

  const rAmp = Math.max(minAmp, Math.min(maxAmp, rawRAmp));
  const tAmp = Math.max(minAmp, Math.min(maxAmp, rawTAmp));

  const isExaggerated = (rAmp !== rawRAmp || tAmp !== rawTAmp);

  return {
    selectedWavelengthNm: wl,
    rSelected,
    tSelected,
    rawRAmp,
    rawTAmp,
    rAmp,
    tAmp,
    isExaggerated,
    VISUAL_AMPLITUDE_EXAGGERATED: isExaggerated,
    waveAmplitudeSource: "SELECTED_WAVELENGTH_R_T_SCHEMATIC",
    animationSemantics: "TEACHING_ILLUSTRATION",
  };
}
