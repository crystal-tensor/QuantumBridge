#!/usr/bin/env python3
"""Attach diagnostic observations without upgrading test or function acceptance."""
import argparse
from pathlib import Path

from record_engineering_verification import ROOT, load, native_fingerprint, sha
import json


def record(checkpoint):
    fingerprint = native_fingerprint(load(checkpoint/"source-manifest.json"))
    script = "studio/downloads/tensorflow_cached_cos_probe.py"
    observations = []
    for profile in ("main", "alternate"):
        for kind, filename in (("tf_cached_cos", "tf-cached-cos-"), ("mps_binding_retention", "mps-retention-")):
            path = checkpoint/(filename+profile+".json")
            report = load(path)
            if report["profile"] != profile or report["native_accepted"] is not False:
                raise ValueError("Diagnostics cannot claim Native acceptance")
            if kind == "tf_cached_cos":
                if (report["source_sha256"] != sha((ROOT/script).read_bytes())
                        or report["quantumbridge_or_sdks_imported"] is not False):
                    raise ValueError("The minimal control changed or imported a quantum library")
            elif (report["source_fingerprint"] != fingerprint or not report["native_modules_checked"]
                    or report["original_constructor_assertion_changed"] is not False
                    or report["constructor_before"] != report["fixed_numeric_bytes"]+sum(row["bytes"] for row in report["retained_binding_allowances"])
                    or report["constructor_after_disposal"] != 0 or report["child_terminal_memory"] != 0):
                raise ValueError("Binding diagnostic identity or lifetime evidence differs")
            observations.append(dict(id=kind+"-"+profile, kind=kind, profile=profile,
                recorded_at=report["recorded_at"], evidence_hash=sha(path.read_bytes()),
                source_file=script if kind == "tf_cached_cos" else None, report=report,
                scope="diagnostic_observation_not_function_or_test_acceptance"))
    value = dict(schema=1, source_fingerprint=fingerprint, observations=observations)
    output = ROOT/"docs/engineering/diagnostic_observations.json"
    output.write_text(json.dumps(value, indent=2)+"\n")
    print(json.dumps(dict(source_fingerprint=fingerprint, observations=len(observations), native_accepted=False)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True, type=Path)
    record(parser.parse_args().checkpoint.resolve())
