import { Badge, escapeHtml } from "../components/Badge.js";
import { progressSnapshot } from "../data/progressData.js";
import { localize, t } from "../i18n.js";

const STATUS = {
  partial: { label: "Partial native", tone: "blue" },
  early: { label: "Early native", tone: "amber" },
  complete: { label: "Complete", tone: "green" },
};

export function ProgressPage({ state }) {
  const locale = state.locale || "zh-CN";
  const selectedTrack = state.progressTrack || "all";
  const tracks = progressSnapshot.tracks.filter((track) => selectedTrack === "all" || track.id === selectedTrack);
  const moduleCount = progressSnapshot.tracks.reduce((sum, track) => sum + track.modules.length, 0);
  const partialCount = progressSnapshot.tracks.reduce(
    (sum, track) => sum + track.modules.filter((module) => module.status === "partial").length,
    0,
  );

  return `
    <section class="page-section progress-page">
      <div class="progress-intro">
        <div>
          <span class="section-kicker">${t("progress.kicker", locale)}</span>
          <h2>${t("progress.title", locale)}</h2>
          <p>${t("progress.subtitle", locale)}</p>
        </div>
        <div class="snapshot-meta">
          <span>${t("progress.branch", locale)} <strong>${escapeHtml(progressSnapshot.branch)}</strong></span>
          <span>HEAD <strong>${escapeHtml(progressSnapshot.head)}</strong></span>
          <span>${t("progress.snapshot", locale)} <strong>${escapeHtml(progressSnapshot.generatedAt)}</strong></span>
        </div>
      </div>

      <div class="validation-strip">
        ${progressSnapshot.validation.map((item) => `
          <article class="validation-item validation-${item.tone}">
            <span>${escapeHtml(localize(item.label, locale))}</span>
            <strong>${escapeHtml(localize(item.value, locale))}</strong>
            <small>${escapeHtml(localize(item.note, locale))}</small>
          </article>
        `).join("")}
      </div>

      <div class="progress-toolbar">
        <div>
          <h3>${t("progress.matrix", locale)}</h3>
          <p>${moduleCount} ${t("progress.matrixSummary", locale)} ${partialCount} ${t("progress.matrixSummaryTail", locale)}</p>
        </div>
        <div class="segmented-control" role="group" aria-label="Filter capability matrix">
          ${trackButton("all", t("progress.all", locale), selectedTrack)}
          ${trackButton("qiskit", "Qiskit", selectedTrack)}
          ${trackButton("pennylane", "PennyLane", selectedTrack)}
        </div>
      </div>

      <div class="track-stack">
        ${tracks.map((track) => renderTrack(track, locale)).join("")}
      </div>

      <section class="delivery-band">
        <div class="section-heading compact-heading">
          <div>
            <h3>${t("progress.recent", locale)}</h3>
            <p>${t("progress.recentBody", locale)}</p>
          </div>
          ${Badge(t("progress.noParity", locale), "amber")}
        </div>
        <div class="delivery-list">
          ${progressSnapshot.recentWork.map((item) => `
            <article class="delivery-row">
              <div class="commit-token">${escapeHtml(item.date === "Working tree" ? t("progress.workingTree", locale) : item.date)}</div>
              <div class="delivery-copy">
                <strong>${escapeHtml(localize(item.title, locale))}</strong>
                <span>${escapeHtml(localize(item.detail, locale))}</span>
              </div>
              ${Badge(item.status === "Committed" ? t("progress.committed", locale) : t("progress.validated", locale), item.tone)}
            </article>
          `).join("")}
        </div>
      </section>
    </section>
  `;
}

function trackButton(id, label, selected) {
  return `<button class="segment ${selected === id ? "active" : ""}" data-progress-track="${id}">${label}</button>`;
}

function renderTrack(track, locale) {
  return `
    <section class="capability-track track-${track.accent}">
      <header class="track-header">
        <div>
          <span class="track-label">${escapeHtml(localize(track.name, locale))}</span>
          <p>${escapeHtml(localize(track.summary, locale))}</p>
        </div>
        <strong>${track.modules.length} ${t("progress.areas", locale)}</strong>
      </header>
      <div class="capability-table-wrap">
        <table class="capability-table">
          <thead>
            <tr>
              <th>${t("progress.capability", locale)}</th>
              <th>${t("progress.status", locale)}</th>
              <th>${t("progress.works", locale)}</th>
              <th>${t("progress.missing", locale)}</th>
            </tr>
          </thead>
          <tbody>
            ${track.modules.map((module) => {
              const status = STATUS[module.status];
              return `
                <tr>
                  <td><strong>${escapeHtml(localize(module.name, locale))}</strong></td>
                  <td>${Badge(t(`progress.${module.status}`, locale), status.tone)}</td>
                  <td>${escapeHtml(localize(module.delivered, locale))}</td>
                  <td>${escapeHtml(localize(module.missing, locale))}</td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}
