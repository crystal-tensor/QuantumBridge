"""Preserve per-observation identities when diagnostic batches are updated."""
from copy import deepcopy

SCOPE = "diagnostic_observation_not_function_or_test_acceptance"


def valid_fingerprint(value):
    return (isinstance(value, str) and len(value) == 64
            and all(char in "0123456789abcdef" for char in value))


def checked_observation(row, fallback):
    value = deepcopy(row)
    report = value["report"]
    explicit = value.get("source_fingerprint")
    reported = report.get("source_fingerprint")
    fingerprint = explicit if "source_fingerprint" in value else reported if "source_fingerprint" in report else fallback
    if (not valid_fingerprint(fingerprint)
            or "source_fingerprint" in value and not valid_fingerprint(explicit)
            or "source_fingerprint" in report and not valid_fingerprint(reported)
            or explicit and reported and explicit != reported):
        raise ValueError("Diagnostic source identity is missing or conflicting")
    if (report["native_accepted"] is not False or value["scope"] != SCOPE
            or not value.get("id") or not value.get("recorded_at") or not value.get("evidence_hash")):
        raise ValueError("Diagnostics require original receipts and cannot claim acceptance")
    value["source_fingerprint"] = fingerprint
    return value


def merge_observations(existing, fingerprint, replacements):
    """Update named diagnostics without relabeling or dropping other evidence."""
    if not valid_fingerprint(fingerprint):
        raise ValueError("New diagnostic source identity is invalid")
    result = deepcopy(existing)
    rows = [checked_observation(row, existing.get("source_fingerprint"))
            for row in existing.get("observations", [])]
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate stored diagnostic identity")
    incoming = [checked_observation(row, fingerprint) for row in replacements]
    if (len({row["id"] for row in incoming}) != len(incoming)
            or any(row["source_fingerprint"] != fingerprint for row in incoming)):
        raise ValueError("Duplicate or mismatched new diagnostic identity")
    history = [checked_observation(row, existing.get("source_fingerprint"))
               for row in existing.get("historical_observations", [])]
    positions = {row["id"]: index for index, row in enumerate(rows)}
    for replacement in incoming:
        index = positions.get(replacement["id"])
        if index is None:
            positions[replacement["id"]] = len(rows)
            rows.append(replacement)
        else:
            previous = rows[index]
            if previous != replacement and previous not in history:
                history.append(previous)
            rows[index] = replacement
    result.update(schema=1, source_fingerprint=fingerprint, observations=rows,
                  historical_observations=history)
    return result
