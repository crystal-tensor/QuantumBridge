import { bi, categories, modules, layers, scenarios, extensions, tracks, glossary, roadmap } from "./content.js";

const root = document.getElementById("ecosystem-app");
const savedLocale = (() => { try { return localStorage.getItem("quantumbridge.locale"); } catch { return null; } })();
const requestedLocale = new URLSearchParams(location.search).get("lang");
const state = { locale: requestedLocale === "en" || (!requestedLocale && savedLocale === "en") ? "en" : "zh-CN", layer: "hardware", scenario: "science", track: "start", module: null };
const tr = value => typeof value === "string" ? value : value[state.locale];
const text = (zh, en) => tr(bi(zh, en));
const arrow = '<span aria-hidden="true">↗</span>';
const packageName = id => `quantum_bridge_${id}`;
let moduleOpener = null;
let navigationFrame;
function updateNavigation() {
  const ids = ["architecture", "modules", "workflow", "learn", "roadmap"];
  const line = window.innerHeight * .33;
  let active = ids[0];
  for (const id of ids) { if (document.getElementById(id)?.getBoundingClientRect().top <= line) active = id; }
  root.querySelectorAll("#site-nav a").forEach(link => { if (link.hash === `#${active}`) link.setAttribute("aria-current", "location"); else link.removeAttribute("aria-current"); });
}
function scheduleNavigationUpdate() {
  cancelAnimationFrame(navigationFrame);
  navigationFrame = requestAnimationFrame(updateNavigation);
}
window.addEventListener("scroll", scheduleNavigationUpdate, {passive:true});
window.addEventListener("resize", scheduleNavigationUpdate);

