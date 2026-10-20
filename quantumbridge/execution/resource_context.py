# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Request-local lifetimes; nested plans inherit one resource account."""

from contextlib import ExitStack, contextmanager
from contextvars import ContextVar
from functools import wraps
from numbers import Integral
from copy import deepcopy

import numpy as np


_current = ContextVar("quantumbridge_derivative_resources", default=None)
_sample_ticket = ContextVar("quantumbridge_native_sample_ticket", default=None)


def current_resources():
    return _current.get()


def numerical_payload_bytes(value):
    """Logical array/scalar/text bytes, excluding Python container overhead."""
    if isinstance(value, np.ndarray):
        return value.nbytes
    if isinstance(value, np.generic):
        return value.dtype.itemsize
    if isinstance(value, (float, int, complex, bool)):
        return 16 if isinstance(value, complex) else 8
    if isinstance(value, (str, bytes)):
        return len(value.encode("utf-8") if isinstance(value, str) else value)
    if isinstance(value, dict):
        return sum(numerical_payload_bytes(k)+numerical_payload_bytes(v) for k, v in value.items())
    if isinstance(value, (tuple, list)):
        return sum(numerical_payload_bytes(item) for item in value)
    return 0


def copy_execution_payload(value):
    """Reserve retained receipt payload before copying, never claim object RSS."""
    resources = current_resources()
    if resources is not None:
        ticket = resources.retain("retained_receipt_payload", numerical_payload_bytes(value))
        resources.ledger.unavailable("python_container_allocator_memory",
            "Receipt accounting covers logical numerical/text payload, not Python objects, container headers or allocator peak.")
    result = deepcopy(value)
    if resources is not None:
        ticket.observe(numerical_payload_bytes(result))
    return result


@contextmanager
def measurement_shots(ledger, shots):
    """Reserve one measurement's sampling before dispatch, then release unused work."""
    with ledger.reserve("measurement_shots", shots=shots) as ticket:
        token = _sample_ticket.set(ticket)
        try:
            yield ticket
        finally:
            _sample_ticket.reset(token)


def meter_native_samples(function):
    """Charge completed buffers before any downstream statistics can fail."""
    @wraps(function)
    def sampled(self, circuit, *args, **kwargs):
        resources = current_resources()
        if resources is None:
            return function(self, circuit, *args, **kwargs)
        shots = kwargs.get("shots", args[1] if len(args) > 1 else 1)
        if isinstance(shots, bool) or not isinstance(shots, Integral) or shots < 0:
            raise ValueError("Native sampling shots must be nonnegative integers.")
        def execute(ticket):
            if shots > ticket.amounts["shots"]:
                from .derivative_status import ResourceLimitError
                raise ResourceLimitError("shots", shots, ticket.amounts["shots"],
                    stage="sample_dispatch", receipt=resources.ledger.receipt())
            try:
                result = function(self, circuit, *args, **kwargs)
            except Exception:
                resources.ledger.unavailable("failed_native_sample_completion",
                    "A failed native sampler did not return a complete buffer; internal partial work is not observable.")
                raise
            ticket.consume(shots=len(result))
            return result
        ticket = _sample_ticket.get()
        if ticket is not None:
            return execute(ticket)
        with measurement_shots(resources.ledger, shots) as ticket:
            return execute(ticket)
    return sampled


class ResourceScope:
    def __init__(self, ledger):
        self.ledger, self.stack = ledger, ExitStack()

    def __enter__(self):
        self.token = _current.set(self)
        return self

    def __exit__(self, *exception):
        try:
            self.stack.__exit__(*exception)
        finally:
            _current.reset(self.token)

    def retain(self, category, memory_bytes):
        return self.stack.enter_context(self.ledger.reserve(category, memory_bytes=memory_bytes))
