import { Badge } from "./Badge.js";

export function Header({ data }) {
  const projectCount = data.catalog.projects.length;
  const workflowCount = data.workflows.workflows.length;
  return `
    <header class="topbar">
      <div>
        <h1>QuantumBridge Studio</h1>
        <p>Catalog, workflows, local execution results, provenance, and exports.</p>
      </div>
      <div class="topbar-badges">
        ${Badge("Local only", "green")}
        ${Badge(`${projectCount} projects`, "blue")}
        ${Badge(`${workflowCount} workflows`, "purple")}
        ${Badge("No official endorsement", "amber")}
      </div>
    </header>
    <section class="notice-band">
      <strong>Independent prototype.</strong>
      No cloud execution, no credential reading, no hardware access, and no production UI claim.
    </section>
  `;
}
