import { ExportPanel } from "../components/ExportPanel.js";
import { Badge } from "../components/Badge.js";

export function ExportsPage({ state }) {
  return `
    <section class="page-section">
      <div class="section-heading">
        <div>
          <h2>Exports</h2>
          <p>JSON, Markdown, Python snippet, and notebook stub samples.</p>
        </div>
        ${Badge("local files only", "green")}
      </div>
      ${ExportPanel(state.data.exports.exports || state.data.results.exports || {})}
    </section>
  `;
}
