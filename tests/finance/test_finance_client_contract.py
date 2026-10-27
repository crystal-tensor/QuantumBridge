"""No-network D3 counterexamples and lossless gateway normalization contracts."""

from copy import deepcopy
import json

import pytest

from quantumbridge.compat.quafu import QuafuCloudBackend
from quantumbridge.finance.client_contract import layout_pinning_verdict, permute_counts, response_field_matrix, trace_count_labels
from quantumbridge.providers import JobError


def test_documented_or_fake_bit_order_never_fills_missing_historical_field():
    real = {"count": {"001": 1024}, "status": "Finished"}
    before = deepcopy(real)
    result = response_field_matrix(real, documentation={"bit_order": "c0_rightmost"})
    assert result["bit_order"]["status"] == "ABSENT"
    assert result["bit_order"]["observed_value"] is None
    assert not result["bit_order"]["hint_is_historical_evidence"]
    assert real == before


def test_accepted_target_parameter_with_remapped_output_is_not_pinned():
    class OfflineFakeClient:
        def run(self, task):
            assert task["options"]["target_qubits"] == [3, 4, 10, 11]
            return {"compiled_measurement_map": [10, 11, 4, 5]}

    result = OfflineFakeClient().run({"options": {"target_qubits": [3, 4, 10, 11]}})
    verdict = layout_pinning_verdict([3, 4, 10, 11], result["compiled_measurement_map"])
    assert verdict["status"] == "ERROR"
    assert verdict["layout_pinning"] == "PHYSICAL_LAYOUT_PINNING_NOT_VERIFIED"
    assert not verdict["future_task_guarantee"]


def test_matching_one_layout_is_still_not_future_placement_guarantee():
    assert layout_pinning_verdict([11, 4, 5], [11, 4, 5])["status"] == "DOCUMENTED_UNVERIFIED"
    assert layout_pinning_verdict([11, 4, 5], [4, 5, 11])["physical_set_matches"]


def test_identity_reverse_and_physical_hypothesis_are_separate_lossless_views():
    payload = {"count": {"001": 200, "100": 700, "111": 124}}
    before = json.dumps(payload)
    result = trace_count_labels(payload, 3, ordered_physical_mapping=[11, 4, 5],
                                financial_counts={"100": 200, "001": 700, "111": 124}, decoder_order="q0-last")
    assert result["finance_decoder_status"] == "GATEWAY_ASSUMPTION_UNVERIFIED"
    assert result["client_decoding_stage"]["status"] == "DOCUMENTED_UNVERIFIED"
    assert result["count_order_status"] == "UNKNOWN"
    assert result["hypotheses"]["reverse"]["counts"]["001"] == 700
    assert result["hypotheses"]["identity"]["counts"]["001"] == 200
    assert result["hypotheses"]["ascending_physical_register"]["positions"] == [2, 0, 1]
    assert all(not view["applied_to_original"] for view in result["hypotheses"].values())
    assert result["project_transforms_exactly_invertible"]
    assert json.dumps(payload) == before


def test_symmetric_data_is_not_used_to_promote_order():
    result = trace_count_labels({"count": {"000": 1024}}, 3, ordered_physical_mapping=[11, 4, 5])
    assert result["count_order_status"] == "UNKNOWN"
    assert result["finance_decoder_status"] == "NOT_USED_FOR_FINANCE_DECODING"


@pytest.mark.parametrize("positions", [[0, 0, 2], [True, 1, 2], [0, 1], [0, 1, 3], "012"])
def test_label_mapping_must_be_a_true_permutation(positions):
    with pytest.raises(ValueError):
        permute_counts({"001": 1024}, 3, positions)


@pytest.mark.parametrize("label", ["01", "0 01", "0x1", "0001"])
def test_padding_or_register_delimiters_are_never_silently_normalized(label):
    with pytest.raises(ValueError):
        trace_count_labels({"count": {label: 1024}}, 3, ordered_physical_mapping=[11, 4, 5])


def test_incorrect_saved_normalization_is_refused():
    with pytest.raises(ValueError, match="normalized"):
        trace_count_labels({"count": {"001": 1024}}, 3, ordered_physical_mapping=[11, 4, 5],
                           financial_counts={"001": 1024}, decoder_order="q0-last")


@pytest.mark.parametrize("width", [0, -1, 7, True])
def test_trace_width_is_bounded_before_enumerating_labels(width):
    with pytest.raises(ValueError):
        trace_count_labels({"count": {"001": 1024}}, width, ordered_physical_mapping=[11, 4, 5])
    with pytest.raises(ValueError):
        permute_counts({"001": 1024}, width, [0, 1, 2])


def test_equal_but_noninteger_normalized_counts_are_not_accepted():
    with pytest.raises(ValueError):
        trace_count_labels({"count": {"001": 1024}}, 3, ordered_physical_mapping=[11, 4, 5],
                           financial_counts={"100": 1024.0}, decoder_order="q0-last")


def test_read_only_gateway_refuses_run_before_touching_circuit_or_transport():
    class NoCalls:
        def submit(self, *args, **kwargs):
            pytest.fail("read-only gateway reached submit")

        def status(self):
            return {"offline_test": True}

    backend = QuafuCloudBackend(transport=NoCalls(), read_only=True)
    assert backend.read_only is True
    with pytest.raises(JobError, match="read-only"):
        backend.run(object())
    assert backend.status() == {"offline_test": True}
    with pytest.raises(AttributeError):
        backend.read_only = False


@pytest.mark.parametrize("value", [1, "true", None])
def test_read_only_mode_is_not_truthiness_coerced(value):
    with pytest.raises(TypeError):
        QuafuCloudBackend(read_only=value)


def test_read_only_mode_does_not_construct_a_credentialed_client(monkeypatch):
    import quantumbridge.compat.quafu.cloud_backend as module

    monkeypatch.setattr(module, "QuarkStudioTransport", lambda **kwargs: pytest.fail("constructed credential client"))
    with pytest.raises(ValueError, match="explicit transport"):
        QuafuCloudBackend(read_only=True)
