# 夸父金融客户端契约与位序溯源

2026-10-23。D3 已完成本地公开契约核查及 13 项历史收据的离线复核，新增任务为 0。
仍为 **13/20 项、剩余 7 项**。项目侧 counts 转换没有丢失或重复计数；
实际服务端端序和固定物理布局仍未证实。金融精度仍 INCONCLUSIVE，
完整原生 Qiskit/PennyLane 替代目标仍 ACTIVE/INCOMPLETE。

## 实际客户端

真实云运行环境为 `/Users/avalok/work/showtime/.venv/bin/python`，Python 3.12.13。
安装元数据列出 `quarkstudio 7.3.9`、`quarkcircuit 0.5.13`、`pyquafu 0.4.5`；
`quafu-sdk` 未安装。`quark` 命名空间由多个发行包使用，
但实际 `quark.quafu.Task` 所在的 `quark/quafu.py` 被 `quarkstudio` 的安装文件清单登记。
不能把 quarkcircuit 或 pyquafu 的版本当作 Task 客户端版本，也不能把客户端版本当服务端编译器版本。

已实际观察的公开签名：

```text
Task.run(self, task: dict, repeat: int = 1)
Task.result(self, tid: int, timeout: float = 0.0)
Task.status(self, tid: int = 0)
```

公开对象检查还列有 backend、query、request、cancel、delete、verify。
本轮没有创建 Task 实例，也没有调用这些服务方法、登录、刷新凭据或修改配置。
只检查公开元数据、签名和首行帮助，不读取或复制上游内部实现／测试。
完整记录见 `diagnostics/d3/installed_client_contract.json`。
签名在禁用方法前采集，避免把用于禁止提交的 mock 签名当成真实公开接口。

项目真实调用链是 FinanceCloudSession → QuafuCloudBackend.submit →
QuarkStudioTransport.submit → Task.run；查询通过 QuafuCloudJob.refresh →
QuarkStudioTransport.retrieve → Task.result。shots 通过 repeat=shots//1024 传递。

## 资料边界与能力矩阵

