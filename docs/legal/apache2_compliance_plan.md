# Apache-2.0 Compliance Plan

Status: Stage 4 draft  
Date: 2026-06-04  

QuantumBridge has changed route from strict clean-room rewrite to Apache-2.0 compliant feature-parity implementation and integration. This document is an engineering compliance plan, not legal advice.

## 1. Why the route changed

The earlier project route prohibited reading or adapting Qiskit and PennyLane source. Stage 4 changes that posture because both upstream ecosystems are distributed under Apache License 2.0, which permits use, modification, distribution, and sublicensing under the license conditions. QuantumBridge will still avoid a coarse fork: the goal is feature alignment through QuantumBridge native architecture, optional adapters, documented dependencies, and attributed source ports only when justified.

## 2. Qiskit license source

Current local reference:

- Installed package: `qiskit==2.4.1`
- License file copied from: `qiskit-2.4.1.dist-info/licenses/LICENSE.txt`
- Repository copy: `LICENSES/QISKIT_LICENSE.txt`

Qiskit attribution must be preserved for direct source ports or adapted code.

## 3. PennyLane license source

Current local reference:

- Installed package: `PennyLane==0.44.1`
- License file copied from: `pennylane-0.44.1.dist-info/licenses/LICENSE`
- Repository copy: `LICENSES/PENNYLANE_LICENSE.txt`

PennyLane attribution must be preserved for direct source ports or adapted code.

## 4. Apache 2.0 allowed behaviors

Subject to the license terms, Apache 2.0 generally permits:

- Use.
- Reproduction.
- Modification.
- Distribution.
- Sublicensing.
- Distribution in source or object form.
- Patent license from contributors under the license scope.

## 5. Apache 2.0 required preservation

QuantumBridge must preserve:

- Copyright notices.
- License text.
- NOTICE file content when upstream distributions provide applicable NOTICE material.
- Modification notices for changed files.
- Attribution for copied, adapted, or ported source files.

## 6. LICENSE handling

- QuantumBridge should adopt Apache License 2.0 for its own project license unless the project owner chooses otherwise.
- The canonical Apache text is stored at `LICENSES/Apache-2.0.txt`.
- Upstream license texts are stored separately in `LICENSES/QISKIT_LICENSE.txt` and `LICENSES/PENNYLANE_LICENSE.txt`.

## 7. NOTICE handling

- `THIRD_PARTY_NOTICES.md` is the project-level attribution ledger for Qiskit, PennyLane, and future migrated files.
- If an upstream package includes a NOTICE file relevant to redistributed content, it must be copied or summarized according to license requirements.
- Every Source Port with Attribution must update `THIRD_PARTY_NOTICES.md`.

## 8. File header handling

Native QuantumBridge files use:

```text
Copyright 2026 QuantumBridge Contributors.
Licensed under the Apache License, Version 2.0.
This file is part of QuantumBridge SDK.
This implementation is developed for the QuantumBridge native architecture.
```

Files adapted from Qiskit or PennyLane must include upstream project, license, and modification notes. Existing Stage 3 clean-room headers should be updated gradually when files are touched for Stage 4, while preserving the historical record in Stage 3 implementation documents.

## 9. Modification statements

For any copied or adapted source:

- Mark the file as derived, adapted, or ported.
- Identify original project and original path.
- Describe modifications.
- Preserve applicable copyright.
- Update migration ledger and notices.

## 10. Third-party dependencies

Dependencies are categorized as:

- Runtime required dependencies.
- Optional adapter dependencies.
- Development/test dependencies.
- Source-ported code.

Qiskit, PennyLane, Torch, and JAX integrations should be optional dependencies where practical.

## 11. Trademark risk

Do not use Qiskit, PennyLane, IBM, or Xanadu names in product names, logos, package names, or promotional language implying endorsement. Use factual compatibility language only.

## 12. Commercial release risk

Before commercial release:

- Complete dependency license inventory.
- Complete source migration ledger.
- Verify NOTICE handling.
- Review patent and trademark risk with counsel.
- Confirm no upstream endorsement is implied.

