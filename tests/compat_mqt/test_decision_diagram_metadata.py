from quantumbridge.compat.mqt import (
    build_decision_diagram_metadata,
    summarize_decision_diagram_metadata,
    wrap_decision_diagram_metadata,
)


def test_decision_diagram_metadata_is_generated_and_wrapped():
    metadata = build_decision_diagram_metadata([1, 0, 0, 0], num_qubits=2)
    wrapped = wrap_decision_diagram_metadata(metadata)

    assert metadata["nonzero_amplitudes"] == 1
    assert metadata["compression_hint"] in {"sparse_support", "repeated_amplitudes"}
    assert "2 qubits" in summarize_decision_diagram_metadata(metadata)
    assert wrapped.validate()
