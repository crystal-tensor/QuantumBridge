# Stage 11E Native Pauli Algebra

Date: 2026-10-19

## Problem and Scope

Previously Pauli was a one-qubit multiplication helper. PauliList composition
dropped complex phase, used a Cartesian product of rows and returned the wrong
operator for noncommuting inputs. For example X times Y became Z instead of iZ.
This made its names insufficient evidence of callable Qiskit behavior.

The replacement retains the phase exponent and multi-qubit Pauli body through
every implemented operation. This is shared mathematical infrastructure under
the four product categories: scientific computing, finance, industrial
optimization and quantum security.

## Executable Behavior

- Phase-aware labels, symplectic construction, dimensions and dense matrices.
- Pauli compose/dot, matrix multiplication, tensor/expand, inverse/adjoint,
  transpose/conjugate, integer powers, indexing and scalar phases.
- Subsystem composition with explicit Qiskit-style qubit indices.
- PauliList row broadcasting, Cartesian tensor, phase-preserving transforms,
  commutation, sorting, uniqueness, indexing and assignment.
- Pairwise commutation matrices and greedy commuting groups.
- Seeded random Pauli and PauliList generators.
- Direct statevector and density-matrix expectation/evolution with Pauli.
- Native matrix instructions and QNode execution with the same observable.

The QNode integration also fixes a generic matrix-conversion defect: a qubit
count was passed positionally to to_matrix(), accidentally activating the
sparse-output flag. Width is now passed by keyword.

## Migration

- Pauli's @ now returns a phase-aware Pauli. The old phase/operator tuple is
  available with multiply().
- PauliList compose now applies the other operator after self and broadcasts
  compatible rows. dot() and @ use the opposite order.
- PauliList commutes() returns row-wise results. Use commutation_matrix() for
  the old all-pairs relation.
- Symplectic columns and Pauli qargs use rightmost-qubit-zero ordering.
  Circuit/QML wires keep their established leftmost-wire-zero ordering.
  Whole-operator matrices use the displayed label tensor order.
- Existing sparse-operator internal products explicitly use multiply(), so
  their native contract is preserved.

## Verification

- Exhaustive products of the one-qubit Pauli group match dense matrices.
- All 8,192 compose/dot products of the two-qubit group match Qiskit 2.6.0.
- Subsystem, broadcast, transform, sort, unique and phase-mutation behavior
  match the installed Qiskit reference.
- Seeded Pauli and PauliList labels match Qiskit for every tested seed.
- Native QNode expectations match PennyLane 0.42.3 to 1e-12 for three
  observables and three parameter values.
- The runnable example reports iZ for X times Y and -1 for the Bell-state
  expectation of -XX.

Clean tracked-tree validation:

| Check | Result |
| --- | --- |
| Core environment without Qiskit or PennyLane | 559 passed, 72 optional skips |
| Installed ecosystem environment, complete suite | 663 passed, 4 skips |
| Coverage measured by explicit pytest-cov invocation | 84.49% statement coverage |
| Existing local matrix script | Exit 0; all available profiles passed |
| Focused Qiskit 2.6.0 / PennyLane 0.42.3 environment | 80 passed |

The local matrix skipped optional profiles whose upstream packages are absent.
Coverage was measured explicitly because the existing matrix's plugin
detection skipped that step. Every validation ran against a clean archive
containing only tracked files and this staged change; unrelated Router and
Studio worktree files were excluded.

## Remaining Boundaries

Clifford-based Pauli evolution, layout application, arbitrary indexed qubit
insertion and full writable-array view semantics are not implemented here.
Sparse output uses optional SciPy. Commuting groups are valid greedy
partitions; an identical Qiskit graph-coloring result is not promised.
This slice does not establish complete Qiskit or PennyLane parity.

The algebra and grouping run classically. Observable-measurement circuits can
feed backend execution; this slice does not claim a new Quafu hardware result.
No frontend or Studio files are part of this change.
