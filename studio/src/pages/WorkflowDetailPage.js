import { Badge, escapeHtml } from "../components/Badge.js";
import { JsonViewer } from "../components/JsonViewer.js";
import { WarningPanel } from "../components/WarningPanel.js";
import { ProvenancePanel } from "../components/ProvenancePanel.js";

export function WorkflowDetailPage({ state }) {
  const detail = state.data.workflows.details.find((item) => item.workflow_id === state.selectedWorkflowId) || state.data.workflows.details[0];
  const fields = detail.input_schema?.fields || [];
  return `
    <section class="page-section">
      <div class="section-heading">
        <div>
          <h2>${escapeHtml(detail.title)}</h2>
          <p>${escapeHtml(detail.workflow_id)}</p>
        </div>
        <div class="topbar-badges">
          ${Badge(detail.project_id, "blue")}
          ${Badge(detail.category, "gray")}
          ${Badge(detail.result_schema || "result", "purple")}
        </div>
      </div>
      <div class="split-grid">
        <section class="panel-block">
          <h3>Input Schema</h3>
          <div class="field-list">
            ${fields.length ? fields.map((field) => `
              <div class="field-row">
                <strong>${escapeHtml(field.name)}</strong>
                <span>${escapeHtml(field.field_type)}</span>
                <code>${escapeHtml(JSON.stringify(field.default))}</code>
              </div>
            `).join("") : "<p>No required inputs.</p>"}
          </div>
          <h3>Output Schema</h3>
          ${JsonViewer(detail.output_schema || {})}
        </section>
        <div>
          ${WarningPanel(detail.warnings || [])}
          ${ProvenancePanel(detail.provenance || {})}
        </div>
      </div>
      <button class="button" data-execute-workflow="${escapeHtml(detail.workflow_id)}">Run Local</button>
    </section>
  `;
}
