"""Parse actual typed feedback source and execute the restored native blocks."""
from quantumbridge import DensityMatrixDevice
from quantumbridge.serialization import qasm3_loads,qasm3_dumps


def main():
    source = '''OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
uint[4] count=0;
x q[0];
c[0]=measure q[0];
while(c[0]) { reset q[0]; c[0]=measure q[0]; count+=1; }
if(count==1) { x q[1]; } else { z q[1]; }
c=measure q;
'''
    original = qasm3_loads(source)
    exported = qasm3_dumps(original)
    restored = qasm3_loads(exported)
    assert DensityMatrixDevice().run(original).probabilities() == {'01':1.}
    assert DensityMatrixDevice().run(restored).probabilities() == {'01':1.}
    print(exported)
    print('Runtime while/feedback/store roundtrip:',DensityMatrixDevice().run(restored).probabilities())


if __name__ == '__main__': main()
