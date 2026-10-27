# Quantum Bridge（量子桥）完整生态 SDK 架构需求文档 V1.1

版本：2026-09-16 · 用途：生态产品定义、研发立项、源码重构与框架汇报。

**本文以用户确定的完整生态框架为目标架构。QuantumBridge、QuantumOS 及既有项目是实现该架构的可复用素材，不构成目标能力的上限。** 下述全栈能力为建设要求；实际交付按模块与里程碑验收。现有代码资产放在文末附录，正文围绕完整生态展开。

---

# 一、项目整体定位

## 1.1 产品名称与定位

**产品名称：Quantum Bridge（量子桥）**。

**产品定位：融合 Qiskit 生态的电路、算法与硬件接入能力，吸纳 PennyLane 的可微量子计算、混合训练与编译能力，并以自研 QuantumOS 统一运行、调度和资源管理的全栈国产化量子计算 SDK 与应用生态。**

生态面向科研院校、量子算法团队、行业客户、量子硬件企业与平台开发者，覆盖“领域问题建模 → 算子/电路 → 可微优化 → 编译 → 调度执行 → 结果验证 → 应用交付”全过程。

目标产品形态包含：独立可安装的 SDK 分包、QuantumOS 运行底座、硬件/框架插件、行业算法工作流、QuantumBridge Studio 与开发工具链。

## 1.2 核心优势与建设目标

1. **四大行业能力统一供给**：Science、Finance、Industry、Crypto-Security 覆盖科学、金融、工业、密码安全；共享电路、算子、优化器、梯度和算力基础设施。
2. **原生可微量子计算**：将 QNode/Tape、梯度规则、混合量子经典计算图和编译优化纳入 Core，支撑所有行业中可微、可训练的算法。
3. **自研 QuantumOS 统一运行**：设备抽象、任务队列、批量调度、资源管理、校准与误差处理通过同一套协议组织，消除框架和硬件之间的重复接入。
4. **模块化与开放生态**：11 个功能分包独立版本、独立安装、按需加载；提供硬件、编译、梯度、算法和可视化扩展机制。
5. **自主核心与国产化适配**：核心流程在不强制安装 Qiskit/PennyLane 等外部量子框架的环境中运行；支持国产量子设备、离线部署和可替换基础软件栈。
6. **从科研到应用的完整闭环**：将可重复实验、经典基线、资源预算、性能评测和可视化作为全生态公共能力，而不是各行业分别建设。

对标用于确定能力范围与验证基线。最终差异体现在统一生态契约、QuantumOS 调度、跨后端工作流和行业集成，性能与算法优势通过基准验证。

## 1.3 五层总体架构

```text
┌─────────────────────────────────────────────────────────────┐
│ 工具链可视化层                                               │
│ Visualization · Benchmark · Tools · QuantumBridge Studio      │
├─────────────────────────────────────────────────────────────┤
│ 插件兼容生态层                                               │
│ Qiskit · PennyLane · PyTorch/JAX · 硬件/模拟器/编译器插件       │
├─────────────────────────────────────────────────────────────┤
│ 四大垂直行业应用层                                           │
│ Science · Finance · Industry · Crypto-Security                │
├─────────────────────────────────────────────────────────────┤
│ 核心编译与电路引擎层                                         │
│ Core · Simulator · ML                                        │
│ Circuit / IR / QNode / Gradient / Compiler / Primitive         │
├─────────────────────────────────────────────────────────────┤
│ QuantumOS 基座                                               │
│ Hardware Abstraction · Runtime · Scheduler · Resource Manager  │
└─────────────────────────────────────────────────────────────┘
```

图中是产品能力分层；插件横跨各层提供扩展。软件依赖按接口单向组织：Core 定义公共契约，OS/Simulator 实现执行协议，ML/行业模块调用公共能力，工具层消费结果。QuantumOS 在运行架构上是基座，但 Core 不反向依赖 OS 实现。

---

# 二、全局核心基座：融合双框架能力与自研 QuantumOS

## 2.1 Quantum-OS：自研量子操作系统层

**目标包：`quantum_bridge_os`**。**对标：Qiskit Runtime 的运行服务与 PennyLane Device 的设备扩展机制**。

QuantumOS 统一量子算力的接入、组织与运行，形成 SDK 到模拟器/真实硬件之间的控制平面与执行平面。

### 完整功能要求

