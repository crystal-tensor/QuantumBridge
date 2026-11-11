// Copyright 2026 QuantumBridge Contributors. Apache-2.0.
// Register every published local page here so the framework remains its entry point.
import { bi, domains, directions } from "./data.js";
import { publicSite, privateDocuments } from "./deployment.js";

const moduleRoot = new URL("../../", import.meta.url);
export const siteBase = moduleRoot.protocol === "file:" ? "/" : moduleRoot.pathname;

export const resources = [
  { domain: "finance", kind: "index", file: "index.html", title: bi("金融案例与报告总目录", "Finance cases & reports") },
  { domain: "finance", kind: "case", direction: "portfolio", file: "01_allocation_quafu.html", title: bi("资产配置 · QAOA 组合选择", "Asset allocation · QAOA portfolio selection") },
  { domain: "finance", kind: "case", direction: "risk", file: "02_risk_quafu.html", title: bi("风险计量 · VaR / CVaR", "Risk measurement · VaR / CVaR") },
  { domain: "finance", kind: "case", direction: "pricing", file: "03_derivatives_quafu.html", title: bi("衍生品 · 期权定价与对冲", "Derivatives · Option pricing & hedging") },
  { domain: "finance", kind: "case", direction: "financial-constraints", file: "04_constraints_quafu.html", title: bi("金融约束 · QUBO 求解", "Financial constraints · QUBO solving") },
  { domain: "finance", kind: "case", direction: "market-models", file: "05_correlation_quafu.html", title: bi("相关性与波动 · 量子重叠估计", "Correlation & volatility · Quantum overlap estimation") },
  { domain: "finance", kind: "case", direction: "portfolio", file: "dwave_portfolio.html", title: bi("D-Wave CQM · 真实股票组合", "D-Wave CQM · Real-stock portfolio") },
  { domain: "finance", kind: "case", direction: "financial-constraints", file: "dwave_constraints.html", title: bi("D-Wave CQM · 预算与行业约束", "D-Wave CQM · Budget & sector constraints") },
  { domain: "finance", kind: "case", direction: "pricing", file: "qmc_pricing.html", title: bi("量子蒙特卡洛 · IBM 期权模型定价", "Quantum Monte Carlo · IBM model pricing") },
  { domain: "finance", kind: "case", direction: "risk", file: "qmc_risk.html", title: bi("量子蒙特卡洛 · 真实损失与 CVaR", "Quantum Monte Carlo · Historical loss & CVaR") },
  { domain: "finance", kind: "case", direction: "market-models", file: "qmc_hybrid.html", title: bi("可微混合模型 · IBM 波动研究", "Differentiable hybrid · IBM volatility research") },
  { domain: "finance", kind: "index", file: "cirq_finance.html", title: bi("Cirq 量子金融 · 方法与案例", "Cirq finance · Methods & cases") },
  { domain: "finance", kind: "case", direction: "portfolio", file: "cirq_portfolio.html", title: bi("Cirq · QAOA 资产组合选择", "Cirq · QAOA portfolio selection") },
  { domain: "finance", kind: "case", direction: "risk", file: "cirq_risk.html", title: bi("Cirq · 损失分布与 VaR / CVaR", "Cirq · Loss distribution & VaR / CVaR") },
  { domain: "finance", kind: "case", direction: "pricing", file: "cirq_pricing.html", title: bi("Cirq · 离散欧式期权定价", "Cirq · Discrete European option pricing") },
  { domain: "finance", kind: "case", direction: "financial-constraints", file: "cirq_constraints.html", title: bi("Cirq · 预算与持仓约束", "Cirq · Budget & position constraints") },
  { domain: "finance", kind: "case", direction: "market-models", file: "cirq_market_walk.html", title: bi("Cirq · 量子游走与波动情景", "Cirq · Quantum walk & volatility scenarios") },
  { domain: "finance", kind: "diagnostic", file: "06_hardware_diagnostics.html", title: bi("D1 · 真机最小诊断", "D1 · Minimal hardware diagnostics") },
  { domain: "finance", kind: "diagnostic", file: "finance_quafu_d2_mapping_diagnosis.html", title: bi("D2 · 位序与映射诊断", "D2 · Bit-order & mapping diagnostics") },
  { domain: "finance", kind: "diagnostic", file: "finance_quafu_d3_client_contract.html", title: bi("D3 · 夸父客户端契约审计", "D3 · Quafu client contract audit") },
  { domain: "science", kind: "index", file: "index.html", title: bi("科学计算 · 四类本地案例", "Science · Four local case studies") },
  { domain: "science", kind: "case", direction: "chemistry", file: "01_chemistry.html", title: bi("量子化学 · H2 变分与测量", "Chemistry · H2 variation & measurement") },
  { domain: "science", kind: "case", direction: "biomedicine", file: "02_biomedicine.html", title: bi("量子生物 · 格点构象", "Biomedicine · Lattice conformation") },
  { domain: "science", kind: "case", direction: "materials", file: "03_materials.html", title: bi("量子材料 · Hubbard 有限簇", "Materials · Finite Hubbard cluster") },
  { domain: "science", kind: "case", direction: "physics", file: "04_physics.html", title: bi("基础物理 · 自旋动力学", "Physics · Spin dynamics") },
  { domain: "industry", kind: "index", file: "index.html", title: bi("工业优化 · 五类本地案例", "Industry · Five local case studies") },
  { domain: "industry", kind: "case", direction: "routing-scheduling", file: "01_routing-scheduling.html", title: bi("生产调度 · 两作业排程", "Scheduling · Two-job schedule") },
  { domain: "industry", kind: "case", direction: "supply-chain", file: "02_supply-chain.html", title: bi("供应链 · 运输配置", "Supply chain · Shipment allocation") },
  { domain: "industry", kind: "case", direction: "energy", file: "03_energy.html", title: bi("能源 · 机组容量承诺", "Energy · Capacity commitment") },
  { domain: "industry", kind: "case", direction: "combinatorial", file: "04_combinatorial.html", title: bi("组合优化 · 加权 MaxCut", "Optimization · Weighted MaxCut") },
  { domain: "industry", kind: "case", direction: "integer-multiobjective", file: "05_integer-multiobjective.html", title: bi("整数多目标 · 收益与排放", "Integer objectives · Profit & emissions") },
  { domain: "security", kind: "index", file: "index.html", title: bi("量子安全 · 五类本地案例", "Security · Five local case studies") },
  { domain: "security", kind: "case", direction: "pqc", file: "01_pqc.html", title: bi("后量子密码 · ML-KEM / ML-DSA", "PQC · ML-KEM / ML-DSA") },
  { domain: "security", kind: "case", direction: "qkd", file: "02_qkd.html", title: bi("QKD · BB84 与窃听实验", "QKD · BB84 & interception experiment") },
  { domain: "security", kind: "case", direction: "threat", file: "03_threat.html", title: bi("量子威胁 · Grover 搜索", "Threat assessment · Grover search") },
  { domain: "security", kind: "case", direction: "qrng", file: "04_qrng.html", title: bi("随机数 · 诊断与去偏模拟", "Randomness · Diagnostics & extraction simulation") },
  { domain: "security", kind: "case", direction: "privacy", file: "05_privacy.html", title: bi("数据安全 · 加密与审计", "Data security · Encryption & audit") },
];

