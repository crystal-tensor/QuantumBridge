import { Badge, escapeHtml } from "../components/Badge.js";
import { ResultPanel } from "../components/ResultPanel.js";

export function ResultsPage({ state }) {
  const results = state.data.results.results;
  const query = (state.resultWorkflowSearch || "").toLowerCase();
  const visible = results.filter((item) => !query || String(item.workflow_id || "").toLowerCase().includes(query));
  const selected = results.find((item) => item.execution_id === state.selectedResultId) || state.mockExecution || visible[0] || results[0];
  return `
    <section class="page-section">
      <div class="section-heading">
        <div>
          <h2>Saved Results</h2>
          <p>${visible.length} visible sample result records.</p>
        </div>
        <div class="toolbar">
          <input class="input" data-search="resultWorkflowSearch" value="${escapeHtml(state.resultWorkflowSearch || "")}" placeholder="Find by workflow_id" />
          ${Badge("local JSON", "blue")}
        </div>
      </div>
      <div class="results-strip">
        ${visible.map((item) => `
          <button class="result-chip" data-result-id="${escapeHtml(item.execution_id)}">
            <strong>${escapeHtml(item.workflow_id)}</strong>
            <span>${escapeHtml(item.status)}</span>
          </button>
        `).join("")}
      </div>
      <div class="button-row">
        <button class="button compact" data-route="exports">JSON export</button>
        <button class="button compact" data-route="exports">Markdown export</button>
        <button class="button compact" data-route="exports">Python snippet export</button>
        <button class="button compact" data-route="exports">Notebook stub export</button>
      </div>
      ${ResultPanel(selected)}
    </section>
  `;
}
