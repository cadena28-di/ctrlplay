"""Modelo de tarea para el agente."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class TaskType(str, Enum):
    RESEARCH = "research"
    CREATIVE = "creative"
    MEMORY_RECALL = "memory_recall"
    SEARCH_INDEX = "search_index"
    NOTION_PAGE = "notion_page"
    NOTION_SEARCH = "notion_search"
    NOTION_TASK = "notion_task"
    GITHUB_ISSUES = "github_issues"
    GITHUB_ISSUE_CREATE = "github_issue_create"
    GITHUB_REPO = "github_repo"
    STATUS = "status"
    CONFIGURE = "configure"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Unidad de trabajo del coordinador."""

    task_type: TaskType
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "payload": self.payload,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
        }
