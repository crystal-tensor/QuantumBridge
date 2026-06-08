import pytest

from quantumbridge.compiler import BasisGateConversionPass
from quantumbridge.core import Circuit


def test_basis_conversion_rejects_unsupported_gate():
    with pytest.raises(ValueError, match="outside basis"):
        BasisGateConversionPass({"x"}).run(Circuit(1).h(0))
