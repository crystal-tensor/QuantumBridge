from quantumbridge.ecosystem import (
    SHARED_FOUNDATION,
    industry_capabilities,
    industry_categories,
    industry_taxonomy,
    validate_industry_taxonomy,
)


def test_industry_taxonomy_preserves_canonical_categories_and_capabilities():
    assert validate_industry_taxonomy()
    categories = industry_categories()
    assert [item.display_name for item in categories] == ["科学计算", "金融", "工业优化", "量子安全"]
    assert [len(item.capabilities) for item in categories] == [4, 5, 5, 5]
    assert len(industry_capabilities()) == 19


def test_qiskit_and_cirq_are_comparisons_not_product_categories():
    payload = industry_taxonomy()
    assert payload["comparison_ecosystems"] == ["Qiskit", "Cirq"]
    assert "quafu_cloud_execution" in SHARED_FOUNDATION
    assert all(item["display_name"] not in {"Qiskit", "Cirq"} for item in payload["product_categories"])
