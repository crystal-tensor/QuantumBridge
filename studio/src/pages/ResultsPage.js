import { Badge, escapeHtml } from "../components/Badge.js";
import { ResultPanel } from "../components/ResultPanel.js";

export function ResultsPage({ state }) {
  const results = state.data.results.results;
  const selected = results.find((item) => item.execution_id === state.selectedResultId) || state.mockExecution || results[0];
  return `
    <section class="page-section">
      <div class="section-heading">
        <div>
          <h2>Saved Results</h2>
          <p>${results.length} sample result records.</p>
        </div>
        ${Badge("local JSON", "blue")}
      </div>
      <div class="results-strip">
        ${results.map((item) => `
          <button class="result-chip" data-route="results">
            <strong>${escapeHtml(item.workflow_id)}</strong>
            <span>${escapeHtml(item.status)}</span>
          </button>
        `).join("")}
      </div>
      ${ResultPanel(selected)}
    </section>
  `;
}
