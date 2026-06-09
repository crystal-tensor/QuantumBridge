# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or IBM ecosystem packages was copied.

from quantumbridge.compat import (
    qiskit_addons,
    qiskit_aer,
    qiskit_algorithms,
    qiskit_core,
    qiskit_dynamics,
    qiskit_experiments,
    qiskit_finance,
    qiskit_machine_learning,
    qiskit_metal,
    qiskit_nature,
    qiskit_optimization,
    qiskit_runtime,
)


def test_qiskit_ecosystem_contract_coverage():
    modules = [
        qiskit_core,
        qiskit_aer,
        qiskit_nature,
        qiskit_algorithms,
        qiskit_finance,
        qiskit_optimization,
        qiskit_machine_learning,
        qiskit_dynamics,
        qiskit_experiments,
        qiskit_metal,
        qiskit_runtime,
        qiskit_addons,
    ]
    reports = [module.get_dependency_report() for module in modules]
    assert {report["ecosystem"] for report in reports} == {
        "qiskit_core",
        "qiskit_aer",
        "qiskit_nature",
        "qiskit_algorithms",
        "qiskit_finance",
        "qiskit_optimization",
        "qiskit_machine_learning",
        "qiskit_dynamics",
        "qiskit_experiments",
        "qiskit_metal",
        "qiskit_runtime",
        "qiskit_addons",
    }
    assert all(report["cloud_access"] is False for report in reports)
    assert all(report["token_read"] is False for report in reports)
    assert all(report["token_storage"] is False for report in reports)
