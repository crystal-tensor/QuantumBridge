# Stage 11O-C Native Chemistry Checkpoint

Date: 2026-10-20. Starting local commit:
`0d00362191efb85d2d7b1d14b15d5234156a74fb`.
This report covers the molecular electronic-structure part of Stage 11O.
Stage 11O as a whole is NOT complete: native Templates and multi-Tape
Transforms remain required work, not optional follow-ups. Full independent
Qiskit/PennyLane parity remains ACTIVE / INCOMPLETE.

## Actual Computation

The existing chemistry models were enhanced rather than replaced by a parallel
SDK wrapper. Native runtime uses NumPy and standard math only. Actual chain:

```text
Molecule geometry and explicit units
  -> normalized contracted s-Gaussian AO basis
  -> overlap / kinetic / nuclear attraction / electron repulsion
  -> iterative closed-shell Roothaan-Hall RHF
  -> MO one-/two-electron integrals
  -> spin-orbital FermionicOp
  -> native Jordan-Wigner Pauli operator
  -> electron-number-sector exact diagonalization
  -> HF reference / native excitation circuit / native QNode VQE
```

No molecular Hamiltonian or energy is obtained from a preset lookup. The old
Stage 9D fixed H2/LiH examples remain explicitly educational reference models;
they are not evidence for this new electronic-structure implementation.

## API And Mathematical Conventions

| API | Native behavior and boundary |
| --- | --- |
| Molecule | Elements, electron count, charge/multiplicity/spin, finite real 3D coordinates and explicit Bohr/Angstrom units |
| build_basis | Normalized hydrogen STO-3G s contractions; other elements/angular types/bases reject |
| primitive_overlap / kinetic / attraction / repulsion | Independent normalized s-Gaussian analytic formulas in atomic units |
| boys0 | Analytic erf form with stable small-argument expansion |
| molecular_integrals | Actual geometry-derived S, T, V, core H, chemist ERI and nuclear repulsion |
| run_restricted_hartree_fock | Symmetric overlap orthogonalization, Fock, orbital/density update, energy/residual convergence and explicit failure |
| electron_integrals | Real RHF AO-to-MO one- and four-index two-electron transform |
| build_fermionic_hamiltonian | Correct spin expansion and nuclear constant, normal ordered using CAR |
| molecular_hamiltonian_native | Actual untapered Jordan-Wigner molecular Pauli Hamiltonian with provenance |
| exact_ground_energy | Bounded eigensolve in the molecule's electron-number sector, nuclear included once |
| hf_state / excitations / excitations_to_wires | Occupation reference, spin-selective singles/doubles and ordered wire ranges |
| apply_fermionic_excitation | Exact commuting-Pauli circuit for a single/double excitation generator, not an upstream ansatz call |

Basis numerical data: H STO-3G three exponents and three coefficients from
MolSSI BSE version 1, revision 2018-06-19, original reference Hehre/Stewart/Pople
1969 (DOI 10.1063/1.1672392). Source/notice is retained in
`LICENSES/BSE_DATA_NOTICE.txt`. Only scientific numerical input is included;
no BSE implementation/test/package is copied and no runtime download occurs.

Primitive normalization is `(2 alpha / pi)^(3/4)` and each contraction is
renormalized from its actual overlap. Boys `F0(t)` is evaluated as the integral
of `exp(-t u^2)` from 0 to 1, with its zero limit treated analytically.
Nuclear energy is computed from charge products divided by Bohr separations.
Angstrom conversion is pinned consistently to CODATA 2018
`1 Bohr = 0.529177210903 Angstrom`, not inferred from raw coordinate magnitudes.

RHF uses `F = h + J[D] - K[D]/2` and electronic energy
`sum(D * (h+F))/2`, with doubly occupied lowest orbitals. Returned converged
density is the occupied-orbital projector, not a fractionally populated mixing
buffer. Nonconvergence carries actual iteration history and raises; no fitted
reference energy is substituted. RHF energy is not exact correlated energy.

Spatial ERI convention is chemist `(pq|rs)`. Spin modes are interleaved
`spatial 0 alpha,beta; spatial 1 alpha,beta; ...`; native bitstrings put mode
zero first. The two-body coefficient is `1/2 (pq|rs)` multiplying
`a+_(p,sigma) a+_(r,tau) a_(s,tau) a_(q,sigma)`. Nuclear repulsion appears
once as the identity coefficient. Untapered H2 therefore has four qubits.

## Repaired Algebra

The previous normal-order implementation only sorted creators/annihilators.
It now includes CAR minus signs, same-mode identity contractions and nilpotent
equal ladders, with bounded iterative expansion. A separate occupation-basis
matrix action does not use the Pauli mapper and supplies an independent check.
Jordan-Wigner now supports general bounded complex ladder products and the
preceding-mode Z string; zero coefficients remain zero. Hermitian chemistry
observables and non-Hermitian general operators are not conflated: conversion
to a real Hamiltonian rejects significant imaginary Pauli coefficients.

## Numerical Evidence

All values below were computed from the geometry during execution, not used
as algorithm inputs. Energies include nuclear repulsion, in Hartree.

| H-H distance (Bohr) | Native RHF | Native exact electron sector |
| --- | --- | --- |
| 1.0 | -1.0659994615565616 | -1.0789697686757536 |
| 1.4 | -1.116714325175768 | -1.1372759437827162 |
| 2.0 | -1.0491709025712759 | -1.0884963088067678 |
| 3.0 | -0.885275000897717 | -0.985156825524814 |