| 子系统 | 功能范围 | 对外能力 |
|---|---|---|
| 统一硬件抽象 HAL | IBM、Google 生态、光量子、超导、离子阱、国产量子芯片与模拟器插件；设备门集、拓扑、测量和控制能力声明 | DeviceSpec、BackendPlugin、能力探测与兼容性校验 |
| 任务运行 Runtime | 单任务/批任务、量子经典混合工作流、异步执行、参数扫描、会话与迭代任务 | JobSpec、JobHandle、状态/取消/结果接口 |
| 调度与队列 Scheduler | 优先级、公平性、保真度/等待/费用约束、任务合并、后端选择与失败转移 | SLA、RouteDecision、AdmissionDecision |
| 资源管理 | qubit/mode、shots、GPU/CPU、执行时间、并发配额、项目/租户预算、资源利用率 | ResourceEstimate、配额与计量 |
| 校准与噪声适配 | 校准版本、T1/T2、门/读出误差、校准有效期、设备噪声模型 | CalSet、噪声快照、编译目标 |
| 误差处理 | ZNE、读出校正、校准矩阵、误差预算与结果不确定性；可扩展纠错研究接口 | MitigationPlan、raw/mitigated Result、成本统计 |
| 可观测与恢复 | 状态事件、日志/trace、资源监控、失败分类、经典优化器/批任务断点续跑 | Event、Checkpoint、Manifest |
| 云端与边缘部署 | 本地运行、私有化控制平面、远程 Worker、供应商云服务接入 | 客户端 API、Worker/HAL 插件、身份与凭证提供器 |

### 设计边界与验收

- 以统一 API 描述跨后端工作流，通过设备能力协商处理门集、离散变量/连续变量和动态控制差异。
- Router 负责估计与可解释推荐；Scheduler 负责准入、队列、公平性和资源租约，服务端保存唯一作业状态。
- 编译制品绑定设备、布局与校准快照；改派、设备变化或校准过期后复验，并在需要时重新编译。
- 断点恢复覆盖经典参数、优化器状态、已完成批次与任务事件；硬件执行恢复通过 provider 状态和明确重执行策略完成。
- 交付验收覆盖提交、查询、取消、重试、幂等、结果回收、校准失效与重启恢复，真实设备插件单独完成端到端测试。

## 2.2 Quantum-Bridge-Core：核心电路与编译引擎

**目标包：`quantum_bridge_core`**。**对标：Qiskit 核心电路/编译能力、PennyLane Core、Catalyst 编译能力**。

Core 是全部 SDK 包共享的语义与算法基座，拥有 **Circuit、IR、QNode/Tape、参数、测量、算子、原语、梯度与编译协议**。ML 使用这些基础能力构建模型，Core 不依赖 ML。

### 完整功能要求

1. **电路与程序构建**：量子寄存器、经典寄存器、标准/自定义量子门、受控操作、参数表达式、复合电路、测量与 reset、动态控制流；提供面向特定硬件的脉冲/波形扩展接口。
2. **OpenQASM 与统一 IR**：OpenQASM 解析/导出、版本化 IR、参数绑定、算子到电路转换、Qiskit/PennyLane 程序导入导出、QISA/QIR 等目标接口。
3. **编译与优化**：门分解、基门转换、冗余剔除、相邻操作合并、线路裁剪、初始布局、拓扑映射、SWAP 路由、噪声/校准感知优化、资源估计与优化报告。
4. **QNode 与可微语义**：函数到 Tape/Program 捕获、可训练参数、测量结果类型、量子经典组合、梯度规则注册和反向传播契约。
5. **梯度体系**：参数偏移、有限差分、支持后端的 adjoint/backprop/device-gradient；支持多输出、批处理、共享参数及梯度统计误差。
6. **JIT 与动态程序**：编译缓存、即时编译、受支持的条件/循环、自适应线路与量子经典控制；支持原生编译和可选编译器插件。
7. **原生原语**：Sampler、Estimator、批量观测、测量分组、参数扫描、shots 管理，面向不同设备保持相同结果合同。
8. **统一算子库**：Pauli、Hamiltonian、稀疏算子、费米子/玻色子、映射、张量积、对易关系和对称性处理。
9. **通用算法与优化器**：VQE、QAOA、Grover、振幅估计、时间演化、经典优化器协议与算法结果，供行业模块组合使用。

### 核心验收

电路/IR/参数/测量往返语义一致；编译前后与解析/独立参考结果一致；后端不支持的指令明确返回诊断；梯度与解析或数值参考对照；冷编译、热执行与缓存命中分别测量。

## 2.3 Quantum-Bridge-Simulator：仿真引擎

**目标包：`quantum_bridge_simulator`**。**对标：Qiskit Aer、PennyLane Lightning 系列模拟器**。

### 完整功能要求

- CPU/GPU 无噪声仿真：statevector、批量参数、shots、精度配置、多线程与向量化执行。
- 带噪声仿真：密度矩阵、Kraus/通道噪声、门噪声、读出噪声、校准数据到噪声模型转换。
- 大规模仿真：张量网络、分布式执行、任务分片、内存预算、问题结构感知的算法选择。
- 高精度多体系统：稀疏 Hamiltonian、时间演化、格点/自旋模型，记录近似、截断与数值收敛。
- 统一仿真配置：随机种子、精度、并行资源、噪声模型、观测量、后端资源预算。
- 双框架兼容：通过 Core IR 及可选 adapter 接入 Qiskit/PennyLane 工作流，提供统一 Result。
- 可微执行支持：对适用模拟算法提供 adjoint/backprop 接口，与 Core 梯度策略协商。

