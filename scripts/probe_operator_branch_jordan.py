# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""Offline high-precision oracle for the exact binary input, never runtime math.

Uses an already installed mpmath only as an independent development oracle.
No SDK implementation/source is inspected and no dependency is installed.
"""

import argparse
import cmath
import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np

from quantumbridge.information import Operator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("output/operator-branch-jordan/post_repair_exact_input.json"))
    parser.add_argument("--public", action="store_true")
    args = parser.parse_args()
    mp.mp.dps = 100
    indices = np.arange(2)
    fourier = np.exp(2j * np.pi * np.outer(indices, indices) / 2) / np.sqrt(2)
    np.testing.assert_allclose(fourier.conj().T @ fourier, np.eye(2), atol=8e-16, rtol=0)
    jordan = -np.eye(2, dtype=complex) + np.diag([.3], 1)
    matrix = fourier @ jordan @ fourier.conj().T
    exact_input = mp.matrix([[mp.mpc(complex(z).real, complex(z).imag) for z in row] for row in matrix])
    center = (exact_input[0, 0] + exact_input[1, 1]) / 2
    split = mp.sqrt(((exact_input[0, 0] - exact_input[1, 1]) / 2)**2 + exact_input[0, 1] * exact_input[1, 0])
    left, right = center + split, center - split
    cut = math.pi * 1e-12
    rotation = mp.mpf(cut)
    fixture = {"oracle": "100-digit exact-binary-input 2x2 spectral interpolation; not rounded ideal Jordan limit",
               "matrix_hex": [[[complex(z).real.hex(), complex(z).imag.hex()] for z in row] for row in matrix],
               "eigenvalues_100_digits": [str(left), str(right)], "branch_cut_rotation": cut,
               "schur_vs_actual_input_warning": "backward-stable Schur perturbations can cross this discontinuous branch cut",
               "cases": []}
    for p in (.5, .3, -.3):
        exponent = mp.mpf(p)

        def power(z):
            return mp.exp(exponent * (mp.log(z * mp.exp(-1j * rotation)) + 1j * rotation))

        ref = power(right) * mp.eye(2) + (power(left) - power(right)) / (left - right) * (exact_input - right * mp.eye(2))
        rounded = np.array(ref.tolist(), dtype=complex)
        try:
            native = Operator(matrix).power(p, branch_cut_rotation=cut).data
            refusal = None
        except np.linalg.LinAlgError as error:
            native, refusal = None, str(error)
        phase = cmath.phase(-cmath.exp(-1j * cut)) + cut
        diagonal = cmath.exp(1j * p * phase)
        ideal = fourier @ (diagonal * np.eye(2) - p * diagonal * np.diag([.3], 1)) @ fourier.conj().T
        row = {"p": p, "reference": [[[complex(z).real, complex(z).imag] for z in line] for line in rounded],
               "native": None if native is None else [[[complex(z).real, complex(z).imag] for z in line] for line in native],
               "numerical_refusal": refusal,
               "max_error_to_actual_input_oracle": None if native is None else float(np.max(abs(native - rounded))),
               "relative_error_to_actual_input_oracle": None if native is None else float(np.max(abs(native - rounded)) / np.max(abs(rounded))),
               "distance_from_ideal_Jordan_limit": float(np.max(abs(rounded - ideal))),
               "input_unchanged": bool(np.array_equal(matrix, fourier @ jordan @ fourier.conj().T)),
               "native_all_finite": None if native is None else bool(np.isfinite(native).all())}
        if p == .5:
            row.update(high_precision_sqrt_residual=str(mp.norm(ref @ ref - exact_input)),
                       rounded_reference_sqrt_residual=float(np.max(abs(rounded @ rounded - matrix))),
                       native_sqrt_residual=None if native is None else float(np.max(abs(native @ native - matrix))))
        fixture["cases"].append(row)
    if args.public:
        fixture["public_differential"] = public_differential(fixture)
    path = args.output
    if path.name.startswith("pre_repair"):
        raise ValueError("the original pre-repair evidence is immutable")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fixture, indent=2), encoding="utf-8")
    print(json.dumps({"artifact": str(path), "cases": [
        {key: value for key, value in row.items() if key not in {"reference", "native"}} for row in fixture["cases"]],
        "public_summary": fixture.get("public_differential", {}).get("summary")}, indent=2))


def public_differential(fixture):
    import qiskit
    from qiskit.quantum_info import Operator as PublicOperator

    records = []

    def observe(name, matrix, p, cut, expected, oracle_valid):
        before = matrix.copy()
        row = {"name": name, "p": p, "cut": cut, "oracle_valid_for_actual_input": oracle_valid}
        for label, factory in (("native", Operator), ("public", PublicOperator)):
            try:
                value = factory(matrix).power(p, branch_cut_rotation=cut).data
                error = float(np.max(abs(value-expected)))
                correct = bool(np.allclose(value, expected, atol=3e-12, rtol=3e-13)) if oracle_valid else None
                row[label] = {"outcome": "NUMERIC", "all_finite": bool(np.isfinite(value).all()),
                              "max_difference_to_reference": error if math.isfinite(error) else None,
                              "correct_against_valid_oracle": correct,
                              "matrix": [[[float(z.real), float(z.imag)] for z in line] for line in value] if np.isfinite(value).all() else None}
            except (ValueError, MemoryError, np.linalg.LinAlgError) as error:
                row[label] = {"outcome": "NUMERICAL_REJECTION", "error_type": type(error).__name__, "message": str(error)}
        row["input_unchanged"] = bool(np.array_equal(before, matrix))
        if not oracle_valid:
            row["classification"] = "UNSUPPORTED"
            row["classification_scope"] = "independent actual-input certification unavailable; not counted as a numeric pass"
        elif row["native"]["outcome"] == "NUMERICAL_REJECTION":
            row["classification"] = "INTENTIONAL_SAFETY_DIFFERENCE"
        elif row["native"]["correct_against_valid_oracle"] is False:
            row["classification"] = "NATIVE_BUG"
        elif row["public"].get("correct_against_valid_oracle") is False:
            row["classification"] = "UPSTREAM_DEFECT"
        else:
            row["classification"] = "MATCH" if row["public"]["outcome"] == "NUMERIC" else "INTENTIONAL_SAFETY_DIFFERENCE"
        records.append(row)

    def jordan_function(size, value, coupling, p, cut):
        phase = cmath.phase(value*cmath.exp(-1j*cut))+cut
        coefficient = cmath.exp(p*(math.log(abs(value))+1j*phase))
        result = np.zeros((size, size), complex)
        for distance in range(size):
            for i in range(size-distance):
                result[i, i+distance] = coefficient
            coefficient *= (p-distance)/(distance+1)*coupling/value
        return result

    for size in (2, 3, 4, 6, 8):
        indices = np.arange(size)
        change = np.exp(2j*np.pi*np.outer(indices, indices)/size)/np.sqrt(size)
        matrix = change@(-np.eye(size)+np.diag(np.full(size-1, .3), 1))@change.conj().T
        for cut in (math.pi*1e-12, .001, -.001):
            for p in (.5, .3, -.3):
                valid = size <= 4 and abs(cut) == .001
                expected = change@jordan_function(size, -1, .3, p, cut)@change.conj().T
                if size == 2 and cut == math.pi*1e-12:
                    captured = next(row for row in fixture["cases"] if row["p"] == p)
                    expected = np.array([[complex(real, imag) for real, imag in line] for line in captured["reference"]])
                    valid = True
                observe(f"original-45-size-{size}", matrix, p, cut, expected, valid)
    for value in (-.25, -1., -2.):
        for coupling in (.125, .25, .5):
            nilpotent = coupling*np.array([[1, 1], [-1, -1]], complex)
            matrix = value*np.eye(2)+nilpotent
            for p in (.5, .3, -.3):
                for cut in (math.pi*1e-12, -math.pi*1e-12, .001, -.001):
                    scalar = cmath.exp(p*(math.log(abs(value))+1j*(cmath.phase(value*cmath.exp(-1j*cut))+cut)))
                    observe("strict-binary-Jordan", matrix, p, cut, scalar*(np.eye(2)+p/value*nilpotent), True)
    summary = {"qiskit_version": qiskit.__version__, "records": len(records),
               "native_wrong_against_valid_oracle": sum(row["native"].get("correct_against_valid_oracle") is False for row in records),
               "public_wrong_against_valid_oracle": sum(row["public"].get("correct_against_valid_oracle") is False for row in records),
               "native_numerical_rejections": sum(row["native"]["outcome"] == "NUMERICAL_REJECTION" for row in records),
               "input_mutations": sum(not row["input_unchanged"] for row in records),
               "reference_limit": "for larger rounded near-cut blocks ideal Jordan limit is not a trusted actual-input oracle; no correctness classification"}
    return {"summary": summary, "records": records}


if __name__ == "__main__":
    main()
