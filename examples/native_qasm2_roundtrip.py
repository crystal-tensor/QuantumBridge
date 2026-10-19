"""Native OpenQASM 2 file/string APIs with strict standard gate expansion."""
from tempfile import TemporaryDirectory
from pathlib import Path
import numpy as np
from quantumbridge import Circuit
from quantumbridge.information import Operator
from quantumbridge.serialization import qasm2_loads,qasm2_dumps,qasm2_load,qasm2_dump


def main():
    circuit = Circuit(3).h(0).cx(0,1).swap(1,2).u3(.2,.3,.4,0)
    source = qasm2_dumps(circuit)
    restored = qasm2_loads(source)
    np.testing.assert_allclose(Operator.from_circuit(circuit).data,Operator.from_circuit(restored).data,atol=1e-12)
    with TemporaryDirectory() as folder:
        path = Path(folder)/'native.qasm'
        qasm2_dump(circuit,path)
        assert qasm2_load(path).num_qubits == 3
    print(source)
    print('QASM2 exact-operator roundtrip passed.')


if __name__ == '__main__': main()