At 1.4 Bohr the native RHF iteration history has two actual Fock/density
iterations (this symmetric two-function example converges immediately after
the first update). Mixed/damping execution and explicit nonconvergence also
have independent tests. AO nuclear energy is `0.7142857142857143`.

Independent public PySCF comparison at the same geometry/basis/units gives RHF
`-1.116714325062552`; absolute difference is about 1.13e-10 Hartree. AO maximum
absolute differences: overlap 3.30e-10, kinetic 3.64e-9, attraction 2.08e-9,
ERI 9.04e-10. Public PennyLane exact energy is `-1.137275943839282`, differing
by about 5.66e-11 Hartree. Small basis-parameter precision differences between
public libraries are below fixed tolerances. Tests fix integral and energy
absolute tolerance at 1e-8 before comparisons, without loosening after failure.

The native one-double-excitation VQE example starts at HF, performs 70 actual
native adjoint gradient steps and reaches `-1.1372759437827038`, about 1.24e-14
above this problem's exact energy. This favorable two-configuration example
does not establish arbitrary molecular VQE convergence or complete UCCSD.
Shift, adjoint, Torch backward and Autograd agree on fixed-Hamiltonian
variational derivatives. Geometry finite differences are checked separately;
integral/SCF response and fully differentiable HF are NOT implemented.

## Verification Status

Targeted checkpoint: 56 native tests (two optional framework tests) plus 15
public comparisons; main installed environment passes all 71. Public tests
include 12 distinct PennyLane contracts and three optional independent PySCF
checks. SDK-free examples execute integrals, RHF/curve and VQE with assertions.

Final clean tracked-tree snapshot: `/tmp/qb-stage11o-qchem-verified-hvpH9f`, built
from the starting commit plus this checkpoint's staged changes. Unrelated
user Router/Studio files were not included or modified. Verified receipts:

| Gate | Result |
| --- | --- |
| SDK-free full pytest | 1174 passed, 121 skipped |
| Main installed full pytest with package-wide coverage | 1437 passed, 4 skipped |
| Alternate Qiskit/PennyLane full pytest | 1397 passed, 44 skipped |
| Main coverage | 20289 / 22946 statements, 88.42063976292164% |
| Coverage exclusions | 68 existing excluded lines, unchanged |
| Local matrix | Exit 0, full script, generated inventories confined to snapshot |
| compileall | Exit 0 for quantumbridge, examples and scripts |
| Focused legal, ledger and no-vendor tests | 7 passed |
| Three new SDK-free examples | All exit 0; PYTHONPATH points to clean snapshot |
| Both isolated environment pip checks | No broken requirements |
| Global environment pip check | Existing pyquafu/NumPy and WeasyPrint/tinycss2 conflicts remain |

Coverage exceeds the Stage 11N baseline 88.18100757913508% without new
exclusions. Newly added basis, excitation, Gaussian, limits, molecular
Hamiltonian, SCF and qchem export modules each exceed 90% line coverage.
An existing optional PySCF adapter test used a physically inconsistent
one-electron hydrogen singlet. Its fixture now explicitly requests a doublet;
the molecule validator was not weakened and the adapter is still only an
availability/provenance check, not a native open-shell solver.

Public FermiSentence in the pinned SDKs has no `normal_order` method. The
normal-order oracle instead compares the native CAR-normal-ordered matrix
against public Jordan-Wigner of the original unordered word; this compares
the physical operators, not a nonexistent SDK method or a token ordering.

## Safety And Remaining Scope

QChemLimits bounds atoms, basis functions, spin orbitals, integral tensor bytes,
SCF iterations and Hamiltonian terms. Reusing an SCF result still enforces the
caller's limits before allocating MO tensors; a forbidden-einsum test verifies
that rejection precedes contraction. Explicit dense Fock/Pauli matrices are
bounded to ten modes; no implicit dense expansion for larger problems.
Unsupported basis/element/open-shell/mapping requests fail without SDK or
network fallback. No token, hardware, cloud, tag/release or Studio work occurs.
Existing user Router/Studio files remain untouched.

Still missing: non-hydrogen and larger/angular basis libraries, open-shell
methods, active spaces/tapering, general properties, correlated classical
methods, complete UCCSD/template families, molecular integral/SCF analytic
geometry derivatives and differentiable HF. General Templates and multi-Tape
Transforms are still unfinished Stage 11O tasks. Full parity is not claimed.

Stage 11M/11N local ancestors remain preserved. Origin tracking is stale after
the prior fetch timeout; existing workflow authorization remains unresolved.
No new remote publication or exact-SHA CI is claimed. This scientific
checkpoint may be committed with an accurately scoped message while full
Stage 11O work continues. Never remove workflow or rewrite history to publish.

## Public References

- [MolSSI BSE H STO-3G numeric data](https://www.basissetexchange.org/api/basis/sto-3g/format/json/?elements=1)
- [Original STO-3G paper](https://doi.org/10.1063/1.1672392)
- [Molecular Gaussian integral formulas, publisher appendix](https://booksite.elsevier.com/9780444594365/downloads/16755_10036.pdf)
- [PennyLane molecular Hamiltonian API](https://docs.pennylane.ai/en/stable/code/api/pennylane.qchem.molecular_hamiltonian.html)

References are mathematical/data/API contracts only, not copied implementation
or a claim that every API on those sites is supported.
