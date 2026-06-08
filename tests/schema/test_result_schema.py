from quantumbridge.results import Result
from quantumbridge.schema import RESULT_SCHEMA_VERSION


def test_result_schema_v02_payload():
    payload = Result(counts_data={"0": 2}, metadata_data={"job_id": "job-1"}).to_dict()
    assert payload["schema_version"] == RESULT_SCHEMA_VERSION
    assert payload["job_id"] == "job-1"
    assert payload["counts"] == {"0": 2}
