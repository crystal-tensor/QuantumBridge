# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from collections.abc import Mapping, Sequence
from numbers import Real
from typing import Any, Optional, Union

import numpy as np

from quantumbridge.core import Circuit, Parameter
from quantumbridge.devices import StatevectorDevice
from quantumbridge.primitives.containers import DataBin, PrimitiveResult, PubResult
from quantumbridge.results import Result


class Estimator:
    def __init__(self, device: Optional[StatevectorDevice] = None, default_precision: Optional[float] = None):
        self.device = device or StatevectorDevice()
        self.default_precision = default_precision

    def run(
        self,
        pubs,
        observable=None,
        precision: Optional[float] = None,
        parameter_values: Optional[Union[Mapping[Union[Parameter, str], Real], Sequence[Mapping[Union[Parameter, str], Real]]]] = None,
    ):
        if observable is not None and isinstance(pubs, Circuit):
            return self._run_legacy(pubs, observable, parameters=_single_parameter_mapping(parameter_values))
        return self.run_pubs(pubs, precision=precision, parameter_values=parameter_values)

    def run_pubs(
        self,
        pubs,
        precision: Optional[float] = None,
        parameter_values: Optional[Union[Mapping[Union[Parameter, str], Real], Sequence[Mapping[Union[Parameter, str], Real]]]] = None,
    ) -> PrimitiveResult:
        pub_sequence = _as_pub_sequence(pubs)
        pub_results: list[PubResult] = []
        for index, pub in enumerate(pub_sequence):
            circuit, observables, pub_parameters, pub_precision = _parse_estimator_pub(pub)
            effective_precision = _resolve_precision(pub_precision, precision, self.default_precision)
            parameter_sets = _resolve_parameter_sets(pub_parameters, parameter_values)
            observable_values = _as_observable_sequence(observables)
            ev_batches = []
            std_batches = []
            for params in parameter_sets:
                evs = [float(self.device.expectation(circuit, observable, parameters=params)) for observable in observable_values]
                ev_batches.append(evs[0] if len(evs) == 1 else evs)
                std_batches.append(0.0 if len(evs) == 1 else [0.0 for _ in evs])
            data = DataBin(
                evs=ev_batches[0] if len(ev_batches) == 1 else ev_batches,
                stds=std_batches[0] if len(std_batches) == 1 else std_batches,
                parameter_values=parameter_sets[0] if len(parameter_sets) == 1 else parameter_sets,
                num_observables=len(observable_values),
            )
            pub_results.append(
                PubResult(
                    data=data,
                    metadata={
                        "primitive": "EstimatorV2",
                        "pub_index": index,
                        "precision": effective_precision,
                        "num_parameter_sets": len(parameter_sets),
                        "num_observables": len(observable_values),
                        "circuit_metadata": dict(getattr(circuit, "metadata", {}) or {}),
                        "simulation": "exact_statevector",
                    },
                )
            )
        return PrimitiveResult(
            pub_results,
            metadata={
                "primitive": "EstimatorV2",
                "num_pubs": len(pub_results),
                "default_precision": self.default_precision,
                "native": True,
            },
        )

    def _run_legacy(
        self,
        circuit: Circuit,
        observable,
        parameters: Optional[Mapping[Union[Parameter, str], Real]] = None,
    ) -> Result:
        value = self.device.expectation(circuit, observable, parameters=parameters)
        return Result(expectation_data=value, metadata_data={"primitive": "Estimator"})


def _as_pub_sequence(pubs) -> Sequence[Any]:
    if not isinstance(pubs, (list, tuple)):
        raise TypeError("QuantumBridge Estimator V2 expects a sequence of pubs or legacy Circuit plus observable.")
    if isinstance(pubs, tuple) and pubs and isinstance(pubs[0], Circuit):
        return (pubs,)
    return pubs


def _parse_estimator_pub(pub) -> tuple[Circuit, Any, Optional[Any], Optional[float]]:
    if isinstance(pub, Mapping):
        circuit = pub.get("circuit")
        observable = pub.get("observable", pub.get("observables"))
        if not isinstance(circuit, Circuit):
            raise TypeError("QuantumBridge estimator pub mapping requires a Circuit under 'circuit'.")
        if observable is None:
            raise TypeError("QuantumBridge estimator pub mapping requires 'observable' or 'observables'.")
        return circuit, observable, pub.get("parameters", pub.get("parameter_values")), pub.get("precision")
    if isinstance(pub, tuple) and len(pub) >= 2:
        circuit = pub[0]
        if not isinstance(circuit, Circuit):
            raise TypeError("QuantumBridge estimator pub tuple must start with a Circuit.")
        observable = pub[1]
        parameters = pub[2] if len(pub) >= 3 else None
        precision = pub[3] if len(pub) >= 4 else None
        return circuit, observable, parameters, precision
    raise TypeError("Unsupported QuantumBridge estimator pub.")


def _as_observable_sequence(observables) -> list[Any]:
    if isinstance(observables, np.ndarray):
        return [observables]
    if isinstance(observables, (list, tuple)):
        if not observables:
            raise ValueError("QuantumBridge estimator pubs require at least one observable.")
        return list(observables)
    return [observables]


def _resolve_parameter_sets(pub_parameters, run_parameters) -> list[Mapping[Union[Parameter, str], Real]]:
    parameters = pub_parameters if pub_parameters is not None else run_parameters
    if parameters is None:
        return [{}]
    if isinstance(parameters, Mapping):
        return [dict(parameters)]
    if isinstance(parameters, Sequence):
        if not parameters:
            return [{}]
        if all(isinstance(item, Mapping) for item in parameters):
            return [dict(item) for item in parameters]
    raise TypeError("QuantumBridge estimator parameters must be a mapping or a sequence of mappings.")


def _resolve_precision(pub_precision: Optional[float], run_precision: Optional[float], default_precision: Optional[float]) -> Optional[float]:
    precision = pub_precision if pub_precision is not None else run_precision if run_precision is not None else default_precision
    if precision is not None and float(precision) <= 0:
        raise ValueError("QuantumBridge estimator precision must be positive when provided.")
    return None if precision is None else float(precision)


def _single_parameter_mapping(parameters):
    if parameters is None or isinstance(parameters, Mapping):
        return parameters
    raise TypeError("Legacy QuantumBridge Estimator.run(Circuit, observable) accepts at most one parameter mapping.")
