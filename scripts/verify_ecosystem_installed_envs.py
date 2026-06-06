#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Verify optional ecosystem extras in isolated temporary environments."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VENV_ROOT = Path("/tmp/quantumbridge-stage72-venvs")
DEFAULT_REPORT = ROOT / "docs/compat/inventory/stage7_2_installed_env_report.json"

PROFILES = {
    "qiskit-nature": {
        "extra": "qiskit-nature",
        "constraint": "requirements/constraints-qiskit-nature.txt",
        "inventory": "scripts/inventory_qiskit_nature_api.py",
        "tests": ["tests/compat_qiskit_nature"],
        "packages": ["qiskit-nature", "qiskit-algorithms", "pyscf", "openfermion"],
        "advisory": False,
    },
    "qiskit-finance": {
        "extra": "qiskit-finance",
        "constraint": "requirements/constraints-qiskit-finance.txt",
        "inventory": "scripts/inventory_qiskit_finance_api.py",
        "tests": ["tests/compat_qiskit_finance"],
        "packages": ["qiskit-finance"],
        "advisory": False,
    },
    "qiskit-algorithms": {
        "extra": "qiskit-algorithms",
        "constraint": "requirements/constraints-qiskit-algorithms.txt",
        "inventory": "scripts/inventory_qiskit_algorithms_api.py",
        "tests": ["tests/compat_qiskit_algorithms"],
        "packages": ["qiskit-algorithms"],
        "advisory": False,
    },
    "qiskit-machine-learning": {
        "extra": "qiskit-machine-learning",
        "constraint": "requirements/constraints-qiskit-machine-learning.txt",
        "inventory": "scripts/inventory_qiskit_machine_learning_api.py",
        "tests": ["tests/compat_qiskit_machine_learning"],
        "packages": ["qiskit-machine-learning"],
        "advisory": False,
    },
    "qiskit-optimization": {
        "extra": "qiskit-optimization",
        "constraint": "requirements/constraints-qiskit-optimization.txt",
        "inventory": "scripts/inventory_qiskit_optimization_api.py",
        "tests": ["tests/compat_qiskit_optimization"],
        "packages": ["qiskit-optimization"],
        "advisory": False,
    },
    "qiskit-dynamics": {
        "extra": "qiskit-dynamics",
        "constraint": "requirements/constraints-qiskit-dynamics.txt",
        "inventory": "scripts/inventory_qiskit_dynamics_api.py",
        "tests": ["tests/compat_qiskit_dynamics"],
        "packages": ["qiskit-dynamics"],
        "advisory": True,
    },
    "qiskit-experiments": {
        "extra": "qiskit-experiments",
        "constraint": "requirements/constraints-qiskit-experiments.txt",
        "inventory": "scripts/inventory_qiskit_experiments_api.py",
        "tests": ["tests/compat_qiskit_experiments"],
        "packages": ["qiskit-experiments"],
        "advisory": True,
    },
    "qiskit-metal": {
        "extra": "qiskit-metal",
        "constraint": "requirements/constraints-qiskit-metal.txt",
        "inventory": "scripts/inventory_qiskit_metal_api.py",
        "tests": ["tests/compat_qiskit_metal"],
        "packages": ["qiskit-metal"],
        "advisory": True,
    },
    "qiskit-aer": {
        "extra": "qiskit-aer",
        "constraint": "requirements/constraints-qiskit-aer.txt",
        "inventory": "scripts/inventory_qiskit_aer_api.py",
        "tests": ["tests/compat_qiskit_aer"],
        "packages": ["qiskit-aer"],
        "advisory": False,
    },
    "pennylane-full": {
        "extra": "pennylane-full",
        "constraint": "requirements/constraints-pennylane-full.txt",
        "inventory": "scripts/inventory_pennylane_full_api.py",
        "tests": ["tests/compat_pennylane_full"],
        "packages": ["pennylane"],
        "advisory": False,
    },
}


def _run(command: list[str], timeout: int) -> dict:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": 124,
            "stdout_tail": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": f"Timed out after {timeout} seconds",
        }


