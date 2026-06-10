from quantumbridge.studio.frontend_contract import (
    build_frontend_seed_bundle,
    load_frontend_seed_bundle,
    validate_frontend_result_coverage,
    validate_frontend_seed_bundle,
    validate_frontend_workflow_coverage,
    write_frontend_seed_bundle,
)


def test_frontend_seed_bundle_validates_and_writes(tmp_path):
    bundle = build_frontend_seed_bundle()

    assert validate_frontend_seed_bundle(bundle)
    assert validate_frontend_workflow_coverage(bundle)
    assert validate_frontend_result_coverage(bundle)
    assert len(bundle["results"]["results"]) >= 10
    assert bundle["benchmark"]["benchmark"]
    assert {"json", "markdown", "python", "notebook_stub"}.issubset(bundle["exports"]["exports"])

    written = write_frontend_seed_bundle(tmp_path)
    assert {path.name for path in written}.issuperset(
        {
            "sampleCatalog.json",
            "sampleWorkflows.json",
            "sampleWorkflowDetails.json",
            "sampleResults.json",
            "sampleBenchmarkReport.json",
            "sampleExports.json",
            "studioSchemaVersion.json",
            "seedData.js",
        }
    )
    loaded = load_frontend_seed_bundle(tmp_path)
    assert validate_frontend_seed_bundle(loaded)


def test_frontend_seed_envelopes_include_contract_metadata():
    bundle = build_frontend_seed_bundle()

    for section in ("catalog", "workflows", "workflow_details", "results", "benchmark", "exports", "schema"):
        payload = bundle[section]
        assert payload["schema_version"]
        assert payload["generated_at"]
        assert payload["source"] == "quantumbridge.studio.backend"
        assert payload["quantumbridge_version"]
        assert payload["warnings"]
        assert payload["provenance"]
        assert payload["clean_room_notice"]
