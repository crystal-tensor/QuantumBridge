# Remaining Full Functional Parity Gaps

Date: 2026-10-20; Stage 11O-B6 checkpoint from local `bd88f88`.
Full independent Qiskit/PennyLane functional replacement remains ACTIVE /
INCOMPLETE. This is a remaining-work ledger, not a reduced definition of success.
The pinned public versions used as test oracles do not prove all versions or
all current public APIs. Inventories, adapters and green tests are not parity.

## Prioritized Core Work

| Priority | Capability still required | Existing evidence versus missing final contract |
| --- | --- | --- |
| 1 | Complete measurement/transform semantics | B1-B6 execute real supported graphs. Complete dispatcher, reset/postselection, general classical measurement expressions, conditional MCM, noisy feedback, snapshots/full-state contracts and arbitrary transforms remain incomplete |
| 2 | Full differentiable interfaces | Native first-order CPU Torch/Autograd are tested. JAX/TF end-to-end, simulator backprop, higher-order differentiation, capture/Catalyst and GPU contracts remain unimplemented/unsupported |
| 3 | Full derivative/device protocols | Actual shift/adjoint/Jacobian products exist. Matrix-free VJP, all generators/gradient transforms, metric/QNG semantics, loop-aware differentiation, stochastic and plugin derivative protocols remain incomplete |
| 4 | Complete QNode/devices/plugins | Existing native runtime supports typed trees, sampling and branches. Full constructor options, executors, dynamic-shot/device-vjp/capture and default.qubit/lightning/mixed/remote/plugin contracts remain incomplete |
| 5 | All operations and template families | Eight template families execute. Complete UCCSD/QAOA/arithmetic/state preparation synthesis, broadcasting, all operation families and compatible object/serialization contracts remain incomplete |
| 6 | Complete QuantumCircuit/classical API | Parameter algebra/control flow/compose/control/inverse/power execute bounded subsets. All signatures/types/scopes/conditions, calibration and instruction scheduling remain incomplete |
| 7 | Complete circuit.library | Native bounded gates, ansatz and arithmetic/data encoding are not the full gate/template/synthesis/data-preparation catalog |
| 8 | Complete quantum_info | Native vector/density/operator/Clifford/Pauli/channels/metrics/random/MPS subsets exist. All dimensions/subsystems, synthesis, general maps and public containers/options remain incomplete |
| 9 | Complete transpile/PassManager/Target | Real DAG translation/routing/static schedules execute. Arbitrary synthesis, full pass/plugin/flow protocols, full backend calibration schemas and dynamic/pulse timing remain incomplete |
| 10 | Complete Aer | CPU vector/density/tableau/MPS and Save/Set/noise subsets execute. Full methods/options/aggregation/readout, optimized performance, GPU/parallelism and extended methods remain incomplete |
| 11 | Complete Primitives V2 | Native PUB/Job/results/counts/observables execute. Full broadcast, precision/shots/containers/errors and provider contracts remain incomplete |
| 12 | Complete Provider/Backend/Job | Native local lifecycle exists. Complete discovery, options, cancellation, true async and authorized remote service behavior remain incomplete |
| 13 | Complete QPY and OpenQASM 2/3 | Real QPY v13 plus bounded QASM2/3 parsing/exporting exist. Other QPY versions, complete languages/types/functions/arrays/includes and all object families remain incomplete |
| 14 | Full algorithms/optimizers | Native bounded eigen/phase/amplitude/VQE/QAOA/Grover slices are not all algorithm families, results, optimizers and execution glue |
| 15 | Full qchem / Nature | Real hydrogen s-shell/RHF/fermionic/JW workflows exist. Differentiable HF, other elements/basis sets/angular momentum, open shells, properties, active spaces/tapering, full UCCSD and all chemistry APIs remain incomplete |
| 16 | Full kernels/QNN/resources/qcut/shadows | Existing executable examples/subsets do not establish complete families, derivative contracts, device integration or public interfaces |
| 17 | Complete industry ecosystem | Finance/Optimization/ML/Experiments/Dynamics and all remaining ecosystem projects need full independent functions, actual composed workflows and validated results; optional upstream object lookup is not completion |
| 18 | Actual authorized remote execution | IBM Runtime full service behavior and real Quafu/QOS-UQCI backend/job/target evidence remain incomplete. A token, offline/mock result or simulator success is not hardware evidence |

The next implementation stage should be selected against these concrete gaps
after the joint review. This ordering does not remove any requirement from the
full goal or declare lower-priority functions complete.

## Explicit B6 Limits Still Open

Coherent deferral currently rejects reset/postselect (including impossible
selection), configured noisy feedback, arbitrary nonunitary/Kraus operations,
conditional measurements, runtime loops, Store/arithmetic, measurement-derived
gate parameters, mid-state snapshots and undefined full-state requests.
Bounded Boolean records and numeric probabilities do not implement the entire
MeasurementValue API. Opaque controls/dense observable remapping, arbitrary
classical memory and full Capture/public dispatcher semantics remain partial.
Fresh ancillas consume actual device/Target capacity. Default output-wire
handling and native `records=` signatures are documented native behavior,
not a claim of identical public API shape. See the B6 implementation report.

## Chemistry And Hardware Truthfulness

Native H2 geometry-dependent energy and gradients do not establish all
molecules, ground-state convergence, complete materials calculations or a
fully differentiable electronic-structure pipeline. Conditional-feedback
chemistry examples need not conserve electrons. Real hardware cannot be
assumed to expose simulator statevector/density APIs or unlimited ancillas;
mapping and measurement limits need actual authorized backend validation.

Industry organization remains the owner's four categories and 19 subdomains:
scientific computing, finance, industrial optimization and quantum security.
That taxonomy is not evidence that their chemistry/biology/materials, financial,
logistics/energy or security workflows have all been implemented and verified.
Core functional implementation remains first priority; Studio remains last.

## Publication And Evidence Gaps

The retained local 11M/11N/11O-C/11O-A/B1-B5 chain is not proof of publication.
Prior workflow OAuth/network limitations have not been bypassed. A fresh
successful fetch, fast-forward verification, ordinary authorized push and
matching new-SHA Actions jobs are still required before claiming remote CI.
The known user untracked Router attribution failure is separate from the
tracked/index snapshot and is not silently repaired or included here.

Final completion must verify every named API/behavior and required workflow.
No local checkpoint, total pytest count, package line coverage or inventory
justifies marking the entire full replacement goal complete.
