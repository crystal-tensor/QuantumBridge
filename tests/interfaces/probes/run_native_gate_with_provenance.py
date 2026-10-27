# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Run an actual local development gate with same-process provenance evidence.

The selected source/test roots are recorded, not full worktree/Git equality.
Evidence is emitted after real pytest/example execution, including failures.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import traceback


ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOTS = ("quantumbridge", "tests", "examples", "docs/compat", "requirements", ".github/workflows")
SOURCE_FILES = ("pyproject.toml", "README.md", "THIRD_PARTY_NOTICES.md")
FORBIDDEN = ("qiskit", "pennylane", "tensorflow", "jax")


def manifest():
    paths = {ROOT/name for name in SOURCE_FILES if (ROOT/name).is_file()}
    for name in SOURCE_ROOTS:
        paths.update(path for path in (ROOT/name).rglob("*") if path.is_file()
            and not any(part in {"__pycache__", ".pytest_cache"} for part in path.relative_to(ROOT).parts)
            and path.name != ".DS_Store")
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


class Outcomes:
    counts = None

    def pytest_terminal_summary(self, terminalreporter):
        self.counts = {name: len(terminalreporter.stats.get(name, ())) for name in
            ("passed", "failed", "skipped", "xfailed", "xpassed", "error", "deselected")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--sdk-free", action="store_true")
    parser.add_argument("--example", action="append", default=[])
    options, arguments = parser.parse_known_args()
    if arguments[:1] == ["--"]:
        arguments = arguments[1:]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    started = datetime.now(timezone.utc).isoformat()
    before, after, error, examples = manifest(), None, None, []
    origins_before = {name: importlib.util.find_spec(name) is not None for name in FORBIDDEN}
    outcomes, code = Outcomes(), 1
    try:
        if options.sdk_free and (not sys.flags.no_user_site or any(origins_before.values())):
            raise RuntimeError("Strict SDK-free gate requires python -s and absent SDK/TF/JAX resolution.")
        if options.example:
            saved = sys.argv
            try:
                for name in options.example:
                    path = ROOT/name
                    sys.argv = [str(path)]
                    runpy.run_path(str(path), run_name="__main__")
                    examples.append(dict(path=name, completed=True))
                code = 0
            finally:
                sys.argv = saved
        else:
            import pytest
            code = int(pytest.main(arguments, plugins=[outcomes]))
    except BaseException:
        error = traceback.format_exc()
    finally:
        after = manifest()
        imported = {name: sys.modules.get(name) for name in
            ("quantumbridge", "numpy", "scipy", "tensorflow", "torch", "autograd", "jax", "jaxlib", "qiskit", "pennylane")}
        origins = {name: dict(imported_in_gate_process=module is not None,
            origin=getattr(module, "__file__", None), version=getattr(module, "__version__", None))
            for name, module in imported.items()}
        forbidden_after = sorted({name.split(".")[0] for name in sys.modules if name.split(".")[0] in FORBIDDEN})
        if before != after or options.sdk_free and forbidden_after:
            code = code or 2
        record = dict(protocol_version=1, started_utc=started, ended_utc=datetime.now(timezone.utc).isoformat(),
            head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            executable=sys.executable, python=sys.version, no_user_site=bool(sys.flags.no_user_site),
            pytest_arguments=arguments, examples=examples, exit_code=code, outcomes=outcomes.counts,
            selected_manifest_roots=SOURCE_ROOTS, selected_manifest_files=SOURCE_FILES,
            source_before=before, source_after=after, source_unchanged=before == after,
            same_process_import_origins=origins, sdk_free_requested=options.sdk_free,
            forbidden_resolution_before=origins_before, forbidden_imports_after=forbidden_after,
            environment={name: os.environ.get(name) for name in ("PYTHONNOUSERSITE", "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
                "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "JAX_ENABLE_X64")}, error=error,
            scope="selected local development gate only; not FULL, full-worktree or staged/commit equality")
        options.evidence.parent.mkdir(parents=True, exist_ok=True)
        options.evidence.write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
        print(json.dumps(dict(evidence=str(options.evidence), exit_code=code, outcomes=outcomes.counts,
            source_files=len(before), source_unchanged=before == after, error=error), indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
