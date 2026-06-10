# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/api_contract_v0.1.md.

from quantumbridge.algorithms import maxcut_hamiltonian, qaoa_circuit, run_qaoa, run_vqe
from quantumbridge.circuit_library import (
    amplitude_encoding,
    basis_state,
    efficient_su2,
    initialize,
    integer_comparator,
    qft,
    real_amplitudes,
    standard_gate,
    two_local,
    weighted_adder,
    zz_feature_map,
)
from quantumbridge.compat import circuit_from_openqasm, circuit_from_qiskit, circuit_to_qiskit
from quantumbridge.core import Circuit, Instruction, Measurement, Operation, Parameter, ParameterExpression, ParameterVector
from quantumbridge.compiler import transpile
from quantumbridge.devices import ShotSampler, StatevectorDevice
from quantumbridge.diff import parameter_shift
from quantumbridge.information import DensityMatrix, Statevector
from quantumbridge.operators import Pauli, SparsePauliOperator
from quantumbridge.primitives import DataBin, Estimator, PrimitiveResult, PubResult, Sampler
from quantumbridge.providers import Backend, BackendV2, Job, JobError, JobStatus, JobTimeoutError, Options, Provider, QiskitBackendNotFoundError
from quantumbridge.results import Result
from quantumbridge.transforms import finite_difference, metric_tensor, qng_step, spsa_gradient
from quantumbridge.utils.math import Hamiltonian, PauliString, PauliX, PauliY, PauliZ

__all__ = [
    "Circuit",
    "Backend",
    "BackendV2",
    "DensityMatrix",
    "DataBin",
    "Estimator",
    "Hamiltonian",
    "Instruction",
    "Job",
    "JobError",
    "JobStatus",
    "JobTimeoutError",
    "Measurement",
    "Operation",
    "Parameter",
    "ParameterExpression",
    "ParameterVector",
    "Options",
    "Pauli",
    "PauliString",
    "PauliX",
    "PauliY",
    "PauliZ",
    "Provider",
    "QiskitBackendNotFoundError",
    "PrimitiveResult",
    "PubResult",
    "Result",
    "Sampler",
    "ShotSampler",
    "SparsePauliOperator",
    "StatevectorDevice",
    "Statevector",
    "circuit_from_openqasm",
    "circuit_from_qiskit",
    "circuit_to_qiskit",
    "amplitude_encoding",
    "basis_state",
    "efficient_su2",
    "finite_difference",
    "initialize",
    "integer_comparator",
    "maxcut_hamiltonian",
    "metric_tensor",
    "parameter_shift",
    "qng_step",
    "qft",
    "qaoa_circuit",
    "real_amplitudes",
    "run_qaoa",
    "run_vqe",
    "spsa_gradient",
    "standard_gate",
    "two_local",
    "transpile",
    "weighted_adder",
    "zz_feature_map",
]
