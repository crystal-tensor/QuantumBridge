import { escapeHtml } from "./Badge.js";

export function WarningPanel(warnings = []) {
  const rows = warnings.slice(0, 8).map((warning) => `<li>${escapeHtml(typeof warning === "string" ? warning : warning.message || JSON.stringify(warning))}</li>`).join("");
  return `
    <section class="panel-block">
      <h3>Warnings</h3>
      <ul class="compact-list">${rows || "<li>No warnings in sample payload.</li>"}</ul>
    </section>
  `;
}
