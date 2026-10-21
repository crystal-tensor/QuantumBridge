# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native bound circuit/instruction execution; no optional SDK or cloud call."""

import json
import numpy as np

from quantumbridge import Circuit, Parameter
from quantumbridge.information import DensityMatrix, Operator, Statevector


def main():
    theta = Parameter("theta")
    circuit = Circuit(2).h(0).ry(theta,1).cx(0,1)
    circuit.global_phase = theta/3
    bound = circuit.assign_parameters({theta:.43})
    source = Statevector.from_label("r-")
    operator = Operator(bound)
    state = source.evolve(operator)
    direct = source.evolve(bound.to_instruction())
    np.testing.assert_allclose(state.data,direct.data,atol=1e-14,rtol=0)
    density = DensityMatrix.from_statevector(source).evolve(bound.to_instruction())
    np.testing.assert_allclose(density.data,np.outer(state.data,state.data.conj()),atol=1e-14,rtol=0)
    reduced = density.partial_trace([0])
    observable = Operator.from_label("Z")
    mixed = Statevector(np.arange(1,9)+1j*np.arange(8,0,-1),dims=(2,4))
    typed = mixed.to_operator()
    expectation = reduced.expectation_value(observable)
    print(json.dumps({"native_only":True,"operator_dims":operator.input_dims(),
        "state_norm":float(state.trace()),"reduced_purity":complex(reduced.purity()).real,
        "reduced_z_expectation":[expectation.real,expectation.imag],
        "typed_projector_dims":typed.input_dims(),"typed_projector_trace":float(np.trace(typed.data).real)},sort_keys=True))


if __name__=="__main__":main()
