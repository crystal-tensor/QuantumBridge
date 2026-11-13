"""Runtime prerequisites must accompany actual worker/version/exit receipts."""
import json
import sys

import pytest

from tests.compat_inventory.test_verification_worker_environment import collect, fixture, recorder, write


def modern_fixture(tmp_path):
    args, receipt, terminal = fixture(tmp_path)
    receipt['schema'] = 2
    for key in ('start', 'end'):
        receipt[key]['runtime_controls'] = {name: None for name in recorder.RUNTIME_CONTROL_KEYS}
        receipt[key]['runtime_controls']['TF_NUM_INTEROP_THREADS'] = '2'
        receipt[key]['interpreter_flags'] = {name: False for name in recorder.INTERPRETER_FLAG_KEYS}
    return args, receipt, terminal


def save(args, receipt, terminal):
    write(args.environment_receipt, receipt)
    terminal['environment_receipt_sha256'] = recorder.sha(args.environment_receipt.read_bytes())
    write(args.terminal, terminal)


def test_legacy_worker_receipts_do_not_invent_requested_thread_settings(tmp_path):
    args, *_ = fixture(tmp_path)
    validation = collect(args)['environment_validation']
    assert validation['verified']
    assert not validation['runtime_controls_provided']
    assert validation['runtime_controls'] is validation['interpreter_flags'] is None
    assert not validation['runtime_controls_complete']


def test_modern_receipts_retain_requested_controls_without_claiming_effective_pool_size(tmp_path):
    args, receipt, terminal = modern_fixture(tmp_path)
    save(args, receipt, terminal)
    row = collect(args)
    validation = row['environment_validation']
    assert validation['runtime_controls'] == receipt['start']['runtime_controls']
    assert validation['runtime_controls']['TF_NUM_INTEROP_THREADS'] == '2'
    assert validation['interpreter_flags'] == receipt['start']['interpreter_flags']
    assert validation['runtime_controls_complete']
    assert 'not_observed_framework_pool_sizes' in validation['runtime_controls_scope']
    assert '/fixture/' not in json.dumps(row)


@pytest.mark.parametrize('fault', ['missing_controls', 'extra_controls', 'controls_type', 'control_value',
    'missing_flags', 'extra_flags', 'flags_type', 'flag_value', 'changed_thread', 'changed_isolation'])
def test_invalid_or_changed_runtime_settings_are_rejected(tmp_path, fault):
    args, receipt, terminal = modern_fixture(tmp_path)
    if fault == 'changed_thread':
        receipt['end']['runtime_controls']['TF_NUM_INTEROP_THREADS'] = '1'
    elif fault == 'changed_isolation':
        receipt['end']['interpreter_flags']['isolated'] = True
    else:
        for key in ('start', 'end'):
            snapshot = receipt[key]
            if fault == 'missing_controls': del snapshot['runtime_controls']
            elif fault == 'extra_controls': snapshot['runtime_controls']['QUAFU_TOKEN'] = 'forbidden'
            elif fault == 'controls_type': snapshot['runtime_controls'] = []
            elif fault == 'control_value': snapshot['runtime_controls']['TF_NUM_INTEROP_THREADS'] = 'private-setting'
            elif fault == 'missing_flags': del snapshot['interpreter_flags']
            elif fault == 'extra_flags': snapshot['interpreter_flags']['unknown'] = False
            elif fault == 'flags_type': snapshot['interpreter_flags'] = []
            elif fault == 'flag_value': snapshot['interpreter_flags']['isolated'] = 0
    save(args, receipt, terminal)
    with pytest.raises(ValueError, match='environment|runtime controls'):
        collect(args)
    assert not args.output.exists()


def test_capture_uses_only_allowlisted_settings_and_does_not_import_frameworks(monkeypatch):
    before = {name for name in sys.modules if name.split('.')[0] in {'tensorflow', 'jax', 'torch', 'qiskit', 'pennylane'}}
    monkeypatch.setattr(recorder.importlib.metadata, 'version', lambda _: 'fixture')
    monkeypatch.setenv('TF_NUM_INTEROP_THREADS', '2')
    monkeypatch.setenv('OMP_NUM_THREADS', '4,2')
    monkeypatch.setenv('JAX_ENABLE_X64', 'TRUE')
    monkeypatch.setenv('MKL_NUM_THREADS', 'private-setting')
    monkeypatch.setenv('QUAFU_TOKEN', 'fictional-secret')
    captured = recorder._capture_environment()
    assert captured['runtime_controls']['TF_NUM_INTEROP_THREADS'] == '2'
    assert captured['runtime_controls']['OMP_NUM_THREADS'] == '4,2'
    assert captured['runtime_controls']['JAX_ENABLE_X64'] == 'true'
    assert captured['runtime_controls']['MKL_NUM_THREADS'] == 'unparsed'
    assert 'fictional-secret' not in json.dumps(captured) and 'private-setting' not in json.dumps(captured)
    assert set(captured['interpreter_flags']) == set(recorder.INTERPRETER_FLAG_KEYS)
    assert before == {name for name in sys.modules if name.split('.')[0] in {'tensorflow', 'jax', 'torch', 'qiskit', 'pennylane'}}
