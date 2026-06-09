import builtins

from quantumbridge.compat.qiskit_nature import run_h2_native, run_lih_native


def test_native_chemistry_paths_do_not_open_cloud_tokens_or_hardware(monkeypatch):
    blocked = {"QISKIT_IBM_TOKEN", "IBM_QUANTUM_TOKEN", "QE_TOKEN"}

    def fail_open(*args, **kwargs):  # pragma: no cover - only called on regression
        raise AssertionError(f"unexpected file access: {args}")

    monkeypatch.setattr(builtins, "open", fail_open)

    h2 = run_h2_native()
    lih = run_lih_native()

    assert h2.metadata["cloud_access"] is False
    assert h2.metadata["token_read"] is False
    assert h2.metadata["hardware_access"] is False
    assert lih.metadata["cloud_access"] is False
    assert lih.metadata["token_read"] is False
    assert lih.metadata["hardware_access"] is False
    assert blocked
