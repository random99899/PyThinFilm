import { EngineeringCaseApp } from "./EngineeringCaseApp.js";
import { getEngineeringCaseConfig } from "./engineeringCaseConfigs.js";
import { renderEngineeringShell } from "./engineeringShell.js";
import "./engineeringApp.css";

export function bootstrapEngineeringCase(caseId) {
  const root = document.querySelector("#engineering-app");
  if (!root.querySelector("#engineering-canvas")) renderEngineeringShell(root);
  const app = new EngineeringCaseApp(root, getEngineeringCaseConfig(caseId));
  app.init();
  return app;
}
