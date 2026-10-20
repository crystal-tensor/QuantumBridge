# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Shared reservations, cumulative consumption and exception-safe lifetimes."""

from copy import deepcopy
from collections import deque
from numbers import Integral
from threading import RLock

from .derivative_status import ResourceLimitError
from .resource_limits import resolve_unified_limits


def _counts(**values):
    if any(isinstance(value, bool) or not isinstance(value, Integral) or value < 0
           for value in values.values()):
        raise ValueError("Resource amounts require nonnegative integers.")
    return {name: int(value) for name, value in values.items()}


class _Reservation:
    def __init__(self, ledger, category, amounts):
        self.ledger, self.category, self.amounts = ledger, category, amounts
        self.released = False

    def __enter__(self):
        if self.released:
            raise ValueError("Cannot reopen a released resource reservation.")
        return self

    def __exit__(self, *exception):
        self.release()

    def release(self):
        with self.ledger._lock:
            if self.released:
                return
            for account in self.ledger._accounts():
                for name, value in self.amounts.items():
                    account._reserved[name] -= value
                account._released_memory += self.amounts["memory_bytes"]
                account._event("release", self.category, self.amounts)
            self.released = True

    def observe(self, memory_bytes):
        memory_bytes = _counts(memory_bytes=memory_bytes)["memory_bytes"]
        with self.ledger._lock:
            if self.released:
                raise ValueError("Cannot observe a released reservation.")
            if memory_bytes > self.amounts["memory_bytes"]:
                raise RuntimeError("Observed owned memory exceeds its prior reservation.")
            for account in self.ledger._accounts():
                account._observed[self.category] = max(account._observed.get(self.category, 0), memory_bytes)
                account._event("observe", self.category, {"memory_bytes": memory_bytes})

    def consume(self, *, shots=0, derivative_work=0, tapes=0):
        values = _counts(shots=shots, derivative_work=derivative_work, tapes=tapes)
        with self.ledger._lock:
            if self.released:
                raise ValueError("Cannot consume a released reservation.")
            if any(values[name] > self.amounts[name] for name in ("shots", "derivative_work")):
                raise ValueError("Consumption exceeds this reservation's remaining work.")
            # Tapes in a reservation describe simultaneous activity; tape
            # consumption describes completed logical executions, independently.
            self.ledger._check({"memory_bytes": 0, "tapes": tapes, "shots": 0, "derivative_work": 0}, stage="runtime", consuming=True)
            for account in self.ledger._accounts():
                for name in ("shots", "derivative_work"):
                    account._reserved[name] -= values[name]
                for name, value in values.items():
                    account._consumed[name] += value
                account._event("consume", self.category, values)
            for name in ("shots", "derivative_work"):
                self.amounts[name] -= values[name]


class UnifiedResourceLedger:
    """Child accounts constrain their subtree and share every ancestor's cap.

    Memory is live reserved storage. Tapes have both active and cumulative
    counts. Shots and derivative work are cumulative consumed plus outstanding
    reservations. Failed reservations are atomic; release never refunds work.
    Observed arrays and conservative reservations are intentionally distinct.
    """

    _fields = {"memory_bytes": "max_total_memory_bytes", "tapes": "max_total_tapes",
               "shots": "max_total_shots", "derivative_work": "max_derivative_work"}

    def __init__(self, limits=None, parent=None):
        if parent is not None and not isinstance(parent, UnifiedResourceLedger):
            raise TypeError("Resource parent must be a UnifiedResourceLedger.")
        self.limits, self.parent = resolve_unified_limits(limits), parent
        self._lock = RLock() if parent is None else parent._lock
        self._reserved = dict.fromkeys(self._fields, 0)
        self._consumed = {"tapes": 0, "shots": 0, "derivative_work": 0}
        self._peak = dict.fromkeys(self._fields, 0)
        self._estimated = dict.fromkeys(self._fields, 0)
        self._observed, self._unavailable, self._events = {}, {}, deque(maxlen=4096)
        self._event_count = 0
        self._reserved_memory = self._released_memory = 0

    def _accounts(self):
        account = self
        while account is not None:
            yield account
            account = account.parent

    def _event(self, action, category, amounts):
        self._event_count += 1
        self._events.append({"action": action, "category": category, **amounts})

    def _check(self, values, *, stage, consuming=False):
        for account in self._accounts():
            for name, limit_name in self._fields.items():
                consumed = account._consumed.get(name, 0)
                total = account._reserved[name] + values[name]
                if name == "tapes":
                    total = max(account._reserved[name] + (0 if consuming else values[name]), consumed + values[name])
                elif name != "memory_bytes":
                    total += consumed
                limit = getattr(account.limits, limit_name)
                if total > limit:
                    raise ResourceLimitError("memory" if name == "memory_bytes" else name,
                        total, limit, actual=consumed if name != "memory_bytes" else account._reserved[name],
                        stage=stage, receipt=account.receipt())

    def preflight(self, *, memory_bytes=0, tapes=0, shots=0, derivative_work=0):
        values = _counts(memory_bytes=memory_bytes, tapes=tapes, shots=shots, derivative_work=derivative_work)
        with self._lock:
            for account in self._accounts():
                for name, value in values.items():
                    account._estimated[name] = max(account._estimated[name], value)
            self._check(values, stage="preflight")
        return values

    def reserve(self, category, *, memory_bytes=0, tapes=0, shots=0, derivative_work=0):
        if not isinstance(category, str) or not category:
            raise ValueError("Resource category requires a nonempty name.")
        values = _counts(memory_bytes=memory_bytes, tapes=tapes, shots=shots, derivative_work=derivative_work)
        with self._lock:
            self._check(values, stage="runtime_reservation")
            for account in self._accounts():
                for name, value in values.items():
                    account._reserved[name] += value
                    account._peak[name] = max(account._peak[name], account._reserved[name])
                account._reserved_memory += memory_bytes
                account._event("reserve", category, values)
        return _Reservation(self, category, values)

    def consume(self, *, shots=0, derivative_work=0, tapes=0, category="execution"):
        values = _counts(shots=shots, derivative_work=derivative_work, tapes=tapes)
        with self._lock:
            self._check({"memory_bytes": 0, **values}, stage="runtime", consuming=True)
            for account in self._accounts():
                for name, value in values.items():
                    account._consumed[name] += value
                account._event("consume", category, values)

    def unavailable(self, category, reason):
        with self._lock:
            for account in self._accounts():
                account._unavailable[category] = reason

    def receipt(self):
        with self._lock:
            return deepcopy({"protocol_version": 1, "scope": "owned numerical resources, not process RSS",
                "live_memory_bytes": self._reserved["memory_bytes"], "active_tapes": self._reserved["tapes"],
                "reserved_shots": self._reserved["shots"], "reserved_derivative_work": self._reserved["derivative_work"],
                "consumed_shots": self._consumed["shots"], "consumed_tapes": self._consumed["tapes"],
                "consumed_derivative_work": self._consumed["derivative_work"],
                "estimated": self._estimated, "peak_reserved": self._peak,
                "peak_memory_bytes": self._peak["memory_bytes"], "observed_array_bytes": self._observed,
                "total_reserved_memory_bytes": self._reserved_memory,
                "total_released_memory_bytes": self._released_memory,
                "unavailable": self._unavailable, "events": list(self._events),
                "event_count": self._event_count, "omitted_events": self._event_count-len(self._events)})
