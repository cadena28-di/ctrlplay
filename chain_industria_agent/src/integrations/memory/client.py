"""
Cliente de memoria: almacén local + opcional HTTP hacia AgentMemory.
"""

from typing import Any

import requests

from src.config import settings
from src.integrations.base import IntegrationResult
from src.integrations.memory.store import LocalMemoryStore


class MemoryClient:
    """Fachada unificada de memoria persistente."""

    def __init__(self, store: LocalMemoryStore | None = None):
        self._store = store or LocalMemoryStore(settings.memory_index_path)
        self._remote_url = settings.agentmemory_url.rstrip("/") if settings.agentmemory_url else ""

    def save(
        self,
        content: str,
        *,
        entry_type: str = "fact",
        concepts: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> IntegrationResult:
        entry = self._store.save(
            content,
            entry_type=entry_type,
            concepts=concepts,
            metadata=metadata,
        )
        remote = self._sync_remote(content, entry_type, concepts)
        return IntegrationResult(
            success=True,
            data=entry,
            provider="local" + ("+remote" if remote else ""),
            metadata={"remote_synced": remote},
        )

    def log_search(
        self,
        query: str,
        sources: list[str],
        results_summary: dict[str, Any],
    ) -> IntegrationResult:
        entry = self._store.log_search(query, sources, results_summary)
        return IntegrationResult(success=True, data=entry, provider="local")

    def recall(self, query: str, limit: int = 10) -> IntegrationResult:
        entries = self._store.search(query, limit=limit)
        return IntegrationResult(
            success=True,
            data=entries,
            provider="local",
            metadata={"count": len(entries)},
        )

    def get_search_index(self, limit: int = 50) -> IntegrationResult:
        entries = self._store.get_search_index(limit=limit)
        return IntegrationResult(
            success=True,
            data=entries,
            provider="local",
            metadata={"count": len(entries)},
        )

    def _sync_remote(
        self,
        content: str,
        entry_type: str,
        concepts: list[str] | None,
    ) -> bool:
        if not self._remote_url:
            return False
        try:
            headers = {}
            if settings.agentmemory_api_key:
                headers["Authorization"] = f"Bearer {settings.agentmemory_api_key}"
            payload = {
                "content": content,
                "type": entry_type,
                "concepts": ",".join(concepts or []),
            }
            response = requests.post(
                f"{self._remote_url}/memory",
                json=payload,
                headers=headers,
                timeout=10,
            )
            return response.ok
        except requests.RequestException:
            return False