**验收**：解析小系统与 CPU 参考一致；CPU/GPU/分布式结果按精度阈值对照；采样给出统计区间；性能报告包含硬件、精度、规模、噪声与内存条件。

## 2.4 Quantum-Bridge-ML：通用量子机器学习包

**目标包：`quantum_bridge_ml`**。**对标：Qiskit Machine Learning、PennyLane QML**。

ML 是四大行业共用的高层 AI 能力层，负责模型、数据管线、损失、训练、评估与框架 connector；基础 QNode/Tape/梯度语义归 Core。

### 完整功能要求

- **模型库**：QNN、QCNN、量子特征映射、量子核、QSVM、分类/回归/聚类。
- **生成与表示学习**：qGAN、量子 PCA、量子降维、量子编码器与表示学习。
- **混合模型**：经典网络 + 量子层、端到端 loss、参数更新、batch/mini-batch、参数初始化与训练 checkpoint。
- **框架集成**：PyTorch/JAX connector；TensorFlow 按兼容版本策略提供独立评估和适配路线。
- **训练与调优**：优化器、超参数扫描、梯度噪声、shots 分配、收敛诊断与 barren plateau 观察工具。
- **行业赋能**：科学性质预测、金融特征建模、工业优化启发式、密码/安全研究模型，以标准数据与模型接口接入。
- **评估与模型交付**：经典基线、训练/验证/测试划分、模型序列化、参数/数据/环境版本及推理 API。

**验收**：混合计算图能更新预期的经典和量子参数；梯度通过独立参考；模型训练可重放；量子与经典基线使用一致数据、评价指标与预算。

---

# 三、四大垂直行业应用分包：完整业务生态

四行业采用统一的 **Problem → Operator/Program → Solver/Workflow → Result/Report** 模式，复用 Core、Simulator、ML 与 OS。领域包负责业务语义和模型，不重复建设调度与执行引擎。

## 3.1 Quantum-Bridge-Science：自然科学计算包

**目标包：`quantum_bridge_science`**。**对标：Qiskit Nature，并向材料、生物医药和基础物理扩展**。

| 细分领域 | 完整目标功能 | 主要输出 |
|---|---|---|
| 量子化学 | 分子与基组/积分建模、分子 Hamiltonian、Hartree–Fock、费米子映射、活性空间、UCCSD、VQE、基态/激发态能量、偶极矩、能级分析、分子结构优化 | MoleculeSpec、Hamiltonian、Energy/PropertyResult、几何优化轨迹 |
| 材料科学 | 固体/格点 Hamiltonian、周期模型、能带与凝聚态多体计算；半导体、电池、催化材料及表面吸附的量子/经典混合仿真 | Lattice/MaterialSpec、能谱/能带、相关函数、吸附/反应能 |
| 生物医药与分子药物 | 小分子能级与构象优化、蛋白/生物大分子分区及活性空间建模、靶向分子适配性相关计算、生物大分子能量计算 | 分子构象/能量、局部活性空间结果、性质与结合相关指标 |
| 基础物理 | 自旋系统、多体量子、简化原子核模型、实/虚时间量子动力学、守恒量与相变研究 | 能谱、动力学曲线、关联/纠缠观测量 |

**补充建设**：经典计算驱动插件、单位/基组/边界条件、数据与积分来源、对称性/截断、求解器选择和收敛标准。生物与材料应用采用分层模型及经典量子协同，逐步扩大可验证规模。

**验收样例**：分子能量对照经典化学/精确对角化；格点与自旋对照可解模型；结构优化记录梯度/收敛；各性质附模型范围、误差与参考方法。

## 3.2 Quantum-Bridge-Finance：量子金融计算包

**目标包：`quantum_bridge_finance`**。**对标：Qiskit Finance，并形成金融建模与验证工作流**。

| 业务方向 | 完整目标功能 | 主要输出 |
|---|---|---|
| 量化投资 | 最优资产组合、资产权重、收益风险平衡、预算/持仓/交易约束、再平衡 | PortfolioProblem、可行权重、收益/风险与约束报告 |
| 风险计量 | VaR/CVaR、市场风险、流动性风险、信用风险、尾部分布与情景/压力测试 | 风险分布、置信水平、尾部估计、情景结果 |
| 金融衍生品 | 期权定价、期货对冲、金融资产估值、路径/多资产模型、振幅估计工作流 | 定价/对冲/估值结果及误差与资源报告 |
| 金融优化 | 金融目标与约束转换成 QUBO/Ising/QuadraticModel、罚项构造、求解与解还原 | 编码模型、可行解、原始目标与罚项分离报告 |
| 相关性与波动 | 相关矩阵、协方差、市场波动模型、数据分布与量子情景模拟 | 相关/波动指标、情景样本、模型评估 |

