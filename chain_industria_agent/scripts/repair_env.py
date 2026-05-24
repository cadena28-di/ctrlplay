#!/usr/bin/env python3
"""Repara .env: elimina líneas inválidas y normaliza formato."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
EXAMPLE_PATH = ROOT / ".env.example"

VALID_KEYS = {
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
}

TOKEN_PATTERNS = [
    re.compile(r"^(github_pat_|ghp_)[A-Za-z0-9_]+$"),
]


def _extract_tokens(lines: list[str]) -> list[str]:
    found = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" in s:
            _, val = s.split("=", 1)
            val = val.strip().strip('"').strip("'")
            if val and any(p.match(val) for p in TOKEN_PATTERNS):
                found.append(val)
        elif any(p.match(s) for p in TOKEN_PATTERNS):
            found.append(s)
    return found


def repair() -> None:
    raw_lines = ENV_PATH.read_text(encoding="utf-8").splitlines() if ENV_PATH.exists() else []
    tokens = _extract_tokens(raw_lines)

    parsed: dict[str, str] = {}
    for line in raw_lines:
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        key, _, val = s.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key in VALID_KEYS and val:
            parsed[key] = val

    if "GITHUB_TOKEN" not in parsed and tokens:
        parsed["GITHUB_TOKEN"] = tokens[-1]

    template = EXAMPLE_PATH.read_text(encoding="utf-8") if EXAMPLE_PATH.exists() else ""
    defaults = {}
    for line in template.splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            defaults[k.strip()] = v.strip()

    merged = {**defaults, **parsed}
    if merged.get("GITHUB_REPO", "").startswith("GITHUB_REPO="):
        merged["GITHUB_REPO"] = "chaiindustriaceoempresa-gif/agente_industrial_cadena"

    out_lines = [
        "# Chain Industria Agent — reparado automáticamente",
        "# No subas este archivo a GitHub",
        "",
    ]
    order = [
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
    for key in order:
        out_lines.append(f"{key}={merged.get(key, '')}")
    out_lines.append("")

    ENV_PATH.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"✅ .env reparado en {ENV_PATH}")
    print(f"   GITHUB_TOKEN: {'configurado' if merged.get('GITHUB_TOKEN') else 'VACÍO'}")
    print(f"   GITHUB_REPO: {merged.get('GITHUB_REPO', '')}")


if __name__ == "__main__":
    repair()
