# Native runtime branch compilation, not a hardware feedback claim.
import numpy as np
from quantumbridge import Circuit, DensityMatrixDevice
from quantumbridge.core.classical import bit
from quantumbridge.compiler import Target, native_transpile


def main():
    circuit = Circuit(3,3).h(0).measure(0,0)
    circuit = circuit.if_else(bit(0),Circuit(3,3).cx(0,2),Circuit(3,3).rx(.3,2))
    circuit.measure(0,0).measure(1,1).measure(2,2)
    compiled = native_transpile(circuit,target=Target(3,("rz","sx","x","cx"),[(0,1),(1,2)]))
    device = DensityMatrixDevice()
    np.testing.assert_allclose(device.density_matrix(circuit),device.density_matrix(compiled),atol=1e-12)
    print("Compiled classical probabilities:",device.run(compiled).probabilities())
    print("Runtime depth and global scheduling remain path-dependent.")


if __name__ == "__main__": main()
