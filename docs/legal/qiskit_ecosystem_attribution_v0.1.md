# Qiskit Ecosystem Attribution v0.1

Status: Stage 7 planning  

QuantumBridge may optionally depend on Qiskit ecosystem packages such as Qiskit, Qiskit Aer, Qiskit IBM Runtime, Qiskit Finance, Qiskit Optimization, Qiskit Machine Learning, Qiskit Experiments, and Qiskit Addons. These packages remain independent upstream projects with their own maintainers, licenses, trademarks, release schedules, and support policies.

QuantumBridge Stage 7 does not vendor these packages and does not copy their source, tests, documentation, comments, or error messages. Adapter files use runtime imports, public object names, and independently written schema wrappers.

Use of package names is for compatibility, dependency, and attribution purposes only. QuantumBridge is not endorsed by IBM or the Qiskit project.

Any future source port must be recorded in `docs/migration/source_migration_ledger.md`, must preserve required notices, and must update `THIRD_PARTY_NOTICES.md`.