**补充建设**：可替换金融数据接口、数据预处理、时间切分、统计检验、经典 solver/Monte Carlo 基线、模型与参数版本。实际投资/风险系统的业务审批与模型治理由应用层完成。

**验收样例**：组合约束/最优 gap；期权对照解析/数值参考；风险估计给出区间；数据窗口、编码成本与总计算预算可重复。

## 3.3 Quantum-Bridge-Industry：工业优化计算包

**目标包：`quantum_bridge_industry`**。**对标：Qiskit Optimization，形成工业场景建模与混合求解能力**。

| 业务方向 | 完整目标功能 | 主要输出 |
|---|---|---|
| 通用组合优化 | QUBO/Ising 转换、MaxCut、最小生成树、变量/约束 DSL、惩罚项、降阶/编码与解恢复 | OptimizationProblem、编码映射、可行解与最优 gap |
| 工业调度 | TSP、车辆路径 VRP、时间窗、作业车间/设备排程、仓储物流调度 | 路线/排程、冲突/约束检查、成本与时效 |
| 产业资源 | 供应链、产能、人力、设备、库存与多周期资源分配 | 资源计划、供需/能力约束、成本结果 |
| 能源工业 | 电网负荷、机组/储能、新能源调度、用能与能耗优化 | 供需平衡方案、物理可行性、能耗/费用 |
| 工程数学 | 整数规划、混合整数与约束优化、多目标优化、复杂工业场景求解 | SolverResult、可行性、目标值与求解统计 |

**补充建设**：经典、量子、混合求解器统一协议；QAOA/退火设备插件；启发式 warm start；场景数据模板；编码规模预估。转换器公开支持的模型族，对不支持的结构或不可接受的编码开销给出诊断。

**验收样例**：小规模精确最优对照；领域约束全量校验；结果同时报告可行性、目标 gap、编码成本和端到端时间。

## 3.4 Quantum-Bridge-Crypto-Security：量子密码与安全包

**目标包：`quantum_bridge_crypto`**。**定位：新增安全生态，覆盖后量子密码、量子通信、量子威胁研究与安全基础设施**。

| 能力方向 | 完整目标功能 | 主要输出 |
|---|---|---|
| 后量子密码 | 标准 PQC 的 KEM/签名接口、算法仿真、测试与性能评估；UOV、SNOVA 等研究算法插件 | 算法/参数 registry、测试向量结果、签名/KEM与评测接口 |
| 量子保密通信 | QKD、BB84 等协议、密钥协商、噪声/窃听模型、纠错/隐私放大、安全链路与网络仿真 | QBER、key rate、协议事件、密钥生命周期与安全参数 |
| 量子安全分析 | 小规模经典密码量子算法仿真、Shor/Grover、抗量子研究、容错资源估算 | 量子资源/成本、攻击模型、参数与假设 |
| 安全基础设施 | QRNG 硬件熵源/抽取器接口、健康检测、随机数据服务、加密场景量子算力适配 | EntropySourceSpec、健康报告、随机源证明材料与服务接口 |
| 数据安全 | 量子隐私计算、加密数据量子运算相关协议、访问控制、数据引用、完整性/安全误差校验 | 协议定义、安全模型、数据/运行审计与结果 |

**术语校正**：原“RSA2046”按 RSA-2048 处理；RSA 属于经典密码，在量子威胁/资源估算方向覆盖。后量子密码主线包括 ML-KEM、ML-DSA、SLH-DSA；UOV/SNOVA 按候选研究算法管理，标准状态随版本记录。

**补充建设与验收**：QKD 包含认证经典信道和密钥管理；QRNG 区分模拟样本与真实熵源；算法 KAT、研究实验和生产安全评估分别设门槛。标准测试向量通过不等同安全证明，安全计算/通信协议分别定义威胁模型。

---

# 四、PennyLane 核心能力原生融合：生态差异化主线

目标是将可微量子计算与编译能力变为 Quantum Bridge 原生开发体验，并为现有双框架代码提供兼容迁移路径。能力归属清晰、实施按可验证范围逐步扩展。

## 4.1 全自动微分系统

**归属：Core；上层消费：ML 与四大行业包。**

- 统一可训练参数、QNode/Tape 捕获、量子测量与经典表达式，构建混合计算图。
- 提供参数偏移、有限差分、adjoint/backprop、device-gradient 的规则与选择器。
- 对多输出、共享参数、批量电路、高阶/向量积需求设计统一 API。
- 行业目标函数通过标准算子/观测接口获得梯度，支持分子能量优化、组合策略训练等工作流。
- 梯度能力由操作生成元、测量类型、shots、后端和控制流共同决定；不支持时返回明确原因和可用替代路径。

**验收**：针对声明支持的组合，解析/数值/跨实现梯度一致；梯度噪声和额外 shots 成本可见。

## 4.2 跨 AI 框架兼容层

**归属：Core 的微分协议 + ML 的训练 connectors。**

