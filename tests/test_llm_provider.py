import pytest

from cityfit.llm.ollama_provider import OllamaProvider
from cityfit.llm.provider import get_llm_provider
from cityfit.llm.template_provider import TemplateProvider


def test_template_provider_returns_prompt_as_text():
    provider = TemplateProvider()

    response = provider.generate("Hello CityFit")

    assert response.text == "Hello CityFit"
    assert response.provider == "deterministic_template"
    assert response.model == "no_llm_v1"


def test_provider_factory_returns_template_provider():
    provider = get_llm_provider("template")

    assert isinstance(provider, TemplateProvider)


def test_provider_factory_returns_ollama_provider():
    provider = get_llm_provider("llm")

    assert isinstance(provider, OllamaProvider)


def test_provider_factory_rejects_invalid_response_mode():
    with pytest.raises(ValueError, match="Unsupported response_mode"):
        get_llm_provider("invalid")