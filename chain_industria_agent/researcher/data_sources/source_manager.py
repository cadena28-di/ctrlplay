"""
Source Manager - Gestor de fuentes de datos
"""

from src.integrations.search.client import SearchClient


class SourceManager:
    def __init__(self, search_client: SearchClient | None = None):
        self.search_client = search_client or SearchClient()
        self.available_sources = [
            "web",
            "api",
            "database",
            "cache",
            "files",
            "social_media",
        ]
        self.default_sources = ["web", "api", "cache"]

    def get_default_sources(self):
        return self.default_sources

    def set_default_sources(self, sources):
        self.default_sources = sources

    def search(self, query, source):
        if source == "web":
            result = self.search_client.search(query)
            if result.success:
                data = result.data or {}
                return {
                    "source": source,
                    "query": query,
                    "provider": result.provider,
                    "results_found": data.get("results_found", 0),
                    "answer": data.get("answer"),
                    "results": data.get("results", []),
                    "relevance": 0.92 if result.provider != "mock" else 0.5,
                    "status": "success",
                }
            return {
                "source": source,
                "query": query,
                "status": "error",
                "error": result.error,
                "results_found": 0,
            }

        if source == "cache":
            return {
                "source": source,
                "query": query,
                "results_found": 0,
                "status": "cache_miss",
                "message": "Sin resultados en caché local",
            }

        return {
            "source": source,
            "query": query,
            "results_found": 0,
            "status": "not_implemented",
            "message": f"Fuente '{source}' pendiente de integración",
        }

    def get_available_sources(self):
        return self.available_sources
