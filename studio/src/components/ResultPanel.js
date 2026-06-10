import { JsonViewer } from "./JsonViewer.js";
import { WarningPanel } from "./WarningPanel.js";
import { ProvenancePanel } from "./ProvenancePanel.js";

export function ResultPanel(result = {}) {
  return `
    <div class="split-grid">
      <section class="panel-block">
        <h3>Result JSON</h3>
        ${JsonViewer(result)}
      </section>
      <div>
        ${WarningPanel(result.warnings || [])}
        ${ProvenancePanel(result.provenance || {})}
      </div>
    </div>
  `;
}
