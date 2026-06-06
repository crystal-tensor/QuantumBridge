# Third-party Source Policy

Status: Stage 7 planning update
Date: 2026-06-05

This policy governs how QuantumBridge may reference, depend on, adapt, or port Qiskit, PennyLane, and related ecosystem code.

## 1. Code that may be directly referenced

Allowed with attribution:

- Apache-2.0 licensed Qiskit source.
- Apache-2.0 licensed PennyLane source.
- Public API documentation.
- Public standards such as OpenQASM.
- Public papers and mathematical definitions.

Any direct source reference must be recorded in `docs/migration/source_migration_ledger.md`.

## 2. Code that may be copied and modified

Allowed only under Source Port with Attribution:

- Small, bounded utility functions.
- Conversion helpers.
- Serialization utilities.
- Mature mathematical helper routines.

Requirements:

- Preserve upstream copyright where applicable.
- Add derived/adapted file header.
- Record original path and license.
- Update `THIRD_PARTY_NOTICES.md`.
- Add tests.

## 3. Code that should be dependency-only

Prefer upstream dependency rather than source migration for:

- Qiskit Aer or simulator internals.
- Hardware providers.
- Complex PennyLane chemistry modules.
- Large plugin devices.
- Vendor cloud SDKs.
- Qiskit Nature, Algorithms, Finance, Optimization, Machine Learning, Experiments, Addons, PySCF, OpenFermion, Quafu, and similar ecosystem packages unless a separate source-port review approves a bounded migration.

## 4. Code not recommended for migration

Avoid migrating:

- Large subsystems that would effectively fork upstream.
- Trademark-heavy provider integrations.
- Rapidly changing plugin internals.
- Deprecated modules.
- Code with unclear transitive licensing.

## 5. Source marking

Every migrated file must state:

- Original project.
- Original license.
- Original path.
- Whether code was copied, adapted, or only referenced.
- Modification summary.

## 6. Modification records

Each migration record must include:

- QuantumBridge file.
- Feature name.
- Implementation mode.
- Upstream project and path.
- License.
- Whether copyright notice was retained.
- Whether tests exist.
- Risk level.

## 7. THIRD_PARTY_NOTICES generation

`THIRD_PARTY_NOTICES.md` is updated manually in Stage 4. Later automation may scan `docs/migration/source_migration_ledger.md` and generate notices.

## 8. Qiskit / PennyLane plugins

Plugins are not part of the core Qiskit or PennyLane projects by default. Each plugin requires independent license review before dependency, adaptation, or source migration.

## 9. Dependency tree licenses

Before public release:

- Generate a dependency inventory.
- Review direct and transitive licenses.
- Flag GPL, AGPL, LGPL, SSPL, commercial-only, source-available, or unknown licenses.
- Keep optional extras isolated when license risk differs from the core.

## 10. Stage 7 ecosystem rules

- Treat Qiskit ecosystem, PennyLane ecosystem, chemistry, finance, optimization, machine-learning, and hardware/provider packages as optional dependencies.
- Prefer passthrough and adapter integration over source migration.
- Do not claim upstream-backed features are QuantumBridge-original.
- Do not claim official endorsement by IBM, Qiskit, Xanadu, PennyLane, or other upstream maintainers.
- Do not require all optional dependencies to coexist in one environment.
- Record every new optional package in `THIRD_PARTY_NOTICES.md` and `docs/migration/source_migration_ledger.md`.
