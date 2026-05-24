#!/usr/bin/env python3
"""
Crea o actualiza .env desde .env.example y variables del sistema.
No imprime valores de claves secretas.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_KEYS = [
    "ORG_NAME",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_MODEL",
    "TAVILY_API_KEY",
    "SEARCH_PROVIDER",
    "NOTION_API_KEY",
    "NOTION_VERSION",
    "NOTION_DATABASE_ID",
    "NOTION_PARENT_PAGE_ID",
    "GITHUB_TOKEN",
    "GITHUB_REPO",
    "GITHUB_API_URL",
    "AGENTMEMORY_URL",
    "AGENTMEMORY_API_KEY",
]


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip()
    return values


def _write_env(path: Path, values: dict[str, str], template_lines: list[str]) -> None:
    out: list[str] = []
    written: set[str] = set()
    for line in template_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in values:
                out.append(f"{key}={values[key]}")
                written.add(key)
                continue
        out.append(line.rstrip("\n"))
    for key in ENV_KEYS:
        if key not in written and key in values and values[key]:
            out.append(f"{key}={values[key]}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    example = ROOT / ".env.example"
    env_path = ROOT / ".env"
    if not example.exists():
        print("❌ Falta .env.example")
        return 1

    template_lines = example.read_text(encoding="utf-8").splitlines()
    current = _parse_env_file(env_path) if env_path.exists() else {}
    merged = {**_parse_env_file(example), **current}

    imported = 0
    for key in ENV_KEYS:
        if os.getenv(key) and not merged.get(key):
            merged[key] = os.getenv(key, "").strip()
            imported += 1

    _write_env(env_path, merged, template_lines)

    configured = [k for k in ENV_KEYS if merged.get(k)]
    secret_keys = {
        "ANTHROPIC_API_KEY",
        "TAVILY_API_KEY",
        "NOTION_API_KEY",
        "GITHUB_TOKEN",
        "AGENTMEMORY_API_KEY",
    }
    ready = [k for k in secret_keys if merged.get(k)]

    print(f"✅ Archivo: {env_path}")
    print(f"   Variables con valor: {len(configured)}")
    print(f"   API keys configuradas: {len(ready)} → {', '.join(ready) or '(ninguna)'}")
    if imported:
        print(f"   Importadas del entorno: {imported}")
    if not ready:
        print("\n⚠️  Edita .env y añade tus API keys. Luego: python main.py configure")
    return 0


if __name__ == "__main__":
    sys.exit(main())
