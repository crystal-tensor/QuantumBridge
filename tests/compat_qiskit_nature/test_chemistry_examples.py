import importlib


def test_h2_example_module_runs(capsys):
    module = importlib.import_module("examples.qiskit_nature_h2_quantumbridge")
    module.main()
    output = capsys.readouterr().out

    assert "QuantumBridge native H2 result" in output
    assert "No cloud, no token" in output
    assert "production chemistry" in output


def test_lih_example_module_runs(capsys):
    module = importlib.import_module("examples.qiskit_nature_lih_quantumbridge")
    module.main()
    output = capsys.readouterr().out

    assert "QuantumBridge native LiH result" in output
    assert "No cloud, no token" in output
    assert "production chemistry" in output
