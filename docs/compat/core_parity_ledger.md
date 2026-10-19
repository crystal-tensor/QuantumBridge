# Core Functional Parity Ledger

Updated: 2026-10-19, Stage 11M tested checkpoint, starting from published `45fe338`.
This is the single current-status view. Full Qiskit/PennyLane functional
replacement remains **incomplete**. Line coverage, inventories, passthrough and
green CI are not proof of complete API coverage.

NATIVE_IMPLEMENTED means executable native code exists; NATIVE_TESTED adds
independent behavioral tests; UPSTREAM_DIFFERENTIAL_TESTED adds public black-box
evidence for the stated scenarios only. PARTIAL/UNSUPPORTED/NOT_STARTED describe
remaining scope. Stage 11M passes the three clean tracked-tree local gates;
publication/exact-SHA CI is a separate receipt, not inferred from prior CI.

## Current Core Status

| Capability | Current evidence/status | Remaining functional work |
| --- | --- | --- |
| QuantumCircuit | NATIVE_TESTED; PARTIAL: typed storage, parameters, arithmetic, compose/control/inverse/power and runtime blocks | Complete builders/signatures, all types/scopes, calibrations and instruction schedules |
| Circuit library | NATIVE_TESTED; PARTIAL: standard gates, bounded ansatz/arithmetic/encoding | All library families and edge cases |
| Quantum information | NATIVE_TESTED; PARTIAL: vector/density/operators/Pauli/channels/metrics/random/Clifford/MPS | Full dimensional, subsystem, synthesis and general-map contracts |
| DAG/mutation/roundtrip | NATIVE_TESTED; PARTIAL: actual wire/classical dependencies and validation | Full graph API and noncontiguous contraction |
| PassManager/PropertySet | NATIVE_TESTED; PARTIAL: analysis lifetime, invalidation, prerequisites, callbacks, stages and limits | Full DAG-pass/flow-controller/plugin protocol |
| Target/CouplingMap/Layout | NATIVE_TESTED; PARTIAL: properties, directed paths, initial/final mapping | Full backend/calibration schema and optimal search |
| Basis translation/routing | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: exact phase, directed routing and permutation tracking | Arbitrary/all-gate synthesis and optimal/stochastic routing |
| Optimization | NATIVE_TESTED; PARTIAL: safe cancellation/identity/rotation merging | General commutation and synthesis methods |
| Static ASAP/ALAP | NATIVE_TESTED; PARTIAL: real configured durations, dependencies and alignment | Pulse/calibration and global dynamic timing UNSUPPORTED |
| Structured dynamic compilation | NATIVE_TESTED; PARTIAL: if/for/while/switch/store/break/continue actually compile and execute | Remaining branch/layout combinations and dynamic timing |
| Primitives V2 | NATIVE_TESTED; PARTIAL: native Job/PUB/counts/observables and dynamic results | Full broadcasting, precision/shots/containers/error protocol |
| Provider/Backend/Job | NATIVE_TESTED; PARTIAL: native local backends and jobs | Complete discovery/options/async/cancellation/remote contracts |
| Aer methods/noise/save | NATIVE_TESTED; PARTIAL: vector/density/tableau/MPS and CPTP/noise execution | Complete save/set/noise/method/option semantics |
| Algorithms | NATIVE_TESTED; PARTIAL: bounded eigen/estimation and VQE/QAOA/Grover | All algorithm families, optimizers and result contracts |
| Nature/Finance/Optimization/ML/Experiments/Dynamics | PARTIAL: native executable slices and separate optional adapters | Complete independent industry functions; upstream passthrough is not parity |
| IBM Runtime | PARTIAL: offline/optional adapters | Authorized real service execution and complete runtime contracts |
| QNode/device/measurement | NATIVE_TESTED; PARTIAL: native vector/density/MPS/tableau, typed trees and dynamic measurements | Complete constructor/plugins/devices/operations/measurement protocols |
| Native parameter-shift/adjoint | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: actual first-order algorithms and classical chain rule | All generators/transforms, reused parameterized loops and mixed/MPS adjoint |
| VJP/JVP/execute derivatives | NATIVE_TESTED; PARTIAL | Current explicit Jacobian products are not full derivative-device contracts |
| Torch/Autograd | NATIVE_TESTED; PARTIAL: CPU framework graphs with native quantum VJP | GPU, higher order and full interface/device contracts |
| JAX/TF/backprop/capture | NOT_STARTED or UNSUPPORTED as documented | Full end-to-end implementations; array conversion is not autodiff |
| Shot vectors/dynamic gradients/MPS gradients | NATIVE_TESTED; PARTIAL: actual sampling/branches, native shift and finite difference | Complete stochastic/loop/postselection contracts; numerical truncation risk |
| Higher-order derivatives | UNSUPPORTED | First-order guards remain active |
| Compiled QNode gradients | NATIVE_TESTED; PARTIAL: expressions, shared inputs, Torch/Autograd and native gradients | Restored identity/equal-width only; general measurement remapping |
| Templates/qchem/math/resources/kernels/qnn/qcut/shadows | PARTIAL: bounded executable workflows | Full library and differentiation contracts |
| Compiled 100-qubit MPS | NATIVE_TESTED for GHZ-chain with dense APIs disabled | No arbitrary-entanglement efficiency claim |
| Quafu/QOS-UQCI/industry taxonomy | PARTIAL: offline target/configuration and existing adapters, four categories/19 subdomains | Real authorized backend/job evidence and complete industry workflows |

