# Stage 6.3 Dependency Compatibility Review

## Scope

Stage 6.3 reviews dependency compatibility after Stage 6.2 installed-environment verification. It does not add large features, does not enter P3, and does not vendor third-party source code.

Branch: `p2/dual-track-expansion`

Input commit: `a95abf49297182cc815653105b76a73df5b6e2f0`

## PR Status

Requested PR:

- Base: `main`
- Head: `p2/dual-track-expansion`
- Title: `Stage 6 P2 Dual-Track Expansion: Core SDK + Chemistry/Algorithms Adapters`

Automation result:

- `gh` is installed but not logged in.
- GitHub connector PR creation returned `403 Resource not accessible by integration`.
- Manual PR URL: `https://github.com/crystal-tensor/QuantumBridge/pull/new/p2/dual-track-expansion`

## Current Installed Versions

Installed in the Stage 6.2 Python 3.12 environment:

| Package | Version | Notes |
|---|---:|---|
| `qiskit` | `2.4.1` | Installed chemistry / algorithms environment |
| `qiskit-nature` | `0.8.0` | Requires `numpy>=2` |
| `qiskit-algorithms` | `0.4.0` | Installed algorithms adapter environment |
| `pyscf` | `2.13.1` | Installed chemistry driver environment |
| `openfermion` | `1.7.1` | Installed chemistry adapter environment |
| `pyquafu` | `0.4.5` | Requires `numpy<2.0.0,>=1.20.3` |
| `numpy` | `2.4.6` | Installed by chemistry stack in Stage 6.2 |

## Conflict

`pyquafu 0.4.5` requires:

```text
numpy<2.0.0,>=1.20.3
```

The Stage 6.2 chemistry install resolved:

```text
numpy==2.4.6
```

`pip check` result in the combined environment:

```text
pyquafu 0.4.5 has requirement numpy<2.0.0,>=1.20.3, but you have numpy 2.4.6.
```

## Chemistry With NumPy 1.x Test

A temporary resolver environment tested:

```text
numpy<2.0.0
qiskit==2.4.1
qiskit-nature==0.8.0
qiskit-algorithms==0.4.0
pyscf==2.13.1
openfermion==1.7.1
```

Result:

```text
ResolutionImpossible
qiskit-nature 0.8.0 depends on numpy>=2
```

Conclusion: the verified Stage 6.2 chemistry stack cannot coexist with `pyquafu==0.4.5` in one environment.

## Quafu-Compatible Environment Test

A temporary quafu-compatible virtual environment installed:

```text
pyquafu==0.4.5
numpy==1.26.4
```

and ran:

```text
tests/compat/test_quafu_dependency_compatibility.py
```

Result:

```text
1 passed
```

## Can One Environment Support PyQuafu + Chemistry?

Not with the currently verified versions:

- `qiskit-nature==0.8.0` requires `numpy>=2`.
- `pyquafu==0.4.5` requires `numpy<2.0.0`.

Recommendation: split environments.

## Recommended Extras Strategy

`pyproject.toml` now separates:

- `chemistry`: NumPy 2 chemistry stack.
- `chemistry-numpy2`: explicit alias for NumPy 2 chemistry stack.
- `quafu`: `pyquafu==0.4.5` with `numpy<2.0.0`.
- `all-optional`: does not force chemistry and quafu stacks into one environment.

## Constraints Files

Added:

- `requirements/constraints-core.txt`
- `requirements/constraints-chemistry.txt`
- `requirements/constraints-quafu.txt`
- `requirements/constraints-dev.txt`

The chemistry constraints intentionally use:

```text
numpy>=2,<3
```

because `qiskit-nature==0.8.0` requires NumPy 2.

The quafu constraints intentionally use:

```text
pyquafu==0.4.5
numpy<2.0.0
```

## CI Matrix Split

Existing profiles retained:

- `core-only`
- `qiskit-extra`
- `pennylane-extra`
- `dev`
- `chemistry-core`
- `chemistry-extra`
- `qiskit-nature-extra`
- `algorithms-extra`
- `openfermion-extra`

Added profiles:

- `chemistry-compatible`: installs `.[chemistry]` with `requirements/constraints-chemistry.txt`, regenerates inventories, and runs chemistry / algorithms / inventory tests.
- `quafu-compatible`: installs `.[quafu]` with `requirements/constraints-quafu.txt` and runs a dependency smoke test.

No CI job requires `all-optional` to pass.

## User Installation Recommendation

Use separate environments:

Chemistry:

```bash
python -m venv .venv-chemistry
. .venv-chemistry/bin/activate
python -m pip install -c requirements/constraints-chemistry.txt -e '.[chemistry]'
```

Quafu:

```bash
python -m venv .venv-quafu
. .venv-quafu/bin/activate
python -m pip install -c requirements/constraints-quafu.txt -e '.[quafu]'
```

## Clean Dependency Policy

No third-party source trees, site-packages, wheels, or vendored upstream code should be committed. Qiskit, Qiskit Nature, Qiskit Algorithms, PySCF, OpenFermion, PennyLane, and Quafu remain optional upstream dependencies.

## Conclusion

The pyquafu / NumPy conflict is not solved in a single combined environment. It is resolved operationally by splitting chemistry and quafu environments and CI profiles.
