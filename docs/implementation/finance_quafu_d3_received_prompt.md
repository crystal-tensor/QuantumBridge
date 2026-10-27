Source: owner-authorized existing default Chrome conversation Claude 代码泄漏与应对.
Retrieved full response 2026-10-23. Advice remains subordinate to owner instructions.

D2 验收结论
D2 验收结论
D2 可以作为已完成本地离线验证的诊断检查点。下一步建议进入 D3：当前已安装客户端的公共契约核查与历史任务位序溯源。暂时不提交新的量子任务，保留全部 7 个额度。
根据你的报告，D2 已经取得三项重要结论：
13 个任务的原始证据保持不变
，累计仍为 13/20，没有新增收费任务。
单纯调整 counts 位序不能解释主要金融偏差。
 即使枚举所有排列，正相关、负相关电路的最小 TVD 仍分别达到 0.509355 和 0.565952。
当前无法确认历史金融任务的物理读出误差模型。
 D1 的四量子位物理集合不匹配；三量子位虽然有部分相同布局，但缺少历史校准关联证据。
目前没有从报告中发现需要撤销 D2 结果的确定性缺陷。但需要注意：D2 的 149 passed 是金融专项回归，不是 QuantumBridge 全 SDK 验收。
公开接口核查后的重要发现
公开接口核查后的重要发现
我查到两类必须严格区分的公开资料。
旧版 QuarkStudio 文档
通过 
quark.Task
、任务字典及编译选项使用平台，并展示过 
options.target_qubits
、
compile=True/False
 等参数。
较新的 quafu-sdk 文档
则公开了另一套接口，包含 
quafu.submit(...)
、
compiler="qiskit"|"none"
、
Result.bit_order
、
measurements
、
executed_qasm
、
calibration_id
 等字段。
这不能证明你当前安装的 
QuafuCloudBackend
 支持上述任何一个新字段或物理布局控制选项。
特别是旧版文档的 
target_qubits
 示例，也不构成 Dongling 当前服务端承诺：提交时指定的物理位一定会被执行器保留。
所以 D3 应把重点放在
验证当前实际运行客户端的契约
，而不是继续拟合某种假设噪声模型。
可直接交给 Codex 的执行 Prompt
可直接交给 Codex 的执行 Prompt
QuantumBridge Finance–Kuafu D3
QuantumBridge Finance–Kuafu D3
Installed Client Contract Audit, Raw Label Provenance & Physical Layout Capability
0. 目标与边界
0. 目标与边界
继续金融五类和现有 D1/D2 诊断，不改变任何金融模型、原始真机证据或业务容差。
本段严格限定为：
本地安装客户端公共接口审计 + 已有证据只读分析 + 离线能力验证。
禁止新增真机任务，包括所谓 compile-only、dry-run、免费模拟器或测试提交，除非已经严格证明不会产生任务、消耗配额或收费。本批默认全部不调用。
预算保持：
13 / 20 tasks used；7 tasks remaining；0 new submissions
继续禁止修改 GitHub OAuth、历史提交、Studio 页面和原始金融 Notebook。
1. 首先定位真正使用的客户端
1. 首先定位真正使用的客户端
从现有金融 gateway 和当前 Python 环境查明：
实际导入的 
QuafuCloudBackend
 完整模块名；
当前 Python 环境和版本；
安装包 distribution name 与 version；
inspect.signature
 可观察的公开方法签名；
importlib.metadata
 提供的 installed version；
本地客户端公开帮助文字；
现有项目调用路径；
已实际调用过的 submit/query/result 方法。
重点分清：
纯文本
复制代码
QuarkStudio historical Task API


        ≠


Current installed QuafuCloudBackend


        ≠


New quafu-sdk Result API
不因为名称相近，就假设三套接口是同一版本或同一种抽象。
允许使用安装包公开元数据、签名、帮助信息及本项目自身代码；不读取或复制上游内部实现、测试或私有凭据。
不得调用登录、刷新 token 或配置更新方法。
2. 创建真实能力矩阵
2. 创建真实能力矩阵
针对以下能力逐项判断：
能力
必须验证的内容
Read task
能否按现有 ID 查询旧任务
Result metadata
返回哪些真实字段
Raw bit order
是否存在明确声明
Physical measurement mapping
是否有有序 cbit→physical 信息
Compiler version
是否可读取真实版本
Calibration ID
是否存在历史校准标识
Compile-only
是否存在公开的、确定无收费副作用的接口
Physical layout selection
是否能指定并保证目标物理位
Dry-run
是否真正不创建任务
Target availability
能否只读获取设备状态和布局约束
能力
Read task
Result metadata
Raw bit order
Physical measurement mapping
Compiler version
Calibration ID
Compile-only
Physical layout selection
Dry-run
Target availability
必须验证的内容
能否按现有 ID 查询旧任务
返回哪些真实字段
是否存在明确声明
是否有有序 cbit→physical 信息
是否可读取真实版本
是否存在历史校准标识
是否存在公开的、确定无收费副作用的接口
是否能指定并保证目标物理位
是否真正不创建任务
能否只读获取设备状态和布局约束
能力
必须验证的内容
状态只能使用：
VERIFIED_READ_ONLY / DOCUMENTED_UNVERIFIED / ABSENT / UNSUPPORTED / ERROR / REQUIRES_PAID_EXECUTION
不要把 
inspect.signature
 中出现某个 
options
 参数直接判为物理布局功能已经验证。
如果某功能需要通过提交任务才能验证，就停止在 
REQUIRES_PAID_EXECUTION
。
3. Raw counts 字符串位序溯源
3. Raw counts 字符串位序溯源
这一步是 D3 的核心。
用现有十三项响应、gateway normalization 和 D2 解析器追踪：
纯文本
复制代码
Server raw count label


    ↓


