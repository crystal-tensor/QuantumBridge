# PennyLane Feature Parity Matrix

Status: Stage 4 draft  
Date: 2026-06-04  

This matrix maps PennyLane-like capability areas to QuantumBridge implementation choices. It is a planning document, not a claim of full compatibility.

| Module | PennyLane feature name | QB current status | Direct dependency? | Migrate code? | Native implementation? | Priority | Complexity | License risk | Trademark risk | Test strategy | Acceptance standard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qnode | QNode-style callable | Missing | Optional adapter | No | Yes | P0 | Medium | Low | Medium | qnode wrapper tests | Callable returns expectation |
| devices | Device interface | MVP statevector | Optional adapter | No | Yes | P0 | Medium | Low | Medium | device tests | Device adapter executes subset |
| operations | Operations | MVP gates | Optional adapter | No | Yes | P1 | High | Low | Low | operation tests | Common operation subset maps to IR |
| measurements | Measurements | Partial | Optional adapter | No | Yes | P0 | Medium | Low | Low | measurement tests | expval/probs/state subset works |
| observables | Observables | Partial PauliString | Optional adapter | No | Yes | P0 | Medium | Low | Low | observable bridge tests | PauliZ bridge works |
| tape | Tape-like representation | Missing | No | No | Yes | P0 | Medium | Low | Low | tape tests | Tape records operations/measurements |
| workflow | Execution workflow | Partial | Optional adapter | No | Mixed | P1 | High | Low | Medium | workflow tests | Deferred beyond P0 |
| gradients | Parameter-shift | Partial | Optional adapter | No | Yes | P0 | Medium | Low | Low | gradient tests | parameter-shift and finite diff pass |
| transforms | Gradient/circuit transforms | Missing | Optional later | No | Mixed | P1 | High | Low | Low | transform tests | Basic transform API exists |
| templates | Templates/ansatz | Missing | No | No | Yes | P0 | Medium | Low | Low | template tests | Basic angle embedding template builds circuit |
| qchem | Quantum chemistry | Missing | Upstream later | No | No for now | P3 | High | Medium | Medium | none in P0 | Optional upstream dependency only |
| math interfaces | Multi-framework math | NumPy native | Optional JAX/Torch | No | Adapter | P0 | Medium | Low | Low | interface tests | NumPy/Torch minimal arrays work; JAX optional |
| numpy wrapper | NumPy interface | Present via NumPy use | No | No | Yes | P0 | Low | Low | Low | interface tests | Converts to NumPy arrays |
| torch interface | Torch interface | Missing | Optional | No | Adapter | P0 | Medium | Low | Low | torch tests | Converts to Torch tensors if installed |
| jax interface | JAX interface | Missing | Optional | No | Adapter | P0 | Medium | Low | Low | optional tests | Clear unavailable behavior if not installed |
| tensorflow interface | TensorFlow interface | Missing | Optional later | No | No for now | P3 | High | Medium | Low | none in P0 | Status noted as version-sensitive/deferred |
| optimizers | Optimizer suite | Simple GD in VQE | No | No | Yes | P1 | Medium | Low | Low | optimizer tests | Deferred beyond P0 |
| resource estimation | Resources | Missing | No | No | Yes later | P2 | Medium | Low | Low | resource tests | Deferred |
| compilation | Compilation | Missing | Optional later | No | Mixed | P2 | High | Low | Low | compilation tests | Deferred |
| plugins | Plugin devices | Missing | Upstream optional | No | Adapter | P2 | High | Medium | Medium | plugin adapter tests | Deferred |

P0 summary:

- QNode-like wrapper, device adapter, tape-like record, observables/Hamiltonian, expectation, parameter-shift, finite-difference, NumPy/Torch/JAX minimal interfaces, basic templates.

