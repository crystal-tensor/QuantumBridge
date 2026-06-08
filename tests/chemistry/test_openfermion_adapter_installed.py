# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.chemistry.adapters import OpenFermionAdapter
from quantumbridge.chemistry.fermion import FermionicOp


def test_openfermion_adapter_installed_converts_small_operator():
    pytest.importorskip("openfermion", reason="optional dependency unavailable: openfermion")

    from openfermion import FermionOperator

    upstream_op = FermionOperator("1^ 0", 0.5)
    result = OpenFermionAdapter().fermion_operator_to_quantumbridge(upstream_op)

    assert isinstance(result, FermionicOp)
    assert result.to_dict()["+_1 -_0"] == 0.5
