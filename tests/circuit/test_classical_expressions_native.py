# Independent QuantumBridge classical semantics tests; no upstream tests copied.

import json
import pytest

from quantumbridge.core.classical import (
    Bool, Bit, UInt, ClassicalType, ClassicalExpression, ClassicalStore, ClassicalExecutionError,
    UnsupportedFeature, literal, bit, register, variable, cast, binary, logical_and, logical_or,
    logical_not, classical_eval, classical_assign, serialize_classical_expr, deserialize_classical_expr,
    validate_classical_expr,
)


def test_bool_and_unsigned_values_remain_distinct():
    assert classical_eval(literal(True), ClassicalStore()) is True
    assert classical_eval(literal(1, Bit()), ClassicalStore()) == 1
    for value, dtype in [(1, Bool()), (True, UInt(3)), (-1, UInt(3)), (8, UInt(3))]:
        with pytest.raises((TypeError, ValueError)): literal(value, dtype)
    with pytest.raises(UnsupportedFeature): literal(1.5)
    for width in (0, 4097, True):
        with pytest.raises(ValueError): UInt(width)
    with pytest.raises(UnsupportedFeature): ClassicalType("float")


def test_register_uses_first_listed_bit_as_least_significant():
    store = ClassicalStore(4)
    classical_assign(store, register([2, 0, 3]), 5)
    assert store.bits == [0, 0, 1, 1]
    assert classical_eval(register([2, 0, 3]), store) == 5
    assert classical_eval(bit(3), store) == 1


def test_runtime_variables_must_be_declared_and_initialized():
    target, store = variable("x", UInt(3)), ClassicalStore()
    with pytest.raises(ClassicalExecutionError, match="lexical"): classical_eval(target, store)
    store.declare(target)
    with pytest.raises(ClassicalExecutionError, match="initialization"): classical_eval(target, store)
    classical_assign(store, target, 4)
    assert classical_eval(target, store) == 4
    with pytest.raises(ClassicalExecutionError): store.declare(target)
    copied = store.copy()
    classical_assign(copied, target, 1)
    assert classical_eval(target, store) == 4
    restored = ClassicalStore.from_dict(json.loads(json.dumps(store.to_dict())))
    assert classical_eval(target, restored) == 4


def test_fixed_width_arithmetic_wraps_modulo_two_to_width():
    store = ClassicalStore()
    assert classical_eval(literal(7, UInt(3)) + 1, store) == 0
    assert classical_eval(literal(0, UInt(3)) - 1, store) == 7
    assert classical_eval(literal(5, UInt(3)) * 3, store) == 7
    assert classical_eval(literal(3, UInt(3)) << 1, store) == 6
    assert classical_eval(literal(6, UInt(3)) >> 1, store) == 3
    assert classical_eval(literal(3, UInt(3)) << 7, store) == 0


def test_boolean_bitwise_and_ordering_expressions_execute():
    store = ClassicalStore()
    a, b = literal(5, UInt(3)), literal(3, UInt(3))
    expected = {"and": 1, "or": 7, "xor": 6, "eq": False, "ne": True, "lt": False, "le": False, "gt": True, "ge": True}
    for op, value in expected.items(): assert classical_eval(binary(op, a, b), store) == value
    assert classical_eval(~a, store) == 2
    assert classical_eval(~literal(True), store) is False
    assert classical_eval(logical_not(a), store) is False
    assert classical_eval(logical_and(a, b), store) is True
    assert classical_eval(logical_or(literal(0), b), store) is True
    assert classical_eval(a == 5, store) is True
    assert classical_eval(a != 5, store) is False


def test_promotions_casts_and_symbolic_truth_are_explicit():
    store = ClassicalStore()
    assert classical_eval(literal(3, UInt(2)) + literal(5, UInt(4)), store) == 8
    assert classical_eval(cast(literal(7, UInt(4)), UInt(2)), store) == 3
    assert classical_eval(cast(literal(7), Bool()), store) is True
    assert classical_eval(cast(literal(True), Bit()), store) == 1
    with pytest.raises(TypeError): bool(literal(True))
    with pytest.raises(TypeError): literal(True) + True
    with pytest.raises(TypeError): literal(True) & literal(1)
    with pytest.raises(UnsupportedFeature): binary("eval", literal(1), literal(1))


def test_expression_json_is_executable_and_not_python_text():
    expr = logical_and(register([1, 0]) >= 1, logical_not(bit(2)))
    restored = deserialize_classical_expr(json.loads(json.dumps(serialize_classical_expr(expr))))
    store = ClassicalStore(3)
    store.bits[:] = [1, 0, 0]
    assert classical_eval(restored, store) is True
    assert classical_eval(restored.remap({0: 2, 1: 1, 2: 0}), store) is False
    with pytest.raises(ValueError): deserialize_classical_expr({"expression": "__import__('os')"})
    with pytest.raises(UnsupportedFeature): validate_classical_expr(ClassicalExpression("unknown", Bool()))
    with pytest.raises(TypeError): validate_classical_expr(ClassicalExpression("add", Bool(), (literal(True), literal(False))))


def test_invalid_references_assignments_and_expression_shapes_fail():
    store = ClassicalStore(1)
    with pytest.raises(ValueError): classical_eval(bit(2), store)
    with pytest.raises(TypeError): classical_assign(store, literal(0), 1)
    with pytest.raises(ValueError): register([0, 0])
    with pytest.raises(ValueError): bit(True)
    with pytest.raises(ValueError): validate_classical_expr(ClassicalExpression("literal", Bool(), (literal(True),), True))
    with pytest.raises(TypeError): validate_classical_expr(ClassicalExpression("not", UInt(1), (literal(True),)))
    with pytest.raises(ValueError): ClassicalStore(-1)
