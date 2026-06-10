import json

import pytest

from quantumbridge.studio.frontend_contract import build_frontend_seed_bundle, validate_no_branding_or_secrets_in_seed


def test_frontend_seed_has_no_external_endpoints_branding_assets_or_secret_like_values():
    bundle = build_frontend_seed_bundle()

    assert validate_no_branding_or_secrets_in_seed(bundle)
    text = json.dumps(bundle, sort_keys=True).lower()
    assert "https://" not in text
    assert "http://" not in text
    assert "ibm-logo" not in text
    assert "qiskit-logo" not in text
    assert "pennylane-logo" not in text
    assert "carbon-components" not in text
    assert "bearer " not in text
    assert "api_key" not in text
    assert "secret_value" not in text


def test_frontend_seed_secret_like_values_are_rejected():
    bundle = build_frontend_seed_bundle()
    bundle["catalog"]["projects"].append({"project_id": "bad", "note": "api_key=not-allowed"})

    with pytest.raises(ValueError, match="forbidden seed pattern"):
        validate_no_branding_or_secrets_in_seed(bundle)
