import pytest

from quantumbridge.chemistry import Molecule
from quantumbridge.chemistry.adapters import PySCFDriverAdapter


def test_pyscf_driver_optional():
    pytest.importorskip("pyscf", reason="optional dependency unavailable: pyscf")
    molecule = Molecule(["H"], [(0, 0, 0)], multiplicity=2)
    result = PySCFDriverAdapter(molecule).run()
    assert result.provenance["dependency"] == "pyscf"
    assert result.metadata["status"] == "adapter-available"
