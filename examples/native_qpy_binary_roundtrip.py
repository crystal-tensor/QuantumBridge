"""Actual public QPY version 13 binary; no SDK is required for native I/O."""
import io
from importlib.util import find_spec
import numpy as np
from quantumbridge import Circuit,Parameter
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads,qpy_get_version,UnsupportedFeature


def main():
    theta = Parameter('theta')
    circuit = Circuit(2,name='native-symbolic',metadata={'example':True}).ry(theta*theta+theta/2,0).cx(0,1)
    circuit.global_phase = theta/3
    binary = qpy_dumps([circuit,Circuit(1,name='second').x(0)])
    restored = qpy_loads(binary)
    np.testing.assert_allclose(Operator.from_circuit(circuit.bind({'theta':.4})).data,Operator.from_circuit(restored[0].bind({'theta':.4})).data,atol=1e-12)
    print('QPY format version:',qpy_get_version(io.BytesIO(binary)),'bytes:',len(binary),'circuits:',len(restored))
    if find_spec('qiskit') is not None:
        from qiskit import qpy
        sdk = qpy.load(io.BytesIO(binary))
        stream = io.BytesIO();qpy.dump(sdk,stream,version=13)
        assert len(qpy_loads(stream.getvalue())) == 2
        print('Optional public SDK reader and writer both accepted the binary.')
    try: qpy_dumps(Circuit(1).delay(3,0,unit='ns'))
    except UnsupportedFeature as exc: print('Explicit unsupported case:',exc)


if __name__ == '__main__': main()
