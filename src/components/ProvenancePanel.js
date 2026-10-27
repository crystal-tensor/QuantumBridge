import { JsonViewer } from "./JsonViewer.js";

export function ProvenancePanel(provenance = {}) {
  return `
    <section class="panel-block">
      <h3>Provenance</h3>
      ${JsonViewer(provenance)}
    </section>
  `;
}
