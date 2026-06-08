import pytest

from quantumbridge.compat.qiskit_optimization.converter_adapter import ADAPTER as CONVERTER
from quantumbridge.compat.qiskit_optimization.optimizer_adapter import ADAPTER as OPTIMIZER
from quantumbridge.compat.qiskit_optimization.quadratic_program_adapter import ADAPTER as QUADRATIC_PROGRAM


def test_qiskit_optimization_dependency_and_inventory_contract():
    assert isinstance(QUADRATIC_PROGRAM.dependency_available(), bool)
    assert QUADRATIC_PROGRAM.list_public_api_inventory()


def test_qiskit_optimization_passthrough_or_clear_import_error():
    if QUADRATIC_PROGRAM.dependency_available():
        assert QUADRATIC_PROGRAM.passthrough_class("QuadraticProgram") is not None
    else:
        with pytest.raises(ImportError, match="qiskit-optimization"):
            QUADRATIC_PROGRAM.passthrough_class("QuadraticProgram")


def test_qiskit_optimization_schema_contract():
    schema = CONVERTER.to_quantumbridge_schema({"qubo": "smoke"})
    assert schema["schema"] == "quantumbridge.ecosystem.object.v0.1"
    assert schema["is_passthrough"] is True


def test_qiskit_optimization_converter_optimizer_availability():
    if CONVERTER.dependency_available():
        assert CONVERTER.passthrough_class("QuadraticProgramToQubo") is not None
    else:
        with pytest.raises(ImportError, match="qiskit-optimization"):
            CONVERTER.passthrough_class("QuadraticProgramToQubo")

    if OPTIMIZER.dependency_available():
        assert OPTIMIZER.list_public_api_inventory()
    else:
        with pytest.raises(ImportError, match="qiskit-optimization"):
            OPTIMIZER.passthrough_class("MinimumEigenOptimizer")


def test_qiskit_optimization_simple_problem_smoke_when_installed():
    if not QUADRATIC_PROGRAM.dependency_available():
        pytest.skip("qiskit-optimization unavailable")
    QuadraticProgram = QUADRATIC_PROGRAM.passthrough_class("QuadraticProgram")
    problem = QuadraticProgram("two_variable_smoke")
    problem.binary_var("x")
    problem.binary_var("y")
    problem.maximize(linear={"x": 1, "y": 1}, quadratic={("x", "y"): -2})
    assert len(problem.variables) == 2


def test_qiskit_optimization_unsupported_warning():
    with pytest.warns(UserWarning, match="does not implement"):
        QUADRATIC_PROGRAM.warn_unsupported("production optimizer parity")
