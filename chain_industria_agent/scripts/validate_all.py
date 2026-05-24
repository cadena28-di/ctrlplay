#!/usr/bin/env python3
"""Valida .env e integraciones sin mostrar secretos."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

import requests

from src.config import settings


def _mask(value: str) -> str:
    if not value:
        return "(vacío)"
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def check_github() -> dict:
    out = {"token_set": bool(settings.github_token), "repo": settings.github_repo}
    if not settings.github_token:
        out["error"] = "GITHUB_TOKEN vacío"
        return out

    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    user = requests.get(f"{settings.github_api_url}/user", headers=headers, timeout=15)
    out["user_status"] = user.status_code
    if user.ok:
        out["login"] = user.json().get("login")

    repo = requests.get(
        f"{settings.github_api_url}/repos/{settings.github_repo}",
        headers=headers,
        timeout=15,
    )
    out["repo_status"] = repo.status_code
    if repo.ok:
        data = repo.json()
        out["repo_name"] = data.get("full_name")
        out["private"] = data.get("private")
    else:
        out["repo_error"] = repo.json().get("message", repo.text[:120])

        # Buscar repos accesibles con nombre similar
        if user.ok:
            login = user.json().get("login", "")
            repos = requests.get(
                f"{settings.github_api_url}/user/repos",
                headers=headers,
                params={"per_page": 30, "sort": "updated"},
                timeout=15,
            )
            if repos.ok:
                names = [r.get("full_name") for r in repos.json()]
                out["accessible_repos"] = names[:15]
                matches = [
                    n for n in names
                    if n and "agente" in n.lower()
                ]
                if matches:
                    out["suggested_repos"] = matches

    return out


def main() -> int:
    print("=== Validación Chain Industria Agent ===\n")
    print(f".env existe: {(ROOT / '.env').exists()}")
    print(f"GITHUB_TOKEN: {_mask(settings.github_token)}")
    print(f"GITHUB_REPO: {settings.github_repo or '(vacío)'}\n")

    status = settings.integration_status()
    print("Integraciones:")
    print(json.dumps(status["integrations"], indent=2, ensure_ascii=False))

    print("\n--- GitHub ---")
    gh = check_github()
    print(json.dumps(gh, indent=2, ensure_ascii=False))

    ok = gh.get("repo_status") == 200
    print("\n" + ("✅ GitHub OK" if ok else "❌ GitHub requiere corrección"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
