from quantumbridge.studio.workflow_inputs import build_input_schema_for_workflow, coerce_input_types, get_default_inputs, validate_inputs_against_schema
from quantumbridge.studio.workflow_registry import list_workflows


def test_each_registered_workflow_has_input_schema():
    for workflow in list_workflows():
        schema = build_input_schema_for_workflow(workflow.workflow_id)
        assert schema.workflow_id == workflow.workflow_id
        assert schema.validate()


def test_input_defaults_validation_and_coercion():
    schema = build_input_schema_for_workflow("aer.qasm_counts_native")
    assert get_default_inputs("aer.qasm_counts_native")["shots"] == 128
    ok, errors = validate_inputs_against_schema(schema, {"shots": "32", "seed": "5"})
    assert ok, errors
    coerced = coerce_input_types(schema, {"shots": "32", "seed": "5"})
    assert coerced["shots"] == 32
    assert coerced["seed"] == 5
