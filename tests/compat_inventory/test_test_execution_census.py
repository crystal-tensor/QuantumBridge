"""Static test plans cannot turn modules or possible SDK references into passes."""
import importlib.util
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location("test_execution_census", Path(__file__).parents[2]/"scripts/census_test_execution.py")
plan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan)


def put(root, name, content):
    path = root/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def test_inventory_never_imports_a_test_or_executes_its_module_body(tmp_path):
    put(tmp_path, "tests/test_bad.py", "raise RuntimeError('do not import')\ndef test_case(): pass\n")
    before = set(sys.modules)
    result = plan.census(tmp_path)
    assert set(sys.modules) == before
    assert result["module_count"] == 1 and result["tests_or_sdk_modules_imported"] is False
    assert result["collection_complete"] is result["execution_complete"] is result["public_api_denominator_closed"] is False
    assert result["modules"][0]["collected"] is result["modules"][0]["executed"] is False


def test_patterns_fixtures_relative_helpers_and_cycles_are_preserved(tmp_path):
    put(tmp_path, "pyproject.toml", '[tool.pytest.ini_options]\ntestpaths=["checks"]\npython_files=["spec_*.py"]\n')
    put(tmp_path, "checks/conftest.py", "def api():\n import pennylane\n")
    put(tmp_path, "checks/spec_one.py", "from . import helper\ndef test_case(): pass\n")
    put(tmp_path, "checks/helper.py", "from . import spec_one\nimport qiskit\n")
    put(tmp_path, "checks/test_ignored.py", "import qiskit_finance\n")
    put(tmp_path, "checks/.hidden/spec_hidden.py", "raise RuntimeError\n")
    result = plan.census(tmp_path)
    assert result["module_count"] == 1
    row, = result["modules"]
    assert row["test_dependencies"] == ["checks/conftest.py", "checks/helper.py"]
    assert row["possible_sdk_families"] == ["pennylane", "qiskit"]
    assert row["collection_lane"] == "pennylane+qiskit"
    assert len(result["source_files"]) == 4


def test_nested_importorskip_aliases_and_explicit_missing_packages_stay_in_scope(tmp_path):
    put(tmp_path, "tests/test_optional.py", 'from pytest import importorskip as require\ndef test_case():\n require("qiskit_finance")\n')
    result = plan.census(tmp_path)
    row, = result["modules"]
    assert row["possible_sdk_families"] == ["qiskit"]
    assert row["dynamic_import_calls"] == ["pytest.importorskip"]
    assert row["executed"] is False


def test_parse_errors_are_reported_without_erasing_the_candidate(tmp_path):
    put(tmp_path, "tests/test_invalid.py", "def broken(\n")
    result = plan.census(tmp_path)
    assert result["module_count"] == len(result["parse_errors"]) == 1
    assert result["parse_errors"][0]["parse_error"] == {"type": "SyntaxError", "line": 1}


def test_plan_retains_distinct_same_basename_modules_and_exact_hashes(tmp_path):
    first = put(tmp_path, "tests/a/test_same.py", "def test_a(): pass\n")
    put(tmp_path, "tests/b/test_same.py", "def test_b(): pass\n")
    result = plan.census(tmp_path)
    assert result["module_count"] == 2
    assert result["modules"][0]["sha256"] != result["modules"][1]["sha256"]
    old = result["modules"][0]["sha256"]
    first.write_text("def test_changed(): pass\n")
    assert plan.census(tmp_path)["modules"][0]["sha256"] != old


def test_cross_directory_test_helper_is_explicit_not_an_import_side_effect(tmp_path):
    put(tmp_path, "tests/compat/test_reference.py", "from test_helper import oracle\n")
    put(tmp_path, "tests/interfaces/test_helper.py", "import pennylane\n")
    row = next(row for row in plan.census(tmp_path)["modules"] if row["file"].endswith("test_reference.py"))
    assert row["test_dependencies"] == ["tests/interfaces/test_helper.py"]
    assert row["required_helper_paths"] == ["tests/interfaces"]
    assert row["possible_sdk_families"] == ["pennylane"]


def test_ambiguous_cross_directory_helpers_are_retained_without_guessing(tmp_path):
    put(tmp_path, "tests/compat/test_reference.py", "from test_helper import oracle\n")
    put(tmp_path, "tests/a/test_helper.py", "import qiskit\n")
    put(tmp_path, "tests/b/test_helper.py", "import pennylane\n")
    row = next(row for row in plan.census(tmp_path)["modules"] if row["file"].endswith("test_reference.py"))
    assert row["test_dependencies"] == row["required_helper_paths"] == []
    assert row["ambiguous_helper_imports"] == {"test_helper": ["tests/a/test_helper.py", "tests/b/test_helper.py"]}
