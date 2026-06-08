import numpy as np

from quantumbridge.interfaces import to_numpy


def test_numpy_interface_p2():
    assert np.allclose(to_numpy([1, 2]), np.array([1, 2]))
