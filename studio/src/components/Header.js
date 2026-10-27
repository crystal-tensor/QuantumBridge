import { Badge } from "./Badge.js";
import { t } from "../i18n.js";

export function Header({ data, route, locale }) {
  const projectCount = data.catalog.projects.length;
  const workflowCount = data.workflows.workflows.length;
  const progressView = route === "progress";
  return `
    <header class="topbar">
      <div>
        <h1>${progressView ? t("header.progressTitle", locale) : t("header.studioTitle", locale)}</h1>
        <p>${progressView ? t("header.progressSubtitle", locale) : t("header.studioSubtitle", locale)}</p>
      </div>
      <div class="topbar-actions">
        <div class="language-switch" role="group" aria-label="Language">
          <button class="language-option ${locale === "zh-CN" ? "active" : ""}" data-locale="zh-CN">中文</button>
          <button class="language-option ${locale === "en" ? "active" : ""}" data-locale="en">EN</button>
        </div>
        <div class="topbar-badges">
          ${Badge(t("header.local", locale), "green")}
          ${Badge(`${projectCount} ${t("header.projects", locale)}`, "blue")}
          ${Badge(`${workflowCount} ${t("header.workflows", locale)}`, "purple")}
          ${Badge(t("header.endorsement", locale), "amber")}
        </div>
      </div>
    </header>
    <section class="notice-band ${progressView ? "progress-notice" : ""}">
      <strong>${progressView ? t("notice.honest", locale) : t("notice.prototype", locale)}</strong>
      ${progressView ? t("notice.honestBody", locale) : t("notice.prototypeBody", locale)}
    </section>
  `;
}