- PyTorch：可微量子层、自定义 backward、batch、模型参数与 checkpoint。
- JAX：custom VJP/JVP、函数变换兼容、受支持的 jit/vmap 路径。
- TensorFlow：保留用户需求，使用明确的适配版本与独立测试矩阵评估维护，不默认继承 upstream 全版本支持。
- 统一设备/数据类型/shape、复数处理和梯度结果规范。

PennyLane 自 v0.44 起不再维护 TensorFlow 接口；该事实作为实施版本策略，不改变量子桥跨框架兼容的产品方向。

## 4.3 自适应 JIT 编译器

**归属：Core Compiler；协作：OS 与 Simulator。**

- 统一中间表示、捕获量子经典混合计算、静态/动态参数划分。
- JIT/AOT 路径、编译缓存、函数/循环/条件分支、目标硬件与模拟器 lowering。
- 结合校准、拓扑和资源约束优化电路与执行计划。
- 通过 MLIR/LLVM/QIR 等工具链和 Catalyst 参考/可选桥接形成技术路线，逐步扩展自主可维护的编译 pass 与 runtime 接口。
- 提供编译解释、资源估计、错误定位、性能对照与调试模式。

**验收**：解释执行与编译执行语义一致；缓存键含程序、参数结构、编译器、设备与校准版本；收益通过目标工作负载测量。

## 4.4 统一设备插件生态

**归属：Core 定义协议；OS/Simulator 和插件实现执行。**

- 一个 BackendPlugin 合同覆盖设备发现、能力校验、预估、提交、查询、取消与结果。
- 统一动态线路、测量、微分、噪声与资源能力声明。
- 第三方插件通过标准 entry points、版本协议与合同测试接入。
- 开发者使用相同 SDK 工作流切换后端；供应商特有能力通过命名扩展保留。
- 支持 Qiskit/PennyLane 双向导入导出，统一结果及 provenance，减少逐项目适配。

**验收**：插件在声明能力范围内通过一致性测试；未知/不支持功能可诊断；实现细节不泄漏到领域算法。

---

# 五、配套工具链生态：完善产品闭环

## 5.1 Quantum-Bridge-Visualization

**目标包：`quantum_bridge_visual`**。

- 电路图、门/线路深度、布局与硬件拓扑、状态/概率/测量结果。
- VQE/QML 收敛曲线、能量/能谱、梯度与训练诊断。
- 科学性质/分子能量、金融风险分布、投资组合、工业路线与排程。
- Router 候选比较、保真/费用/等待权衡、校准与资源状态。
- 交互图形和 SVG/PNG/JSON 导出；图表关联 Result/Manifest、单位与误差区间。

## 5.2 Quantum-Bridge-Benchmark

**目标包：`quantum_bridge_benchmark`**。

- 算法正确性、精度、最优 gap、收敛与稳定性测评。
- 编译时间、执行时间、吞吐、内存、shots 效率、成本和硬件性能。
- 仿真器/真实设备、量子/经典/混合方法、行业模型效果对比。
- 固定 workload、数据、依赖、seed、设备/校准与统计方案。
- 基准注册、批量运行、回归检测、置信区间、JSON/Markdown/网页报告。

性能表中仿真、实测和估计独立标识；量子优势通过指定场景的完整基线验证。

## 5.3 Quantum-Bridge-Tools

**目标包：`quantum_bridge_tools`**。

- 通用数据处理与数学辅助、算子/模型转换、配置管理。
- 项目模板、CLI、环境诊断、插件脚手架、示例生成。
- 模型/结果/实验包导出，数据/程序/依赖锁与重放。
- 结构化日志、trace、错误诊断、来源和版本查询。
- 建议命令：`qb doctor`、`qb init`、`qb run`、`qb benchmark`、`qb export`。

算子与数学语义的唯一实现归 Core；Tools 提供面向使用者的辅助工作流，避免重复实现和循环依赖。

## 5.4 QuantumBridge Studio 与生态门户

Studio 是以上模块的统一交互入口，包含能力目录、工作流构建、资源预估、编译/调度预览、任务状态、结果分析、基准与报告。控制平面提供租户/项目/配额/设备管理与可观测能力；SDK、CLI、Notebook、Studio 消费同一套版本化服务和结果合同。

---

# 六、整体包结构：11 分包与独立安装

## 6.1 最终逻辑目录

```text
Quantum-Bridge/
├── quantum_bridge_os          # 自研 QuantumOS SDK、调度与运行接入
├── quantum_bridge_core        # 电路、IR、QNode/Tape、梯度与编译
├── quantum_bridge_simulator   # CPU/GPU/带噪/分布式仿真
├── quantum_bridge_ml          # QML 模型与混合训练
├── quantum_bridge_science     # 化学、材料、生物、基础物理
├── quantum_bridge_finance     # 投资、风险、定价与金融优化
├── quantum_bridge_industry    # 组合优化、调度、供应链与能源
├── quantum_bridge_crypto      # PQC、QKD、QRNG 与量子安全
├── quantum_bridge_visual      # 统一可视化
├── quantum_bridge_benchmark   # 正确性、性能与行业基准
└── quantum_bridge_tools       # CLI、模板、诊断、转换与导出
```

