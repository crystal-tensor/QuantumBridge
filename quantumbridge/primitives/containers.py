# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping, Sequence


@dataclass
class DataBin:
    """Attribute and mapping-style primitive data container."""

    _fields: dict[str, Any] = field(default_factory=dict)

    def __init__(self, **fields: Any) -> None:
        object.__setattr__(self, "_fields", dict(fields))

    def __getattr__(self, name: str) -> Any:
        try:
            return self._fields[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __getitem__(self, name: str) -> Any:
        return self._fields[name]

    def __contains__(self, name: object) -> bool:
        return name in self._fields

    def __iter__(self) -> Iterator[str]:
        return iter(self._fields)

    def keys(self):
        return self._fields.keys()

    def items(self):
        return self._fields.items()

    def values(self):
        return self._fields.values()

    def get(self, name: str, default: Any = None) -> Any:
        return self._fields.get(name, default)

    def to_dict(self) -> dict[str, Any]:
        return _to_plain_dict(self._fields)


@dataclass(frozen=True)
class PubResult:
    """Result for one primitive unified bloc."""

    data: DataBin
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"data": self.data.to_dict(), "metadata": _to_plain_dict(dict(self.metadata))}


@dataclass(frozen=True)
class PrimitiveResult:
    """Sequence-like container for primitive pub results."""

    pub_results: Sequence[PubResult]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __iter__(self) -> Iterator[PubResult]:
        return iter(self.pub_results)

    def __len__(self) -> int:
        return len(self.pub_results)

    def __getitem__(self, index: int) -> PubResult:
        return self.pub_results[index]

    def to_dict(self) -> dict[str, Any]:
        return {
            "results": [result.to_dict() for result in self.pub_results],
            "metadata": _to_plain_dict(dict(self.metadata)),
        }


def _to_plain_dict(value: Any) -> Any:
    if isinstance(value, DataBin):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {str(key): _to_plain_dict(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_plain_dict(item) for item in value]
    if isinstance(value, list):
        return [_to_plain_dict(item) for item in value]
    return value
