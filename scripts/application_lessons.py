# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Chinese teaching notes accompanying independently authored executable studies."""

DOMAIN_NAMES = {"science": "科学计算", "industry": "工业优化", "security": "量子安全"}

LESSONS = {
    "chemistry": {
        "title": "量子化学 · H2 的 RHF、变分能量与 Pauli 测量",
        "principle": r"""从 H-H 核坐标和氢原子 STO-3G 收缩高斯基开始，计算单、双电子积分，RHF 自洽得到轨道，再进行 Jordan-Wigner 映射。电子哈密顿量为
\(H=E_{nuc}+\sum h_{pq}a_p^\dagger a_q+\frac12\sum g_{pqrs}a_p^\dagger a_q^\dagger a_s a_r\)。
四个自旋轨道映射为四个量子比特，初态 |1100>。原生双激发门产生变分态，最小化 \(E(\theta)=\langle\psi(\theta)|H|\psi(\theta)\rangle\)。本例用确定性网格及局部细化，优化目标是本地精确态能量，不是带噪真机 VQE。

每个非平凡 Pauli 项独立测量；X 项先 H，Y 项先 S† 再 H。由对应位的奇偶性得到 ±1 样本，最后 \(\hat E=E_{const}+\sum c_j\hat P_j\)。独立电路的能量标准误为 \(\sqrt{\sum c_j^2 SE_j^2}\)。核排斥能只计入一次。""",
        "steps": [
            "设置 0.735 Å 键长和 2 个电子，构造本地分子积分与 RHF 历史。",
            "输出全部 Pauli 系数；在固定电子数扇区对角化得到经典精确基线。",
            "搜索双激发角，保存每一步角度与能量；另做键长扫描。",
            "逐项构建测量基变换，输出原生电路的 OpenQASM 2。",
            "每项采样 1024 次，合并能量及标准误，与变分值、RHF、精确值分别比较。",
        ],
        "boundary": "仅 H2 的氢原子 s 基、四模式教学体系；不代表任意元素、激发态、偶极矩或分子结构优化全覆盖。采样能量可能在统计误差内低于精确能量，这不意味着突破变分原理。键长扫描是经典参考，不是真机结构优化。",
        "interpret": "变分误差和采样误差是两个不同指标。先看 variational_gap_hartree，再看 sampled_energy_hartree 及 energy_standard_error_hartree；14 个测量电路均为本地模拟。",
        "sources": [
            (
                "PennyLane 分子量子化学概念",
                "https://docs.pennylane.ai/en/stable/introduction/chemistry.html",
            )
        ],
    },
    "biomedicine": {
        "title": "量子生物 · 四残基格点构象与接触能",
        "principle": r"""使用 HHHH 四个疏水残基的二维方格链，固定第一条键方向以消除整体旋转自由度。剩下两次转向各用两比特编码：00 左转、01 直行、10 右转，11 为非法码。
非相邻残基 0 与 3 相距一个格点时接触能为 -1。代价 \(C(x)=-contact_{03}+5\,violations\)，违反项包括非法编码和链重叠。完整枚举 16 个串独立给出最优构象基线。

将代价真值表用 Walsh 展开写成 \(H_C=\sum_S c_S\prod_{i\in S}Z_i\)。本例允许三、四体项，**不是声称所有构象都已转成二次 QUBO**。一层 QAOA 为 \(e^{-i\beta\sum X}e^{-i\gamma H_C}|+\rangle^{\otimes4}\)。Z 项相互对易，成本演化无 Trotter 分裂误差；一层表达能力仍有限。""",
        "steps": [
            "枚举两次转向，重建每个候选的四个坐标。",
            "检查链自交、编码有效性及非键接触；输出所有候选表。",
            "展开对角代价并检查罚函数最小值可行。",
            "本地理想态搜索 QAOA 参数，记录接受的改进。",
            "采样、筛选实际观测到的可行构象，报告能量差与可行率；绘制折叠形状。",
        ],
        "boundary": "这是粗粒度 HP 风格教学模型，非真实原子结构、蛋白预测、药物构象筛选或生物活性验证；没有使用患者或药物数据。",
        "interpret": "best_observed_feasible 只从实际采到的可行串中选择。optimal_probability 是最优串的采样总频率，不等同于真实蛋白折叠成功率。",
        "sources": [("二维 HP 格点模型研究", "https://arxiv.org/abs/1608.05855")],
    },
    "materials": {
        "title": "量子材料 · 两站点 Hubbard 能谱与双占据",
        "principle": r"""采用两站点、每站点两自旋的开边界费米 Hubbard 模型：
\(H=-t\sum_\sigma(a^\dagger_{0\sigma}a_{1\sigma}+h.c.)+U\sum_i n_{i\uparrow}n_{i\downarrow}\)。
模式依次为 site0 up/down、site1 up/down，Jordan-Wigner 映射到四比特。在 N=1、2、3 扇区独立对角化。
半填充基态 \(E_2=(U-\sqrt{U^2+16t^2})/2\)，双占据 \(D=(1-U/\sqrt{U^2+16t^2})/2\)。有限簇电荷隙为 \(E_3+E_1-2E_2\)，**不是周期晶体能带隙**。

选 U/t=4 的经典精确基态，使用现有原生实幅度制备电路加载，再测量 \(n_0n_1+n_2n_3\)。因此本例验证的是建模、态制备和可观测量采样，不是用量子算法求出了未知基态。""",
        "steps": [
            "构造跃迁与在位相互作用的费米算子，并映射原生 Pauli 哈密顿量。",
            "扫描 U/t=0,1,2,4,6,8，记录粒子数扇区能量、电荷隙与双占据。",
            "用解析公式交叉验证本地矩阵本征值。",
            "将 U/t=4 的经典基态振幅加载到四比特电路。",
            "对占据数采样并与解析双占据比较，给出标准误。",
        ],
        "boundary": "两站点有限簇示例，没有晶体几何、周期边界、真实半导体能带、电池或催化材料数据库；不能直接输出真实材料带隙。",
        "interpret": "interaction_sweep 展示相互作用增强时双占据下降。occupation 的 ideal_reference 应匹配解析值；estimate 的偏差属于有限 shots 采样误差。",
        "sources": [
            (
                "Qiskit Nature 格点模型定义",
                "https://qiskit-community.github.io/qiskit-nature/tutorials/10_lattice_models.html",
            )
        ],
    },
    "physics": {
        "title": "基础物理 · 三自旋动力学与 Trotter 误差",
        "principle": r"""三自旋横场模型 \(H=Z_0Z_1+Z_1Z_2+0.7\sum_iX_i\)，初态 |100>，取 ħ=1。
精确基线用 8×8 矩阵谱分解计算 \(e^{-itH}|100\rangle\)。电路使用一阶乘积公式，按 ZZ 项后 X 项执行，每步 RZZ(2t/n)、RX(1.4t/n)。记录 n=1、4、12 的动力学。

比较 \(\langle Z_0\rangle\)、\(\langle Z_0Z_2\rangle\) 及失真 \(1-|\langle\psi_{exact}|\psi_n\rangle|^2\)。有限步分裂误差与最后 1024 shots 的统计误差分别展示，不能相互抵消后宣称完全准确。""",
        "steps": [
            "明确耦合、横场、初态与时间单位。",
            "生成精确谱演化及 13 个时间点的原生电路。",
            "比较 1/4/12 步的磁化和态失真。",
            "在 t=1.5、12 步电路独立采样磁化与关联函数。",
            "输出中间曲线、最终估计、标准误及 QASM。",
        ],
        "boundary": "仅三自旋模型与小规模全态基线，不声称大规模多体、核物理模拟或量子优势；本例一阶公式与参考资料中的其他阶数应分开看待。",
        "interpret": "增加步数在本例减少末态分裂误差，但不改变给定 shots 的统计规律。先看 final_trotter_infidelity，再比较采样值与理想电路、精确演化两个基线。",
        "sources": [
            (
                "IBM 时间演化与乘积公式",
                "https://quantum.cloud.ibm.com/docs/en/tutorials/time-evolution",
            )
        ],
    },
}

