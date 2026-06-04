from cityfit.llm.base import LLMProvider
from cityfit.llm.ollama_provider import OllamaProvider
from cityfit.llm.template_provider import TemplateProvider


def get_llm_provider(response_mode: str) -> LLMProvider:
    """
    Return the requested response generation provider.

    response_mode options:
    - template: deterministic fallback
    - llm: local Ollama provider
    """
    if response_mode == "template":
        return TemplateProvider()

    if response_mode == "llm":
        return OllamaProvider()

    raise ValueError(f"Unsupported response_mode: {response_mode}")