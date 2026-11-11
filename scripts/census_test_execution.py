#!/usr/bin/env python3
"""Inventory repository test inputs without importing tests or quantum SDKs.

This is a collection/execution plan, not the public API denominator and not
evidence that any test or function has passed.
"""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
from pathlib import Path
import tomllib


DEFAULT_PATTERNS = ("test_*.py", "*_test.py")
IGNORED_DIRECTORIES = (".*", "__pycache__", "*.egg", "_darcs", "build", "CVS", "dist", "node_modules", "venv", "{arch}")


def qualified_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = qualified_name(node.value)
        return parent+"."+node.attr if parent else ""
    return ""


def sdk_family(name):
    root = name.split(".", 1)[0]
    if root == "pennylane_qiskit":
        return {"qiskit", "pennylane"}
    if root == "qiskit" or root.startswith("qiskit_"):
        return {"qiskit"}
    if root == "pennylane" or root.startswith("pennylane_"):
        return {"pennylane"}
    return set()


def test_files(root, paths, ignored):
    found = set()
    for name in paths:
        path = root/name
        if not path.resolve().is_relative_to(root):
            raise ValueError("Test inputs cannot leave the repository root")
        if path.is_file():
            found.add(path)
            continue
        if not path.is_dir():
            raise ValueError("Configured test path is missing: "+name)
        for candidate in path.rglob("*.py"):
            relative = candidate.relative_to(root)
            if any(fnmatch.fnmatchcase(part, pattern) for part in relative.parts[:-1] for pattern in ignored):
                continue
            if not candidate.resolve().is_relative_to(root):
                raise ValueError("Test inputs cannot follow an external symlink")
            found.add(candidate)
    return sorted(found)


def analyze(root, path, all_files):
    relative = path.relative_to(root).as_posix()
    data = path.read_bytes()
    row = dict(file=relative, sha256=hashlib.sha256(data).hexdigest(), direct_sdk_families=[],
        test_dependencies=[], dynamic_import_calls=[], parse_error=None)
    try:
        tree = ast.parse(data, filename=relative)
    except SyntaxError as error:
        row["parse_error"] = dict(type=type(error).__name__, line=error.lineno)
        return row
    families, dependencies, dynamic = set(), set(), set()
    helper_paths, ambiguous_helpers = set(), {}
    aliases = {}

    def resolve(parts):
        base = Path(*parts)
        for candidate in (base.with_suffix(".py"), base/"__init__.py"):
            name = candidate.as_posix()
            if name in all_files:
                dependencies.add(name)
                return True
        return False

    def resolve_helper(parts):
        if len(parts) != 1 or not parts[0].startswith("test_"):
            return
        matches = sorted(name for name in all_files if Path(name).name == parts[0]+".py")
        if len(matches) == 1:
            dependencies.add(matches[0])
            helper_paths.add(Path(matches[0]).parent.as_posix())
        elif matches:
            ambiguous_helpers[parts[0]] = matches

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                families.update(sdk_family(item.name))
                aliases[item.asname or item.name.split(".")[0]] = item.name if item.asname else item.name.split(".")[0]
                parts = item.name.split(".")
                if not resolve(parts):
                    if not resolve([*path.parent.relative_to(root).parts, *parts]):
                        resolve_helper(parts)
        elif isinstance(node, ast.ImportFrom):
            families.update(sdk_family(node.module or ""))
            for item in node.names:
                aliases[item.asname or item.name] = (node.module+"." if node.module else "")+item.name
            if node.level:
                parts = list(path.parent.relative_to(root).parts)
                parts = parts[:len(parts)-node.level+1]
                parts += (node.module or "").split(".") if node.module else []
            else:
                parts = (node.module or "").split(".")
            resolved = resolve(parts) if parts else False
            if not resolved and not node.level:
                resolved = resolve([*path.parent.relative_to(root).parts, *parts])
            if not resolved:
                for item in node.names:
                    resolve([*parts, item.name])
                if not node.level:
                    resolve_helper(parts)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = qualified_name(node.func)
        first, separator, tail = name.partition(".")
        resolved = aliases.get(first, first)+(separator+tail if separator else "")
        if resolved.rsplit(".", 1)[-1] not in {"importorskip", "import_module", "__import__", "find_spec", "spec_from_file_location", "run_path"}:
            continue
        dynamic.add(resolved)
        if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            families.update(sdk_family(node.args[0].value))
    row.update(direct_sdk_families=sorted(families), test_dependencies=sorted(dependencies),
        dynamic_import_calls=sorted(dynamic), required_helper_paths=sorted(helper_paths),
        ambiguous_helper_imports=ambiguous_helpers)
    return row


def census(root):
    root = root.resolve()
    config_path = root/"pyproject.toml"
    config = tomllib.loads(config_path.read_text()) if config_path.exists() else {}
    options = config.get("tool", {}).get("pytest", {}).get("ini_options", {})
    paths = options.get("testpaths", ["tests"])
    patterns = options.get("python_files", DEFAULT_PATTERNS)
    ignored = options.get("norecursedirs", IGNORED_DIRECTORIES)
    paths = paths.split() if isinstance(paths, str) else list(paths)
    patterns = patterns.split() if isinstance(patterns, str) else list(patterns)
    ignored = ignored.split() if isinstance(ignored, str) else list(ignored)
    files = test_files(root, paths, ignored)
    names = {path.relative_to(root).as_posix() for path in files}
    analyzed = {path.relative_to(root).as_posix(): analyze(root, path, names) for path in files}
    for name, row in analyzed.items():
        parent = Path(name).parent
        while parent != Path("."):
            fixture = (parent/"conftest.py").as_posix()
            if fixture in analyzed and fixture != name:
                row["test_dependencies"].append(fixture)
            parent = parent.parent
        row["test_dependencies"] = sorted(set(row["test_dependencies"])-{name})
    closure = {name: set(row["direct_sdk_families"]) for name, row in analyzed.items()}
    changed = True
    while changed:
        changed = False
        for name, row in analyzed.items():
            expanded = closure[name].union(*(closure[item] for item in row["test_dependencies"]))
            if expanded != closure[name]:
                closure[name] = expanded
                changed = True
    modules = []
    for name, row in analyzed.items():
        if any(fnmatch.fnmatchcase(Path(name).name, pattern) for pattern in patterns):
            families = sorted(closure[name])
            modules.append({**row, "possible_sdk_families": families,
                "collection_lane": "+".join(families) or "no_sdk_declared",
                "collected": False, "executed": False})
    return dict(schema=1, generated_at=datetime.now(timezone.utc).isoformat(),
        scope="repository_test_execution_plan_not_public_api_denominator", tests_or_sdk_modules_imported=False,
        configured_testpaths=paths, python_files=patterns, ignored_directories=ignored,
        source_files=[dict(file=name, sha256=row["sha256"]) for name, row in analyzed.items()],
        modules=modules, module_count=len(modules), lane_counts=dict(Counter(row["collection_lane"] for row in modules)),
        parse_errors=[row for row in analyzed.values() if row["parse_error"]],
        collection_complete=False, execution_complete=False, public_api_denominator_closed=False,
        limits=["Static SDK references include function bodies and test fixtures; they do not prove actual imports or execution.",
            "Dynamic paths, custom collectors, pytest hooks and plugin differences require actual isolated collection.",
            "No module, collected-item or passing-test count is an implementation percentage."])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    value = census(arguments.root)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(value, indent=2)+"\n")
    print(json.dumps({key: value[key] for key in ("scope", "module_count", "lane_counts", "collection_complete", "execution_complete")}))
