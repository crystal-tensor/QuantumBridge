// Copyright 2026 QuantumBridge Contributors. Apache-2.0.
import path from "node:path";
import { readFile, realpath } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { domains, directions } from "../src/framework/data.js";
import { resources, resourceHref } from "../src/framework/resources.js";

const output = fileURLToPath(new URL("../../output/jupyter-notebook/", import.meta.url));
const escape = value => String(value).replace(/[&<>"']/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[character]));

export async function readArtifact(pathname) {
  const resource = resources.find(item => resourceHref(item) === pathname || (item.kind !== "index" && resourceHref(item, true) === pathname));
  if (!resource) return null;
  const directory = await realpath(path.join(output, resource.domain));
  const filename = await realpath(path.join(directory, path.basename(pathname)));
  if (!filename.startsWith(directory + path.sep)) return null;
  return { resource, filename, body: await readFile(filename) };
}

export function artifactPage(html, resource, locale = "zh-CN", basePath = "/") {
  const en = locale === "en";
  const label = (zh, english) => en ? english : zh;
  const domain = domains.find(item => item.id === resource.domain);
  const category = directions.find(item => item.id === resource.direction);
  const href = (item, notebook = false) => basePath + resourceHref(item, notebook).replace(/^\//, "");
  const home = `${basePath}framework.html?category=${resource.domain}&lang=${en ? "en" : "zh"}`;
  const index = resources.find(item => item.domain === resource.domain && item.kind === "index");
  const diagnostics = resources.filter(item => item.domain === resource.domain && item.kind === "diagnostic");
  const table = resource.kind === "index" && diagnostics.length ? `<section id="qb-report-directory"><h2>${label("真机诊断与审计报告", "Hardware diagnostics & audit reports")}</h2><ul>${diagnostics.map(item => `<li><a href="${href(item)}">${escape(item.title[locale])}</a> · <a href="${href(item, true)}" download>Notebook</a></li>`).join("")}</ul></section>` : "";
  const navigation = `<style>
    #qb-artifact-nav{box-sizing:border-box;display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center;padding:16px 24px;border-bottom:1px solid #cdd8d4;background:#eff5f2;color:#244336;font:14px/1.7 system-ui,sans-serif;letter-spacing:0}
    #qb-artifact-nav a,#qb-report-directory a{color:#186353;text-decoration:underline;text-underline-offset:3px;overflow-wrap:anywhere}
    #qb-artifact-nav a:focus-visible,#qb-report-directory a:focus-visible{outline:3px solid #408a70;outline-offset:4px}
    #qb-artifact-nav strong{flex:1 1 220px;font-size:14px;font-weight:600;overflow-wrap:anywhere}
    #qb-report-directory{margin:28px 0;padding:20px 0;border-top:1px solid #cdd8d4;font:16px/1.8 system-ui,sans-serif;letter-spacing:0}#qb-report-directory h2{font-size:21px}#qb-report-directory li{margin:10px 0}
    @media(max-width:550px){#qb-artifact-nav{padding:14px 16px;gap:8px 18px;font-size:13px}#qb-artifact-nav strong{flex-basis:100%}}
    </style><nav id="qb-artifact-nav" aria-label="${label("项目导航", "Project navigation")}"><a href="${home}">${label("返回首页", "Back to home")}</a>${resource.kind !== "index" ? `<a href="${resourceHref(index)}${en ? "?lang=en" : ""}">${escape(index.title[locale])}</a>` : ""}${category ? `<a href="${home}#${category.id}">${escape(category.name[locale])}</a>` : ""}<strong>${escape(domain.name[locale])} / ${escape(resource.title[locale])}</strong>${resource.kind !== "index" ? `<a href="${resourceHref(resource, true)}" download>${label("下载 Notebook", "Download notebook")}</a>` : ""}</nav>`;
  // Prefix only injected navigation; scientific notebook output is not rewritten.
  const publishedNavigation = navigation.replaceAll('href="/examples/', `href="${basePath}examples/`);
  // nbconvert emits an explicit body; the original compact index uses implicit HTML body tags.
  const decorated = /<body(?:\s[^>]*)?>/i.test(html) ? html.replace(/<body(?:\s[^>]*)?>/i, opening => opening + publishedNavigation) : html.replace(/<header\b/i, publishedNavigation + "<header");
  return table ? decorated.replace("</main>", table + "</main>") : decorated;
}