LESSONS.update(
    {
        "routing-scheduling": {
            "title": "路径与生产调度 · 两作业两机器排程",
            "principle": r"""两个作业 A、B 都依次经过机器 M0、M1，每道工序时长 1。四比特分别编码 A1、B1 的开始时刻 0/1，以及 A2、B2 的开始时刻 1/2。
必须满足同作业内先后顺序，以及同一机器不得同时加工。目标是加权完工时间 \(2C_A+C_B\)，而非声称最小化所有工厂的 makespan。罚函数为 10 倍先后和冲突违反数。

先枚举全部 16 种排程作为可行性与最优值基线，再将代价对角展开并用原生 QAOA 采样。输出实际可行串对应的工序起止时间，并绘制经典最优排程的甘特图。""",
            "steps": [
                "声明工序路线、时长、时间窗和完工权重。",
                "逐候选恢复四道工序，检查先后关系和机器冲突。",
                "计算加权完工代价与罚项，枚举最优基线。",
                "训练一层原生 QAOA，输出成本 Pauli 阶数。",
                "对采样可行解解码，比较目标差、可行率和经典甘特图。",
            ],
            "boundary": "这是四工序固定路线作业车间案例；没有实现 TSP、车辆路径、复杂时间窗、设备故障或完整生产调度系统。",
            "interpret": "objective 是加权完工时间，makespan 另列。采样最优与精确最优分别呈现，不能用最频繁串替代可行性检查。",
            "sources": [
                (
                    "Google OR-Tools 作业车间约束定义",
                    "https://developers.google.com/optimization/scheduling/job_shop",
                )
            ],
        },
        "supply-chain": {
            "title": "供应链与资源配置 · 双供应商运输分配",
            "principle": r"""两供应商各有一个不可拆分货运单位，两客户各需一个单位。四个二元变量表示 S0-C0、S0-C1、S1-C0、S1-C1 的运输选择。成本矩阵为 [[2,5],[4,1]]。
目标 \(\sum c_{ij}x_{ij}\)，客户需求用 \((\sum_i x_{ij}-1)^2\) 罚项，供应容量用 \(\max(0,\sum_jx_{ij}-1)^2\) 罚项。罚系数 20，全部 16 个真值检查罚项是否足够。

这是单期匹配运输，不是库存或跨期协同。经典完全枚举提供独立决策基线；QAOA 的最终输出须恢复运输矩阵，再检查每个供应行和客户列。""",
            "steps": [
                "输入合成运输成本、两供应容量和两客户需求。",
                "枚举四条边，恢复运输矩阵和供需合计。",
                "计算运输费、缺额与超额罚项，确定最优成本。",
                "构造原生对角成本演化及混合门，优化参数。",
                "采样、还原运输矩阵并报告成本差与可行率。",
            ],
            "boundary": "单期两对两不可分割运输模型，不包含库存、缺货动态、多周期产能或真实供应链系统接口。",
            "interpret": "正确最优运输是 S0→C0 和 S1→C1，成本 3。任何低成本但客户没收到货的串都应判为不可行，不进入最终决策。",
            "sources": [
                (
                    "Qiskit Optimization 建模概念",
                    "https://qiskit-community.github.io/qiskit-optimization/tutorials/01_quadratic_program.html",
                )
            ],
        },
        "energy": {
            "title": "能源与电力优化 · 两时段机组容量承诺",
            "principle": r"""两机组容量为 2、1，两时段需求为 2、3。四比特按时段编码两台机组开关。目标为开机费用 3/2 加每次启动费用 1；初始均停机。
约束只要求可用容量至少达到需求，缺额平方罚系数 20。\(C=\sum_{t,g}c_g u_{tg}+\sum startup+20\sum_t\max(0,d_t-\sum_g P_g u_{tg})^2\)。

容量超过需求并不表示实际发电超额，因为本例没有建立出力决策；输出必须叫 available_capacity，而不能伪装成可直接下发的发电功率。""",
            "steps": [
                "设置机组容量、时段需求、开机及启动成本。",
                "逐候选计算开关状态、容量缺口和启动次数。",
                "用完全枚举检查可行性与最优开机成本。",
                "训练原生对角 QAOA 并采样候选。",
                "解码可行承诺计划，比较目标差并保留容量约束检查。",
            ],
            "boundary": "仅容量充裕度教学模型；未含 AC/DC 潮流、备用、爬坡、最小启停时间、储能或电网安全约束，不可作为真实电网调度指令。",
            "interpret": "检查 capacity_deficit 全为零后才能解释经济性。available_capacity 是可用容量，不是实际发电量；精确最优承诺成本为本模型的比较基线。",
            "sources": [
                (
                    "Qiskit Optimization 整数与约束建模",
                    "https://qiskit-community.github.io/qiskit-optimization/tutorials/01_quadratic_program.html",
                )
            ],
        },
        "combinatorial": {
            "title": "通用组合优化 · 四节点加权 MaxCut",
            "principle": r"""四个节点划入两组，跨组边权之和为割值。令 \(x_i=(1-Z_i)/2\)，单条边是否被割为 \((1-Z_iZ_j)/2\)。所以负割值是严格二次 Ising 代价：\(H_C=-\sum w_{ij}(1-Z_iZ_j)/2\)。
这一例确实是二次模型，成本 Pauli 阶数应为 2。通过原生一层 QAOA 生成候选，与所有 16 个划分的完全枚举比较；互补位串表示同一个无向割。""",
            "steps": [
                "声明四节点五条带权边。",
                "枚举割划分、计算负割代价与精确最优。",
                "校验二次 Z 展开并优化 QAOA 参数。",
                "采样并恢复节点分组。",
                "报告最佳实际观测割、最优频率和成本差。",
            ],
            "boundary": "小图 MaxCut 可执行案例，不等于图优化全部问题族或工业规模求解能力；没有性能或量子加速结论。",
            "interpret": "最优割权为 6，目标值为 -6。两组名称交换不改变割，不应误报为两个不同业务解。",
            "sources": [
                (
                    "Qiskit Optimization MaxCut 定义",
                    "https://qiskit-community.github.io/qiskit-optimization/tutorials/06_examples_max_cut_and_tsp.html",
                )
            ],
        },
        "integer-multiobjective": {
            "title": "整数规划与多目标 · 收益与排放权衡",
            "principle": r"""A、B 两类资源配置分别为 0..3，用各两比特二进制编码。资源约束 \(2A+B\le5\)，收益 \(5A+2B\)，排放 \(4A+B\)。标量代价为负收益加 λ 倍排放，λ=1.2；超资源量平方罚系数 20。

经典枚举可行解得到 Pareto 前沿：若另一解收益不低、排放不高且至少一项严格更好，则当前解被支配。QAOA 只对选定 λ 的一个标量问题采样，**不是量子算法一次求出了整个 Pareto 前沿**。不同偏好需重新求解；加权和也不保证覆盖所有离散非凸前沿点。""",
            "steps": [
                "定义整数范围、二进制编码、资源约束与两个业务目标。",
                "输出 16 个候选及可行性，经典计算非支配前沿。",
                "设 λ=1.2，构造标量罚函数和原生电路。",
                "训练、采样并还原整数 A/B。",
                "比较选定偏好下的观测目标差，同时展示经典 Pareto 图。",
            ],
            "boundary": "两变量有界整数模型；不包含通用混合整数、无限规模、多目标全部偏好或业务决策自动化。排放和利润是合成单位。",
            "interpret": "展示完整 Pareto 表和 λ=1.2 的最终决策，避免将经典枚举成果归功于量子采样。最优目标差只针对当前权重有效。",
            "sources": [
                (
                    "Qiskit Optimization 变量与约束",
                    "https://qiskit-community.github.io/qiskit-optimization/tutorials/01_quadratic_program.html",
                )
            ],
        },
    }
)

