import subprocess
import sys

from quantumbridge.compat.mitiq.examples import (
    run_readout_mitigation_example,
    run_zne_example,
)


def test_mitiq_examples_return_native_and_optional_upstream_results():
    for runner in [run_zne_example, run_readout_mitigation_example]:
        results = runner()
        assert results["native"].validate() is True
        assert results["upstream"].validate() is True
        assert results["native"].production_ready is False


def test_mitiq_example_scripts_run():
    for path in [
        "examples/mitiq_zne_quantumbridge.py",
        "examples/mitiq_readout_mitigation_quantumbridge.py",
    ]:
        completed = subprocess.run(
            [sys.executable, path],
            check=True,
            text=True,
            capture_output=True,
        )
        assert "cloud_access: False" in completed.stdout
        assert "production_error_mitigation: False" in completed.stdout