function heading(number, title, desc = "") {
  return `<div class="section-heading"><div><span class="section-index">${number}</span><h2>${title}</h2></div>${desc ? `<p>${desc}</p>` : ""}</div>`;
}
function moduleLink(id) {
  const module = modules.find(item => item.id === id);
  return `<button class="text-link" data-module="${id}">${module.name} ${arrow}</button>`;
}
function architectureDetail() {
  const layer = layers.find(item => item.id === state.layer);
  return `<div class="detail-eyebrow">${text("正在探索", "EXPLORING")} <span>${layer.number} / 05</span></div>
    <h3>${tr(layer.title)}</h3><p class="detail-description">${tr(layer.desc)}</p>
    <ul class="detail-points">${tr(layer.points).map(point => `<li>${point}</li>`).join("")}</ul>
    <div class="interface-note"><span>${text("接口关系", "INTERFACE")}</span><p>${tr(layer.interface)}</p></div>
    <div class="detail-modules"><span>${text("关联模块", "RELATED MODULES")}</span><div>${layer.modules.map(moduleLink).join("")}</div></div>`;
}
function architecture() {
  return `<section id="architecture" class="section container" aria-labelledby="architecture-title">
    ${heading("01", `<span id="architecture-title">${text("从基座，读懂整个生态", "Read the ecosystem from the ground up")}</span>`, text("点击任意一层，了解它的职责和接口。", "Select a layer to explore its role and interfaces."))}
    <div class="architecture-layout">
      <div class="stack-panel">
        <div class="stack-caption"><span>${text("完整计算栈", "THE COMPUTE STACK")}</span><span>${text("能力自下而上支撑 ↑", "Capabilities build upward ↑")}</span></div>
        <div class="layer-stack" role="group" aria-label="${text("生态架构层", "Ecosystem architecture layers")}">${layers.map((layer, index) => `
          <button class="layer ${state.layer === layer.id ? "selected" : ""}" data-layer="${layer.id}" aria-pressed="${state.layer === layer.id}" aria-controls="layer-detail">
            <span class="layer-number">${layer.number}</span><span class="layer-copy"><strong>${tr(layer.name)}</strong><span>${tr(layer.short)}</span></span><span class="layer-arrow" aria-hidden="true">↗</span>
          </button>${index < 4 ? `<div class="layer-connector" aria-hidden="true"><span>↑</span>${["", "QIR / OpenQASM", "QOS-DP", text("控制器 / 设备 API", "Controller / device API")][index]}</div>` : ""}`).join("")}</div>
      </div>
      <aside id="layer-detail" class="layer-detail" aria-live="polite" aria-atomic="true">${architectureDetail()}</aside>
    </div>
    <div class="cross-layer"><span>${text("跨层支撑", "ACROSS THE STACK")}</span><div>${moduleLink("visual")}${moduleLink("benchmark")}<a href="#extensions">Studio / Plugins / Tooling ${arrow}</a><a href="#qos-design">${text("校准与 QEC", "Calibration & QEC")} ${arrow}</a></div></div>
    <p class="architecture-note">${text("这是生态目标架构，基于 QuantumOS 的微内核与 HAL 设计。Core 提供前端与目标编译，OS 分包连接独立运行服务；硬件能力按插件逐项验证。", "This target architecture extends the QuantumOS microkernel and HAL design. Core supplies frontend and target compilation; the OS package connects to a separate runtime. Device support is validated per plugin.")}</p>
  </section>`;
}
function moduleCards() {
  return `<section id="modules" class="section section-tint"><div class="container">
    ${heading("02", text("十个分包，一个计算生态", "Ten packages. One computing ecosystem."), text("按职责分包，按需组合。打开模块查看完整功能。", "Organized by responsibility, composed as needed. Open a module to see its scope."))}
    ${Object.entries(categories).map(([category, title]) => `<div class="module-group"><h3 class="group-label">${tr(title)}<span>${modules.filter(m => m.category === category).length.toString().padStart(2, "0")}</span></h3>
    <div class="module-grid ${category === "tools" ? "two-column" : ""}">${modules.filter(m => m.category === category).map(module => `
      <button class="module-card" data-module="${module.id}" aria-haspopup="dialog" aria-label="${text("了解", "Explore")} ${module.name}">
        <span class="module-top"><span class="module-name">${module.name}</span><span class="card-arrow" aria-hidden="true">↗</span></span>
        <span class="module-title">${tr(module.title)}</span><span class="module-summary">${tr(module.summary)}</span>
        <code>${packageName(module.id)}</code>
      </button>`).join("")}</div></div>`).join("")}
  </div></section>`;
}
function scenarioContent() {
  const scenario = scenarios.find(item => item.id === state.scenario);
  const steps = [
    ["05", text("行业应用", "Application"), tr(scenario.inputs), scenario.module],
    ["04", "QB SDK", tr(scenario.model), "core"],
    ["03", "Quantum OS", text("后端选择、预算、批次和校准快照", "Backend selection, budget, batches and calibration snapshot"), "os"],
    ["02", "Compiler / HAL", text("目标转译、布局路由和执行计划", "Target compilation, layout, routing and execution plan"), "core"],
    ["01", text("硬件 / Simulator", "Hardware / Simulator"), text("执行、采样、测量和结果归一化", "Execution, sampling, measurement and normalized results"), "simulator"],
  ];
  return `<div class="workflow-chain">${steps.map((step, i) => `<div class="workflow-step"><span class="step-index">${i + 1}</span><div><h3>${step[1]}</h3><p>${step[2]}</p></div><button class="step-module" data-module="${step[3]}" aria-label="${text("了解模块", "Explore module")} ${step[3]}">↗</button></div>`).join("")}</div>
    <aside class="workflow-result"><span class="eyebrow">${text("返回领域结果", "RETURN A DOMAIN RESULT")}</span><h3>${tr(scenario.name)}</h3><p>${tr(scenario.output)}</p><div class="iteration"><span aria-hidden="true">↻</span><p>${tr(scenario.loop)}</p></div><div class="manifest-line"><code>Result + Manifest</code><span>${text("原始结果、参数、误差、成本与版本", "Raw results, parameters, error, cost and versions")}</span></div><span class="educational-label">${text("流程示意 · 不执行实际计算", "Workflow illustration · no computation is run")}</span></aside>`;
}
function workflow() {
  return `<section id="workflow" class="section container">
    ${heading("03", text("一项任务，如何经过五层", "Follow a job through all five layers"), text("选择一个例子，看同一套基础能力如何服务不同领域。", "Choose an example to see how shared capabilities serve different domains."))}
    <div class="scenario-tabs" role="tablist" aria-label="${text("工作流示例", "Workflow examples")}">${scenarios.map(item => `<button role="tab" id="scenario-${item.id}" aria-selected="${item.id === state.scenario}" aria-controls="scenario-content" tabindex="${item.id === state.scenario ? 0 : -1}" data-scenario="${item.id}">${tr(item.name)}</button>`).join("")}</div>
    <div id="scenario-content" class="workflow-layout" role="tabpanel" aria-labelledby="scenario-${state.scenario}">${scenarioContent()}</div>
    <div id="qos-design" class="qos-design"><div class="qos-heading"><span class="eyebrow">QUANTUM OS</span><h3>${text("运行基座里的三个关键机制", "Three key runtime mechanisms")}</h3><p>${text("继承 QuantumOS 框架图的模块关系，按生态目标继续扩展。", "Extend the relationships in the QuantumOS architecture diagrams.")}</p></div>
      <div class="qos-accordions">
        <details id="qos-mlfq"><summary><span>01</span>${text("MLFQ：任务如何排队与让出", "MLFQ: queueing and yielding jobs")}<span class="plus" aria-hidden="true">+</span></summary><div class="accordion-content"><p>${text("任务经准入进入多级优先队列，由调度器分配资源。预算耗尽可降级，等待老化可提升，经典计算或 I/O 就绪后重新准入。", "Jobs enter priority queues through admission and receive resources from the scheduler. Budget exhaustion can demote jobs, aging can promote them, and completed classical or I/O work can trigger readmission.")}</p><div class="mini-flow"><span>Q1</span><i>→</i><span>Q2</span><i>→</i><span>Q3</span><i>→</i><span>Runtime</span></div><p class="small-note">${text("目标策略在批次、测量或会话边界安全让出，不中断任意未知量子态。", "The target policy yields at safe batch, measurement or session boundaries, not by interrupting arbitrary unknown quantum states.")}</p></div></details>
        <details id="qos-dp"><summary><span>02</span>${text("QOS-DP：内核如何连接设备", "QOS-DP: connecting the kernel to devices")}<span class="plus" aria-hidden="true">+</span></summary><div class="accordion-content"><p>${text("SDK 与编译器提交 QIR/JobSpec，内核调度并预约资源，HAL 加载驱动、下发设备指令，再将测量与事件返回统一结果。", "The SDK and compiler submit QIR/JobSpec. The kernel schedules and reserves resources; HAL loads drivers, dispatches device instructions and returns normalized measurements and events.")}</p><div class="mini-flow"><span>QB</span><i>→</i><span>QOS</span><i>→</i><span>HAL</span><i>→</i><span>QPU</span></div></div></details>
        <details id="qos-qec"><summary><span>03</span>${text("QEC：测量与纠错如何反馈", "QEC: measurement and correction feedback")}<span class="plus" aria-hidden="true">+</span></summary><div class="accordion-content"><p>${text("QPU 输出错误综合征，解码器计算纠错动作，控制器将反馈送回设备。该通路独立于常规结果展示，需要按硬件能力验证时延。", "The QPU supplies error syndromes, a decoder computes correction actions, and a controller feeds them back to the device. This path is separate from ordinary result visualization and requires device-specific latency validation.")}</p><div class="mini-flow"><span>${text("综合征", "Syndrome")}</span><i>→</i><span>${text("解码", "Decode")}</span><i>→</i><span>${text("反馈", "Feedback")}</span></div></div></details>
      </div>
    </div>
  </section>`;
}
function extensionSection() {
  const names = [bi("智能路由", "Intelligent routing"), bi("Studio 工作台", "Studio workspace"), bi("框架与设备插件", "Framework & device plugins"), bi("实验、校准与误差缓解", "Experiments & mitigation"), bi("统一契约与溯源", "Contracts & provenance"), bi("开发工具", "Developer tools")];
  return `<section id="extensions" class="section section-tint"><div class="container">
    ${heading("04", text("让已有能力，各就其位", "Give existing capabilities a clear home"), text("旧项目补充到主包子模块与配套目录，保持十个主分包不变。", "Existing work extends submodules and supporting directories, preserving the ten primary packages."))}
    <div class="extension-grid">${extensions.map((item, index) => `<article class="extension-item"><span class="extension-number">${String(index + 1).padStart(2, "0")}</span><div><h3>${tr(names[index])}</h3><code>${item[1]}</code><p>${tr(item[2])}</p></div></article>`).join("")}</div>
  </div></section>`;
}
function trackContent() {
  const track = tracks.find(item => item.id === state.track);
  return `<ol class="learning-steps">${track.steps.map((step, i) => `<li><span class="lesson-number">${String(i + 1).padStart(2, "0")}</span><div><h3>${tr(step[0])}</h3><p>${tr(step[1])}</p></div>${modules.some(m => m.id === step[2]) ? `<button class="lesson-link" data-module="${step[2]}" aria-label="${text("打开", "Open")} ${step[2]}">${text("了解模块", "Explore module")} ${arrow}</button>` : `<a class="lesson-link" href="#${step[2]}">${text("前往学习", "Explore section")} ${arrow}</a>`}</li>`).join("")}</ol>`;
}
function learning() {
  return `<section id="learn" class="section container">
    ${heading("05", text("找到你的学习起点", "Find your starting point"), text("从概念、接口或领域问题进入，逐步建立完整理解。", "Start with concepts, interfaces or domain problems and build a complete understanding."))}
    <div class="track-tabs" role="tablist" aria-label="${text("学习路线", "Learning paths")}">${tracks.map(item => `<button id="track-${item.id}" role="tab" aria-selected="${state.track === item.id}" aria-controls="track-content" tabindex="${state.track === item.id ? 0 : -1}" data-track="${item.id}"><span>${tr(item.tag)}</span><strong>${tr(item.name)}</strong></button>`).join("")}</div>
    <div id="track-content" role="tabpanel" aria-labelledby="track-${state.track}">${trackContent()}</div>
    <div class="glossary"><div><span class="eyebrow">${text("概念速查", "CONCEPT REFERENCE")}</span><h3>${text("几个经常遇到的术语", "Terms you’ll encounter")}</h3></div><div class="glossary-list">${glossary.map((item, i) => `<details id="term-${i}"><summary>${item[0]}<span class="plus" aria-hidden="true">+</span></summary><p>${tr(item[1])}</p></details>`).join("")}</div></div>
  </section>`;
}
function roadmapSection() {
  return `<section id="roadmap" class="section section-tint"><div class="container">
    ${heading("06", text("从架构蓝图，到分层交付", "From architecture to staged delivery"), text("开发优先级与验收要求，不代表当前完成进度。", "Development priorities and acceptance criteria, not a report of current completion."))}
    <div class="roadmap-grid">${roadmap.map(item => `<article><span class="roadmap-number">${item.n}</span><h3>${tr(item.title)}</h3><p class="roadmap-packages">${item.packages}</p><p>${tr(item.desc)}</p><div class="roadmap-gate"><span>${text("验收重点", "ACCEPTANCE")}</span><p>${tr(item.gate)}</p></div></article>`).join("")}</div>
  </div></section>`;
}
function modalContent(id) {
  const module = modules.find(item => item.id === id);
  return `<div class="modal-header"><div><span class="eyebrow">${tr(categories[module.category])}</span><h2 id="module-dialog-title" tabindex="-1">${module.name}<span>${tr(module.title)}</span></h2><code>${packageName(module.id)}</code></div><button class="modal-close" data-close-module aria-label="${text("关闭模块详情", "Close module details")}">×</button></div>
    <div class="modal-content"><p class="module-concept">${tr(module.concepts)}</p><div class="module-tags">${module.tags.map(tag => `<span>${tag}</span>`).join("")}</div><h3>${text("功能框架", "CAPABILITY FRAMEWORK")}</h3><ul class="feature-list">${tr(module.features).map(feature => `<li>${feature}</li>`).join("")}</ul><div class="module-boundary"><strong>${text("职责与范围", "RESPONSIBILITY & SCOPE")}</strong><p>${tr(module.boundary)}</p></div><div class="modal-related"><h3>${text("继续探索", "CONTINUE EXPLORING")}</h3><div>${module.related.map(moduleLink).join("")}</div></div><p class="modal-source">${text("依据架构 PPT", "Architecture deck")}: ${text("第", "slides")} ${module.slides} ${text("页 · 目标能力按阶段建设", "· target capabilities are developed in stages")}</p></div>`;
}
function render() {
  const openDetails = [...root.querySelectorAll("details[open]")].map(item => item.id);
  const scrollY = window.scrollY;
  document.documentElement.lang = state.locale;
  document.title = text("Quantum Bridge · 生态学习中心", "Quantum Bridge · Ecosystem Learning Center");
  document.querySelector('meta[name="description"]').content = text("探索 Quantum Bridge 量子生态：从硬件、编译器和 QuantumOS，到十个主分包与行业应用。", "Explore the Quantum Bridge ecosystem, from hardware, compilers and QuantumOS to ten packages and industry applications.");
  root.innerHTML = `<a class="skip-link" href="#main">${text("跳到正文", "Skip to content")}</a>
    <header class="site-header"><div class="nav-container"><a class="brand" href="#main" aria-label="Quantum Bridge"><span class="brand-symbol">QB</span><span>Quantum<span class="brand-light">Bridge</span><small>${text("生态学习中心", "ECOSYSTEM GUIDE")}</small></span></a>
    <nav id="site-nav" aria-label="${text("页面导航", "Page navigation")}"><a href="#architecture">${text("架构", "Architecture")}</a><a href="#modules">${text("生态模块", "Modules")}</a><a href="#workflow">${text("运行机制", "Workflows")}</a><a href="#learn">${text("学习路径", "Learn")}</a><a href="#roadmap">${text("路线图", "Roadmap")}</a></nav>
    <div class="nav-actions"><div class="locale-switch" role="group" aria-label="${text("页面语言", "Page language")}"><button data-language="zh-CN" aria-pressed="${state.locale === "zh-CN"}" lang="zh-CN">中文</button><button data-language="en" aria-pressed="${state.locale === "en"}" lang="en">EN</button></div><button class="menu-toggle" aria-controls="site-nav" aria-expanded="false" aria-label="${text("打开导航", "Open navigation")}"><span></span><span></span></button></div></div></header>
    <main id="main"><section class="hero container"><div class="hero-copy"><div class="hero-kicker"><span class="kicker-line"></span>QUANTUM BRIDGE ECOSYSTEM<span class="blueprint-badge">${text("架构蓝图", "ARCHITECTURE BLUEPRINT")}</span></div><h1>${text("从量子硬件，<br>到每一个应用。", "From quantum hardware<br>to real-world applications.")}</h1><p>${text("一个贯通硬件、编译器、QuantumOS 与行业应用的量子生态。沿着架构探索十个主分包，理解每一层如何协作。", "A quantum ecosystem connecting hardware, compilers, QuantumOS and domain applications. Explore ten packages and discover how every layer works together.")}</p><a class="primary-link" href="#architecture">${text("开始探索架构", "Explore the architecture")}<span aria-hidden="true">↓</span></a></div><div class="hero-facts"><div><strong>05</strong><span>${text("架构层", "Architecture layers")}</span></div><div><strong>10</strong><span>${text("主分包", "Primary packages")}</span></div><div><strong>04</strong><span>${text("应用领域", "Application domains")}</span></div><p>QB + QuantumOS</p></div></section>
    ${architecture()}${moduleCards()}${workflow()}${extensionSection()}${learning()}${roadmapSection()}
    <section class="resources container"><div><span class="eyebrow">${text("继续阅读", "KEEP EXPLORING")}</span><h2>${text("从框架图，走向源码与实践", "From architecture to code and practice")}</h2><p>${text("本指南依据 33 页生态架构 PPT v2.4 整理。QuantumOS 原架构提供微内核、HAL、调度与驱动时序的设计参考。", "This guide follows the 33-slide ecosystem architecture deck v2.4. QuantumOS provides the reference microkernel, HAL, scheduling and driver-sequence design.")}</p></div><div class="resource-links"><a href="./assets/quantumbridge-ecosystem.pptx" download="QuantumBridge-Ecosystem-v2.4.pptx"><span>${text("下载可编辑架构 PPT", "Download the editable architecture deck")}<small>PPTX · 33 ${text("页", "slides")}</small></span><span aria-hidden="true">↓</span></a><a href="https://github.com/crystal-tensor/QuantumOS#4-system-architecture" target="_blank" rel="noopener noreferrer"><span>${text("QuantumOS 架构与源码", "QuantumOS architecture & source")}<small>GitHub · crystal-tensor/QuantumOS</small></span>${arrow}</a><a href="./index.html"><span>${text("打开 QuantumBridge Studio", "Open QuantumBridge Studio")}<small>${text("本地原型与工作流", "Local prototype & workflows")}</small></span>${arrow}</a></div></section></main>
    <footer class="site-footer container"><span>Quantum Bridge</span><p>${text("理解架构，探索模块，连接量子计算。", "Understand the architecture. Explore the modules. Connect quantum computing.")}</p><a href="#main">${text("回到顶部 ↑", "Back to top ↑")}</a></footer>
    <dialog class="module-dialog" id="module-dialog" aria-labelledby="module-dialog-title"></dialog>`;
  openDetails.forEach(id => { const item = document.getElementById(id); if (item) item.open = true; });
  if (state.module) { const dialog = root.querySelector("#module-dialog"); dialog.innerHTML = modalContent(state.module); dialog.showModal(); }
  root.querySelector("#module-dialog").addEventListener("close", () => { state.module = null; document.body.classList.remove("dialog-open"); moduleOpener?.isConnected && moduleOpener.focus({preventScroll:true}); });
  window.scrollTo({ top: scrollY, behavior: "instant" });
  scheduleNavigationUpdate();
}
function openModule(id, opener) {
  if (!modules.some(item => item.id === id)) return;
  const dialog = root.querySelector("#module-dialog");
  if (!dialog.open) moduleOpener = opener;
  state.module = id;
  dialog.innerHTML = modalContent(id);
  if (!dialog.open) dialog.showModal();
  document.body.classList.add("dialog-open");
  dialog.scrollTop = 0;
  dialog.querySelector(".modal-close").focus({preventScroll:true});
}
function closeMenu() {
  root.querySelector("#site-nav").classList.remove("open");
  const menu = root.querySelector(".menu-toggle");
  menu.setAttribute("aria-expanded", "false");
  menu.setAttribute("aria-label", text("打开导航", "Open navigation"));
}
function selectTab(attribute, id) {
  const selector = attribute === "scenario" ? "scenario" : "track";
  state[selector] = id;
  root.querySelectorAll(`[data-${selector}]`).forEach(button => { const active = button.dataset[selector] === id; button.setAttribute("aria-selected", String(active)); button.tabIndex = active ? 0 : -1; });
  const target = root.querySelector(`#${selector}-content`);
  target.setAttribute("aria-labelledby", `${selector}-${id}`);
  target.innerHTML = selector === "scenario" ? scenarioContent() : trackContent();
}
root.addEventListener("click", event => {
  const language = event.target.closest("[data-language]");
  if (language) { state.locale = language.dataset.language; try { localStorage.setItem("quantumbridge.locale", state.locale); } catch {} const url=new URL(location.href);url.searchParams.set("lang", state.locale === "en" ? "en" : "zh");history.replaceState(null,"",url);render();root.querySelector(`[data-language="${state.locale}"]`).focus({preventScroll:true});return; }
  const layer = event.target.closest("[data-layer]");
  if (layer) { state.layer=layer.dataset.layer;root.querySelectorAll("[data-layer]").forEach(button => {const active=button.dataset.layer===state.layer;button.classList.toggle("selected",active);button.setAttribute("aria-pressed",String(active));});root.querySelector("#layer-detail").innerHTML=architectureDetail();return; }
  const module = event.target.closest("[data-module]");
  if (module) {openModule(module.dataset.module,module);return;}
  if (event.target.closest("[data-close-module]")) {root.querySelector("#module-dialog").close();return;}
  if (event.target === root.querySelector("#module-dialog")) {const box=event.target.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)event.target.close();}
  const scenario=event.target.closest("[data-scenario]");if(scenario){selectTab("scenario",scenario.dataset.scenario);return;}
  const track=event.target.closest("[data-track]");if(track){selectTab("track",track.dataset.track);return;}
  const menu=event.target.closest(".menu-toggle");if(menu){const open=menu.getAttribute("aria-expanded")!=="true";menu.setAttribute("aria-expanded",String(open));menu.setAttribute("aria-label",open?text("关闭导航","Close navigation"):text("打开导航","Open navigation"));root.querySelector("#site-nav").classList.toggle("open",open);return;}
  if(event.target.closest("#site-nav a")) closeMenu();
});
root.addEventListener("keydown",event=>{
  if(event.key === "Escape" && root.querySelector(".menu-toggle").getAttribute("aria-expanded") === "true") { closeMenu(); root.querySelector(".menu-toggle").focus(); }
  const tab=event.target.closest('[role="tab"]');
  if(!tab||!["ArrowLeft","ArrowRight","Home","End"].includes(event.key))return;
  event.preventDefault();const tabs=[...tab.closest('[role="tablist"]').querySelectorAll('[role="tab"]')];const current=tabs.indexOf(tab);const next=event.key==="Home"?0:event.key==="End"?tabs.length-1:(current+(event.key==="ArrowRight"?1:-1)+tabs.length)%tabs.length;tabs[next].click();tabs[next].focus();
});
render();
if(location.hash)requestAnimationFrame(()=>document.getElementById(location.hash.slice(1))?.scrollIntoView());
