import pytest

from quantumbridge.schema import SchemaValidationError, validate_result_schema


def test_result_validation_rejects_missing_keys():
    with pytest.raises(SchemaValidationError):
        validate_result_schema({"schema_version": "0.2"})
