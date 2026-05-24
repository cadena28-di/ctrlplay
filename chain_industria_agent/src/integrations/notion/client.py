"""
Cliente Notion API — páginas, búsqueda y tareas en base de datos.
"""

from typing import Any

import requests

from src.config import settings
from src.integrations.base import IntegrationResult


class NotionClient:
    """Integración REST con Notion."""

    BASE_URL = "https://api.notion.com/v1"

    def __init__(self):
        self._headers = {
            "Authorization": f"Bearer {settings.notion_api_key}",
            "Notion-Version": settings.notion_version,
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs) -> IntegrationResult:
        if not settings.notion_enabled:
            return IntegrationResult(
                success=False,
                error="NOTION_API_KEY no configurada. Ejecuta: python scripts/setup_env.py",
                provider="notion",
            )
        try:
            response = requests.request(
                method,
                f"{self.BASE_URL}{path}",
                headers=self._headers,
                timeout=30,
                **kwargs,
            )
            if response.status_code >= 400:
                return IntegrationResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text[:300]}",
                    provider="notion",
                )
            body = response.json() if response.text else {}
            return IntegrationResult(success=True, data=body, provider="notion")
        except requests.RequestException as exc:
            return IntegrationResult(success=False, error=str(exc), provider="notion")

    def search(self, query: str, *, page_size: int = 10) -> IntegrationResult:
        return self._request(
            "POST",
            "/search",
            json={"query": query, "page_size": page_size},
        )

    def create_page(
        self,
        title: str,
        *,
        content: str | None = None,
        parent_page_id: str | None = None,
        database_id: str | None = None,
    ) -> IntegrationResult:
        parent: dict[str, Any]
        db_id = database_id or settings.notion_database_id
        page_id = parent_page_id or settings.notion_parent_page_id

        if db_id:
            parent = {"database_id": db_id}
            properties = {
                "Name": {"title": [{"text": {"content": title[:2000]}}]},
            }
        elif page_id:
            parent = {"page_id": page_id}
            properties = {
                "title": {"title": [{"text": {"content": title[:2000]}}]},
            }
        else:
            return IntegrationResult(
                success=False,
                error="Define NOTION_DATABASE_ID o NOTION_PARENT_PAGE_ID en .env",
                provider="notion",
            )

        children = []
        if content:
            for chunk in _chunk_text(content, 1900):
                children.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": chunk}}],
                        },
                    }
                )

        payload: dict[str, Any] = {"parent": parent, "properties": properties}
        if children:
            payload["children"] = children

        return self._request("POST", "/pages", json=payload)

    def create_task(
        self,
        title: str,
        *,
        status: str = "Not started",
        notes: str = "",
    ) -> IntegrationResult:
        """Crea entrada en base de datos de tareas (propiedades comunes)."""
        if not settings.notion_database_id:
            return self.create_page(title, content=notes)

        properties: dict[str, Any] = {
            "Name": {"title": [{"text": {"content": title[:2000]}}]},
        }
        properties["Status"] = {"status": {"name": status}}

        children = []
        if notes:
            children.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": notes[:1900]}}],
                    },
                }
            )

        payload: dict[str, Any] = {
            "parent": {"database_id": settings.notion_database_id},
            "properties": properties,
        }
        if children:
            payload["children"] = children

        result = self._request("POST", "/pages", json=payload)
        if result.success:
            return result

        return self.create_page(title, content=notes or f"Estado: {status}")

    def query_database(self, database_id: str | None = None, *, page_size: int = 10) -> IntegrationResult:
        db_id = database_id or settings.notion_database_id
        if not db_id:
            return IntegrationResult(
                success=False,
                error="NOTION_DATABASE_ID no configurado",
                provider="notion",
            )
        return self._request(
            "POST",
            f"/databases/{db_id}/query",
            json={"page_size": page_size},
        )


def _chunk_text(text: str, size: int) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)] or [text]
