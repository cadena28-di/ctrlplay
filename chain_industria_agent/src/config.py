"""
Configuración central del agente Chain Industria.
Carga variables desde .env (python-dotenv).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEMORY_DIR = PROJECT_ROOT / "memory"
MEMORY_INDEX_PATH = MEMORY_DIR / "index.json"
ENV_PATH = PROJECT_ROOT / ".env"
ENV_EXAMPLE_PATH = PROJECT_ROOT / ".env.example"


def _load_env() -> None:
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH, override=True)


def _env(key: str, default: str = "") -> str:
    value = os.getenv(key, default) or ""
    return value.strip().strip('"').strip("'")


class Settings:
    """Configuración leída del entorno."""

    def __init__(self) -> None:
        _load_env()
        self.project_root: Path = PROJECT_ROOT
        self.memory_dir: Path = MEMORY_DIR
        self.memory_index_path: Path = MEMORY_INDEX_PATH
        self.env_path: Path = ENV_PATH

        self.anthropic_api_key: str = _env("ANTHROPIC_API_KEY")
        self.anthropic_model: str = _env("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        self.tavily_api_key: str = _env("TAVILY_API_KEY")
        self.search_provider: str = _env("SEARCH_PROVIDER", "auto")
        self.agentmemory_url: str = _env("AGENTMEMORY_URL")
        self.agentmemory_api_key: str = _env("AGENTMEMORY_API_KEY")
        self.notion_api_key: str = _env("NOTION_API_KEY")
        self.notion_version: str = _env("NOTION_VERSION", "2022-06-28")
        self.notion_database_id: str = _env("NOTION_DATABASE_ID")
        self.notion_parent_page_id: str = _env("NOTION_PARENT_PAGE_ID")
        self.github_token: str = _env("GITHUB_TOKEN")
        self.github_repo: str = _env(
            "GITHUB_REPO", "chaiindustriaceoempresa-gif/agente_industrial_cadena"
        )
        self.github_api_url: str = _env("GITHUB_API_URL", "https://api.github.com")
        self.org_name: str = _env("ORG_NAME", "Chain Industria")

    @property
    def llm_enabled(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def search_enabled(self) -> bool:
        if self.search_provider == "mock":
            return False
        if self.search_provider == "tavily":
            return bool(self.tavily_api_key)
        return bool(self.tavily_api_key)

    @property
    def notion_enabled(self) -> bool:
        return bool(self.notion_api_key)

    @property
    def github_enabled(self) -> bool:
        return bool(self.github_token)

    def integration_status(self) -> dict:
        return {
            "org_name": self.org_name,
            "env_file": str(self.env_path),
            "env_exists": self.env_path.exists(),
            "integrations": {
                "llm_anthropic": {
                    "enabled": self.llm_enabled,
                    "model": self.anthropic_model,
                },
                "search_tavily": {
                    "enabled": self.search_enabled,
                    "provider": self.search_provider,
                },
                "memory_local": {
                    "enabled": True,
                    "index": str(self.memory_index_path),
                },
                "agentmemory_remote": {
                    "enabled": bool(self.agentmemory_url),
                    "url": self.agentmemory_url or None,
                },
                "notion": {
                    "enabled": self.notion_enabled,
                    "database_id": self.notion_database_id or None,
                    "parent_page_id": self.notion_parent_page_id or None,
                },
                "github": {
                    "enabled": self.github_enabled,
                    "repo": self.github_repo,
                    "token_prefix": (self.github_token[:10] + "...") if self.github_token else None,
                },
            },
        }


def reload_settings() -> Settings:
    global settings
    _load_env()
    settings = Settings()
    return settings


settings = Settings()
