import { EvidenceCaseApp } from "./EvidenceCaseApp.js";
import "./evidenceApp.css";

const root = document.querySelector("#evidence-app");
const app = new EvidenceCaseApp(root, root?.dataset.caseId);
app.init();
