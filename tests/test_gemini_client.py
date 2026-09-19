import pytest
from unittest.mock import MagicMock, patch
from src.ai.gemini_client import get_available_gemini_models, GeminiClient
from src.config import DEFAULT_GEMINI_MODELS

class MockModel:
    def __init__(self, name, supported_actions=None):
        self.name = name
        self.supported_actions = supported_actions or ['generateContent']

def test_get_available_gemini_models_with_none_client():
    models = get_available_gemini_models(None)
    assert models == DEFAULT_GEMINI_MODELS[:5]

def test_get_available_gemini_models_filtering_and_sorting():
    mock_client = MagicMock()
    mock_client.models.list.return_value = [
        MockModel('models/gemini-1.5-pro', ['generateContent']),
        MockModel('models/gemini-2.5-flash-lite', ['generateContent']),
        MockModel('models/gemini-2.5-flash', ['generateContent']),
        MockModel('models/gemini-2.0-flash', ['generateContent']),
        MockModel('models/gemini-1.5-flash', ['generateContent']),
        MockModel('models/text-embedding-004', ['embedContent']),
        MockModel('models/imagen-3.0-generate-002', ['generateImages']),
        MockModel('models/gemini-2.0-flash-exp', ['generateContent']),
        MockModel('models/gemini-2.5-flash-tts', ['generateContent']),
        MockModel('models/gemini-2.5-flash-realtime', ['generateContent']),
    ]

    models = get_available_gemini_models(mock_client, max_candidates=4)

    # 期待される順序:
    # 1. gemini-2.5-flash (Flash, v2.5, 安定版, 標準)
    # 2. gemini-2.5-flash-lite (Flash, v2.5, 安定版, lite)
    # 3. gemini-2.0-flash (Flash, v2.0, 安定版, 標準)
    # 4. gemini-1.5-flash (Flash, v1.5, 安定版, 標準)
    assert models == [
        'gemini-2.5-flash',
        'gemini-2.5-flash-lite',
        'gemini-2.0-flash',
        'gemini-1.5-flash'
    ]

def test_get_available_gemini_models_exception_fallback():
    mock_client = MagicMock()
    mock_client.models.list.side_effect = Exception("API Connection Error")

    models = get_available_gemini_models(mock_client)
    assert models == DEFAULT_GEMINI_MODELS[:5]

def test_gemini_client_fallback_execution():
    client = GeminiClient(api_key="fake-key", models=["model-a", "model-b"])

    # model-a で 404 エラー、model-b で成功するケース
    calls = []
    def mock_func(*args, **kwargs):
        model = kwargs.get("model")
        calls.append(model)
        if model == "model-a":
            raise Exception("404 Model Not Found")
        return "success-result"

    result, used_model = client._call_with_fallback(mock_func)
    assert result == "success-result"
    assert used_model == "model-b"
    assert calls == ["model-a", "model-b"]

def test_gemini_client_all_fallback_fail():
    client = GeminiClient(api_key="fake-key", models=["model-a", "model-b"])

    def mock_func(*args, **kwargs):
        raise Exception("500 Internal Error")

    with pytest.raises(Exception) as exc_info:
        client._call_with_fallback(mock_func)

    assert "500 Internal Error" in str(exc_info.value)
