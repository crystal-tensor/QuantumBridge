import pytest

from quantumbridge.chemistry import Molecule
from quantumbridge.chemistry.adapters import PySCFDriverAdapter


def test_pyscf_driver_optional():
    pytest.importorskip("pyscf", reason="optional dependency unavailable: pyscf")
    result = PySCFDriverAdapter(Molecule(["H"], [(0, 0, 0)])).run()
    assert result.provenance["dependency"] == "pyscf"
