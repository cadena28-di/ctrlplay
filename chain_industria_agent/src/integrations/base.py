"""Tipos base para integraciones externas."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntegrationResult:
    """Resultado estándar de una integración."""

    success: bool
    data: Any = None
    error: str | None = None
    provider: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)
