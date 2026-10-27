import { t } from "../i18n.js";

const ITEMS = [
  ["progress", "nav.progress"],
  ["catalog", "nav.catalog"],
  ["workflows", "nav.workflows"],
  ["execute", "nav.execute"],
  ["benchmarks", "nav.benchmarks"],
  ["results", "nav.results"],
  ["exports", "nav.exports"],
];

export function Sidebar({ route, locale }) {
  return `
    <aside class="sidebar">
      <div class="brand-block">
        <div class="brand-mark">QB</div>
        <div>
          <div class="brand-title">QuantumBridge Studio</div>
          <div class="brand-subtitle">${t("brand.subtitle", locale)}</div>
        </div>
      </div>
      <nav class="nav-list">
        <a class="nav-item" style="text-decoration:none" href="./framework.html">${locale === "zh-CN" ? "应用框架 · 4 大类 / 19 方向" : "Application framework · 4 domains / 19 directions"}</a>
        <a class="nav-item" style="text-decoration:none" href="./ecosystem.html">${locale === "zh-CN" ? "生态学习中心" : "Ecosystem guide"}</a>
        ${ITEMS.map(([id, label]) => `<button class="nav-item ${route === id ? "active" : ""}" data-route="${id}">${t(label, locale)}</button>`).join("")}
      </nav>
      <div class="sidebar-note">
        <span class="status-dot"></span>
        ${t("sidebar.status", locale)}
      </div>
    </aside>
  `;
}
