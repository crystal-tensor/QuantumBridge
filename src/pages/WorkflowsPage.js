import { Badge, escapeHtml } from "../components/Badge.js";
import { Card } from "../components/Card.js";

export function WorkflowsPage({ state }) {
  const query = (state.workflowSearch || "").toLowerCase();
  const category = state.workflowCategory || "";
  const project = state.workflowProject || "";
  const localOnly = state.workflowLocalOnly || "";
  const executable = state.workflowExecutable || "";
  const categories = unique(state.data.workflows.workflows.map((item) => item.category));
  const projects = unique(state.data.workflows.workflows.map((item) => item.project_id));
  const workflows = state.data.workflows.workflows.filter((item) => {
    const matchesQuery = !query || `${item.workflow_id} ${item.title} ${item.project_id} ${item.category}`.toLowerCase().includes(query);
    const matchesCategory = !category || item.category === category;
    const matchesProject = !project || item.project_id === project;
    const matchesLocalOnly = !localOnly || String(item.local_only) === localOnly;
    const matchesExecutable = !executable || String(item.executable) === executable;
    return matchesQuery && matchesCategory && matchesProject && matchesLocalOnly && matchesExecutable;
  });

  return `
    <section class="page-section">
      <div class="section-heading">
        <div>
          <h2>Workflow Registry</h2>
          <p>${workflows.length} local workflow entries.</p>
        </div>
        <div class="toolbar">
          <input class="input" data-search="workflowSearch" value="${escapeHtml(state.workflowSearch || "")}" placeholder="Search workflows" />
          <select class="input" data-filter="workflowCategory">
            <option value="">All categories</option>
            ${categories.map((value) => `<option value="${escapeHtml(value)}" ${value === category ? "selected" : ""}>${escapeHtml(value)}</option>`).join("")}
          </select>
          <select class="input" data-filter="workflowProject">
            <option value="">All projects</option>
            ${projects.map((value) => `<option value="${escapeHtml(value)}" ${value === project ? "selected" : ""}>${escapeHtml(value)}</option>`).join("")}
          </select>
          <select class="input" data-filter="workflowLocalOnly">
            <option value="">Any locality</option>
            <option value="true" ${localOnly === "true" ? "selected" : ""}>local_only</option>
            <option value="false" ${localOnly === "false" ? "selected" : ""}>remote</option>
          </select>
          <select class="input" data-filter="workflowExecutable">
            <option value="">Any executable state</option>
            <option value="true" ${executable === "true" ? "selected" : ""}>executable</option>
            <option value="false" ${executable === "false" ? "selected" : ""}>advisory</option>
          </select>
        </div>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th>Workflow</th><th>Project</th><th>Category</th><th>State</th><th>Boundaries</th><th></th></tr>
          </thead>
          <tbody>
            ${workflows.map((item) => `
              <tr>
                <td><button class="link-button" data-workflow-id="${escapeHtml(item.workflow_id)}">${escapeHtml(item.workflow_id)}</button><span>${escapeHtml(item.title)}</span></td>
                <td>${escapeHtml(item.project_id)}</td>
                <td>${Badge(item.category, "gray")}</td>
                <td>${Badge(item.executable ? "executable" : "advisory", item.executable ? "green" : "amber")}${warningBadge(item)}</td>
                <td>${boundaryBadges(item)}</td>
                <td><button class="button compact" data-execute-workflow="${escapeHtml(item.workflow_id)}">Run</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function warningBadge(item) {
  return (item.warnings || []).length ? Badge(`${item.warnings.length} warnings`, "amber") : Badge("no warning", "green");
}

function boundaryBadges(item) {
  return [
    Badge(item.local_only ? "local" : "remote", item.local_only ? "green" : "amber"),
    Badge(item.cloud_access ? "cloud" : "no cloud", item.cloud_access ? "amber" : "green"),
    Badge(item.token_access ? "credential" : "no credential", item.token_access ? "amber" : "green"),
    Badge(item.hardware_access ? "hardware" : "no hardware", item.hardware_access ? "amber" : "green"),
    Badge(item.production_ready ? "production" : "prototype", item.production_ready ? "amber" : "blue"),
  ].join("");
}

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort();
}