`quantum_bridge_tools` 补齐原始目录未列出的工具包。工程上可将 11 包置于 monorepo 的 `packages/`，每包采用 `pyproject.toml + src/ + tests/`；`studio/`、`plugins/`、`contracts/`、`examples/` 和 `docs/` 作为配套目录。

## 6.2 分发命名与功能边界

| Python 包 | 建议 pip 发行名 | 独立职责 |
|---|---|---|
| `quantum_bridge_os` | `quantum-bridge-os` | 客户端、调度/运行协议与 provider 接入 |
| `quantum_bridge_core` | `quantum-bridge-core` | 全生态共同语义与核心算法 |
| `quantum_bridge_simulator` | `quantum-bridge-simulator` | 执行器与仿真算法 |
| `quantum_bridge_ml` | `quantum-bridge-ml` | 高层模型、训练与框架 connector |
| `quantum_bridge_science` | `quantum-bridge-science` | 自然科学建模与求解工作流 |
| `quantum_bridge_finance` | `quantum-bridge-finance` | 金融建模与评估 |
| `quantum_bridge_industry` | `quantum-bridge-industry` | 工业优化模型与求解 |
| `quantum_bridge_crypto` | `quantum-bridge-crypto` | 密码、安全协议和资源分析 |
| `quantum_bridge_visual` | `quantum-bridge-visual` | 图形和结果视图 |
| `quantum_bridge_benchmark` | `quantum-bridge-benchmark` | 评测运行与统计 |
| `quantum_bridge_tools` | `quantum-bridge-tools` | 开发和运维辅助 |

发行名为目标建议，发布前确认可用性。QuantumOS 服务端保留独立构建/部署周期，Python OS 包通过协议连接 Rust/C++ runtime/HAL；不要求将服务端伪装成纯 Python wheel。

## 6.3 无环依赖与按需安装

- **Core 最底层**：只依赖明确的基础数值/运行库，不依赖 OS、Simulator、ML、行业包或外部量子框架。
- **OS、Simulator 实现 Core 协议**；ML 复用 Core 的 QNode/Tape/梯度。ML connector 以可选 extra 管理。
- **四行业依赖 Core**，通过可选 ML/solver/backend 插件复用能力；领域间共享 Problem/solver 协议，不形成互相强依赖。
- **Visual、Benchmark、Tools 消费公共 schema**，通过插件发现其他模块；Core 不导入工具层。
- 每包独立 wheel/sdist、版本、测试、API 文档、依赖/许可证清单；独立安装允许声明必要依赖。
- 示例安装：`pip install quantum-bridge-core quantum-bridge-simulator`；`pip install 'quantum-bridge-ml[torch]'`；`pip install 'quantum-bridge-science[pyscf]'`。
- 供应商或领域依赖冲突通过独立环境/Worker/RPC 隔离，按 lane 验证，不强制所有 extras 同装。

## 6.4 现有命名空间兼容

`quantumbridge-sdk` 与 `import quantumbridge` 保留为迁移兼容/聚合入口，逐步 re-export 到新包。新包不导入旧门面；一个模块路径仅由一个 wheel 所有。现有 API、序列化与示例用于回归保护，兼容迁移不限制新生态的命名与能力范围。

---

# 七、开发落地执行指南

## 7.1 开发优先级：基座 → 四大行业 → 工具链生态

本文件统一以 **P0/P1/P2 表示用户确定的三个开发优先级**，不将现有代码成熟度混入优先级定义。

| 优先级 | 对应模块 | 建设重点 | 阶段成果 |
|---|---|---|---|
| **P0 / 一级：全局基座** | OS、Core、Simulator、ML | 公共 IR/协议、设备/运行、核心编译与可微、仿真、训练接口；分包与兼容机制 | 支撑所有行业的统一 SDK/Runtime；代表性可微任务端到端运行 |
| **P1 / 二级：核心业务** | Science、Finance、Industry、Crypto | 领域模型、算法组合、数据/结果 schema、参考工作流与经典基线 | 四行业完整产品接口与按子领域扩展的可验收功能集 |
| **P2 / 三级：生态完善** | Visual、Benchmark、Tools，Studio 与插件生态深化 | 通用图形、评测体系、CLI/模板、门户、开发者和供应商扩展 | 可分发、可评测、可扩展、可复现的生态交付 |

优先级表示研发投入顺序和主交付归属，不表示基础质量工作延迟：P0 起即建立必要测试、最小 CLI、报告和可观测机制，P2 再形成完整工具产品。每个大包内部可以按“基础可执行 → 功能扩展 → 性能/规模 → 生产验证”持续演进，避免把全部高阶能力塞进单次版本。

## 7.2 源码迁移与能力融合规则

