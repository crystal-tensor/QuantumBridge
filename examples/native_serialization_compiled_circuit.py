"""Directed native compilation and exact execution after standard serialization."""
import numpy as np
from quantumbridge import Circuit,StatevectorDevice
from quantumbridge.compiler import Target,native_transpile
from quantumbridge.serialization import serialize_circuit,deserialize_circuit


def main():
    circuit = Circuit(3).h(0).ry(.3,1).cx(0,2)
    target = Target(3,('rz','sx','x','cx'),[(0,1),(1,2)],dt=1e-9,
                    durations={'rz':0.,'sx':4e-9,'x':8e-9,'cx':12e-9})
    compiled = native_transpile(circuit,target=target,optimization_level=0,scheduling_method='asap')
    for format in ('qasm3','qpy'):
        artifact = serialize_circuit(compiled,format,metadata_policy='external')
        restored = deserialize_circuit(artifact)
        np.testing.assert_allclose(StatevectorDevice().statevector(compiled),StatevectorDevice().statevector(restored),atol=1e-12)
        assert restored.metadata['schedule'] == compiled.metadata['schedule']
        print(format,'exact-phase execution passed; layout/schedule kept in external sidecar.')


if __name__ == '__main__': main()
