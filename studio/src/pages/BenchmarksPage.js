import { Badge, escapeHtml } from "../components/Badge.js";
import { JsonViewer } from "../components/JsonViewer.js";
import { WarningPanel } from "../components/WarningPanel.js";

export function BenchmarksPage({ state }) {
  const benchmark = state.data.benchmark.benchmark;
  const result = benchmark.result || {};
  return `
    <section class="page-section">
      <div class="section-heading">
        <div>
          <h2>Benchmark Report</h2>
          <p>${escapeHtml(benchmark.suite_id || "circuit_basic")}</p>
        </div>
        <div class="topbar-badges">
          ${Badge(result.status || "completed", result.passed ? "green" : "amber")}
          ${Badge("not official benchmark", "amber")}
        </div>
      </div>
      <div class="metrics-grid">
        <div class="metric"><span>Passed</span><strong>${escapeHtml(result.passed ?? "n/a")}</strong></div>
        <div class="metric"><span>Elapsed</span><strong>${escapeHtml(result.elapsed_seconds ?? "n/a")}</strong></div>
        <div class="metric"><span>Capability</span><strong>${escapeHtml(result.capability_level ?? "n/a")}</strong></div>
      </div>
      ${WarningPanel(benchmark.warnings || [])}
      ${JsonViewer(benchmark)}
    </section>
  `;
}
