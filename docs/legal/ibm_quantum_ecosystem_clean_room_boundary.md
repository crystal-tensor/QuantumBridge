# IBM Quantum Ecosystem Clean-Room Boundary

Status: Stage 9C-Revision policy

QuantumBridge is an independent project. It is not IBM, Qiskit, PennyLane,
Xanadu, Azure Quantum, MQT, Mitiq, TorchQuantum, or any other upstream
project.

## Allowed

- Reference public project names to identify compatibility targets.
- Use optional upstream packages when installed by the user.
- Build independent QuantumBridge adapters, schemas, warnings, provenance,
  examples, tests, and educational native subsets.
- Link to upstream projects in attribution and compatibility docs.

## Not Allowed

- Copy IBM Quantum Ecosystem web page text, UI, layout, screenshots, icons,
  images, or brand assets.
- Copy Qiskit, PennyLane, IBM, or third-party source code, tests, comments,
  documentation prose, error strings, wheels, dist-info, egg-info,
  site-packages trees, or virtual environments.
- Use IBM or Qiskit branding as QuantumBridge product branding.
- Suggest IBM, Qiskit, PennyLane, or third-party endorsement.
- Access IBM Cloud, read tokens, store credentials, or access real hardware by
  default.
- Claim full replacement or production parity unless separately reviewed and
  explicitly approved.

## Attribution

Upstream projects retain their own names, licenses, authorship, maintainers,
and documentation. QuantumBridge compatibility docs must describe upstream
dependencies as optional and must not present upstream functionality as
QuantumBridge original work unless QuantumBridge independently implemented the
specific subset.