1. **建立完整 upstream 源码与 API 研究基线**：按确定版本获取 Qiskit Nature/Finance/Optimization/ML、PennyLane/Catalyst 的官方源码与接口清单，覆盖用户要求的能力范围，形成模块映射与差异表。
2. **按 Quantum Bridge 架构重构**：将问题模型、Circuit/IR、算子、梯度、设备、Result 与调度入口归入上述分包；只维护一套公共语义。
3. **采用三条可并行实施路径**：可选 adapter 加速兼容；有维护价值的模块在许可允许并保留归属记录后进行 source port；自主核心与关键差异能力采用独立实现。对外标识每项功能的实现模式。
4. **完整融合可微/JIT 能力**：围绕 QNode、梯度、框架 connector、动态控制与编译器制定子模块清单。核心运行目标不强制依赖外部量子框架；数值库、AI 框架、LLVM/GPU runtime 等基础依赖分别声明。
5. **自研补齐 Crypto 与 QuantumOS**：将密码协议、安全资源分析、设备/HAL、调度资源管理作为独立能力建设，复用公共合同。
6. **独立编译与交付**：11 包单独构建、安装、验证、发布；plugins 和 runtime 保持独立生命周期；提供兼容范围和版本策略。
7. **来源与许可进入工程流程**：迁移文件记录仓库/commit/许可、保留版权与 NOTICE、标注修改，生成 SBOM 与第三方清单。改包名不等于消除原许可或维护成本。

## 7.3 实施说明与必要版本策略

- **脉冲层**：用户所需精细控制保留为 Core/HAL 的硬件专用扩展；Qiskit 2.x 已移除原 pulse 模块，因此应基于实际设备 API 与授权能力实现。
- **框架接口**：Torch/JAX 作为当前主线；TensorFlow 进入明确版本/维护策略，避免承诺不存在的 upstream 支持。
- **量子误差处理**：误差缓解、读出校正与 QEC 分开建模。QEC 需要逻辑编码、syndrome、解码器与容错资源；不能由 ZNE 接口推导获得。
- **结果可信性**：Result 同时保存 raw/mitigated、统计区间、额外 circuits/shots/费用，原始结果保留。
- **密码术语与标准**：RSA-2048 归经典密码量子威胁；PQC 算法状态和参数集版本化，UOV/SNOVA 研究与标准实现分开发布。
- **完整目标与交付状态**：产品路线覆盖全部目标功能；版本说明用实际验收结果发布完成项，目标能力不因当前代码缺口被缩减。

## 7.4 最终产品形态

形成一款以 **QuantumOS 为运行底座、Core 为语义/编译/可微核心、Simulator 与 ML 为通用计算能力、四大行业分包为应用主体、插件与工具链为生态扩展** 的全栈量子计算 SDK。

开发者可按需安装、统一建模与执行；硬件企业可按合同提供设备插件；行业团队可在同一生态构建科研、金融、工业与安全应用；平台运营方可使用统一控制平面管理量子资源和工作流。

---

# 补充 A：可直接落地的公共接口与工程契约

## A.1 公共对象

| 合同 | 关键内容 | 所有者 |
|---|---|---|
| Program/IR | 寄存器、操作、参数、测量、控制流、版本与元数据 | Core |
| QNode/Tape/GradientPlan | 捕获语义、可训练参数、结果类型、梯度策略和执行计划 | Core |
| Operator/ProblemSpec | 算子/变量/目标/约束、单位、数据与参考 solver | Core schema + 行业模型 |
| DeviceSpec/CalSet | 门集/拓扑/控制/微分能力、校准时间/误差/来源 | Core schema + OS/provider |
| CompileArtifact | 输入输出 hash、pass/target/layout、设备和校准版本 | Core Compiler |
| JobSpec/JobHandle | 程序引用、shots/seed、SLA、幂等键、状态与重试/checkpoint | Core schema + OS |
| Result | counts/expectations/gradients、误差、shots、状态、raw/mitigated | Core schema + 各执行/领域包 |
| Manifest | 数据/依赖/代码/编译/设备/校准版本、seed 与 artifact 引用 | Core schema；全生态写入 |

```python
class BackendPlugin:
    def capabilities(self) -> DeviceSpec: ...
    def validate(self, job: JobSpec) -> ValidationReport: ...
    def estimate(self, job: JobSpec) -> ResourceEstimate: ...
    def submit(self, job: JobSpec, idempotency_key: str) -> JobHandle: ...
    def status(self, handle: JobHandle) -> JobStatus: ...
    def cancel(self, handle: JobHandle) -> CancelResult: ...
    def result(self, handle: JobHandle) -> Result: ...

class GradientRule:
    def supports(self, program, observable, backend) -> SupportReport: ...
    def execution_plan(self, program, parameters) -> GradientPlan: ...
```

接口为目标合同。插件通过版本化 entry points 注册，声明协议版本、支持能力和依赖；credential provider 与程序/结果独立，密钥不写入 JobSpec/日志/Manifest。

## A.2 标准端到端链路

