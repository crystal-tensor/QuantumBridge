# Stage 11L Compiler Gap Audit

Baseline: local `d0cca5b`, last verified remote `8e47c9b`. Existing unpublished
Stage 11K is retained. Audit date: 2026-10-19. Native Implementation; no source port.

## Findings Before This Batch

- No native quantum/classical dependency DAG or executable static scheduler.
- PassManager rejected all structured runtime blocks. Analysis lifetime,
  invalidation, prerequisites and bounded iterative execution were absent.
- Target declared only capacity, basis, coupling and dt; not per-qargs
  properties, durations, error, feedback or timing alignment.
- SWAP insertion selected the first neighbor but neither rewrote the original
  nonlocal operands nor tracked their permutation. Reproduction:
  `Circuit(3).x(0).cx(0,2)` on line 0-1-2 produced 010 instead of 101 and
  retained an illegal CX(0,2). Level 0 did not actually route.
- Phase-to-RZ translation discarded the scalar phase, invalidating exact
  operators and coherent control of compiled definitions.
- Layout lacked validation, inverse and final routing mapping.
- Rotation optimizers cast symbolic angles to float and could not preserve
  first-order differentiation through split/merged compiled expressions.
- MQT and QOS-UQCI/Quafu integration were not native transpiler substitutes:
  inventory/passthrough/offline mock metadata are not compiler correctness.

## Reused Architecture

Changes extend `quantumbridge/compiler/`, native Circuit/Operation/Measurement,
typed parameter AST and Stage 11J ControlBlock, rather than creating a second
compiler framework. DAG transformations have native wire interfaces. Existing
CompilerPass/PassResult remain the pass protocol, with DAG validation around
each pass. The pass protocol itself is not claimed to equal Qiskit's DAG API.

Native static translation/routing/optimization and static ASAP/ALAP are actual
execution paths. Dynamic bodies recursively compile in lexical scope and
restore branch-local physical permutations. Runtime loop depth/global dynamic
timing remain explicit partial/unsupported contracts, not static metadata
claimed as hardware scheduling. Initial layout and final physical permutation
are reported separately; external logical decoding is required when requesting
an unrestored permutation. Compiled QNodes currently require restored identity
layout and equal width, rejecting measurement mappings not yet implemented.

## Remaining Scope

No arbitrary unitary synthesis, all-gate decomposition, SABRE/optimal routing,
pulse calibration scheduling, dynamic hardware timing, plugin parity, coherent
symbolic controlled global phase, all QNode interfaces or full SDK replacement.
No secret was read and no cloud job was submitted in this batch. DeviceSpec and
Quafu-style backend configuration evidence is offline only; it does not satisfy
the owner's separate real Quafu hardware acceptance requirement.
