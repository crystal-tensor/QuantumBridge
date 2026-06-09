from quantumbridge.studio.fastapi_adapter import create_fastapi_app_if_available, fastapi_available


def test_fastapi_adapter_optional_boundary():
    result = create_fastapi_app_if_available()
    if fastapi_available():
        assert getattr(result.state, "server_started") is False
    else:
        assert result["available"] is False
        assert result["server_started"] is False
        assert result["token_access"] is False
