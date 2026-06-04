from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standard response returned by all LLM providers."""

    text: str
    provider: str
    model: str


class LLMProvider(ABC):
    """Base interface for all CityFit response generation providers."""

    provider_name: str
    model_name: str

    @abstractmethod
    def generate(self, prompt: str) -> LLMResponse:
        """Generate a response from a prompt."""
        raise NotImplementedError