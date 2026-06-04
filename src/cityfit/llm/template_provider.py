from cityfit.llm.base import LLMProvider, LLMResponse


class TemplateProvider(LLMProvider):
    """Deterministic fallback provider that returns a prebuilt answer."""

    provider_name = "deterministic_template"
    model_name = "no_llm_v1"

    def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(
            text=prompt,
            provider=self.provider_name,
            model=self.model_name,
        )