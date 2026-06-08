import pytest

from quantumbridge.compat.qiskit_finance.applications_adapter import ADAPTER as APPLICATIONS
from quantumbridge.compat.qiskit_finance.data_provider_adapter import ADAPTER as DATA_PROVIDER


def test_qiskit_finance_dependency_and_inventory_contract():
    assert isinstance(APPLICATIONS.dependency_available(), bool)
    assert APPLICATIONS.list_public_api_inventory()


def test_qiskit_finance_passthrough_or_clear_import_error():
    if APPLICATIONS.dependency_available():
        assert APPLICATIONS.passthrough_class("PortfolioOptimization") is not None
    else:
        with pytest.raises(ImportError, match="qiskit-finance"):
            APPLICATIONS.passthrough_class("PortfolioOptimization")


def test_qiskit_finance_data_provider_result_wrapper():
    wrapped = DATA_PROVIDER.wrap_result({"assets": ["A", "B"], "mode": "smoke"})
    assert wrapped["provenance"]["adapter_package"] == "qiskit-finance"
    assert wrapped["provenance"]["official_endorsement"] is False


def test_qiskit_finance_named_availability_or_clear_import_error():
    if APPLICATIONS.dependency_available():
        assert APPLICATIONS.passthrough_class("PortfolioOptimization") is not None
        assert APPLICATIONS.passthrough_class("EuropeanCallPricing") is not None
    else:
        with pytest.raises(ImportError, match="qiskit-finance"):
            APPLICATIONS.passthrough_class("EuropeanCallPricing")

    if DATA_PROVIDER.dependency_available():
        assert DATA_PROVIDER.passthrough_class("RandomDataProvider") is not None
    else:
        with pytest.raises(ImportError, match="qiskit-finance"):
            DATA_PROVIDER.passthrough_class("RandomDataProvider")


def test_qiskit_finance_unsupported_warning():
    with pytest.warns(UserWarning, match="does not implement"):
        APPLICATIONS.warn_unsupported("production finance valuation")
