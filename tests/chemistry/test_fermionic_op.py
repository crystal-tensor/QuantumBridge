from quantumbridge.chemistry import FermionicOp


def test_fermionic_op_normal_order():
    op = FermionicOp({"-_0 +_0": 1.0})
    assert op.normal_ordered().terms[0][0] == "+_0 -_0"
