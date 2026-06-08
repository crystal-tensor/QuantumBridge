from quantumbridge.compiler import Layout


def test_trivial_layout():
    assert Layout.trivial(3).to_dict() == {0: 0, 1: 1, 2: 2}
