import { escapeHtml } from "./Badge.js";

export function ExportPanel(exports = {}) {
  const entries = Object.entries(exports);
  return `
    <section class="panel-block">
      <h3>Exports</h3>
      <div class="export-grid">
        ${entries.map(([name, payload]) => `
          <div class="export-item">
            <div class="export-title">${escapeHtml(name)}</div>
            <pre>${escapeHtml(String(payload.content || "").slice(0, 900))}</pre>
          </div>
        `).join("")}
      </div>
    </section>
  `;
}