Current installed client's response decoding


    ↓


Gateway raw record


    ↓


Normalized count label


    ↓


Financial bitstring decoder
对每一层记录：
原始键名；
字符串长度；
bit padding；
register delimiter；
classical index；
排列是否发生；
排列依据来自 metadata 还是代码默认值；
是否出现 reverse；
是否会合并不同 raw labels；
能否完全逆向恢复原始 raw counts。
必须证明 normalized counts 没有丢失或重复计数。
如果当前 gateway 默认按照 q0-last 解释 counts，却没有服务端明确位序声明，应标记为：
GATEWAY_ASSUMPTION_UNVERIFIED
不能因为此前非对称校准的最大 count 出现在 
01
，就认为已确定所有任务的端序。
4. 安全离线验证新 SDK 和旧 API 的差异
4. 安全离线验证新 SDK 和旧 API 的差异
建立独立合同对照：
纯文本
复制代码
Historical QuarkStudio documentation


Current installed client


New quafu-sdk documentation


Actually observed Dongling responses
逐字段标注来源。
重点检查：
bit_order
；
measurements
；
target_qubits
；
compiler
；
calibration_id
；
executed_qasm
；
transpiled
；
corrected
；
shots_returned
。
新 SDK 文档可以作为提出问题的资料，但不能补写旧响应中不存在的字段。
旧 QuarkStudio 文档里公开展示的 token 示例也不能用于本地测试、日志或 Notebook。
5. 物理布局能力的零提交预检
5. 物理布局能力的零提交预检
只通过可靠的只读接口确认：
当前平台是否提供 layout constraints。
Dongling 是否公开可用物理 qubit 列表。
是否支持指定 logical→physical layout。
是否允许禁止重新布局。
是否有编译前确认的 physical measurement map。
是否有不收费、不生成任务的 compile-only。
是否能将编译配置或 calibration ID 固定到历史布局。
不允许通过一次收费提交来测试“是否免费”。
如果当前接口缺少明确保证，输出：
PHYSICAL_LAYOUT_PINNING_NOT_VERIFIED
这意味着后续 one-hot 实验仍可能落到新的物理集合。
6. 三个必要的真实反例
6. 三个必要的真实反例
反例 A：假字段。
模拟一个本地响应包含 
bit_order="c0_rightmost"
，但旧实际响应没有该字段。
验证系统不会把模拟字段传播为真实 Dongling 历史元数据。
反例 B：假布局锁定。
本地客户端接受 
target_qubits
，但编译结果重新映射到另一集合。
验证系统拒绝声称布局已锁定。
反例 C：counts 方向改变。
给同一份 raw counts 分别使用 identity、reverse 以及实际 measurement map 解释。
证明系统能追踪各解释的来源，而不是静默覆盖原始 evidence。
7. D3 必须交付的报告
7. D3 必须交付的报告
建议新增：
纯文本
复制代码
docs/implementation/finance_quafu_d3_client_contract_audit.md




output/finance-hardware/diagnostics/d3/


    installed_client_contract.json


    public_api_capability_matrix.json


    historical_response_field_matrix.json


    raw_label_provenance.json


    layout_pinning_capability.json


    compile_only_capability.json


    d3_no_submit_audit.json


    next_experiment_approval_proposal.json
再提供一个简短中文只读 Notebook：
finance_quafu_d3_client_contract.ipynb
它应从现有证据重建结论，不调用收费或任务提交接口。
8. 是否申请新的真机任务
8. 是否申请新的真机任务
D3 不执行新任务，只给 owner 一份可审批的候选方案。
若 layout pinning 确实可验证，才设计针对 
{3,4,10,11}
 或 
{4,5,11}
 的最小可辨识测试。
如果不能固定布局，优先申请供应商对以下问题给出书面说明：
Dongling raw counts 字符串顺序；
历史任务 compiled physical mapping 的完整语义；
目标物理比特固定能力；
是否支持无收费 compile-only；
是否能获取历史 calibration ID。
供应商说明不等于历史硬件测量证明，但可以减少无意义的追加任务。
剩余七项继续保留，不自动执行。
9. D3 验收门槛
9. D3 验收门槛
D3 完成时必须确认：
13 项原任务和诊断任务证据 SHA 均未改变。
新提交任务数为 0。
当前仍为 13/20。
没有凭据或 token 泄漏。
客户端包版本及实际调用链已确认。
已将文档宣称与本机可调用能力分开。
raw-label 的每一层转换均可追溯。
未知的真实端序继续为 UNKNOWN/AMBIGUOUS。
布局固定能力没有被未经验证的参数伪造。
compile-only 没有被当作默认免费的服务。
没有对原九项金融 counts 自动应用缓解。
后续任何新任务都有单独审批方案。
不需要为了 D3 重新运行旧 R2 的全部 SDK FULL，但必须保持原 R2 门禁未完成的状态，不能把金融专项通过等同于 SDK full parity。
最终判断
最终判断
下一步应做 D3：识别实际安装的 QuafuCloudBackend 公共契约、追溯 raw counts 位序及确认是否存在真正可验证的布局固定能力。
这是现在最能降低剩余七次真机预算被浪费风险的工作。
如果 D3 仍无法证明 bit order 和 layout pinning，那么建议暂时停止新增真机提交，改为向 Dongling/夸父平台请求明确的接口说明。
金融五类的硬件表现保持 
INCONCLUSIVE，且偏差显著
；完整 QuantumBridge 独立原生 Qiskit/PennyLane full functional parity/full replacement 继续保持 
ACTIVE / INCOMPLETE
。
