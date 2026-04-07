from __future__ import annotations

import json
import os
import re
from typing import Any, Callable, TypeVar

from pydantic import BaseModel

from harness.models import LLMSettings


SchemaModel = TypeVar("SchemaModel", bound=BaseModel)
FallbackFactory = Callable[[], str | BaseModel]


class LLMClient:
    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings
        self._client: Any | None = None

    @property
    def provider(self) -> str:
        return self.settings.provider

    def is_configured(self) -> bool:
        env_name = "OPENAI_API_KEY" if self.provider == "openai" else "ANTHROPIC_API_KEY"
        return bool(os.getenv(env_name))

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        fallback: FallbackFactory | None = None,
    ) -> str:
        if self.is_configured():
            return self._complete_text_with_provider(system_prompt, user_prompt)

        if fallback and self.settings.allow_fallback:
            value = fallback()
            if isinstance(value, BaseModel):
                return value.model_dump_json(indent=2)
            return str(value)

        env_name = "OPENAI_API_KEY" if self.provider == "openai" else "ANTHROPIC_API_KEY"
        raise RuntimeError(
            f"{env_name} is not set. Configure the provider or enable a fallback implementation."
        )

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: type[SchemaModel],
        *,
        fallback: Callable[[], SchemaModel] | None = None,
    ) -> SchemaModel:
        if self.is_configured():
            instructions = (
                f"{system_prompt}\n\n"
                "Return JSON only. Follow this JSON schema exactly:\n"
                f"{json.dumps(schema.model_json_schema(), indent=2, ensure_ascii=False)}"
            )
            raw = self._complete_text_with_provider(instructions, user_prompt)
            payload = self._extract_json(raw)
            return schema.model_validate(payload)

        if fallback and self.settings.allow_fallback:
            return fallback()

        env_name = "OPENAI_API_KEY" if self.provider == "openai" else "ANTHROPIC_API_KEY"
        raise RuntimeError(
            f"{env_name} is not set. Configure the provider or enable a fallback implementation."
        )

    def _complete_text_with_provider(self, system_prompt: str, user_prompt: str) -> str:
        if self.provider == "openai":
            return self._complete_with_openai(system_prompt, user_prompt)
        if self.provider == "anthropic":
            return self._complete_with_anthropic(system_prompt, user_prompt)
        raise ValueError(f"Unsupported provider: {self.provider}")

    def _complete_with_openai(self, system_prompt: str, user_prompt: str) -> str:
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI()

        response = self._client.responses.create(
            model=self.settings.model,
            instructions=system_prompt,
            input=user_prompt,
            temperature=self.settings.temperature,
            max_output_tokens=self.settings.max_output_tokens,
        )

        output_text = getattr(response, "output_text", None)
        if output_text:
            return output_text.strip()

        parts: list[str] = []
        for item in getattr(response, "output", []):
            for content in getattr(item, "content", []):
                text = getattr(content, "text", None)
                if text:
                    parts.append(text)
        return "\n".join(parts).strip()

    def _complete_with_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        if self._client is None:
            from anthropic import Anthropic

            self._client = Anthropic()

        response = self._client.messages.create(
            model=self.settings.model,
            max_tokens=self.settings.max_output_tokens,
            temperature=self.settings.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        parts: list[str] = []
        for block in getattr(response, "content", []):
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "\n".join(parts).strip()

    @staticmethod
    def _extract_json(raw: str) -> Any:
        stripped = raw.strip()
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

        fenced = re.search(r"```json\s*(.*?)```", stripped, re.DOTALL | re.IGNORECASE)
        if fenced:
            return json.loads(fenced.group(1).strip())

        for pattern in (r"\{.*\}", r"\[.*\]"):
            match = re.search(pattern, stripped, re.DOTALL)
            if match:
                return json.loads(match.group(0))

        raise ValueError("Model response did not contain valid JSON.")
