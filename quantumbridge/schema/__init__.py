# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
# Design source: docs/roadmap/p2_execution_plan_v0.1.md.

# --- P2 Result Schema (Stage 6) ---
from .errors import SchemaValidationError
from .result_schema import RESULT_SCHEMA_VERSION, make_result_payload
from .serialization import from_json, to_json
from .validation import validate_result_schema

# --- Stage 7 Ecosystem Schemas (optional, may require extra dependencies) ---
try:
    from quantumbridge.schema.ecosystem_results import (
        AerResult,
        AlgorithmsResult,
        ChemistryResult,
        DynamicsResult,
        EcosystemResult,
        ExperimentsResult,
        FinanceResult,
        MLResult,
        MetalDesignResult,
        OptimizationResult,
        PennyLaneResult,
    )
    __all__ = [
        # P2 schema exports
        "RESULT_SCHEMA_VERSION",
        "SchemaValidationError",
        "from_json",
        "make_result_payload",
        "to_json",
        "validate_result_schema",
        # Stage 7 ecosystem exports (optional, may require extras)
        "AerResult",
        "AlgorithmsResult",
        "ChemistryResult",
        "DynamicsResult",
        "EcosystemResult",
        "ExperimentsResult",
        "FinanceResult",
        "MLResult",
        "MetalDesignResult",
        "OptimizationResult",
        "PennyLaneResult",
    ]
except ImportError:
    # Fallback when ecosystem extras not installed
    __all__ = [
        "RESULT_SCHEMA_VERSION",
        "SchemaValidationError",
        "from_json",
        "make_result_payload",
        "to_json",
        "validate_result_schema",
    ]