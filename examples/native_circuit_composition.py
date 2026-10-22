# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Run native composition, derivatives and captured state without either SDK."""
import json
import numpy as np
import quantumbridge as qb
from quantumbridge.core.classical import Var, UInt
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.serialization import qpy_dumps,qpy_loads


def main():
    p=qb.Parameter("p")
    inner=qb.Circuit(1,name="rotation").ry(2*p+p.sin(),0)
    inner.global_phase=p/3
    circuit=qb.Circuit(1).compose(inner,wrap=True).compose(inner,wrap=True)
    restored=qpy_loads(qpy_dumps(circuit))[0]
    node=QNode.from_circuit(restored,qb.PauliZ(0),diff_method="parameter-shift",max_diff=2)
    x=.3;angle=4*x+2*np.sin(x);first=4+2*np.cos(x);second=-2*np.sin(x)
    expected=-np.cos(angle)*first**2-np.sin(angle)*second
    hessian=float(node.compute_hessian(x))
    assert np.isclose(hessian,expected,atol=5e-10,rtol=0)
    assert np.isclose(node.compute_hvp(.7,x),.7*expected,atol=5e-10,rtol=0)
    c,s=np.cos(angle/2),np.sin(angle/2)
    np.testing.assert_allclose(Operator(restored.bind({p:x})).data,
        np.exp(2j*x/3)*np.array([[c,-s],[s,c]]),atol=5e-13,rtol=0)
    target=qb.Circuit(3,3)
    counter=target.add_var(Var.new("counter",UInt(4)),0)
    source=qb.Circuit(1,1);source.add_capture(counter)
    body=source.copy_empty_like(vars_mode="captures").store(counter,counter+1).x(0)
    source=source.while_loop(counter<3,body).measure(0,0)
    assert target.compose(source,qubits=2,clbits=1,inline_captures=True,inplace=True) is None
    result=qb.StatevectorDevice().run_shots(target,shots=4,memory=True)
    assert result.counts()=={"010":4}
    values=[record["variables"][counter.value[0]]["value"] for record in result.metadata()["classical_memory"]]
    assert values==[3]*4
    wide=qb.Circuit(100).compose(qb.Circuit(100).ry(.4,99),wrap=True)
    expectation=qb.MatrixProductStateDevice().expectation(wide,qb.PauliZ(99))
    assert np.isclose(expectation,np.cos(.4),atol=3e-12,rtol=0)
    print(json.dumps({"native_composition":"passed","hessian":hessian,"counts":result.counts(),
        "captured_counter_values":values,"mps100_expectation":expectation,"full_sdk_parity":False},sort_keys=True))


if __name__=="__main__":main()
