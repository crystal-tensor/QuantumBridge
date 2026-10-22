# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Two native parameterized execution chains with explicit numerical receipts."""

import json
from itertools import product

import numpy as np

from quantumbridge import Circuit, Parameter
from quantumbridge.information import DensityMatrix, Operator, Statevector


def encoded(value):
    data=np.asarray(value)
    return {"real":data.real.tolist(),"imag":data.imag.tolist()}


def reference(width,p,q,blocks):
    c,s=np.cos((p+q)/2),np.sin((p+q)/2)
    rx=np.array([[c,-1j*s],[-1j*s,c]])
    c,s=np.cos(p*q/2),np.sin(p*q/2)
    ry=np.array([[c,-s],[s,c]],complex)
    rz=np.diag([np.exp(-.5j*q),np.exp(.5j*q)])
    cx=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],complex)
    result=np.eye(1<<width,dtype=complex)
    for first,second in blocks:
        for gate,wires in ((rx,(first,)),(ry,(second,)),(cx,(first,second)),(rz,(first,))):
            embedded=np.zeros_like(result)
            for column,bits in enumerate(product((0,1),repeat=width)):
                local=sum(bits[wire]*(1<<(len(wires)-1-i)) for i,wire in enumerate(wires))
                for row,replacement in enumerate(product((0,1),repeat=len(wires))):
                    output=list(bits)
                    for wire,bit in zip(wires,replacement):output[wire]=bit
                    index=sum(bit*(1<<(width-1-i)) for i,bit in enumerate(output))
                    embedded[index,column]=gate[row,local]
            result=embedded@result
    return np.exp(1j*len(blocks)*p/7)*result


def initial(width):
    indices=np.arange(1,(1<<width)+1)
    first=np.cos(indices)+1j*np.sin(2*indices)
    second=np.sin(3*indices)+1j*np.cos(2*indices)
    first/=np.linalg.norm(first);second/=np.linalg.norm(second)
    return first,.3*np.outer(first,first.conj())+.7*np.outer(second,second.conj())


def main():
    p,q=Parameter("p"),Parameter("q")
    child=Circuit(2).rx(p+q,0).ry(p*q,1).cx(0,1).rz(q,0)
    child.global_phase=p/7
    instruction=child.to_instruction()
    parent=Circuit(3).append(instruction,(2,0)).append(instruction,(0,1))
    observable=np.diag([1.,-2.,.5,3.])+1j*np.eye(4,k=1)
    diagonal=np.diag([1.,-2.,.5,3.])
    records=[]
    for pvalue,qvalue in ((.2,-.3),(-.7,.5),(.8,1.1)):
        bound=child.assign_parameters({p:pvalue}).assign_parameters({q:qvalue})
        source,_=initial(2)
        matrix=Operator(bound)
        state=Statevector(source).evolve(matrix)
        expectation=state.expectation_value(Operator(observable))
        expected=reference(2,pvalue,qvalue,[(0,1)])
        error_a=float(np.max(np.abs(matrix.data-expected)))
        np.testing.assert_allclose(state.data,expected@source,atol=6e-15,rtol=0)
        _,mixed=initial(3)
        density=DensityMatrix(mixed).evolve(parent.bind({p:pvalue,q:qvalue}).to_instruction())
        reduced=density.partial_trace([2,0])
        expected_b=reference(3,pvalue,qvalue,[(2,0),(0,1)])
        expected_density=expected_b@mixed@expected_b.conj().T
        expected_reduced=np.trace(expected_density.reshape((2,)*6),axis1=1,axis2=4).reshape(4,4)
        error_b=float(np.max(np.abs(density.data-expected_density)))
        np.testing.assert_allclose(matrix.data,expected,atol=6e-15,rtol=0)
        np.testing.assert_allclose(reduced.data,expected_reduced,atol=7e-15,rtol=0)
        records.append({"parameters":{"p":pvalue,"q":qvalue},
            "chain_a":{"order":["rx(p+q,0)","ry(p*q,1)","cx(0,1)","rz(q,0)"],
                "phase":pvalue/7,"operator":encoded(matrix.data),"state":encoded(state.data),
                "expectation":encoded(expectation),"max_operator_error":error_a},
            "chain_b":{"block_wires":[[2,0],[0,1]],"phase":2*pvalue/7,
                "density":encoded(density.data),"keep_original_wire_order":[0,2],
                "reduced":encoded(reduced.data),"purity":encoded(reduced.purity()),
                "expectation":encoded(reduced.expectation_value(Operator(diagonal))),
                "max_density_error":error_b}})
    assert child.parameters==(p,q) and parent.parameters==(p,q)
    print(json.dumps({"native_only":True,"wire_convention":"q0-high","records":records},sort_keys=True))


if __name__=="__main__":main()