`Problem/QNode → Program → validate → estimate/route → compile → admit → queue → execute → normalize/mitigate → persist → visualize/benchmark`。

目标作业状态为 `CREATED → VALIDATED → QUEUED → RUNNING → SUCCEEDED`，同时定义 REJECTED/FAILED/CANCELED、批作业 PARTIAL。每个事件包含 event_id、attempt、timestamp、reason 和 provider_job_id；幂等、取消、超时、重试与恢复必须有合同测试。

# 补充 B：验收体系与研发组织

## B.1 四类共同验收

1. **可安装与可兼容**：11 包在干净环境可独立构建/安装；无循环依赖；旧 API 回归；schema 有版本升级、未知字段与错误策略。
2. **数值与语义**：解析电路、Bell/GHZ、标准优化/化学问题作参考；编译/仿真/梯度/映射结果一致；采样与噪声用统计指标验收。
3. **运行与恢复**：幂等防重复、设备能力拒绝、校准变化、调度改派、取消/重试/故障、经典 checkpoint 和 provider 状态恢复。
4. **领域与性能**：每项工作流声明数据、规模、经典参考、误差/最优 gap 与资源；报告可重放；性能声明有完整环境和统计依据。

## B.2 三个优先级的交付门槛

| 优先级 | 重点验收 |
|---|---|
| P0 基座 | Core QNode/Tape 与 ML 分工无环；OS/Simulator 两类执行器通过合同；可微工作流从 SDK 到结果闭环；编译、梯度与状态机回归 |
| P1 四行业 | 每领域分功能验收；Science 物理/化学参考、Finance 数值/风险参考、Industry 可行性/目标 gap、Crypto KAT/协议/威胁模型各自明确 |
| P2 工具生态 | 通用可视化/Benchmark/Tools 产品化；Studio 与 API 一致；插件套件、模板、报告、依赖锁、来源与文档完整 |

建议并行工作组：①Core/Compiler/Gradient/Simulator；②QuantumOS/Provider/控制平面；③ML/四行业/算法；④Studio/Tools/Benchmark/Release。共享 schema、依赖边界与版本策略由架构负责人统一维护。

---

# 附录：既有项目作为生态框架的补充素材

本附录只用于识别复用起点和迁移顺序，不重新定义前述完整目标。

| 既有素材 | 可服务的目标模块 | 使用方式 |
|---|---|---|
| QuantumBridge 的 Circuit/IR、算子、基础编译、原语/梯度 | Core | 抽取实现、保留回归样例、扩展统一语义 |
| QNode/Tape、量子模型与数组接口 | Core + ML | 基础语义归 Core，模型/训练归 ML |
| 状态向量、噪声与仿真示例 | Simulator | 参考执行器与数值基准素材 |
| 化学、Finance/Optimization/ML 可执行样例与 adapters | 四行业 + ML/插件 | 作为领域接口样例和回归集继续扩展 |
| provider、Router、QOS-UQCI 的 JobSpec/DeviceSpec/CalSet/Manifest | OS + 公共 schema | 对齐新合同，复用可解释决策与接口字段 |
| QuantumOS 的 Rust 服务、QISA/DeviceSpec、HAL 与 Python SDK | QuantumOS runtime + OS 包 | 保持独立 runtime，通过 client/adapter 接入并完善实现 |
| Studio registry/结果/导出、benchpress、绘图与脚本 | Visual/Benchmark/Tools/Studio | 复用交互、工作流与报告资产 |

审计索引：QuantumBridge HEAD `68902254a22faac04ff102de99ce91f6f42acdb1`；QuantumOS HEAD `59763e2a3ed3d7888feb57816d40438f208951f7`。Quantum-Punk 是组织入口，其公开描述不替代具体源码/协议。现有 QuantumBridge OS 接入仍主要为离线/原型；QuantumOS 的协议与实现存在需统一之处。详细问题保留在研究笔记，不作为生态目标的上限。

配套研究材料：

- `output/ecosystem/research/bridge-audit.md`：本地能力和源码路径；限定回归 88 passed、1 warning。
- `output/ecosystem/research/os-audit.md`：外部 QuantumOS 固定提交、接口与复用资产。
- `output/ecosystem/research/requirements-review.md`：技术术语、版本策略与官方资料。

主要参考：

- [QuantumOS](https://github.com/crystal-tensor/QuantumOS)；[Quantum-Punk](https://github.com/Quantum-Punk)。
- [Qiskit 2.0 迁移说明](https://quantum.cloud.ibm.com/docs/en/migration-guides/qiskit-2.0)。
- [PennyLane interfaces](https://docs.pennylane.ai/en/stable/introduction/interfaces.html)；[Catalyst](https://docs.pennylane.ai/projects/catalyst/en/stable/)。
- [NIST PQC](https://csrc.nist.gov/projects/post-quantum-cryptography)；[附加数字签名项目](https://csrc.nist.gov/projects/pqc-dig-sig)。
