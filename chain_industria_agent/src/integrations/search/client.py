"""
Cliente de búsqueda web: Tavily (real) o mock (desarrollo sin API key).
"""

from typing import Any

import requests

from src.config import settings
from src.integrations.base import IntegrationResult


class SearchClient:
    """Búsqueda unificada para el módulo Researcher."""

    TAVILY_URL = "https://api.tavily.com/search"

    def search(self, query: str, *, max_results: int = 5) -> IntegrationResult:
        if self._use_tavily():
            return self._search_tavily(query, max_results=max_results)
        return self._search_mock(query, max_results=max_results)

    def _use_tavily(self) -> bool:
        if settings.search_provider == "mock":
            return False
        if settings.search_provider == "tavily":
            return bool(settings.tavily_api_key)
        return settings.search_enabled

    def _search_tavily(self, query: str, *, max_results: int) -> IntegrationResult:
        try:
            response = requests.post(
                self.TAVILY_URL,
                json={
                    "api_key": settings.tavily_api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": True,
                },
                timeout=30,
            )
            response.raise_for_status()
            body = response.json()
            results = [
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")[:500],
                }
                for item in body.get("results", [])
            ]
            return IntegrationResult(
                success=True,
                data={
                    "query": query,
                    "answer": body.get("answer"),
                    "results": results,
                    "results_found": len(results),
                },
                provider="tavily",
                metadata={"max_results": max_results},
            )
        except requests.RequestException as exc:
            return IntegrationResult(
                success=False,
                error=str(exc),
                provider="tavily",
            )

    def _search_mock(self, query: str, *, max_results: int) -> IntegrationResult:
        results = [
            {
                "title": f"Resultado mock {i + 1} para '{query}'",
                "url": f"https://example.com/result/{i + 1}",
                "snippet": f"Fragmento simulado sobre {query} (configura TAVILY_API_KEY para datos reales).",
            }
            for i in range(min(max_results, 3))
        ]
        return IntegrationResult(
            success=True,
            data={
                "query": query,
                "answer": f"Resumen simulado para: {query}",
                "results": results,
                "results_found": len(results),
            },
            provider="mock",
            metadata={"hint": "Define TAVILY_API_KEY en .env para búsqueda real"},
        )
