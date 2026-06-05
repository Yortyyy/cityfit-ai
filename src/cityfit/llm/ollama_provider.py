import os

import requests

from cityfit.llm.base import LLMProvider, LLMResponse


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


class OllamaProvider(LLMProvider):
    """Local Ollama provider for optional LLM-generated responses."""

    provider_name = "ollama"

    def __init__(self, model_name: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> LLMResponse:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return LLMResponse(
            text=data.get("response", "").strip(),
            provider=self.provider_name,
            model=self.model_name,
        )