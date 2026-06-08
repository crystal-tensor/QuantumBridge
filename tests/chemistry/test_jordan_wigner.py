from quantumbridge.chemistry import FermionicOp, JordanWignerMapper


def test_jordan_wigner_number_operator():
    mapped = JordanWignerMapper().map(FermionicOp({"+_0 -_0": 1.0}))
    assert len(mapped.terms) == 2
