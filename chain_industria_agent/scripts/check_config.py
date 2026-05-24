#!/usr/bin/env python3
"""Verifica integraciones configuradas (sin mostrar secretos)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import settings  # noqa: E402


def main() -> int:
    print(json.dumps(settings.integration_status(), indent=2, ensure_ascii=False))
    integrations = settings.integration_status()["integrations"]
    enabled = sum(1 for v in integrations.values() if v.get("enabled"))
    print(f"\n✅ Integraciones activas: {enabled}/{len(integrations)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
