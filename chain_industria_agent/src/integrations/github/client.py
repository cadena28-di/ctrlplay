"""
Cliente GitHub REST API — issues, repositorio y búsqueda de código.
"""

from typing import Any

import requests

from src.config import settings
from src.integrations.base import IntegrationResult


class GitHubClient:
    """Integración con GitHub API."""

    def __init__(self):
        self._headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if settings.github_token:
            self._headers["Authorization"] = f"Bearer {settings.github_token}"

    @property
    def _base(self) -> str:
        return settings.github_api_url.rstrip("/")

    def _repo_path(self, repo: str | None = None) -> str:
        return f"/repos/{repo or settings.github_repo}"

    def _request(self, method: str, path: str, **kwargs) -> IntegrationResult:
        if not settings.github_enabled:
            return IntegrationResult(
                success=False,
                error="GITHUB_TOKEN no configurado. Ejecuta: python scripts/setup_env.py",
                provider="github",
            )
        try:
            response = requests.request(
                method,
                f"{self._base}{path}",
                headers=self._headers,
                timeout=30,
                **kwargs,
            )
            if response.status_code >= 400:
                return IntegrationResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text[:300]}",
                    provider="github",
                )
            if response.status_code == 204:
                return IntegrationResult(success=True, data={}, provider="github")
            body = response.json() if response.text else {}
            return IntegrationResult(success=True, data=body, provider="github")
        except requests.RequestException as exc:
            return IntegrationResult(success=False, error=str(exc), provider="github")

    def verify_token(self) -> IntegrationResult:
        """Comprueba que el token es válido (GET /user)."""
        return self._request("GET", "/user")

    def get_repo(self, repo: str | None = None) -> IntegrationResult:
        verify = self.verify_token()
        if not verify.success:
            return verify
        target = repo or settings.github_repo
        result = self._request("GET", self._repo_path(target))
        if not result.success and "404" in (result.error or ""):
            login = (verify.data or {}).get("login", "")
            hint = (
                f"Repo '{target}' no encontrado o sin acceso. "
                f"Verifica GITHUB_REPO en .env. Usuario del token: {login}"
            )
            return IntegrationResult(
                success=False,
                error=hint,
                provider="github",
                metadata={"login": login, "repo": target},
            )
        return result

    def list_issues(
        self,
        *,
        repo: str | None = None,
        state: str = "open",
        per_page: int = 10,
    ) -> IntegrationResult:
        return self._request(
            "GET",
            f"{self._repo_path(repo)}/issues",
            params={"state": state, "per_page": per_page},
        )

    def create_issue(
        self,
        title: str,
        *,
        body: str = "",
        labels: list[str] | None = None,
        repo: str | None = None,
    ) -> IntegrationResult:
        payload: dict[str, Any] = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels
        return self._request("POST", f"{self._repo_path(repo)}/issues", json=payload)

    def search_code(self, query: str, *, per_page: int = 5) -> IntegrationResult:
        q = f"{query} repo:{settings.github_repo}"
        return self._request(
            "GET",
            "/search/code",
            params={"q": q, "per_page": per_page},
        )

    def list_pulls(
        self,
        *,
        repo: str | None = None,
        state: str = "open",
        per_page: int = 5,
    ) -> IntegrationResult:
        return self._request(
            "GET",
            f"{self._repo_path(repo)}/pulls",
            params={"state": state, "per_page": per_page},
        )
