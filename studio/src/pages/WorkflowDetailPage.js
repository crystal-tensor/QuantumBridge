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
          <h3>Default Inputs</h3>
          ${JsonViewer(detail.default_inputs || detail.input_schema?.defaults || {})}
          <h3>Output Schema</h3>
          ${JsonViewer(detail.output_schema || {})}
          <h3>Result Schema</h3>
          <p><code>${escapeHtml(detail.result_schema || "QuantumBridgeResult")}</code></p>
          <h3>Unsupported Limitations</h3>
          <ul class="compact-list">
            ${(detail.unsupported_limitations || [detail.unsupported_reason || "local prototype only"]).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
          </ul>
        </section>
        <div>
          <section class="panel-block">
            <h3>Clean-room notice</h3>
            <p>${escapeHtml(detail.clean_room_notice || state.data.workflowDetails.clean_room_notice || "Generated from QuantumBridge-owned local backend services.")}</p>
          </section>
          ${WarningPanel(detail.warnings || [])}
          ${ProvenancePanel(detail.provenance || {})}
        </div>
      </div>
      <button class="button" data-execute-workflow="${escapeHtml(detail.workflow_id)}">Run Local</button>
    </section>
  `;
}
