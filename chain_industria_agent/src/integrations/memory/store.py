"""
Almacén local de memoria (índice JSON).
Persiste búsquedas, decisiones e insights del agente.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalMemoryStore:
    """Índice persistente en memory/index.json."""

    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.index_path.exists():
            self._write([])

    def _read(self) -> list[dict[str, Any]]:
        try:
            raw = self.index_path.read_text(encoding="utf-8")
            data = json.loads(raw) if raw.strip() else []
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def _write(self, entries: list[dict[str, Any]]) -> None:
        self.index_path.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def save(
        self,
        content: str,
        *,
        entry_type: str = "fact",
        concepts: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        entry = {
            "id": str(uuid.uuid4()),
            "type": entry_type,
            "content": content,
            "concepts": concepts or [],
            "metadata": metadata or {},
            "created_at": _utc_now(),
        }
        entries = self._read()
        entries.append(entry)
        self._write(entries)
        return entry

    def log_search(
        self,
        query: str,
        sources: list[str],
        results_summary: dict[str, Any],
    ) -> dict[str, Any]:
        return self.save(
            f"Búsqueda: {query}",
            entry_type="search",
            concepts=[query, *sources],
            metadata={
                "query": query,
                "sources": sources,
                "results": results_summary,
            },
        )

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        terms = [t.lower() for t in query.split() if t.strip()]
        if not terms:
            return self._read()[-limit:]

        scored: list[tuple[int, dict[str, Any]]] = []
        for entry in self._read():
            haystack = " ".join(
                [
                    entry.get("content", ""),
                    " ".join(entry.get("concepts", [])),
                    json.dumps(entry.get("metadata", {}), ensure_ascii=False),
                ]
            ).lower()
            score = sum(1 for term in terms if term in haystack)
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:limit]]

    def list_by_type(self, entry_type: str, limit: int = 50) -> list[dict[str, Any]]:
        matches = [e for e in self._read() if e.get("type") == entry_type]
        return matches[-limit:]

    def get_search_index(self, limit: int = 50) -> list[dict[str, Any]]:
        """Índice de búsquedas/visitas registradas."""
        return self.list_by_type("search", limit=limit)
