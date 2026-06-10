import { Badge, escapeHtml } from "../components/Badge.js";
import { ResultPanel } from "../components/ResultPanel.js";

export function ExecutePage({ state }) {
  const workflows = state.data.workflows.details;
  const detail = workflows.find((item) => item.workflow_id === state.selectedWorkflowId) || workflows[0];
  const fields = detail.input_schema?.fields || [];
  const result = state.mockExecution || state.data.results.results[0];
  return `
    <section class="page-section">
      <div class="section-heading">
        <div>
          <h2>Local Execution</h2>
          <p>${escapeHtml(detail.workflow_id)}</p>
        </div>
        <div class="topbar-badges">
          ${Badge("mock local JSON client", "blue")}
          ${Badge("Stage 10C backend source", "green")}
        </div>
      </div>
      <section class="execute-panel">
        <label>
          <span>Workflow</span>
          <select class="input wide" data-workflow-select>
            ${workflows.map((item) => `<option value="${escapeHtml(item.workflow_id)}" ${item.workflow_id === detail.workflow_id ? "selected" : ""}>${escapeHtml(item.workflow_id)}</option>`).join("")}
          </select>
        </label>
        <div class="form-grid">
          ${fields.length ? fields.map((field) => inputField(field)).join("") : "<p>No input form fields for this workflow.</p>"}
        </div>
        <button class="button primary" data-run-local>Run Local</button>
      </section>
      ${ResultPanel(result)}
    </section>
  `;
}

function inputField(field) {
  const type = field.field_type === "integer" || field.field_type === "float" ? "number" : "text";
  return `
    <label class="input-field">
      <span>${escapeHtml(field.name)}</span>
      <input class="input" data-input-name="${escapeHtml(field.name)}" type="${type}" value="${escapeHtml(field.default ?? "")}" />
    </label>
  `;
}
