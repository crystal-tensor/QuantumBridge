# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
# Design source: docs/roadmap/p2_upstream_integration_strategy_v0.1.md.

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Molecule:
    atoms: tuple[str, ...]
    coordinates: tuple[tuple[float, float, float], ...]
    charge: int = 0
    multiplicity: int = 1
    spin: int | None = None
    basis: str = "sto-3g"
    unit: str = "angstrom"

    def __init__(
        self,
        atoms: Iterable[str],
        coordinates: Iterable[Iterable[float]],
        charge: int = 0,
        multiplicity: int = 1,
        spin: int | None = None,
        basis: str = "sto-3g",
        unit: str = "angstrom",
    ):
        atoms_tuple = tuple(str(atom) for atom in atoms)
        coords_tuple = tuple(tuple(float(value) for value in coord) for coord in coordinates)
        if len(atoms_tuple) != len(coords_tuple) or not atoms_tuple:
            raise ValueError("QuantumBridge Molecule requires matching non-empty atoms and coordinates.")
        if any(len(coord) != 3 for coord in coords_tuple):
            raise ValueError("QuantumBridge Molecule coordinates must be 3D.")
        object.__setattr__(self, "atoms", atoms_tuple)
        object.__setattr__(self, "coordinates", coords_tuple)
        object.__setattr__(self, "charge", int(charge))
        object.__setattr__(self, "multiplicity", int(multiplicity))
        object.__setattr__(self, "spin", None if spin is None else int(spin))
        object.__setattr__(self, "basis", str(basis))
        object.__setattr__(self, "unit", str(unit))

    def to_xyz(self) -> str:
        lines = [str(len(self.atoms)), f"charge={self.charge} multiplicity={self.multiplicity} basis={self.basis} unit={self.unit}"]
        for atom, coord in zip(self.atoms, self.coordinates):
            lines.append(f"{atom} {coord[0]:.12g} {coord[1]:.12g} {coord[2]:.12g}")
        return "\n".join(lines) + "\n"

    @classmethod
    def from_xyz(cls, text: str, **kwargs) -> "Molecule":
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) < 2:
            raise ValueError("QuantumBridge XYZ text requires atom count and at least one atom line.")
        count = int(lines[0])
        atom_lines = lines[2 : 2 + count]
        atoms = []
        coords = []
        for line in atom_lines:
            parts = line.split()
            if len(parts) != 4:
                raise ValueError("QuantumBridge XYZ atom lines must contain symbol and three coordinates.")
            atoms.append(parts[0])
            coords.append(tuple(float(value) for value in parts[1:]))
        return cls(atoms, coords, **kwargs)

    def bond_scan(self, atom_a: int, atom_b: int, distances: Iterable[float]) -> list["Molecule"]:
        if len(self.atoms) != 2 or {atom_a, atom_b} != {0, 1}:
            raise ValueError("QuantumBridge minimal bond_scan currently supports two-atom molecules.")
        out = []
        for distance in distances:
            coords = [(0.0, 0.0, 0.0), (0.0, 0.0, float(distance))]
            out.append(Molecule(self.atoms, coords, self.charge, self.multiplicity, self.spin, self.basis, self.unit))
        return out
