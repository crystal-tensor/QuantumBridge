// Copyright 2026 QuantumBridge Contributors. Apache-2.0.
// Owner-provided target taxonomy, not a claim of implemented domain parity.
export const bi = (zh, en) => ({ "zh-CN": zh, en });
export const domains = [
  { id: "science", icon: "atom", name: bi("科学计算", "Scientific computing"), code: "QB.SCIENCE", summary: bi("从分子、材料到多体系统", "Molecules, materials and many-body systems") },
  { id: "finance", icon: "chart-no-axes-combined", name: bi("金融", "Finance"), code: "QB.FINANCE", summary: bi("投资、风险与资产定价", "Investments, risk and asset valuation") },
  { id: "industry", icon: "workflow", name: bi("工业优化", "Industrial optimization"), code: "QB.OPTIMIZATION", summary: bi("约束建模、求解与决策", "Constrained models, solvers and decisions") },
  { id: "security", icon: "shield-check", name: bi("量子安全", "Quantum security"), code: "QB.SECURITY", summary: bi("密码、通信与可信计算", "Cryptography, communication and trust") },
];

const item = (id, domain, name, en, summary, summaryEn, features, featuresEn, modules, boundary, boundaryEn, reference, referenceEn, source) =>
  ({ id, domain, name: bi(name,en), summary: bi(summary,summaryEn), features: bi(features,featuresEn), modules, boundary: bi(boundary,boundaryEn), reference: bi(reference,referenceEn), source });

