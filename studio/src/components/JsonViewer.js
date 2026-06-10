import { escapeHtml } from "./Badge.js";

export function JsonViewer(value) {
  return `<pre class="json-viewer">${escapeHtml(JSON.stringify(value, null, 2))}</pre>`;
}
