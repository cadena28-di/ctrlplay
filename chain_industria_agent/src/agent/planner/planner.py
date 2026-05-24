"""Planificador: convierte intención en pasos ejecutables."""

from src.agent.task import Task, TaskType


class Planner:
    """Plan simple por tipo de tarea."""

    def plan(self, task_type: TaskType, payload: dict) -> Task:
        return Task(task_type=task_type, payload=payload)

    def plan_research(self, query: str, sources: list[str] | None = None) -> Task:
        return self.plan(
            TaskType.RESEARCH,
            {"query": query, "sources": sources or ["web"]},
        )

    def plan_creative_ideas(self, topic: str, quantity: int = 3) -> Task:
        return self.plan(
            TaskType.CREATIVE,
            {"mode": "ideas", "topic": topic, "quantity": quantity},
        )

    def plan_memory_recall(self, query: str, limit: int = 10) -> Task:
        return self.plan(
            TaskType.MEMORY_RECALL,
            {"query": query, "limit": limit},
        )

    def plan_notion_page(self, title: str, content: str = "") -> Task:
        return self.plan(TaskType.NOTION_PAGE, {"title": title, "content": content})

    def plan_notion_search(self, query: str, limit: int = 10) -> Task:
        return self.plan(TaskType.NOTION_SEARCH, {"query": query, "limit": limit})

    def plan_notion_task(self, title: str, notes: str = "", status: str = "Not started") -> Task:
        return self.plan(
            TaskType.NOTION_TASK,
            {"title": title, "notes": notes, "status": status},
        )

    def plan_github_issues(self, state: str = "open", limit: int = 10) -> Task:
        return self.plan(TaskType.GITHUB_ISSUES, {"state": state, "limit": limit})

    def plan_github_issue_create(self, title: str, body: str = "", labels: list[str] | None = None) -> Task:
        return self.plan(
            TaskType.GITHUB_ISSUE_CREATE,
            {"title": title, "body": body, "labels": labels or []},
        )

    def plan_github_repo(self) -> Task:
        return self.plan(TaskType.GITHUB_REPO, {})
