"""D2 offline red lights for misleading permutation/readout conclusions."""

from copy import deepcopy

import numpy as np
import pytest

from quantumbridge.finance.mapping_diagnostics import (
    compare_tasks, count_order_hypotheses, experiment_identifiability, gate_profile, joint_error_bootstrap, ordered_mapping,
)


def audit(mapping, created="2026-10-23 13:00:00", calibration=None):
    return {"task_id": "stub", "native_compiled": {"physical_measurement_map": dict(enumerate(mapping))},
            "fields": {"calibration_id": {"value": calibration}, "created": {"value": created},
                       "finished": {"value": "2026-10-23 12:30:00"}, "corrected": {"value": {}}},
            "gate_profile": {"gate_families": ["u"], "logical_layer_depth": 1},
            "submitted_options": {"compile": True}, "source_sha256": "stub"}


def test_same_set_not_same_measurement_order_or_calibration():
    result = compare_tasks(audit([10, 3, 4, 11]), audit([10, 3, 11, 4]))
    assert result["physical_set_matches"]
    assert not result["ordered_measurement_mapping_matches"]
    assert result["classification"] == "PARTIALLY_COMPARABLE"
    assert not result["error_model_transfer_proven"]


def test_same_width_other_physical_set_not_transferable():
    result = compare_tasks(audit([10, 3, 4, 11]), audit([10, 11, 4, 5]))
    assert result["classification"] == "NOT_TRANSFERABLE"


def test_missing_calibration_and_time_never_certify_noise_transfer():
    result = compare_tasks(audit([11, 4, 5]), audit([11, 4, 5]))
    assert result["classification"] == "PARTIALLY_COMPARABLE"
    assert result["finish_to_probe_creation_seconds"] == 1800
    assert not result["calibration_id_available_and_equal"]
    unknown = audit([11, 4, 5])
    unknown["fields"]["created"]["value"] = None
    assert compare_tasks(audit([11, 4, 5]), unknown)["classification"] == "UNKNOWN"


def test_direct_comparison_is_still_not_readout_model_proof():
    result = compare_tasks(audit([11, 4, 5], calibration="same"), audit([11, 4, 5], calibration="same"))
    assert result["classification"] == "DIRECTLY_COMPARABLE"
    assert not result["error_model_transfer_proven"]


def test_raw_reverse_not_compiled_physical_map():
    result = count_order_hypotheses({"100": 1024}, [0, 1, 0, 0, 0, 0, 0, 0], [11, 4, 5])
    reverse = next(candidate for candidate in result["candidates"] if "reverse" in candidate["aliases"])
    assert reverse["decoded_counts"] == {"001": 1024}
    assert reverse["TVD"] == 0
    assert result["status"] == "AMBIGUOUS" and result["selected_permutation"] is None


@pytest.mark.parametrize("width", [3, 4])
@pytest.mark.parametrize("prepared", [0, 1])
def test_uniform_zero_one_cannot_rank_any_permutation(width, prepared):
    ideal = np.zeros(1 << width)
    ideal[0 if not prepared else -1] = 1
    target = str(prepared) * width
    error = "1" + target[1:] if not prepared else "0" + target[1:]
    result = count_order_hypotheses({target: 900, error: 124}, ideal, list(range(width)))
    candidates = result["candidates"]
    assert len({candidate["noiseless_multinomial_log_likelihood_up_to_constant"] for candidate in candidates}) == 1
    assert len({candidate["TVD"] for candidate in candidates}) == 1
    assert all(candidate["positive_counts_at_zero_ideal_probability"] for candidate in candidates)


def test_noise_can_favor_wrong_order_without_certifying_it():
    # A toy noise channel swaps the masses. Best noiseless fit is then wrong.
    result = count_order_hypotheses({"001": 100, "100": 924}, [.01, .90, .01, .01, .04, .01, .01, .01], [11, 4, 5])
    identity = next(candidate for candidate in result["candidates"] if "identity" in candidate["aliases"])
    reverse = next(candidate for candidate in result["candidates"] if "reverse" in candidate["aliases"])
    assert reverse["TVD"] < identity["TVD"]
    assert result["selected_permutation"] is None


def test_joint_bootstrap_does_not_assume_independent_bit_errors():
    result = joint_error_bootstrap({"000": 512, "110": 512}, "000", draws=100)
    pair = result["pairs"][0]
    assert pair["joint_error"] == .5
    assert pair["independent_marginals_prediction"] == .25
    assert pair["excess_joint_error"] == .25
    assert pair["empirical_bootstrap_covariance_percentile_95"][0] > .2


def test_two_asymmetric_patterns_identify_four_noiseless_positions_conditionally():
    plan = experiment_identifiability(["0011", "0101"])
    assert plan["distinct_noiseless_observations"] == 24
    assert plan["worst_indistinguishable_permutations"] == 1
    assert not plan["execute"]
    assert experiment_identifiability(["0001"])["worst_indistinguishable_permutations"] == 6


def test_mapping_conflict_and_incomplete_metadata_refused():
    for mapping in ({0: 11, 2: 4}, {0: 11, 1: 11}):
        value = deepcopy(audit([11, 4, 5]))
        value["native_compiled"]["physical_measurement_map"] = mapping
        with pytest.raises(ValueError):
            ordered_mapping(value)


def test_gate_layer_depth_respects_barrier_without_claiming_physical_time():
    profile = gate_profile('''OPENQASM 2.0;
include "qelib1.inc";
qreg q[3]; creg c[3];
h q[0]; x q[1]; cx q[0],q[1]; barrier q; z q[2];
measure q -> c;
''')
    assert profile["unitary_operation_count"] == 4
    assert profile["logical_layer_depth"] == 3
    assert "physical timing" in profile["depth_scope"]


@pytest.mark.parametrize("invalid", ["width", "probabilities", "preparation", "draws", "patterns", "nonbinary"])
def test_malformed_offline_analysis_inputs_are_refused(invalid):
    with pytest.raises(ValueError):
        if invalid == "width":
            count_order_hypotheses({"00": 1024}, [.25] * 4, [3, 3])
        elif invalid == "probabilities":
            count_order_hypotheses({"00": 1024}, [.1] * 4, [3, 4])
        elif invalid == "preparation":
            joint_error_bootstrap({"010": 1024}, "010")
        elif invalid == "draws":
            joint_error_bootstrap({"000": 1024}, "000", draws=0)
        elif invalid == "patterns":
            experiment_identifiability(["00", "000"])
        else:
            experiment_identifiability(["00x"])