// Project-wide Word documents are shared by domains and have no paired notebook.
export const privateDocumentResources = ["science", "finance", "industry", "security"].map(domain => ({
  domain,
  kind: "document",
  href: `/reports/qb-project/index.html?category=${domain}`,
  title: bi("QB 项目立项申请书 · Word", "QB project applications · Word"),
}));
export const projectDocuments = !publicSite && privateDocuments ? privateDocumentResources : [];

// Guides share the owner-facing taxonomy; they are not notebook artifacts.
export const documentationResources = [
  ...domains.map(domain => ({ domain: domain.id, kind: "guide", href: `/readme.html#${domain.id}`, title: bi(`${domain.name["zh-CN"]} · 安装与使用指南`, `${domain.name.en} · User guide`) })),
  ...directions.map(direction => ({ domain: direction.domain, direction: direction.id, kind: "guide", href: `/readme.html#${direction.id}`, title: bi(`${direction.name["zh-CN"]} · 使用教程`, `${direction.name.en} · Tutorial`) })),
];

// The owner wants a subtle entrance; keep it registered in every relevant domain.
export const engineeringResources = domains.map(domain => ({
  domain: domain.id, kind: "engineering", subtle: true,
  href: `/engineering.html?domain=${domain.id}`,
  title: bi("工程进展", "Engineering progress"),
}));

export const resourceHref = (resource, notebook = false) => resource.href ?
  `${siteBase}${resource.href.replace(/^\//, "")}` :
  `${siteBase}examples/${resource.domain}/${notebook ? resource.file.replace(/\.html$/, ".ipynb") : resource.file}`;

export const domainResources = domain => [...resources, ...projectDocuments, ...engineeringResources, ...documentationResources.filter(resource => !resource.direction)].filter(resource => resource.domain === domain && resource.kind !== "case");
export const directionResources = direction => [...resources, ...documentationResources].filter(resource => resource.direction === direction);
