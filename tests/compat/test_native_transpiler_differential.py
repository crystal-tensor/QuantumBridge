# Public SDK black-box behavior only; no upstream source or tests copied.
import numpy as np
import pytest

qiskit = pytest.importorskip("qiskit")
from qiskit import QuantumCircuit, transpile as sdk_transpile
from qiskit.quantum_info import Operator as SDKOperator

from quantumbridge import Circuit
from quantumbridge.compiler import native_transpile, Target, CouplingMap
from quantumbridge.information import Operator


@pytest.mark.parametrize("scenario", ["hadamard_phase", "euler", "bell", "ghz", "nonlocal", "reverse_cx", "swap_conjugation", "rzz", "rxx", "controlled_phase", "rotation_merge", "interleaved_entanglers"])
def test_public_transpiler_operator_scenarios(scenario):
    native, sdk = Circuit(3), QuantumCircuit(3)
    def gate(name,*args):
        getattr(native,name)(*args)
        getattr(sdk,"p" if name == "phase" else name)(*args)
    if scenario == "hadamard_phase": gate("h",0); gate("phase",.39,0)
    elif scenario == "euler": gate("rz",.27,0); gate("ry",-.36,0); gate("rx",.61,0)
    elif scenario == "bell": gate("h",0); gate("cx",0,1)
    elif scenario == "ghz": gate("h",0); gate("cx",0,1); gate("cx",1,2)
    elif scenario == "nonlocal": gate("x",0); gate("cx",0,2)
    elif scenario == "reverse_cx": gate("h",2); gate("cx",2,0)
    elif scenario == "swap_conjugation": gate("h",0); gate("swap",0,2); gate("phase",.43,2); gate("swap",0,2)
    elif scenario in {"rzz","rxx"}: gate("h",0); gate(scenario,.47,0,2)
    elif scenario == "controlled_phase": gate("h",0); gate("h",2); gate("cp",.38,0,2)
    elif scenario == "rotation_merge": gate("ry",.26,0); gate("ry",-.13,0); gate("x",2); gate("x",2)
    else: gate("h",0); gate("cx",0,2); gate("ry",.33,1); gate("cx",2,1); gate("cz",0,2)
    basis = ["rz","sx","x","cx"]
    compiled = native_transpile(native,target=Target(3,basis,[(0,1),(1,2)]),optimization_level=2)
    expected = SDKOperator(sdk.reverse_bits()).data
    # Reference compiler is invoked only in this optional oracle test, never by the implementation.
    reference = sdk_transpile(sdk,basis_gates=basis,optimization_level=2,seed_transpiler=23)
    np.testing.assert_allclose(SDKOperator(reference.reverse_bits()).data, expected,atol=2e-12)
    np.testing.assert_allclose(Operator.from_circuit(compiled).data,expected,atol=2e-12)
    assert all(len(op.wires) != 2 or op.wires in {(0,1),(1,2)} for op in compiled.operations)
