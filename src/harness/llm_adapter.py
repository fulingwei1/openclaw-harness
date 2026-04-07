"""
LLM Adapter - 统一的 LLM 调用接口
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import openai
import anthropic


class LLMAdapter(ABC):
    """Abstract base class for LLM adapters"""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate response from LLM"""
        pass


class OpenAIAdapter(LLMAdapter):
    """OpenAI API adapter"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content


class AnthropicAdapter(LLMAdapter):
    """Anthropic API adapter"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        kwargs.setdefault("max_tokens", 4096)

        response = self.client.messages.create(
            model=self.model,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.content[0].text


def get_llm_adapter(provider: str = "openai", **kwargs) -> LLMAdapter:
    """Factory function to get LLM adapter"""
    if provider == "openai":
        return OpenAIAdapter(**kwargs)
    elif provider == "anthropic":
        return AnthropicAdapter(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")