旧 QuarkStudio 示例使用任务字典并展示 `options.target_qubits`；
这只是公开参数示例，不证明本机 adapter 支持它或 Dongling 保留指定布局。
该文档也把 `compile=False` 放在 Task.run 的执行流程中，不能据此当作免费 dry-run。
[QuarkStudio Transpiler](https://quarkstudio.readthedocs.io/en/latest/usage/code/transpiler/)

Quafu-SQC 使用说明描述 Task.run、status、result 及 count/transpiled/qlisp 返回字典。
它没有为本轮 13 项历史响应补出端序声明或历史校准 ID。
[Quafu-SQC 使用说明](https://quafu-sqc.readthedocs.io/en/latest/)

另一个未安装的 quafu-sdk 发行包自述包含 bit_order、measurements、executed_qasm、compiler、
calibration_id 等另一套结果契约；这些字段不能回填到当前旧 Task 响应。
这份发行包自述也不是对本机服务行为的独立验证。
[quafu-sdk 0.2.2 自述](https://pypi.org/project/quafu-sdk/0.2.2/)

未复制或使用任何资料中的 token 示例。能力判定与范围如下：

| 能力 | 当前证据状态 | 范围 |
| --- | --- | --- |
| 按既有 ID 读取结果 | VERIFIED_READ_ONLY | 前轮取得的 13 份 Task.result 响应；D3 不再请求 |
| 返回字段、物理测量连接 | VERIFIED_READ_ONLY | 实际 JSON 与原生解析的终端测量，不等于 raw label 排列 |
| bit_order 声明 | ABSENT | 全 13 份历史响应均未提供 |
| 编译器版本、calibration ID | ABSENT | 不以安装包版本代替 |
| 固定物理布局 | DOCUMENTED_UNVERIFIED | 文档参数已查到，本机 adapter 未暴露该参数，服务保证未验证 |
| compile-only、dry-run | UNSUPPORTED | 当前项目 adapter 无接口；整个平台能力 DOCUMENTED_UNVERIFIED |
| 设备状态与布局约束 | DOCUMENTED_UNVERIFIED | 公开方法签名存在，本轮不作活查询 |
| compile=False 后执行 run | REQUIRES_PAID_EXECUTION | 仍是任务执行路径，可能使用额度／收费；本轮没有试跑或测量费用 |

完整逐项、逐字段状态见 `public_api_capability_matrix.json` 和
`historical_response_field_matrix.json`。没有用通用 **kwargs 或 options 签名证明任何物理保证。

## Counts 逐层溯源

关键区别：保存的所谓 provider 原始结果是 **Task.result 已经解码后的 Python 响应**，
并不是原始 HTTP 字节。因此本轮不声称已证明服务端 → 客户端内部没有换序。
该段状态是 DOCUMENTED_UNVERIFIED，真实 raw-label 位序保持 UNKNOWN/AMBIGUOUS。

项目自身链路已对 13 项记录逐项验证：

1. Task.result 的顶层 `count` 与对应持久账本 raw_counts 完全相同。
2. Gateway `_extract_counts` 不改标签，没有 padding、寄存器分隔符清理或不同标签合并。
3. 8 项业务 normalized counts 对 raw counts 执行显式反转，与保存的 q0-last 假设一致。
4. 反转／identity／物理编号排序假设均为双射，可逐项逆向恢复 raw counts，shots 总数严格不变。
5. FinanceCase.analyze 使用规范化的 q0-first 索引；该约定不是服务端端序声明。

8 项业务的解码来源统一标记 **GATEWAY_ASSUMPTION_UNVERIFIED**，
而不是“服务端位序已确定”。2q 原校准和 D1 四项不是金融解码输入，单独标记。
原来的 normalized counts、金融指标和 notebook 没有覆盖，假设来源在新的独立 D3 文件中澄清。

## 反例与保护

独立离线测试覆盖：

- 模拟文档写 bit_order=c0_rightmost，而历史响应缺失：历史字段仍 ABSENT，不传播假字段。
- 本地接受 target_qubits，但 compiled 输出为另一物理集合：判 ERROR，布局仍未锁定。
- 同一 raw counts 用 identity／reverse／物理排序解释：各自记录来源、可逆且不覆盖原始证据。
- 非整数 counts、非双射排列、超宽位串、padding、分隔符、错误 normalized counts 被拒绝。
- 只读 backend 误调用 run：在检查电路或接触 transport.submit 前拒绝。

新增 gateway `read_only=True` 必须传显式 transport，不会隐式创建需凭据的客户端。
该模式不声称能约束任意自定义 transport 的内部行为。
D3 runner 另外禁用 socket connect/connect_ex、Task.run、gateway submit 和需凭据 transport 构造，
没有读取凭据。13 项证据和原五类金融结果的散列全部未变。

## 决策与待审批方案

结论为 **NO_NEW_SUBMISSION_RECOMMENDED**，固定布局状态为
**PHYSICAL_LAYOUT_PINNING_NOT_VERIFIED**。本轮申请的新增任务数为 0。
供应商问题草案已列出但没有发送：

1. Dongling raw counts 字符串位序及多寄存器顺序是什么？
2. 当前 Task.result 是否会改变服务端标签？
3. 历史 compiled physical measurement map 的精确定义是什么？
4. target_qubits 是集合约束、初始建议还是有序固定映射？如何禁止再次重布局？
5. 是否存在明确保证零任务、零额度、零收费的 compile-only 接口？
6. 能否取得原任务对应的历史 calibration ID？

供应商说明也不等于历史硬件测量证明。先取得可靠契约，再审阅 D2 的最小非对称基态计划，
给出具体 QASM、目标布局、预计成本和停止条件供 owner 决定；不自动动用剩余七项。
硬件接口未知不等于整个原生 SDK 工作无法继续；既存核心正确性问题仍待修复。

## 验证与产物

金融及全部 compat_quafu 专项：主环境、另一 SDK 环境、SDK-free 环境各 **183 passed**。
金融模块覆盖 **906/960，94.38%**，不是全仓 GLOBAL 或全 SDK 功能覆盖。
新增中文只读 notebook `finance_quafu_d3_client_contract.ipynb`：6/6 代码单元实际执行，零错误。
HTML 在 1440 和 390 像素视口检查，无页面横向溢出或 notebook 错误输出。
Ruff、diff 检查通过。完整旧 R2/FULL/matrix 门禁没有在本轮宣称通过。

全部指定 JSON 位于 `output/finance-hardware/diagnostics/d3/`；
notebook 与 HTML 位于 `output/jupyter-notebook/finance/`。
没有 commit、push、OAuth、tag、release、Studio、依赖安装或 vendor。

```bash
# 在已经安装当前 Task 客户端的云运行环境执行，默认全离线
python scripts/audit_finance_client_contract.py
# 在已有 Jupyter 依赖的环境回放，不导入云客户端
python scripts/build_finance_client_contract_notebook.py
```