LESSONS.update(
    {
        "pqc": {
            "title": "后量子密码与迁移 · ML-KEM 与 ML-DSA 实际调用",
            "principle": r"""后量子密码在经典计算机上运行。本例调用已安装 OpenSSL 的 ML-KEM-768 密钥封装与 ML-DSA-65 签名，不自行实现格密码。
ML-KEM 接收方生成密钥；发送方用公钥封装得到公开密文和共享秘密，接收方解封装得到相同秘密。密文被修改时，隐式拒绝通常返回不同秘密而不是命令报错，因此检查的是秘密不匹配，不能把返回码 0 当成篡改通过。

ML-DSA 对合成迁移清单签名，用公钥验签，再修改清单验证拒绝。全部密钥与共享秘密只放在仅本人可访问的临时目录，完成后删除；结果只记录成功标志和公开尺寸。OpenSSL 正常随机源用于密钥与封装，没有设置测试熵或固定密码种子。""",
            "steps": [
                "确认本地 OpenSSL 支持两个算法；缺少支持时明确失败，不生成模拟密码输出。",
                "在 0700 临时目录生成 KEM 密钥，公钥封装、私钥解封装并比较秘密。",
                "修改密文，检查解封装秘密不同的隐式拒绝行为。",
                "生成 ML-DSA-65 密钥，对合成清单签名并验签。",
                "修改清单验证拒绝；记录命令状态、尺寸及临时目录删除结果。",
            ],
            "boundary": "调用实际密码实现不等于 FIPS 140 模块认证、完整系统迁移或所有 PQC 候选支持。公钥 DER 尺寸包含容器开销；不把 SPKI 尺寸误当原始公钥长度。不包含 UOV/SNOVA 插件。",
            "interpret": "共享秘密一致、合法签名接受、改动消息拒绝三个条件应同时成立。KEM 密文 1088 字节、秘密 32 字节、ML-DSA-65 签名 3309 字节；后两种安全性质仍依赖标准假设与正确部署。",
            "sources": [
                ("NIST FIPS 203：ML-KEM", "https://csrc.nist.gov/pubs/fips/203/final"),
                ("NIST FIPS 204：ML-DSA", "https://csrc.nist.gov/pubs/fips/204/final"),
                (
                    "OpenSSL 3.6 pkeyutl 接口",
                    "https://docs.openssl.org/3.6/man1/openssl-pkeyutl/",
                ),
            ],
        },
        "qkd": {
            "title": "量子保密通信 · BB84、窃听误码与纠错教学块",
            "principle": r"""Alice 随机选择比特和 Z/X 编码基，Bob 随机选测量基，公开比较基后保留一致的记录。本例固定随机种子，全部数据公开，仅用于教学。
无噪且无窃听时，筛选后的 QBER 为 0。Eve 随机选基截获并重发，有一半概率选错基，错基分支中 Bob 又有一半概率出错，所以理想截获重发 QBER 为 1/4。每个比特由原生单比特电路制备与采样，不用事先写死 25% 作为实验结果。

另演示 Hamming(7,4) 的单比特纠错：四个数据位扩成七码，异或校验给出错误位置。它不能保证纠正双错，不是完整 QKD 纠错与隐私放大协议。11% 仅作为本例的示意终止阈值，不能当成任意设备、有限密钥长度下的安全证书。""",
            "steps": [
                "运行无 Eve 与截获重发两个 1024 光子模拟场景。",
                "公开展示前 24 条基选择、接收位与筛选标志；统计筛选数与误码。",
                "比较实际 QBER 和 0/0.25 理论值，超过示意阈值中止。",
                "演示一个教学码字的单错、综合征和恢复数据。",
                "输出三个制备/测量基电路与采样结果，明确不产生生产密钥。",
            ],
            "boundary": "没有真实光链路、设备噪声校准、身份认证信道、有限密钥证明、完整纠错或隐私放大；不构成可部署 QKD 网络。公开种子与转录不能用作秘密密钥。",
            "interpret": "查看 scenarios 的筛选数、误码数和 qber，再看 eve_scenario_aborted。三个独立测量示例只解释基选择；协议统计来自前面的逐光子模拟，二者不混称同一批测量。",
            "sources": [
                (
                    "IBM BB84 与量子密钥分发教学",
                    "https://quantum.cloud.ibm.com/learning/en/modules/computer-science/quantum-key-distribution",
                )
            ],
        },
        "threat": {
            "title": "量子威胁评估 · Grover 放大与资源假设",
            "principle": r"""在 16 个候选中标记已知字符串 1011，四个搜索比特加一个工作比特。相位预言机用 X、H、Toffoli 构造；工作位计算并反计算回 |0>，没有任意稠密酉黑箱。
Grover 迭代交替使用标记相位与关于均匀态的反射。单目标情况下 \(\theta=\arcsin(1/\sqrt{16})\)，r 次迭代成功率为 \(\sin^2((2r+1)\theta)\)。记录 0..5 次的原生概率并与公式核对，最后对 r=3 的电路采样。

预言机已经包含已知答案，是算法教学而非密码攻击。3 次预言机查询不等于 3 个基础门或 3 秒；真实密码的可逆预言机、纠错、连通性和门时长均不在这个查询模型里。""",
            "steps": [
                "声明 4 比特搜索空间、已知标记态及工作位。",
                "构造基础门预言机和扩散步骤，核对工作位反计算。",
                "比较 0..5 次迭代的原生概率、解析公式与门数。",
                "对三次迭代电路采样，估计成功率与标准误。",
                "列出查询资源模型没有包含的硬件和密码代价。",
            ],
            "boundary": "未实现真实 RSA/AES 破解、Shor 大整数分解或容错资源评估。这个已知目标的 4 比特实验不能外推成真实密码被破解。",
            "interpret": "第三次迭代成功概率约 0.9613；继续迭代可能下降，图表会显示过旋转。比较查询次数必须同时说明单目标、均匀起态和理想预言机假设。",
            "sources": [
                ("Grover 原始搜索算法论文", "https://arxiv.org/abs/quant-ph/9605043")
            ],
        },
        "qrng": {
            "title": "量子随机数 · 模拟熵管线、健康诊断与提取",
            "principle": r"""本地 RY 电路产生 P(1)=0.72 的已知偏置，按固定种子保留 4096 个有序样本。必须保留顺序才能做连续重复和窗口频数诊断；不能从汇总 counts 拼出顺序。
采用 Von Neumann 成对去偏：01→0，10→1，00/11 丢弃。若输入独立同分布，01 和 10 都有概率 p(1-p)，于是输出理论上均衡，平均输出长度占输入长度比例为 p(1-p)。关联源不满足此保证。

最长重复与 128 样本窗口的阈值是**显式示意诊断阈值，不是 NIST 800-90B 认证配置**。频率接近 1/2、通过诊断或做过提取都不能证明有物理熵；确定性模拟器输出仍是伪随机。""",
            "steps": [
                "构建偏置 RY 电路并获取有序本地样本。",
                "显示原始流、最长重复与各窗口 ones 数。",
                "逐对提取并记录输出长度和偏置变化。",
                "比较计数图、理论均值与独立的 1024 shots 观测。",
                "明确物理熵声明为 false，不生成生产随机数服务或虚构真机回执。",
            ],
            "boundary": "本批没有真实硬件熵源或认证；未提供安全随机数服务。示意检测不能替代熵估计、源失效处理、设备溯源及安全认证。",
            "interpret": "中间的 4096 位有序流和最后 1024 shots 测量是不同展示对象。extracted_ones_fraction 接近 0.5 仅说明去偏效果，不表示得到安全密钥或真实量子熵。",
            "sources": [
                (
                    "NIST SP 800-90B 熵源要求",
                    "https://csrc.nist.gov/pubs/sp/800/90/b/final",
                )
            ],
        },
        "privacy": {
            "title": "数据安全与隐私 · 结果加密、访问控制与审计",
            "principle": r"""使用已安装 cryptography 的 AES-256-GCM 加密合成量子任务结果，同时认证未加密的任务上下文 AAD。每次执行新生成密钥与 12 字节 nonce，不复用同一密钥/nonce 对。
修改密文或 AAD 时，库应抛出 InvalidTag。角色表采用默认拒绝，viewer 只读、operator 可准备本地任务；角色输入不是已经实现了身份认证。

审计记录对规范 JSON、索引和前一条标签计算 HMAC-SHA256。验证端另存可信链长和尾标签，检查篡改及截断。没有外部可信锚时，单纯哈希链不能保证管理员无法截断历史；本例明确携带验证锚，并不冒充生产审计系统。""",
            "steps": [
                "创建纯合成任务结果和上下文，不接触患者、金融或账户私密数据。",
                "执行 AES-GCM 加密/解密，验证正常往返。",
                "分别篡改密文和上下文，确认认证失败。",
                "运行默认拒绝角色表并记录决策。",
                "生成带认证的审计链，用可信长度与尾标签检出改动及截断。",
            ],
            "boundary": "经典安全工程教学流程，不是量子加密、同态计算、MPC、身份服务或完整生产权限平台。密钥管理、可信锚持久化及部署安全需另行设计。",
            "interpret": "roundtrip_ok、altered_ciphertext_rejected、altered_aad_rejected、audit_tamper_rejected 均应为 true。密文长度比明文多 16 字节认证标签；密钥不写入 Notebook 或证据。",
            "sources": [
                (
                    "cryptography 46.0.7 AEAD 接口与 nonce 约束",
                    "https://cryptography.io/en/46.0.7/hazmat/primitives/aead/",
                )
            ],
        },
    }
)
