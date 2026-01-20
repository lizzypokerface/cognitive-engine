import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    @abstractmethod
    def query(self, prompt: str, model: str = "default") -> str:
        pass


class MockLLMClient(BaseLLMClient):
    """
    Simulates an LLM response for testing workflows without cost.
    """

    def query(self, prompt: str, model: str = "default") -> str:
        # Determine what kind of prompt it is to give a relevant mock response
        if "summary" in prompt.lower() or "summarize" in prompt.lower():
            return f"[[Mock Summary using {model}]]: The text discusses key concepts X, Y, and Z. It argues that..."
        elif "action" in prompt.lower() or "strategy" in prompt.lower():
            return f"[[Mock Action Plan using {model}]]:\n1. Do this.\n2. Do that.\n3. Profit."
        else:
            return (
                f"[[Mock Response using {model}]]: Processed {len(prompt)} characters."
            )


class ProductionLLMClient(BaseLLMClient):
    """
    The real client. Currently disabled/placeholder until you add API keys.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Future: Initialize OpenAI/Poe client here
        # self.api_key = config.get("api_keys", {}).get("poe_api")

    def query(self, prompt: str, model: str = "default") -> str:
        raise NotImplementedError(
            "Real API calls are not yet enabled. Use the Mock client."
        )


def get_llm_client(config: Dict[str, Any]) -> BaseLLMClient:
    """
    Factory to return the correct client.
    For now, we strictly return MockLLMClient to keep the testing free.
    """
    # In the future, you can toggle this via config.yaml:
    # provider = config.get("llm_provider", "mock")
    # if provider == "poe": return ProductionLLMClient(config)

    return MockLLMClient()