export const directions = [
  item("chemistry","science","量子化学","Quantum chemistry","分子哈密顿量、电子结构与能量求解","Molecular Hamiltonians, electronic structure and energies",
    ["分子哈密顿量、Hartree–Fock 与活性空间","UCCSD / VQE、基态与激发态","偶极矩、分子性质与结构优化"],
    ["Molecular Hamiltonians, Hartree–Fock and active spaces","UCCSD / VQE, ground and excited states","Dipoles, molecular properties and geometry optimization"],
    ["Hamiltonian","Fermion mapping","VQE / UCCSD"],"分子规模、基组、活性空间及误差须分别验证；小分子实验不等同于生产级化学计算。","Validate molecular scale, basis sets, active spaces and errors separately; small-molecule experiments are not production chemistry.","Qiskit Nature · OpenFermion","Qiskit Nature · OpenFermion","https://qiskit-community.github.io/qiskit-nature/"),
  item("biomedicine","science","量子生物／生物医药","Biology & biomedicine","小分子、构象与分子相互作用","Small molecules, conformations and molecular interactions",
    ["药物小分子能量与构象比较","蛋白局部活性空间与分子相互作用","衔接经典筛选与实验验证"],
    ["Small-molecule energies and conformations","Protein-fragment active spaces and molecular interactions","Connections to classical screening and experimental validation"],
    ["Chemistry","Active space","Hybrid workflow"],"蛋白分区、业务数据与实验接口需独立建设，不将化学适配器描述为完整药物研发平台。","Protein partitioning, domain data and experimental interfaces require separate work; a chemistry adapter is not a complete drug discovery platform.","Nature 化学组件 · OpenFermion","Nature chemistry components · OpenFermion","https://quantumai.google/openfermion"),
  item("materials","science","量子材料","Quantum materials","晶格、能谱与周期模型","Lattices, spectra and periodic models",
    ["晶格与周期模型、能谱及能带相关计算","电池、催化剂、半导体模型","表面吸附及材料性质计算流程"],
    ["Lattice and periodic models, spectra and band-related calculations","Battery, catalyst and semiconductor models","Surface adsorption and materials-property workflows"],
    ["Lattice models","Hamiltonian","Eigensolver"],"模型能谱不等于真实材料能带；周期边界、物理近似和材料参数须单独验收。","Model spectra are not real-material band structures; boundaries, approximations and material parameters need separate validation.","Nature 格点模型 · OpenFermion","Nature lattice models · OpenFermion","https://qiskit-community.github.io/qiskit-nature/"),
  item("physics","science","基础物理与多体系统","Physics & many-body systems","自旋、动力学与关联函数","Spins, dynamics and correlation functions",
    ["Ising、Heisenberg 与多体模型","时间演化、关联函数及观测量","简化核物理模型与经典对照"],
    ["Ising, Heisenberg and many-body models","Time evolution, correlations and observables","Simplified nuclear models and classical references"],
    ["Spin algebra","Time evolution","Observables"],"科研模型和近似条件需要溯源，不能将简化模型结果扩大解释为真实系统精确预测。","Research models and approximations need provenance; simplified models do not establish exact predictions for real systems.","Qiskit Nature · Cirq / ReCirq","Qiskit Nature · Cirq / ReCirq","https://quantumai.google/cirq/experiments"),
  item("portfolio","finance","量化投资与资产配置","Investing & asset allocation","组合、权重与风险收益约束","Portfolios, weights and risk–return constraints",
    ["组合选择、权重分配与预算约束","持仓限制、风险收益平衡及再平衡","经典基线、可行性与结果验证"],
    ["Portfolio selection, weights and budgets","Position limits, risk–return trade-offs and rebalancing","Classical baselines, feasibility and result validation"],
    ["Quadratic model","QUBO / Ising","QAOA / VQE"],"保留数据假设、交易约束与回测；教学组合优化不构成投资建议或实盘系统。","Retain data assumptions, trading constraints and backtests; tutorial optimization is not investment advice or a live trading system.","Qiskit Finance · Optimization","Qiskit Finance · Optimization","https://qiskit-community.github.io/qiskit-finance/tutorials/01_portfolio_optimization.html"),
  item("risk","finance","风险计量","Risk measurement","VaR / CVaR、尾部风险与压力测试","VaR / CVaR, tail risk and stress tests",
    ["VaR / CVaR 与预期损失","信用、市场与流动性风险模型","尾部情景、压力测试与误差分析"],
    ["VaR / CVaR and expected loss","Credit, market and liquidity risk models","Tail scenarios, stress tests and error analysis"],
    ["Distributions","Amplitude estimation","Classical baseline"],"完整风控还需数据治理、模型校准和业务验证，不能用采样演示代替实际风险系统。","Complete risk management also needs data governance, model calibration and domain validation; a sampling demo is not a risk platform.","Qiskit Finance 风险分析教程","Qiskit Finance risk tutorials","https://qiskit-community.github.io/qiskit-finance/tutorials/09_credit_risk_analysis.html"),
  item("pricing","finance","衍生品定价与对冲","Derivatives & hedging","期权、固定收益与多资产估值","Options, fixed income and multi-asset valuation",
    ["期权、固定收益及多资产估值","路径模型与期货对冲","经典定价对照、置信区间与误差"],
    ["Options, fixed income and multi-asset valuation","Path models and futures hedging","Classical pricing, confidence intervals and errors"],
    ["Payoff encoding","Amplitude estimation","Error analysis"],"明确市场与分布假设；示例定价模型不等于完整交易、对冲或风险管理平台。","State market and distribution assumptions; example pricing models are not complete trading, hedging or risk platforms.","Qiskit Finance 定价示例","Qiskit Finance pricing examples","https://qiskit-community.github.io/qiskit-finance/tutorials/index.html"),
  item("financial-constraints","finance","金融约束优化","Financial constraint optimization","金融约束到 QUBO / Ising 的转换","Financial constraints encoded as QUBO / Ising",
    ["投资与交易约束建模","QUBO / Ising 编码、求解及解码","原始约束恢复与可行性检查"],
    ["Investment and trading constraints","QUBO / Ising encoding, solving and decoding","Original-constraint recovery and feasibility checks"],
    ["Constraints","QUBO encoder","Solution decoder"],"惩罚项与编码必须逐项校验，低目标值不代表原始业务约束已满足。","Validate penalties and encodings individually; a low objective does not imply original business constraints are satisfied.","Finance + Optimization 组合流程","Finance + Optimization workflows","https://qiskit-community.github.io/qiskit-optimization/"),
  item("market-models","finance","相关性与市场波动","Correlation & volatility","协方差、波动情景与混合 AI 模型","Covariance, volatility scenarios and hybrid AI",
    ["资产相关性、协方差与市场数据","波动情景、概率分布及混合 AI 模型","数据版本、训练验证与回测连接"],
    ["Asset correlations, covariance and market data","Volatility scenarios, distributions and hybrid AI","Data versions, validation and backtest integration"],
    ["Data encoding","QML","Scenario models"],"外接数据与高级波动模型需另行开发，数据泄漏、过拟合与样本偏差须独立评估。","External data and advanced volatility models need additional development; evaluate leakage, overfitting and sample bias separately.","Finance 数据及概率组件","Finance data and probability components","https://qiskit-community.github.io/qiskit-finance/"),
  item("routing-scheduling","industry","路径与生产调度优化","Routing & production scheduling","物流路径、时间窗与作业车间调度","Logistics, time windows and job-shop scheduling",
    ["TSP、车辆路径与时间窗","仓储物流、设备排程与作业车间","业务约束、可行解和成本比较"],
    ["TSP, vehicle routing and time windows","Warehousing, machine and job-shop scheduling","Domain constraints, feasible solutions and costs"],
    ["Problem modeling","QUBO / Ising","Hybrid solver"],"复杂时间窗与生产约束需要专用模型；可运行的图优化样例不代表完整调度系统。","Complex time windows and production constraints need dedicated models; a graph optimization example is not a scheduling platform.","Optimization 应用模型 · Cirq QAOA","Optimization applications · Cirq QAOA","https://qiskit-community.github.io/qiskit-optimization/apidocs/qiskit_optimization.applications.html"),
  item("supply-chain","industry","供应链与资源配置","Supply chain & allocation","供需网络、库存与多周期资源协同","Supply networks, inventory and multi-period resources",
    ["供应网络、库存与产能配置","人力、设备及多周期供需协同","成本、约束与经典解对照"],
    ["Supply networks, inventory and capacity","Workforce, equipment and multi-period coordination","Costs, constraints and classical solution references"],
    ["Integer model","Constraints","Decomposition"],"供应链业务数据、网络约束与跨周期决策需定制，不将通用求解器描述为现成业务套件。","Domain data, network constraints and multi-period decisions require customization; a generic solver is not a ready-made supply-chain suite.","Optimization 二次规划与资源模型","Optimization quadratic and resource models","https://qiskit-community.github.io/qiskit-optimization/"),
  item("energy","industry","能源与电力优化","Energy & power optimization","电网负荷、储能与新能源调度","Grid loads, storage and renewable scheduling",
    ["机组组合、电网负荷与储能","新能源调度与能耗优化","电力约束及物理可行性验证"],
    ["Unit commitment, grid loads and storage","Renewable scheduling and energy optimization","Power-system constraints and physical feasibility"],
    ["Mixed integer model","Constraints","Hybrid solver"],"电力系统接口、物理模型和安全约束需独立集成，不能将编码结果当作可直接下发的调度计划。","Integrate power-system interfaces, physics and safety constraints separately; an encoded solution is not a dispatch-ready schedule.","通用 Optimization 框架","General Optimization framework","https://qiskit-community.github.io/qiskit-optimization/"),
  item("combinatorial","industry","通用组合优化","Combinatorial optimization","QUBO / Ising、最大割与图优化","QUBO / Ising, MaxCut and graph optimization",
    ["QUBO / Ising 与图优化建模","MaxCut、编码与解恢复","经典、量子和混合求解器统一接口"],
    ["QUBO / Ising and graph models","MaxCut, encodings and solution recovery","Unified classical, quantum and hybrid solver contracts"],
    ["Quadratic model","QAOA","Solution decoder"],"按问题族验证编码与解码，同时报告可行性、目标值、经典基线和最优性差距。","Validate encoders and decoders by problem family; report feasibility, objectives, classical baselines and optimality gaps.","Optimization / QAOA · Cirq Ising","Optimization / QAOA · Cirq Ising","https://quantumai.google/cirq/experiments/qaoa/qaoa_ising"),
  item("integer-multiobjective","industry","整数规划与多目标决策","Integer & multi-objective decisions","整数、混合整数与多目标模型","Integer, mixed-integer and multi-objective models",
    ["整数、混合整数及约束模型","多目标决策与分解策略","经典基线、适用范围与解质量评估"],
    ["Integer, mixed-integer and constrained models","Multi-objective decisions and decomposition","Classical baselines, applicability and solution quality"],
    ["Integer model","Decomposition","Optimizer interface"],"模型与求解器有明确适用范围；多目标业务偏好及可行性不由量子电路自动保证。","Models and solvers have defined domains; quantum circuits do not automatically establish preferences or feasibility.","Optimization 建模及求解器接口","Optimization modeling and solver interfaces","https://qiskit-community.github.io/qiskit-optimization/"),
  item("pqc","security","后量子密码与迁移","Post-quantum cryptography","密钥封装、签名与系统迁移","Key encapsulation, signatures and migration",
    ["PQC 密钥封装、签名及参数评估","系统适配与迁移验证","UOV / SNOVA 等研究插件"],
    ["PQC encapsulation, signatures and parameter evaluation","System adaptation and migration validation","Research plugins including UOV / SNOVA"],
    ["Classical crypto","Plugin protocol","Audit"],"PQC 在经典计算机运行；研究候选不等同于标准算法，Qiskit 核心与 IBM Quantum Safe 产品必须区分。","PQC runs classically; research candidates are not standards. Distinguish Qiskit core from IBM Quantum Safe products.","独立密码库 · IBM Quantum Safe","Independent cryptographic libraries · IBM Quantum Safe","https://www.ibm.com/quantum/quantum-safe"),
  item("qkd","security","量子保密通信／QKD","Quantum key distribution","BB84、链路噪声与密钥协商","BB84, link noise and key agreement",
    ["BB84、噪声与窃听模型、误码率","密钥协商、纠错与隐私放大","链路仿真及设备、密钥管理接口"],
    ["BB84, noise, eavesdropping and error rates","Key agreement, correction and privacy amplification","Link simulation, device and key management interfaces"],
    ["Protocol circuits","Noise models","Classical channel"],"电路协议实验不等于实际 QKD 网络，认证信道、设备与工程安全仍需验证。","Circuit protocol experiments are not deployed QKD networks; validate authenticated channels, devices and engineering security separately.","Qiskit QKD 教程 · 通用协议电路","Qiskit QKD tutorials · Protocol circuits","https://quantum.cloud.ibm.com/learning/en/modules/computer-science/quantum-key-distribution"),
  item("threat","security","量子威胁与密码安全评估","Quantum threat assessment","Shor / Grover 与密码资源估算","Shor / Grover and cryptographic resource estimates",
    ["Shor / Grover 小规模算法实验","RSA 等经典密码的量子资源估算","威胁模型、假设与评测报告"],
    ["Small-scale Shor / Grover experiments","Quantum resource estimates for classical cryptography","Threat models, assumptions and assessment reports"],
    ["Algorithms","Resource estimation","Reports"],"小规模算法演示或资源估计不代表已破解实际密码；必须给出误差校正与硬件假设。","Small algorithm demos or estimates do not imply real cryptosystems have been broken; state error-correction and hardware assumptions.","Qiskit 算法教学 · Cirq Shor","Qiskit algorithm education · Cirq Shor","https://quantumai.google/cirq/experiments/shor"),
  item("qrng","security","量子随机数／QRNG","Quantum random numbers","物理熵源、健康检测与随机性提取","Physical entropy, health checks and extraction",
    ["真实硬件熵源与设备接入","健康检测及随机性提取","随机数服务与可追踪结果"],
    ["Physical entropy sources and device integration","Health checks and randomness extraction","Random-number services and traceable results"],
    ["Device interface","Entropy extraction","Health checks"],"模拟随机数不等于真实量子熵源；安全级 QRNG 需要物理源、检测及认证体系。","Simulated randomness is not physical quantum entropy; secure QRNG needs physical sources, checks and certification.","硬件测量采样 · 独立 QRNG 工程","Hardware measurement · Independent QRNG engineering","https://quantum.cloud.ibm.com/learning"),
  item("privacy","security","数据安全与隐私计算","Data security & privacy","协议研究、访问控制与运行审计","Protocols, access control and execution audits",
    ["隐私计算与安全协议研究","访问控制、数据完整性及安全接口","运行审计与可追踪结果"],
    ["Privacy computing and security protocol research","Access control, integrity and secure interfaces","Execution audits and result provenance"],
    ["Protocol circuits","Access control","Provenance"],"协议电路不是完整隐私计算系统，安全工程、威胁模型和外部系统集成需分别验收。","Protocol circuits are not complete privacy systems; validate security engineering, threat models and external integrations separately.","通用电路组件 · 独立安全工程","General circuits · Independent security engineering","https://quantum.cloud.ibm.com/docs/"),
];

