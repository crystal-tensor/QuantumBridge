# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/api_contract_v0.1.md and docs/mvp/simulator_design_v0.1.md.

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional, Union

import numpy as np

from quantumbridge.schema.result_schema import RESULT_SCHEMA_VERSION, make_result_payload
from quantumbridge.schema.validation import validate_result_schema


def _complex_list(values: Optional[np.ndarray]) -> Optional[list[dict[str, float]]]:
    if values is None:
        return None
    return [{"real": float(np.real(value)), "imag": float(np.imag(value))} for value in values]


def _complex_array(values) -> Optional[np.ndarray]:
    if values is None:
        return None
    return np.asarray([complex(item.get("real", 0.0), item.get("imag", 0.0)) for item in values], dtype=complex)


@dataclass
class Result:
    state: Optional[np.ndarray] = None
    probabilities_data: Optional[dict[str, float]] = None
    counts_data: Optional[dict[str, int]] = None
    expectation_data: Optional[Union[float, dict[str, float]]] = None
    metadata_data: dict[str, Any] = field(default_factory=dict)
    trace: Optional[list[dict[str, Any]]] = None

    def statevector(self) -> Optional[np.ndarray]:
        return None if self.state is None else self.state.copy()

    def probabilities(self) -> Optional[dict[str, float]]:
        return None if self.probabilities_data is None else dict(self.probabilities_data)

    def counts(self) -> Optional[dict[str, int]]:
        return None if self.counts_data is None else dict(self.counts_data)

    def expectation_value(self):
        return self.expectation_data

    def metadata(self) -> dict[str, Any]:
        return dict(self.metadata_data)

    def to_dict(self) -> dict[str, Any]:
        metadata = self.metadata()
        expectation_values = self.expectation_data if isinstance(self.expectation_data, dict) else None
        if self.expectation_data is not None and not isinstance(self.expectation_data, dict):
            expectation_values = {"default": float(self.expectation_data)}
        payload = make_result_payload(
            job_id=metadata.get("job_id"),
            backend_name=metadata.get("backend_name", metadata.get("device")),
            backend_version=metadata.get("backend_version"),
            experiment_id=metadata.get("experiment_id"),
            shots=metadata.get("shots"),
            counts=self.counts(),
            probabilities=self.probabilities(),
            statevector=_complex_list(self.state),
            density_matrix=metadata.get("density_matrix"),
            expectation_values=expectation_values,
            observable_metadata=metadata.get("observable_metadata", {}),
            circuit_metadata=metadata.get("circuit_metadata", {}),
            noise_model_metadata=metadata.get("noise_model_metadata", metadata.get("noise_model", {})),
            seed=metadata.get("seed"),
            timing=metadata.get("timing", {}),
            errors=metadata.get("errors", []),
            warnings=metadata.get("warnings", []),
            provenance=metadata.get("provenance", {}),
            metadata=metadata,
        )
        payload["expectation"] = self.expectation_data
        payload["trace"] = self.trace
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Result":
        if "schema_version" not in payload:
            payload = {
                "schema_version": "0.1",
                "counts": payload.get("counts"),
                "probabilities": payload.get("probabilities"),
                "statevector": payload.get("statevector"),
                "density_matrix": None,
                "expectation_values": {"default": payload.get("expectation")} if payload.get("expectation") is not None else None,
                "metadata": payload.get("metadata", {}),
                "provenance": {},
                "errors": [],
                "warnings": [],
            }
        validate_result_schema(payload)
        expectation = payload.get("expectation")
        if expectation is None:
            values = payload.get("expectation_values")
            if isinstance(values, dict):
                expectation = values if set(values) != {"default"} else values.get("default")
        metadata = dict(payload.get("metadata") or {})
        for key in (
            "job_id",
            "backend_name",
            "backend_version",
            "experiment_id",
            "shots",
            "seed",
            "observable_metadata",
            "circuit_metadata",
            "noise_model_metadata",
            "timing",
            "errors",
            "warnings",
            "provenance",
        ):
            if payload.get(key) not in (None, {}, []):
                metadata.setdefault(key, payload.get(key))
        metadata.setdefault("schema_version", payload.get("schema_version", RESULT_SCHEMA_VERSION))
        return cls(
            state=_complex_array(payload.get("statevector")),
            probabilities_data=None if payload.get("probabilities") is None else dict(payload.get("probabilities")),
            counts_data=None if payload.get("counts") is None else {str(k): int(v) for k, v in payload.get("counts").items()},
            expectation_data=expectation,
            metadata_data=metadata,
            trace=payload.get("trace"),
        )

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=indent)

    @classmethod
    def from_json(cls, text: str) -> "Result":
        return cls.from_dict(json.loads(text))

    def validate_schema(self) -> bool:
        return validate_result_schema(self.to_dict())
