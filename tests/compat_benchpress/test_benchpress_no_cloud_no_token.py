from quantumbridge.compat.benchpress import full_smoke_suite, run_benchmark_suite


def test_benchpress_paths_do_not_access_cloud_tokens_or_hardware():
    result = run_benchmark_suite(full_smoke_suite()[:3], suite_name="safety_subset")
    assert result.provenance["cloud_access"] is False
    assert result.provenance["token_access"] is False
    assert result.provenance["hardware_access"] is False
    assert result.provenance["official_benchmark"] is False
