from quantumbridge.compat.qos_uqci.calset_adapter import build_calset, validate_calset
from quantumbridge.compat.qos_uqci.devicespec_adapter import build_devicespec, validate_devicespec
from quantumbridge.compat.qos_uqci.examples import qos_uqci_bell_circuit
from quantumbridge.compat.qos_uqci.job_spec import build_qos_uqci_job_spec
from quantumbridge.compat.qos_uqci.manifest_adapter import validate_manifest


def test_devicespec_calset_manifest_validate():
    assert validate_devicespec(build_devicespec(num_qubits=2))
    assert validate_calset(build_calset(num_qubits=2))
    spec = build_qos_uqci_job_spec(qos_uqci_bell_circuit())
    assert validate_manifest(spec["manifest"])
