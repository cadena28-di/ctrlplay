"""
Coordinator - Orquestador principal del agente Chain Industria.
"""

from src.agent.executor.executor import Executor
from src.agent.planner.planner import Planner
from src.agent.task import Task, TaskType
from src.integrations import GitHubClient, MemoryClient, NotionClient


class Coordinator:
    def __init__(self, researcher=None, creative=None):
        self.name = "Chain Industria Agent"
        self.status = "initialized"
        self.planner = Planner()
        self.memory = MemoryClient()
        self.notion = NotionClient()
        self.github = GitHubClient()
        self.executor = Executor(
            researcher=researcher,
            creative=creative,
            memory=self.memory,
            notion=self.notion,
            github=self.github,
        )
        self._history: list[Task] = []

    def run(self) -> dict:
        """Arranque y comprobación de integraciones."""
        task = self.planner.plan(TaskType.STATUS, {})
        completed = self.execute(task)
        self.status = "ready"
        return completed.result or {}

    def execute(self, task: Task) -> Task:
        completed = self.executor.run(task)
        self._history.append(completed)
        return completed

    def configure(self) -> Task:
        task = self.planner.plan(TaskType.CONFIGURE, {})
        return self.execute(task)

    def research(self, query: str, sources: list[str] | None = None) -> Task:
        task = self.planner.plan_research(query, sources)
        return self.execute(task)

    def creative_ideas(self, topic: str, quantity: int = 3) -> Task:
        task = self.planner.plan_creative_ideas(topic, quantity)
        return self.execute(task)

    def recall_memory(self, query: str, limit: int = 10) -> Task:
        task = self.planner.plan_memory_recall(query, limit)
        return self.execute(task)

    def search_index(self, limit: int = 50) -> Task:
        task = self.planner.plan(TaskType.SEARCH_INDEX, {"limit": limit})
        return self.execute(task)

    def notion_page(self, title: str, content: str = "") -> Task:
        return self.execute(self.planner.plan_notion_page(title, content))

    def notion_search(self, query: str, limit: int = 10) -> Task:
        return self.execute(self.planner.plan_notion_search(query, limit))

    def notion_task(self, title: str, notes: str = "", status: str = "Not started") -> Task:
        return self.execute(self.planner.plan_notion_task(title, notes, status))

    def github_issues(self, state: str = "open", limit: int = 10) -> Task:
        return self.execute(self.planner.plan_github_issues(state, limit))

    def github_create_issue(self, title: str, body: str = "", labels: list[str] | None = None) -> Task:
        return self.execute(self.planner.plan_github_issue_create(title, body, labels))

    def github_repo(self) -> Task:
        return self.execute(self.planner.plan_github_repo())

    def get_history(self) -> list[dict]:
        return [t.to_dict() for t in self._history]
