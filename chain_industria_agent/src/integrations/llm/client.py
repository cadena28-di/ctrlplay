"""
Cliente LLM: Anthropic Messages API con fallback a plantillas locales.
"""

from typing import Any

import requests

from src.config import settings
from src.integrations.base import IntegrationResult


class LLMClient:
    """Generación de texto para Creative y análisis asistido."""

    ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> IntegrationResult:
        if settings.llm_enabled:
            return self._complete_anthropic(
                prompt,
                system=system,
                max_tokens=max_tokens,
            )
        return self._complete_fallback(prompt)

    def _complete_anthropic(
        self,
        prompt: str,
        *,
        system: str | None,
        max_tokens: int,
    ) -> IntegrationResult:
        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": settings.anthropic_model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system

        try:
            response = requests.post(
                self.ANTHROPIC_URL,
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            body = response.json()
            text = ""
            for block in body.get("content", []):
                if block.get("type") == "text":
                    text += block.get("text", "")
            return IntegrationResult(
                success=True,
                data={"text": text.strip()},
                provider="anthropic",
                metadata={"model": settings.anthropic_model},
            )
        except requests.RequestException as exc:
            return IntegrationResult(
                success=False,
                error=str(exc),
                provider="anthropic",
            )

    def _complete_fallback(self, prompt: str) -> IntegrationResult:
        preview = prompt[:200] + ("..." if len(prompt) > 200 else "")
        return IntegrationResult(
            success=True,
            data={
                "text": (
                    f"[Modo local — sin ANTHROPIC_API_KEY]\n"
                    f"Respuesta simulada para: {preview}"
                )
            },
            provider="fallback",
            metadata={"hint": "Define ANTHROPIC_API_KEY en .env para LLM real"},
        )
