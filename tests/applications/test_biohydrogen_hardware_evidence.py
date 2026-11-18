"""Audit the published measurements; this test never contacts the provider."""
from pathlib import Path
import hashlib,json
import pytest
from scripts.analyze_biohydrogen_hardware import analyze

DATA=Path(__file__).resolve().parents[2]/'studio/downloads/biohydrogen-patent'


def test_receipts_and_frozen_submission_circuits_reconcile():
    h=json.loads((DATA/'hardware-evidence.json').read_text())
    m=json.loads((DATA/'execution-plan.json').read_text())
    assert h['verified_tasks']==len(h['receipts'])==8
    assert len({r['task_id'] for r in h['receipts'].values()})==8
    for key,r in h['receipts'].items():
        assert r['status']=='Finished' and r['mode']=='cloud_hardware'
        assert r['backend']==r['target']=='Baihua'
        assert r['calibration_id'] and r['compiler'] and len(r['measurements'])==3
        assert sum(r['counts_raw'].values())==sum(r['counts_q0_first'].values())==1024
        assert r['counts_q0_first']=={k[::-1]:v for k,v in r['counts_raw'].items()}
        assert hashlib.sha256(r['executed_qasm'].encode()).hexdigest()==r['executed_qasm_sha256']
        assert hashlib.sha256(m['kernels'][key]['openqasm'].encode()).hexdigest()==r['submitted_qasm_sha256']


def test_public_statistics_reproduce_from_raw_counts():
    h=json.loads((DATA/'hardware-evidence.json').read_text())
    local=json.loads((DATA/'local-evidence.json').read_text())
    journal={'jobs':{k:{'receipt':v} for k,v in h['receipts'].items()},'sdk':h['sdk']}
    result=analyze(journal,local)
    for expected,actual in zip(h['rows'],result['rows']):
        for key in ['energy_dimensionless','standard_error','p111']:
            assert actual[key]==pytest.approx(expected[key],abs=1e-12)
        assert actual['p111_wilson95']==pytest.approx(expected['p111_wilson95'],abs=1e-12)
