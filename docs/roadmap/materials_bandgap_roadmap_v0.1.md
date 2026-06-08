# Materials Band Gap Roadmap v0.1

P2 does not implement real materials band gap prediction.

## 1. Molecules vs Materials

Molecular ground-state energy estimates finite molecular systems. Materials band
gaps require periodic systems and electronic structure methods suited to solids.

## 2. Requirements for Real Band Gaps

Realistic band gaps typically need periodic boundary conditions, DFT or beyond,
k-point sampling, basis or pseudopotential choices, and excited-state or
quasiparticle corrections.

## 3. P2 Boundary

P2 does not promise real material band gaps or materials prediction.

## 4. P2 Toy Scope

P2 may plan toy tight-binding, Fermi-Hubbard, and lattice Hamiltonian demos.

## 5. P3 / P4 Candidates

Future phases may consider PySCF periodic adapters, ASE adapters, Quantum
ESPRESSO adapters, and simple band-structure workflows.

## 6. Risks

Band gaps are method-sensitive, basis-sensitive, and not reliable without
careful scientific validation.

## 7. Public Wording

Do not market QuantumBridge as a materials prediction tool.
