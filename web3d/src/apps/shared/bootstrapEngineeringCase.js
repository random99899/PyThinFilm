import { EngineeringCaseApp } from "./EngineeringCaseApp.js";
import { getEngineeringCaseConfig } from "./engineeringCaseConfigs.js";
import "./engineeringApp.css";

export function bootstrapEngineeringCase(caseId) {
  const root = document.querySelector("#engineering-app");
  const app = new EngineeringCaseApp(root, getEngineeringCaseConfig(caseId));
  app.init();
  return app;
}