## Serialization Status

| Capability | Stage 11M current status | Remaining gate |
| --- | --- | --- |
| QASM2 parsing/exporting/files/strings | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: 27 native + 10 bilateral public scenarios | Full language/object API is not claimed |
| QASM2 custom gates | NATIVE_TESTED via budgeted semantic expansion | Full definition-object identity/opaque execution not claimed |
| QASM2 conditional subset | NATIVE_TESTED for complete-register equality | Nonrepresentable dynamic/phase/delay objects explicitly reject |
| QASM3 typed AST/source lowering | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: typed source executes, 10 bilateral public scenarios | Complete language types/functions/arrays remain partial; standard U vs SDK dialect explicit |
| QASM3 control flow | NATIVE_TESTED: 14 independent dynamic sources + 3 legacy snapshot cases | Full types/capture/subroutine behavior remains partial |
| QASM3 timing/custom definitions | NATIVE_TESTED subset: real delay units/expanded definitions | Full timing algebra and object fidelity partial |
| QASM3 OpenPulse/defcal/stretch/extern/complex arrays | UNSUPPORTED | Must reject without deleting statements |
| QPY native reader/writer | UPSTREAM_DIFFERENTIAL_TESTED; PARTIAL: 18 native binary + 10 bilateral public + multicircuit cases | Real public version 13 binary, not an IR envelope; unsupported branches below |
| QPY format versions | Version 13 only; all other versions UNSUPPORTED | Version is distinct from source SDK version |
| QPY parameters/global phase | UPSTREAM_DIFFERENTIAL_TESTED: UUIDs, arithmetic replay, symbolic/numeric phase | Full symbolic function/vector/object encoding partial; native equality remains name-based |
| QPY dynamic circuits/custom instructions/layout | UNSUPPORTED at this checkpoint | Do not infer completion from static QPY success |
| QPY non-dt Delay | UNSUPPORTED | Tested v13 SDK payload loses units; native export rejects; QASM3 retains units |
| Cross-format interchange | NATIVE_TESTED; PARTIAL | Default lossless semantics or rejection; explicit external root metadata only |
| Serialization gradient/compiler/MPS preservation | NATIVE_TESTED: six gradient scenarios in two formats, compiled routing/phase/order, 100-qubit non-dense MPS | Does not serialize Python callables or promise arbitrary MPS efficiency |
| Parsing security/limits | NATIVE_TESTED: hostile includes/code-like source, lengths/flags/versions/replay/identity/numeric budgets | Full protocol and all source types remain partial |

No QPY or serialization subsystem is marked complete merely because a file has
the correct header. Actual independent readers/writers and both SDK versions
must load and execute the resulting circuits. Hardware/cloud work and Studio
are outside this serialization batch.

## Evidence History

The obsolete pre-reconciliation text is preserved verbatim in
[Stage 11L ledger snapshot](history/core_parity_ledger_stage11l_snapshot.md);
it is historical, not a second current status table.

- [Stage 11J dynamic execution report](../implementation/stage11j_native_dynamic_control_flow_report.md)
- [Stage 11K differentiation report](../implementation/stage11k_native_qnode_autodiff_report.md)
- [Stage 11L compiler report](../implementation/stage11l_native_transpiler_report.md)
- [Stage 11M gap audit](../implementation/stage11m_serialization_gap_audit.md)
- [Stage 11M implementation/test report](../implementation/stage11m_native_qasm_qpy_serialization_report.md)

Stage 11L exact-SHA CI: 39259350086, 22/22 success. Its clean local runs:
SDK-free 899 passed/116 skipped, installed 1090/4, alternate 1054/40, measured
line coverage 87.5253299%, local matrix exit 0. These are Stage 11M baselines,
not proof that new serialization changes pass. Stage 11M local results are
1030/117 SDK-free, 1252/4 installed, 1216/40 alternate; 162 new serialization
cases pass in each SDK environment; coverage 87.8801865%. Next work remains
remaining serialization branches, Aer save/set/noise, complete templates/qchem/transforms and
JAX/TF/capture/higher-order autodiff. Studio stays last.
