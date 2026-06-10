import { Badge, escapeHtml } from "../components/Badge.js";
import { Card } from "../components/Card.js";
import { WarningPanel } from "../components/WarningPanel.js";

export function CatalogPage({ state, navigate }) {
  const query = (state.catalogSearch || "").toLowerCase();
  const category = state.catalogCategory || "";
  const ready = state.catalogReady || "";
  const categories = unique(state.data.catalog.projects.map((item) => item.category));
  const executableWorkflowCount = state.data.workflows.workflows.filter((item) => item.executable).length;
  const items = state.data.catalog.projects.filter((item) => {
    const matchesQuery = !query || `${item.project_id} ${item.title} ${item.category}`.toLowerCase().includes(query);
    const matchesCategory = !category || item.category === category;
    const matchesReady = !ready || item.studio_ready === ready;
    return matchesQuery && matchesCategory && matchesReady;
  });

  return `
    <section class="page-section">
      <div class="section-heading">
        <div>
          <h2>Ecosystem Catalog</h2>
          <p>${items.length} visible projects from local clean-room metadata.</p>
        </div>
        <div class="metrics-inline">
          <span><strong>${state.data.catalog.projects.length}</strong> project count</span>
          <span><strong>${executableWorkflowCount}</strong> executable workflow count</span>
        </div>
        <div class="toolbar">
          <input class="input" data-search="catalogSearch" value="${escapeHtml(state.catalogSearch || "")}" placeholder="Search projects" />
          <select class="input" data-filter="catalogCategory">
            <option value="">All categories</option>
            ${categories.map((value) => `<option value="${escapeHtml(value)}" ${value === category ? "selected" : ""}>${escapeHtml(value)}</option>`).join("")}
          </select>
          <select class="input" data-filter="catalogReady">
            <option value="">All statuses</option>
            ${unique(state.data.catalog.projects.map((item) => item.studio_ready)).map((value) => `<option value="${escapeHtml(value)}" ${value === ready ? "selected" : ""}>${escapeHtml(value)}</option>`).join("")}
          </select>
        </div>
      </div>
      <div class="notice-line">Clean-room notice: ${escapeHtml(state.data.catalog.clean_room_notice || "local metadata only; no official endorsement.")}</div>
      <div class="catalog-grid">
        ${items.map((item) => Card(`
          <div class="card-header">
            <div>
              <h3>${escapeHtml(item.title)}</h3>
              <p>${escapeHtml(item.project_id)}</p>
            </div>
            ${Badge(`L${item.capability_level}`, "blue")}
          </div>
          <div class="meta-row">
            ${Badge(item.category, "gray")}
            ${Badge(item.studio_ready, item.studio_ready === "true" ? "green" : "amber")}
            ${Badge(`${item.executable_workflows.length} workflows`, "purple")}
          </div>
          ${WarningPanel((item.warnings || []).slice(0, 3))}
          <button class="button" data-route="workflows">View workflows</button>
        `)).join("")}
      </div>
    </section>
  `;
}

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort();
}
