from quantumbridge.compat.qiskit_aer.aer_adapter import ADAPTER as AER
from quantumbridge.compat.qiskit_core.circuit_adapter import ADAPTER as QISKIT_CIRCUIT
from quantumbridge.compat.qiskit_finance.applications_adapter import ADAPTER as FINANCE
from quantumbridge.compat.qiskit_machine_learning.qnn_adapter import ADAPTER as ML_QNN
from quantumbridge.compat.qiskit_optimization.quadratic_program_adapter import ADAPTER as OPTIMIZATION
from quantumbridge.compat.pennylane_full.operations_adapter import ADAPTER as PENNYLANE_OPS


def test_ecosystem_adapters_expose_required_contract():
    for adapter in (QISKIT_CIRCUIT, AER, FINANCE, OPTIMIZATION, ML_QNN, PENNYLANE_OPS):
        assert isinstance(adapter.dependency_available(), bool)
        assert adapter.get_upstream_version() is None or isinstance(adapter.get_upstream_version(), str)
        assert isinstance(adapter.list_public_api_inventory(), list)
        assert adapter.provenance_metadata()["source_policy"] == "optional_dependency_no_vendored_source"