def _versions(python: Path, package_names: list[str]) -> dict[str, str | None]:
    helper = (
        "import importlib.metadata as m,json,sys\n"
        "def version(name):\n"
        "    try:\n"
        "        return m.version(name)\n"
        "    except m.PackageNotFoundError:\n"
        "        return None\n"
        "print(json.dumps({name: version(name) for name in sys.argv[1:]}, sort_keys=True))\n"
    )
    completed = subprocess.run(
        [str(python), "-c", helper, *package_names],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        return {name: None for name in package_names}
    return json.loads(completed.stdout)


def _inventory_evidence(profile_name: str) -> dict:
    prefix = profile_name.replace("-", "_")
    aliases = {
        "pennylane_full": "pennylane",
        "qiskit_nature": "qiskit_nature",
        "qiskit_algorithms": "qiskit_algorithms",
        "qiskit_machine_learning": "qiskit_machine_learning",
        "qiskit_optimization": "qiskit_optimization",
        "qiskit_dynamics": "qiskit_dynamics",
        "qiskit_experiments": "qiskit_experiments",
        "qiskit_metal": "qiskit_metal",
        "qiskit_aer": "qiskit_aer",
        "qiskit_finance": "qiskit_finance",
    }
    file_prefix = aliases.get(prefix, prefix)
    files = sorted((ROOT / "docs/compat/inventory").glob(f"{file_prefix}*_inventory.json"))
    count = 0
    unsupported = 0
    for path in files:
        rows = json.loads(path.read_text(encoding="utf-8"))
        count += sum(1 for row in rows if row.get("public_api") not in {"dependency-not-installed", "import-failed"})
        unsupported += sum(1 for row in rows if row.get("public_api") in {"dependency-not-installed", "import-failed"})
    return {
        "files": [str(path.relative_to(ROOT)) for path in files],
        "public_api_count": count,
        "unsupported_count": unsupported,
    }


def verify_profile(name: str, config: dict, venv_root: Path) -> dict:
    venv = venv_root / name
    if venv.exists():
        shutil.rmtree(venv)
    create = _run([sys.executable, "-m", "venv", str(venv)], timeout=120)
    result = {
        "profile": name,
        "extra": config["extra"],
        "constraint": config["constraint"],
        "advisory": config["advisory"],
        "python": sys.version.split()[0],
        "venv": str(venv),
        "create": create,
    }
    if create["returncode"] != 0:
        result["status"] = "venv-failed"
        return result

    python = venv / "bin/python"
    _run([str(python), "-m", "pip", "install", "--upgrade", "pip"], timeout=300)
    install = _run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "-c",
            config["constraint"],
            "-e",
            f".[{config['extra']}]",
            "pytest",
        ],
        timeout=1200,
    )
    result["install"] = install
    result["installed"] = install["returncode"] == 0
    if not result["installed"]:
        result["status"] = "install-failed"
        result["versions"] = {package: None for package in config["packages"]}
        return result

    result["versions"] = _versions(python, config["packages"])
    result["inventory"] = _run([str(python), config["inventory"]], timeout=300)
    result["tests"] = _run(
        [str(python), "-m", "pytest", "-q", "-rs", *config["tests"]],
        timeout=900,
    )
    result["pip_check"] = _run([str(python), "-m", "pip", "check"], timeout=120)
    result["inventory_evidence"] = _inventory_evidence(name)
    if result["inventory"]["returncode"] != 0:
        result["status"] = "inventory-failed"
    elif result["tests"]["returncode"] != 0:
        result["status"] = "tests-failed"
    elif result["pip_check"]["returncode"] != 0:
        result["status"] = "dependency-conflict"
    else:
        result["status"] = "verified"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", nargs="*", choices=sorted(PROFILES), default=sorted(PROFILES))
    parser.add_argument("--venv-root", type=Path, default=DEFAULT_VENV_ROOT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    args.venv_root.mkdir(parents=True, exist_ok=True)
    results = []
    for name in args.profiles:
        print(f"== verifying {name} ==", flush=True)
        result = verify_profile(name, PROFILES[name], args.venv_root)
        results.append(result)
        print(f"{name}: {result['status']}", flush=True)

    report = {
        "schema_version": "0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": str(ROOT),
        "base_python": sys.version.split()[0],
        "all_optional_mixed": False,
        "profiles": results,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