export const foundation = [
  { icon:"code-2", title:bi("统一开发接口","Unified development"), code:"Circuit · QNode · Tape", body:bi("Qiskit 与 PennyLane 核心语义融合；参数、算子、测量与控制流。","Qiskit and PennyLane core semantics: parameters, operators, measurements and control flow.") },
  { icon:"git-branch", title:bi("编译与转换","Compilation & transforms"), code:"IR · PassManager · QPY / QASM", body:bi("门分解、优化、布局、路由、调度与可验证的格式互操作。","Decomposition, optimization, layout, routing, scheduling and verified interchange.") },
  { icon:"sigma", title:bi("算法与可微计算","Algorithms & differentiation"), code:"Solver · Gradient · Hessian / HVP", body:bi("VQE、QAOA、量子算法及 Torch、JAX、Autograd、TensorFlow 计算图。","VQE, QAOA, quantum algorithms and Torch, JAX, Autograd and TensorFlow graphs.") },
  { icon:"cpu", title:bi("仿真与设备协议","Simulation & devices"), code:"Statevector · Density · MPS · Backend", body:bi("统一执行、噪声、资源预算与后端协议；真机能力需逐项实测。","Execution, noise, resource budgets and backend contracts; hardware capabilities require explicit tests.") },
  { icon:"file-check-2", title:bi("结果与验证","Results & verification"), code:"Result · Provenance · Benchmark", body:bi("复数结果、误差、经典基线、来源记录与可复现报告。","Complex results, errors, classical baselines, provenance and reproducible reports.") },
];

export function validateTaxonomy() {
  if (domains.length!==4 || directions.length!==19) throw new Error("Expected four domains and nineteen directions");
  if (new Set(directions.map(x=>x.id)).size!==19) throw new Error("Direction identifiers must be unique");
  for (const domain of domains) if (directions.filter(x=>x.domain===domain.id).length!==(domain.id==="science"?4:5)) throw new Error("Invalid domain membership");
  for (const entry of directions) {
    if (!domains.some(x=>x.id===entry.domain)) throw new Error("Unknown domain");
    for (const locale of ["zh-CN","en"]) if (!entry.name[locale] || entry.features[locale].length!==3 || !entry.boundary[locale]) throw new Error("Missing bilingual content");
  }
  return true;
}
validateTaxonomy();
