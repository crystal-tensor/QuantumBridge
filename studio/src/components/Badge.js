export function Badge(label, tone = "gray") {
  return `<span class="badge badge-${tone}">${escapeHtml(label)}</span>`;
}

export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
