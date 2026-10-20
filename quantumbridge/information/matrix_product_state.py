# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independently implemented from tensor contraction and Schmidt decomposition.

from __future__ import annotations

from numbers import Integral, Real

import numpy as np

from quantumbridge.utils.math import gate_matrix, pauli_matrix


class MatrixProductState:
    """Open-boundary qubit MPS in q0-first order with an orthogonality center.

    cutoff bounds discarded squared Schmidt weight per split, not the final
    simulation error. max_bond_dim may force additional, reported truncation.
    """

    def __init__(self, tensors, *, max_bond_dim=None, cutoff=1e-16, max_memory_mb=1024):
        if max_bond_dim is not None and (isinstance(max_bond_dim, bool) or not isinstance(max_bond_dim, Integral) or max_bond_dim < 1):
            raise ValueError("QuantumBridge max_bond_dim must be a positive integer or None.")
        if isinstance(cutoff, bool) or not isinstance(cutoff, Real) or not np.isfinite(cutoff) or not 0 <= cutoff < 1:
            raise ValueError("QuantumBridge MPS cutoff must be in [0, 1).")
        if max_memory_mb is not None and (isinstance(max_memory_mb, bool) or not isinstance(max_memory_mb, Real) or not np.isfinite(max_memory_mb) or max_memory_mb <= 0):
            raise ValueError("QuantumBridge max_memory_mb must be positive or None.")
        self.max_bond_dim = None if max_bond_dim is None else int(max_bond_dim)
        self.cutoff = float(cutoff)
        self.max_memory_mb = None if max_memory_mb is None else float(max_memory_mb)
        self.discarded_weight = 0.0
        self.truncations = 0
        self._tensors = [np.asarray(tensor, dtype=complex) for tensor in tensors]
        if not self._tensors:
            raise ValueError("QuantumBridge MPS needs at least one qubit tensor.")
        previous = 1
        for tensor in self._tensors:
            if tensor.ndim != 3 or tensor.shape[0] != previous or tensor.shape[1] != 2 or min(tensor.shape) < 1 or not np.all(np.isfinite(tensor)):
                raise ValueError("QuantumBridge MPS tensors require finite connected (left, 2, right) shapes.")
            previous = tensor.shape[2]
        if previous != 1:
            raise ValueError("QuantumBridge MPS boundary bonds must have dimension one.")
        self._guard(sum(tensor.size for tensor in self._tensors) * 3)
        self._tensors = [tensor.copy() for tensor in self._tensors]
        self.peak_bond_dimension = max(self.bond_dimensions, default=1)
        self._center = len(self._tensors) - 1
        # A left-to-right QR sweep canonicalizes arbitrary supplied tensors.
        for index in range(len(self._tensors) - 1):
            tensor = self._tensors[index]
            q, r = np.linalg.qr(tensor.reshape(-1, tensor.shape[2]), mode="reduced")
            self._tensors[index] = q.reshape(tensor.shape[0], 2, q.shape[1])
            self._tensors[index + 1] = np.tensordot(r, self._tensors[index + 1], axes=1)
        if not np.isclose(np.linalg.norm(self._tensors[-1]) ** 2, 1, atol=1e-10, rtol=0):
            raise ValueError("QuantumBridge MPS tensors must describe a normalized state.")
        if max_bond_dim is not None and max(self.bond_dimensions, default=1) > max_bond_dim:
            raise ValueError("Supplied MPS bonds exceed max_bond_dim; explicitly compress the initial state first.")

    @classmethod
    def zero(cls, num_qubits, **options):
        if isinstance(num_qubits, bool) or not isinstance(num_qubits, Integral) or num_qubits < 1:
            raise ValueError("QuantumBridge MPS width must be a positive integer.")
        return cls([np.array([1, 0], complex).reshape(1, 2, 1) for _ in range(num_qubits)], **options)

    @classmethod
    def from_statevector(cls, state, **options):
        data = np.asarray(getattr(state, "data", state), dtype=complex)
        if data.ndim != 1 or data.size < 2 or data.size & (data.size - 1) or not np.all(np.isfinite(data)) or not np.isclose(np.vdot(data, data), 1, atol=1e-10, rtol=0):
            raise ValueError("QuantumBridge MPS initial vector must be finite, normalized and have qubit dimension.")
        result = cls.zero(data.size.bit_length() - 1, **options)
        result._guard(data.size * 8)
        result._split(0, result.num_qubits, data.reshape(1, -1, 1))
        return result

    @property
    def num_qubits(self):
        return len(self._tensors)

    @property
    def tensors(self):
        return tuple(tensor.copy() for tensor in self._tensors)

    @property
    def tensor_bytes(self):
        return sum(tensor.nbytes for tensor in self._tensors)

    @property
    def bond_dimensions(self):
        return tuple(tensor.shape[2] for tensor in self._tensors[:-1])

    def copy(self):
        result = object.__new__(MatrixProductState)
        result.__dict__ = dict(self.__dict__)
        result._tensors = [tensor.copy() for tensor in self._tensors]
        return result

    def _guard(self, elements):
        if self.max_memory_mb is not None and 16 * elements > self.max_memory_mb * 1024 ** 2:
            raise MemoryError("QuantumBridge MPS contraction/output exceeds max_memory_mb.")

    def _wires(self, wires):
        selected = tuple(range(self.num_qubits) if wires is None else wires)
        if len(set(selected)) != len(selected) or any(isinstance(wire, bool) or not isinstance(wire, Integral) or not 0 <= wire < self.num_qubits for wire in selected):
            raise ValueError("QuantumBridge MPS wires must be distinct valid integer wires.")
        return selected

    def _move_center(self, target):
        while self._center < target:
            index = self._center
            tensor = self._tensors[index]
            q, r = np.linalg.qr(tensor.reshape(-1, tensor.shape[2]), mode="reduced")
            self._tensors[index] = q.reshape(tensor.shape[0], 2, q.shape[1])
            self._tensors[index + 1] = np.tensordot(r, self._tensors[index + 1], axes=1)
            self._center += 1
        while self._center > target:
            index = self._center
            tensor = self._tensors[index]
            q, r = np.linalg.qr(tensor.reshape(tensor.shape[0], -1).T, mode="reduced")
            self._tensors[index] = q.T.reshape(q.shape[1], 2, tensor.shape[2])
            self._tensors[index - 1] = np.tensordot(self._tensors[index - 1], r.T, axes=1)
            self._center -= 1

    def _split(self, start, width, block):
        left, right = block.shape[0], block.shape[-1]
        for offset in range(width - 1):
            matrix = block.reshape(left * 2, -1)
            self._guard(matrix.size * 8 + sum(tensor.size for tensor in self._tensors))
            u, singular, vh = np.linalg.svd(matrix, full_matrices=False)
            total = float(np.sum(singular ** 2))
            tails = np.cumsum((singular ** 2)[::-1])[::-1]
            rank = len(singular)
            for candidate in range(1, len(singular)):
                if tails[candidate] <= self.cutoff * total:
                    rank = candidate
                    break
            if self.max_bond_dim is not None:
                rank = min(rank, self.max_bond_dim)
            self.peak_bond_dimension = max(self.peak_bond_dimension, rank)
            discarded = float(np.sum(singular[rank:] ** 2) / total) if total else 0.0
            if discarded:
                self.discarded_weight += discarded
                self.truncations += 1
            retained = float(np.sum(singular[:rank] ** 2))
            self._tensors[start + offset] = u[:, :rank].reshape(left, 2, rank)
            block = (singular[:rank, None] * vh[:rank]) / np.sqrt(retained)
            left = rank
        self._tensors[start + width - 1] = block.reshape(left, 2, right)
        self._center = start + width - 1

    def _block_gate(self, matrix, start, width):
        self._move_center(start)
        left = self._tensors[start].shape[0]
        right = self._tensors[start + width - 1].shape[2]
        self._guard(left * (1 << width) * right * 10 + sum(tensor.size for tensor in self._tensors))
        block = self._tensors[start]
        for tensor in self._tensors[start + 1:start + width]:
            block = np.tensordot(block, tensor, axes=1)
        block = np.einsum("ij,ajb->aib", matrix, block.reshape(left, 1 << width, right))
        norm = float(np.linalg.norm(block) ** 2)
        if norm <= 0:
            raise ValueError("QuantumBridge cannot normalize a zero MPS branch.")
        self._split(start, width, block / np.sqrt(norm))

    def apply(self, matrix, wires):
        """Apply a supplied local matrix, normalizing the resulting pure branch."""
        selected = self._wires(wires)
        if not selected:
            raise ValueError("QuantumBridge MPS matrix application requires wires.")
        matrix = np.asarray(matrix, dtype=complex)
        dimension = 1 << len(selected)
        if matrix.shape != (dimension, dimension) or not np.all(np.isfinite(matrix)):
            raise ValueError("QuantumBridge MPS matrix dimensions must match its wires.")
        if len(selected) == 1:
            self._block_gate(matrix, selected[0], 1)
            return self
        # Gather logical wires in the matrix's order, then restore physical order.
        labels, swaps = list(range(self.num_qubits)), []
        start = min(selected)
        for offset, wire in enumerate(selected):
            position = labels.index(wire)
            while position > start + offset:
                self._block_gate(gate_matrix("swap"), position - 1, 2)
                labels[position - 1], labels[position] = labels[position], labels[position - 1]
                swaps.append(position - 1)
                position -= 1
        self._block_gate(matrix, start, len(selected))
        for position in reversed(swaps):
            self._block_gate(gate_matrix("swap"), position, 2)
        return self

    def statevector(self):
        self._guard((1 << self.num_qubits) * 4)
        block = self._tensors[0]
        for tensor in self._tensors[1:]:
            self._guard(block.size * tensor.shape[2] * 4)
            block = np.tensordot(block, tensor, axes=1)
        return block.reshape(-1).copy()

    def reduced_density_matrix(self, wires=None):
        selected = self._wires(wires)
        env = np.ones((1, 1, 1, 1), complex)
        kept = 0
        for index, tensor in enumerate(self._tensors):
            next_kept = kept + int(index in selected)
            self._guard((tensor.shape[0] ** 2 + tensor.shape[2] ** 2) * (1 << (2 * next_kept)) * 8)
            if index in selected:
                env = np.einsum("abij,asr,btv->rvisjt", env, tensor, tensor.conj(), optimize=True)
                env = env.reshape(tensor.shape[2], tensor.shape[2], 1 << next_kept, 1 << next_kept)
            else:
                env = np.einsum("abij,asr,bst->rtij", env, tensor, tensor.conj(), optimize=True)
            kept = next_kept
        matrix = env[0, 0]
        order = [sorted(selected).index(wire) for wire in selected]
        axes = order + [axis + len(order) for axis in order]
        return matrix.reshape((2,) * (2 * kept)).transpose(axes).reshape(1 << kept, 1 << kept).copy()

    def probabilities(self, wires=None):
        selected = self._wires(wires)
        env, kept = np.ones((1, 1, 1), complex), 0
        for index, tensor in enumerate(self._tensors):
            next_kept = kept + int(index in selected)
            self._guard((tensor.shape[0] ** 2 + tensor.shape[2] ** 2) * (1 << next_kept) * 8)
            if index in selected:
                env = np.einsum("abi,asr,bst->rtis", env, tensor, tensor.conj(), optimize=True)
                env = env.reshape(tensor.shape[2], tensor.shape[2], 1 << next_kept)
            else:
                env = np.einsum("abi,asr,bst->rti", env, tensor, tensor.conj(), optimize=True)
            kept = next_kept
        order = [sorted(selected).index(wire) for wire in selected]
        values = env[0, 0].real.reshape((2,) * kept).transpose(order).reshape(-1)
        return {format(index, f"0{kept}b") if kept else "": max(0.0, float(value)) for index, value in enumerate(values)}

    def expectation_pauli(self, label):
        if not isinstance(label, str) or len(label) != self.num_qubits or set(label) - set("IXYZ"):
            raise ValueError("QuantumBridge MPS Pauli labels must match the state width.")
        env = np.ones((1, 1), complex)
        for tensor, char in zip(self._tensors, label):
            self._guard((tensor.shape[0] ** 2 + tensor.shape[2] ** 2) * 8)
            env = np.einsum("ab,asr,st,btv->rv", env, tensor.conj(), pauli_matrix(char), tensor, optimize=True)
        return complex(env[0, 0])

    def project(self, wire, outcome):
        self._wires((wire,))
        if outcome not in (0, 1):
            raise ValueError("QuantumBridge MPS measurement outcomes must be zero or one.")
        self._move_center(wire)
        tensor = self._tensors[wire]
        probability = float(np.clip(np.linalg.norm(tensor[:, outcome, :]) ** 2, 0, 1))
        if probability:
            tensor[:, 1 - outcome, :] = 0
            tensor /= np.sqrt(probability)
        return probability

    def measure(self, wire, rng):
        self._wires((wire,))
        self._move_center(wire)
        p0 = float(np.clip(np.linalg.norm(self._tensors[wire][:, 0, :]) ** 2, 0, 1))
        outcome = int(rng.random() >= p0)
        self.project(wire, outcome)
        return outcome

    def to_dict(self):
        return {"format": "quantumbridge.mps.v1", "tensors": [
            {"real": tensor.real.tolist(), "imag": tensor.imag.tolist()} for tensor in self._tensors
        ], "discarded_weight": self.discarded_weight, "truncations": self.truncations,
                "max_bond_dim": self.max_bond_dim, "cutoff": self.cutoff,
                "peak_bond_dimension": self.peak_bond_dimension}

    @classmethod
    def from_dict(cls, payload, *, max_memory_mb=1024):
        if payload.get("format") != "quantumbridge.mps.v1":
            raise ValueError("Unsupported QuantumBridge MPS serialization format.")
        from quantumbridge.ir.qb_ir import matrix_from_ir

        result = cls([matrix_from_ir(value) for value in payload["tensors"]], max_memory_mb=max_memory_mb,
                     max_bond_dim=payload.get("max_bond_dim"), cutoff=payload.get("cutoff", 1e-16))
        weight, count = payload.get("discarded_weight", 0.0), payload.get("truncations", 0)
        if not isinstance(weight, Real) or not np.isfinite(weight) or weight < 0 or not isinstance(count, Integral) or count < 0:
            raise ValueError("Invalid QuantumBridge MPS truncation metadata.")
        result.discarded_weight, result.truncations = float(weight), int(count)
        peak = payload.get("peak_bond_dimension", result.peak_bond_dimension)
        if isinstance(peak, bool) or not isinstance(peak, Integral) or peak < result.peak_bond_dimension:
            raise ValueError("Invalid QuantumBridge MPS peak bond metadata.")
        result.peak_bond_dimension = int(peak)
        return result
