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
        <div class="metric"><span>Skipped</span><strong>${escapeHtml(result.skipped ?? 0)}</strong></div>
        <div class="metric"><span>Unsupported</span><strong>${escapeHtml(result.unsupported ?? 0)}</strong></div>
        <div class="metric"><span>Elapsed</span><strong>${escapeHtml(result.elapsed_seconds ?? "n/a")}</strong></div>
        <div class="metric"><span>Capability</span><strong>${escapeHtml(result.capability_level ?? "n/a")}</strong></div>
      </div>
      ${WarningPanel(benchmark.warnings || [])}
      <div class="split-grid">
        <section class="panel-block">
          <h3>Markdown Export Preview</h3>
          <pre>${escapeHtml((benchmark.report_markdown || "").slice(0, 1200))}</pre>
        </section>
        <section class="panel-block">
          <h3>JSON Export Preview</h3>
          <pre>${escapeHtml((benchmark.report_json || "").slice(0, 1200))}</pre>
        </section>
      </div>
      ${JsonViewer(benchmark)}
    </section>
  `;
}
