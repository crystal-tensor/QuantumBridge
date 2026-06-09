from quantumbridge.compat.benchpress.examples import (
    run_algorithms_suite_example,
    run_backend_suite_example,
    run_basic_suite_example,
    run_full_smoke_suite_example,
)


def test_benchpress_examples_run():
    for helper in (
        run_basic_suite_example,
        run_algorithms_suite_example,
        run_backend_suite_example,
        run_full_smoke_suite_example,
    ):
        output = helper()
        assert output["native"].passed
        assert "not official Benchpress" in output["markdown_report"]
        assert output["cloud_access"] is False
