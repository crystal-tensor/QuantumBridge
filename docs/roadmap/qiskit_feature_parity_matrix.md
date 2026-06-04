# Qiskit Feature Parity Matrix

Status: Stage 4 draft  
Date: 2026-06-04  

This matrix maps Qiskit-like capability areas to QuantumBridge implementation choices. It is a planning document, not a claim of full compatibility.

| Module | Qiskit feature name | QB current status | Direct dependency? | Migrate code? | Native implementation? | Priority | Complexity | License risk | Trademark risk | Test strategy | Acceptance standard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| circuit | QuantumCircuit-style construction | Partial MVP Circuit | Optional for adapter | No | Yes | P0 | Medium | Low | Medium | import/export/roundtrip tests | Basic H/CX/measure circuit converts both ways |
| circuit library | Standard gate library | Partial MVP gates | No | No | Yes | P1 | High | Low | Low | gate matrix tests | Common gate subset matches math |
| quantum_info | Pauli, Statevector, DensityMatrix | Partial | No | No | Yes | P0 | Medium | Low | Low | numeric tests | Pauli, state, density matrix basics pass |
| primitives | Sampler, Estimator | Partial sampler | No | No | Yes | P0 | Medium | Low | Low | sampler/estimator tests | Counts/probabilities/expectation results pass |
| transpiler | transpilation pipeline | Missing | Optional later | No | Mixed | P2 | High | Medium | Low | pass fixtures from QB scenarios | Simple pass manager can run QB passes |
| providers | Backend, Job, Provider | Missing | Optional for adapter | No | Native interface + adapter | P0 | Medium | Low | Medium | backend adapter tests | QB backend adapter returns Result |
| qasm | OpenQASM import/export | Export partial | No | No | Yes | P0 | Medium | Low | Low | import/export tests | Supported subset roundtrips through IR |
| visualization | circuit drawing | Missing | No | No | Yes | P2 | Medium | Low | Low | text drawer tests | Simple circuit text includes wires and gates |
| synthesis | synthesis tools | Missing | Optional later | No | Later native | P3 | High | Medium | Low | algorithmic tests | Deferred |
| dagcircuit | DAG circuit | Missing | No | No | Native IR graph view later | P2 | High | Low | Low | graph conversion tests | Deferred |
| converters | circuit converters | Partial IR | Optional | No | Mixed | P1 | Medium | Low | Medium | object conversion tests | QB/Qiskit object bridge works for subset |
| pass manager | pass orchestration | Missing | No | No | Yes | P1 | Medium | Low | Low | pass manager tests | Ordered passes run and record metadata |
| result | Result object | MVP Result | No | No | Yes | P0 | Low | Low | Low | serialization tests | Dict output stable |
| pulse | Pulse-related functionality | Missing | Upstream only later | No | No for now | P3 | High | Medium | Medium | none in P0 | Mark split/deprecated/version-sensitive where relevant |
| algorithms | Algorithm interfaces | MVP VQE/QAOA | Optional later | No | Yes | P1 | High | Low | Low | VQE/QAOA tests | Native algorithms pass small cases |
| aer/noise | Aer/noise simulation | Missing | Optional upstream | No | Later minimal native noise | P2 | High | Medium | Medium | adapter tests if installed | Keep Aer as optional dependency |

P0 summary:

- Circuit adapter, QASM subset, Pauli/operator basics, Statevector, DensityMatrix, Sampler, Estimator, Backend adapter, Result adapter.

