// Copyright 2026 QuantumBridge Contributors. Apache-2.0.
import { domains, directions, foundation } from "./data.js";
import { resources, projectDocuments, resourceHref, domainResources, directionResources } from "./resources.js";

const root=document.querySelector("#framework-app");
const params=new URLSearchParams(location.search);
const state={locale:params.get("lang")==="en"?"en":"zh-CN",category:domains.some(domain=>domain.id===params.get("category"))?params.get("category"):"all",view:"overview",query:"",detail:null};
const text=(zh,en)=>state.locale==="en"?en:zh;
const tr=value=>value[state.locale];
const esc=value=>String(value).replace(/[&<>"']/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const icon=name=>`<i data-lucide="${name}" aria-hidden="true"></i>`;
const domainFor=id=>domains.find(item=>item.id===id);
const matching=()=>directions.filter(item=>(state.category==="all"||item.domain===state.category)&&
  [...Object.values(item.name),...Object.values(item.summary),...Object.values(item.features).flat(),...item.modules,item.id,...[...directionResources(item.id),...domainResources(item.domain)].flatMap(page=>Object.values(page.title))].join(" ").toLocaleLowerCase().includes(state.query.toLocaleLowerCase().trim()));
function icons(){window.lucide?.createIcons({attrs:{"stroke-width":1.6}});}

function resourceLinks(items, compact=false){
  if(!items.length)return "";
  return `<nav class="resource-links ${compact?"compact-resources":""}" aria-label="${text("案例与报告","Cases & reports")}">${items.map(item=>`<a href="${resourceHref(item)}${state.locale==="en"?(resourceHref(item).includes("?")?"&lang=en":"?lang=en"):""}">${icon(item.kind==="diagnostic"?"file-search":item.kind==="index"?"folder-open":"book-open")}<span>${esc(tr(item.title))}</span>${icon("arrow-up-right")}</a>`).join("")}</nav>`;
}

function directionCard(item){
  const cases=directionResources(item.id);
  return `<article class="direction-entry"><button class="direction-card" data-direction="${item.id}" aria-haspopup="dialog" aria-label="${text("查看","View")} ${tr(item.name)}"><span class="direction-number">${String(directions.indexOf(item)+1).padStart(2,"0")}</span><span class="direction-title">${tr(item.name)}</span><span class="direction-summary">${tr(item.summary)}</span><span class="direction-bottom"><span>${text("目标规划","Target scope")}</span>${icon("arrow-up-right")}</span></button>${resourceLinks(cases,true)}</article>`;
}

function domainColumn(domain, items){
  const pages=domainResources(domain.id);
  return `<section class="domain-column ${domain.id}" aria-labelledby="domain-${domain.id}"><header class="domain-heading"><div class="domain-icon">${icon(domain.icon)}</div><div><h2 id="domain-${domain.id}">${tr(domain.name)}</h2><span>${domain.code}</span></div><span class="domain-count">${items.length}</span></header><p class="domain-summary">${tr(domain.summary)}</p>${pages.length?`<div class="domain-resources"><h3>${text("案例与报告","Cases & reports")}</h3>${resourceLinks(pages)}</div>`:""}<div class="direction-list">${items.map(directionCard).join("")}</div></section>`;
}

function renderShell(){
  document.documentElement.lang=state.locale;
  document.title=text("QuantumBridge · 应用框架","QuantumBridge · Application Framework");
  root.innerHTML=`<a class="skip" href="#workspace">${text("跳到应用框架","Skip to framework")}</a>
  <aside class="framework-sidebar">
    <a class="brand" href="./framework.html"><img src="./assets/ecosystem-icon.svg" alt="" width="36" height="36"><span>QuantumBridge<small>${text("量子开发与应用生态","QUANTUM DEVELOPMENT")}</small></span></a>
    <div class="workspace-label">${text("项目工作区","PROJECT WORKSPACE")}</div>
    <button class="side-button active" data-category="all">${icon("layout-grid")}<span>${text("应用框架总览","Application framework")}</span><span class="count">19</span></button>
    <div class="sidebar-label">${text("应用领域","APPLICATION DOMAINS")}</div>
    <nav aria-label="${text("应用领域","Application domains")}">${domains.map(domain=>`<button class="side-button ${domain.id}" data-category="${domain.id}">${icon(domain.icon)}<span>${tr(domain.name)}</span><span class="count">${directions.filter(item=>item.domain===domain.id).length}</span></button>`).join("")}</nav>
    <div class="sidebar-label">${text("计算基础","SHARED FOUNDATION")}</div>
    <button class="side-button" data-view="foundation">${icon("layers")}<span>${text("共享计算基座","Compute foundation")}</span></button>
    <a class="side-button" href="./index.html">${icon("activity")}<span>${text("开发进展","Development progress")}</span>${icon("arrow-up-right")}</a>
    <a class="side-button" href="./ecosystem.html">${icon("network")}<span>${text("生态架构","Ecosystem architecture")}</span>${icon("arrow-up-right")}</a>
    <div class="sidebar-bottom"><span class="local-indicator"></span><div>${text("本地架构预览","LOCAL ARCHITECTURE PREVIEW")}<small>${text("目标规划，不代表功能验收","Target scope, not a parity certificate")}</small></div></div>
  </aside>
  <main class="framework-main" id="workspace">
    <header class="framework-topbar"><div class="project-identity"><img class="company-logo" src="./assets/xianggan-logo.jpg" alt="相干(北京)科技有限公司 logo" width="1474" height="500"><div class="project-identity-text"><div class="breadcrumb">QuantumBridge <span>/</span> ${text("项目框架","Project framework")}</div><div class="company-attribution"><span>${text("所属","Owned by")}</span> <span class="company-name">相干(北京)科技有限公司</span></div></div></div><div class="top-actions"><span class="preview-label">${text("架构预览","ARCHITECTURE PREVIEW")}</span><div class="locale-control" role="group" aria-label="${text("语言","Language")}"><button data-locale="zh-CN" aria-pressed="${state.locale==="zh-CN"}">中文</button><button data-locale="en" aria-pressed="${state.locale==="en"}">EN</button></div></div></header>
    <div class="framework-content">
      <div class="page-heading"><div><div class="eyebrow">QUANTUMBRIDGE / APPLICATION ECOSYSTEM</div><h1>${text("QuantumBridge 应用框架","QuantumBridge application framework")}</h1><p>${text("科学计算、金融、工业优化、量子安全。行业模型共享同一套量子开发与执行基座。","Science, finance, industry and security, built on a shared quantum development and execution foundation.")}</p></div><button class="export-button" data-export>${icon("download")}<span>${text("导出框架","Export framework")}</span></button></div>
      <div class="scope-strip"><div><strong>04</strong><span>${text("应用大类","Domains")}</span></div><div><strong>19</strong><span>${text("细分方向","Directions")}</span></div><div><strong>01</strong><span>${text("共享计算基座","Shared foundation")}</span></div><p>${icon("flag")}${text("首要目标：Qiskit + PennyLane 核心能力融合","Primary objective: unify Qiskit + PennyLane core capabilities")}</p></div>
      <div class="view-toolbar"><div class="view-tabs" role="tablist" aria-label="${text("框架视图","Framework views")}">${[["overview",text("应用总览","Applications")],["foundation",text("共享基座","Foundation")],["comparison",text("生态对照","Ecosystem reference")]].map(([id,label])=>`<button id="view-${id}" role="tab" data-view="${id}" aria-controls="view-content" aria-selected="${state.view===id}" tabindex="${state.view===id?0:-1}">${label}</button>`).join("")}</div><label class="search-field">${icon("search")}<input type="search" id="direction-search" placeholder="${text("搜索方向、模型或算法","Search directions, models or algorithms")}" aria-label="${text("搜索细分方向","Search directions")}" value="${esc(state.query)}"></label></div>
      <div class="result-line"><span id="result-count" role="status" aria-live="polite"></span><span class="target-status"><span></span>${text("目标规划 · 待逐项验收","TARGET SCOPE · VALIDATION REQUIRED")}</span></div>
      <div id="view-content" role="tabpanel" aria-labelledby="view-${state.view}"></div>
      <footer class="framework-footer"><div class="footer-identity"><span>QuantumBridge</span><small>${text("所属","Owned by")} 相干(北京)科技有限公司</small></div><p>${text("分类依据：项目目标分类表 · 不以页面覆盖代替原生函数、真实调用与测试验证。","Based on the project taxonomy. UI coverage does not establish native functionality, real execution or verified parity.")}</p><span>04 / 19</span></footer>
    </div>
  </main>
  <dialog id="direction-dialog" aria-labelledby="direction-title"></dialog><div class="toast" id="toast" role="status" hidden></div>`;
  root.querySelector("#direction-dialog").addEventListener("close",()=>{
    state.detail=null;history.replaceState(null,"",location.pathname+location.search);
  });
  renderBody();
}

function foundationView(compact=false){
  return `<section class="foundation-section ${compact?"compact":""}" aria-labelledby="foundation-title"><div class="section-heading"><div><span class="eyebrow">SHARED QUANTUM FOUNDATION</span><h2 id="foundation-title">${text("一个基座，连接全部应用方向","One foundation for every application")}</h2></div><span class="outline-label">${text("核心研发优先","CORE DEVELOPMENT FIRST")}</span></div><div class="foundation-flow">${foundation.map((layer,index)=>`<div class="foundation-node"><span class="foundation-number">0${index+1}</span>${icon(layer.icon)}<h3>${tr(layer.title)}</h3><code>${layer.code}</code>${compact?"":`<p>${tr(layer.body)}</p>`}</div>`).join("")}</div><div class="execution-boundary">${icon("info")}<p>${text("这是目标架构。Qiskit / PennyLane 全量替代仍在开发；仿真验证、真机调用、密码安全与行业效果须分别提供证据。","This is the target architecture. Full Qiskit / PennyLane replacement remains in development; simulation, hardware, cryptographic security and domain outcomes each require evidence.")}</p></div></section>`;
}

function renderBody(){
  const items=matching();
  root.querySelector("#result-count").textContent=state.view==="foundation"?text("共享基座 / 5 个能力层","Shared foundation / 5 capability layers"):
    `${state.category==="all"?text("全部应用方向","All application directions"):tr(domainFor(state.category).name)} / ${items.length} ${text("个方向","directions")}`;
  root.querySelectorAll("[data-category]").forEach(button=>{
    const active=state.category===button.dataset.category&&state.view!=="foundation";
    button.classList.toggle("active",active);button.setAttribute("aria-pressed",String(active));
  });
  root.querySelectorAll('[role="tab"]').forEach(button=>{
    const active=button.dataset.view===state.view;button.setAttribute("aria-selected",String(active));button.tabIndex=active?0:-1;
  });
  root.querySelector(".search-field").hidden=state.view==="foundation";
  const body=root.querySelector("#view-content");body.setAttribute("aria-labelledby",`view-${state.view}`);
  if(state.view==="foundation")body.innerHTML=foundationView();
  else if(!items.length)body.innerHTML=`<div class="empty-state">${icon("search-x")}<h2>${text("没有匹配的方向","No matching directions")}</h2><p>${esc(state.query)}</p><button class="export-button" data-clear>${text("清除搜索","Clear search")}</button></div>`;
  else if(state.view==="comparison")body.innerHTML=`<div class="comparison-intro">${text("生态参考依据原始分类表；不作为当前版本的逐函数兼容或行业支持认证。","Ecosystem references follow the original taxonomy, not a version-specific function parity or industry-support certification.")}</div><div class="comparison-scroll"><table><thead><tr><th>${text("领域 / 方向","Domain / direction")}</th><th>${text("QuantumBridge 目标能力","QuantumBridge target capability")}</th><th>${text("生态参考","Ecosystem reference")}</th><th>${text("范围","Scope")}</th></tr></thead><tbody>${items.map(item=>`<tr><td><small class="domain-text ${item.domain}">${tr(domainFor(item.domain).name)}</small><button class="table-link" data-direction="${item.id}">${tr(item.name)}${icon("arrow-up-right")}</button></td><td>${tr(item.summary)}</td><td><a href="${item.source}" target="_blank" rel="noopener noreferrer">${tr(item.reference)}${icon("external-link")}</a></td><td><span class="table-status">${text("目标规划","Target scope")}</span></td></tr>`).join("")}</tbody></table></div>`;
  else body.innerHTML=`<div class="domain-grid ${state.category!=="all"?"filtered":""}">${domains.filter(domain=>items.some(item=>item.domain===domain.id)).map(domain=>domainColumn(domain,items.filter(item=>item.domain===domain.id))).join("")}</div>${foundationView(true)}`;
  icons();
}

function openDetail(id){
  const item=directions.find(item=>item.id===id);if(!item)return;
  const domain=domainFor(item.domain);state.detail=id;
  const flows={science:biFlow(["模型与数据","哈密顿量与映射","量子 / 经典求解","性质与误差"],["Models & data","Hamiltonian & mapping","Quantum / classical solver","Properties & errors"]),finance:biFlow(["数据与假设","约束 / 概率编码","优化 / 估计","业务验证"],["Data & assumptions","Constraints / probabilities","Optimization / estimation","Domain validation"]),industry:biFlow(["目标与约束","QUBO / Ising","求解与解码","可行性检查"],["Objectives & constraints","QUBO / Ising","Solve & decode","Feasibility checks"]),security:biFlow(["威胁与安全模型","协议 / 密钥 / 熵源","实验与系统接口","安全验证与审计"],["Threat & security model","Protocols / keys / entropy","Experiments & integration","Validation & audit"])};
  const dialog=root.querySelector("#direction-dialog");const index=directions.indexOf(item);
  dialog.innerHTML=`<div class="detail-top ${item.domain}"><span>${tr(domain.name)}<span class="detail-separator">/</span>${String(index+1).padStart(2,"0")} / 19</span><button class="icon-button close-dialog" data-close title="${text("关闭详情","Close details")}" aria-label="${text("关闭详情","Close details")}">${icon("x")}<span class="symbol-fallback" aria-hidden="true">×</span></button></div><div class="detail-body"><span class="detail-domain-icon ${item.domain}">${icon(domain.icon)}</span><h2 id="direction-title">${tr(item.name)}</h2><p class="detail-summary">${tr(item.summary)}</p><span class="outline-label">${text("目标规划 · 未作全量验收","TARGET SCOPE · NOT FULLY VALIDATED")}</span><section><h3>${text("目标能力","Target capabilities")}</h3><ul class="capability-list">${tr(item.features).map(feature=>`<li>${icon("corner-down-right")}<span>${feature}</span></li>`).join("")}</ul></section><section><h3>${text("计算链路","Computation workflow")}</h3><ol class="workflow-steps">${flows[item.domain].map((step,i)=>`<li><span>0${i+1}</span>${step}</li>`).join("")}</ol></section><section><h3>${text("共享能力依赖","Shared capability dependencies")}</h3><div class="module-list">${item.modules.map(module=>`<code>${module}</code>`).join("")}</div></section><section class="boundary-section">${icon("shield-alert")}<div><h3>${text("交付与验证边界","Delivery & validation boundary")}</h3><p>${tr(item.boundary)}</p></div></section><section class="reference-section"><h3>${text("生态参考","Ecosystem reference")}</h3><a href="${item.source}" target="_blank" rel="noopener noreferrer">${tr(item.reference)}${icon("external-link")}</a></section></div><footer class="detail-footer"><button data-direction="${directions[index-1]?.id||""}" ${index===0?"disabled":""}>${icon("arrow-left")}<span>${text("上一方向","Previous")}</span></button><span>${index+1} / 19</span><button data-direction="${directions[index+1]?.id||""}" ${index===18?"disabled":""}><span>${text("下一方向","Next")}</span>${icon("arrow-right")}</button></footer>`;
  const pages=directionResources(id);
  if(pages.length){
    const section=document.createElement("section");section.className="detail-resources";
    const note=item.domain==="finance"?text("研究案例；真机结果精度尚未通过验收。","Research cases; hardware accuracy has not passed acceptance."):text("本地案例已执行；本批未提交真机，不代表完整行业能力或安全认证。","Executed locally; no hardware submissions in this batch. Not full domain support or security certification.");
    section.innerHTML=`<h3>${text("案例与 Notebook","Cases & notebooks")}</h3>${resourceLinks(pages)}<p>${note}</p><h3>${text("共享案例与报告","Shared cases & reports")}</h3>${resourceLinks(domainResources(item.domain))}`;
    dialog.querySelector(".detail-body").insertBefore(section,dialog.querySelector(".detail-body section"));
  }
  if(!dialog.open)dialog.showModal();
  dialog.scrollTop=0;dialog.querySelector("[data-close]").focus({preventScroll:true});icons();
  history.replaceState(null,"",location.pathname+location.search+"#"+id);
}
const biFlow=(zh,en)=>state.locale==="en"?en:zh;

root.addEventListener("input",event=>{if(event.target.id==="direction-search"){state.query=event.target.value;renderBody();}});
root.addEventListener("click",event=>{
  const button=event.target.closest("button");if(!button||button.disabled)return;
  if(button.hasAttribute("data-category")){state.category=button.dataset.category;state.view="overview";renderBody();}
  else if(button.hasAttribute("data-view")){state.view=button.dataset.view;if(state.view==="overview")state.category="all";renderBody();}
  else if(button.hasAttribute("data-direction")){openDetail(button.dataset.direction);}
  else if(button.hasAttribute("data-close")){root.querySelector("#direction-dialog").close();}
  else if(button.hasAttribute("data-clear")){state.query="";root.querySelector("#direction-search").value="";renderBody();root.querySelector("#direction-search").focus();}
  else if(button.hasAttribute("data-locale")){
    const detail=state.detail;state.locale=button.dataset.locale;
    const url=new URL(location.href);url.searchParams.set("lang",state.locale==="en"?"en":"zh");history.replaceState(null,"",url);
    renderShell();if(detail)openDetail(detail);else root.querySelector(`[data-locale="${state.locale}"]`).focus();
  }else if(button.hasAttribute("data-export")){
    const payload={project:"QuantumBridge",scope:"target-architecture-not-implementation-certificate",domains,directions,foundation,resources,projectDocuments};
    const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:"application/json;charset=utf-8"}));
    const anchor=document.createElement("a");anchor.href=url;anchor.download="quantumbridge-framework-4-domains-19-directions.json";anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    const toast=root.querySelector("#toast");toast.textContent=text("框架数据已导出","Framework data exported");toast.hidden=false;setTimeout(()=>{toast.hidden=true;},3500);
  }
});
root.addEventListener("keydown",event=>{
  const tab=event.target.closest('[role="tab"]');if(!tab||!["ArrowLeft","ArrowRight","Home","End"].includes(event.key))return;
  event.preventDefault();const tabs=[...root.querySelectorAll('[role="tab"]')];const current=tabs.indexOf(tab);
  const next=event.key==="Home"?0:event.key==="End"?tabs.length-1:(current+(event.key==="ArrowRight"?1:-1)+tabs.length)%tabs.length;
  tabs[next].click();tabs[next].focus();
});
renderShell();
if(location.hash)openDetail(location.hash.slice(1));
window.addEventListener("hashchange",()=>{
  if(location.hash)openDetail(location.hash.slice(1));
  else if(root.querySelector("#direction-dialog").open)root.querySelector("#direction-dialog").close();
});
window.addEventListener("load",icons);
