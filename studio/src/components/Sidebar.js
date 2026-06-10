const ITEMS = [
  ["catalog", "Catalog"],
  ["workflows", "Workflows"],
  ["execute", "Execute"],
  ["benchmarks", "Benchmarks"],
  ["results", "Results"],
  ["exports", "Exports"],
];

export function Sidebar({ route }) {
  return `
    <aside class="sidebar">
      <div class="brand-block">
        <div class="brand-mark">QB</div>
        <div>
          <div class="brand-title">QuantumBridge Studio</div>
          <div class="brand-subtitle">Local Prototype</div>
        </div>
      </div>
      <nav class="nav-list">
        ${ITEMS.map(([id, label]) => `<button class="nav-item ${route === id ? "active" : ""}" data-route="${id}">${label}</button>`).join("")}
      </nav>
      <div class="sidebar-note">
        <span class="status-dot"></span>
        Local-only execution view
      </div>
    </aside>
  `;
}
