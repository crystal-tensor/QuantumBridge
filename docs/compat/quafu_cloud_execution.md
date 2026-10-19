# Quafu Cloud Execution

Status: executable adapter slice
Date: 2026-10-19

QuantumBridge 提供显式的 QuarkStudio 传输层，把已绑定参数、可导出为 OpenQASM 2 的 QuantumBridge 电路提交到夸父云。导入模块不会读取凭据或访问网络；只有构造 `QuarkStudioTransport` 或 `QuafuCloudBackend` 时才读取显式 token 或 `QUAFU_TOKEN` / `QUAFU_API_TOKEN`。

## 安装

当前 QuarkStudio 云客户端要求 Python 3.12 或更高版本。

```bash
python -m pip install -e '.[quafu-cloud]'
```

## 安全调用

```bash
export QUAFU_TOKEN='your-token-from-the-provider'
python - <<'PY'
from quantumbridge import Circuit
from quantumbridge.compat.quafu import QuafuCloudBackend

circuit = Circuit(2, 2, name="bell")
circuit.h(0).cx(0, 1).measure_all()

backend = QuafuCloudBackend("Baihua")
result = backend.run(circuit, shots=1024)
print(result.counts)
PY
```

不要把 token 写进源码、notebook、示例、测试、日志或 Git。已经在聊天或其他明文位置暴露过的 token 应在平台侧轮换。

## 当前边界

- QuarkStudio 的 `repeat` 以 1024 shots 为单位，因此 `shots` 必须是 1024 的整数倍。
- 当前云路径接受 QuantumBridge `Circuit`，要求参数已绑定，并导出项目已支持的 OpenQASM 2 子集。
- 没有测量时默认追加全量测量；可用 `auto_measure=False` 禁止。
- 返回 `QuafuBackendResult(mode="cloud_hardware")`，包含 task ID、backend、counts、probabilities、shots、QASM 摘要和来源信息，但绝不序列化 token。
- “能提交电路”不等于“所有 Qiskit/PennyLane API 都能直接在硬件运行”。经典优化器、数据处理、结果分析和某些模拟器能力仍在本地执行；只有可编译电路部分提交到硬件。
