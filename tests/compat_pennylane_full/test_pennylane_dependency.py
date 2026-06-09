# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.pennylane_full.dependency import (
    dependency_available,
    get_dependency_report,
    get_upstream_version,
    require_pennylane,
)


def test_pennylane_dependency_report_is_optional_and_offline():
    report = get_dependency_report()
    assert report["optional_dependency"] is True
    assert report["auto_install"] is False
    assert report["network_access"] is False
    assert report["token_access"] is False
    assert report["available"] == dependency_available()
    assert get_upstream_version() is None or isinstance(get_upstream_version(), str)


def test_require_pennylane_returns_module_or_clear_error():
    if dependency_available():
        assert require_pennylane().__name__ == "pennylane"
    else:
        with pytest.raises(ImportError, match="pennylane-full"):
            require_pennylane()
