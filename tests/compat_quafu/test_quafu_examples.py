from quantumbridge.compat.quafu.examples import run_quafu_bell_payload_example, run_quafu_mock_backend_example


def test_quafu_examples_return_payload_and_result():
    payload = run_quafu_bell_payload_example()
    runtime = run_quafu_mock_backend_example()
    assert payload["payload"]["payload_type"] == "quafu_clean_room_payload"
    assert runtime["result"].counts
