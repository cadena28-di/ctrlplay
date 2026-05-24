"""Ejecutor: corre tareas contra módulos e integraciones."""

import subprocess
import sys
from pathlib import Path

from src.agent.task import Task, TaskStatus, TaskType
from src.config import settings
from src.integrations import (
    GitHubClient,
    LLMClient,
    MemoryClient,
    NotionClient,
    SearchClient,
)


class Executor:
    """Ejecuta tareas delegando a Researcher, Creative y memoria."""

    def __init__(
        self,
        researcher=None,
        creative=None,
        memory: MemoryClient | None = None,
        search: SearchClient | None = None,
        llm: LLMClient | None = None,
        notion: NotionClient | None = None,
        github: GitHubClient | None = None,
    ):
        self._researcher = researcher
        self._creative = creative
        self._memory = memory or MemoryClient()
        self._search = search or SearchClient()
        self._llm = llm or LLMClient()
        self._notion = notion or NotionClient()
        self._github = github or GitHubClient()

    def run(self, task: Task) -> Task:
        task.status = TaskStatus.RUNNING
        handlers = {
            TaskType.RESEARCH: self._run_research,
            TaskType.CREATIVE: self._run_creative,
            TaskType.MEMORY_RECALL: self._run_memory_recall,
            TaskType.SEARCH_INDEX: self._run_search_index,
            TaskType.NOTION_PAGE: self._run_notion_page,
            TaskType.NOTION_SEARCH: self._run_notion_search,
            TaskType.NOTION_TASK: self._run_notion_task,
            TaskType.GITHUB_ISSUES: self._run_github_issues,
            TaskType.GITHUB_ISSUE_CREATE: self._run_github_issue_create,
            TaskType.GITHUB_REPO: self._run_github_repo,
            TaskType.STATUS: self._run_status,
            TaskType.CONFIGURE: self._run_configure,
        }
        handler = handlers.get(task.task_type)
        if not handler:
            task.status = TaskStatus.FAILED
            task.error = f"Tipo de tarea no soportado: {task.task_type}"
            return task

        try:
            task.result = handler(task)
            task.status = TaskStatus.COMPLETED
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error = str(exc)
        return task

    def _run_research(self, task: Task) -> dict:
        query = task.payload.get("query", "")
        sources = task.payload.get("sources", ["web"])

        if self._researcher:
            return self._researcher.search(query, sources)

        web_result = None
        if "web" in sources:
            web_result = self._search.search(query)
        return {
            "query": query,
            "sources": sources,
            "web": web_result.data if web_result and web_result.success else None,
        }

    def _run_creative(self, task: Task) -> dict:
        mode = task.payload.get("mode", "ideas")
        topic = task.payload.get("topic", "")
        quantity = int(task.payload.get("quantity", 3))

        if self._creative and mode == "ideas":
            return {"ideas": self._creative.generate_ideas(topic, quantity)}

        if mode == "ideas":
            return {"ideas": self._generate_ideas_llm(topic, quantity)}
        return {
            "content": self._generate_content_llm(
                topic, task.payload.get("content_type", "article")
            )
        }

    def _generate_ideas_llm(self, topic: str, quantity: int) -> list[dict]:
        prompt = (
            f"Genera exactamente {quantity} ideas creativas y accionables sobre: {topic}. "
            f"Organización: Chain Industria. "
            "Responde en español, una idea por línea numerada (1. 2. 3.)."
        )
        result = self._llm.complete(
            prompt, system="Eres un consultor estratégico de Chain Industria."
        )
        lines = []
        if result.success and result.data:
            text = result.data.get("text", "")
            lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

        ideas = []
        for i in range(quantity):
            text = lines[i] if i < len(lines) else f"Idea #{i + 1} sobre {topic}"
            ideas.append(
                {"id": i + 1, "topic": topic, "idea": text, "provider": result.provider}
            )
        return ideas

    def _generate_content_llm(self, topic: str, content_type: str) -> dict:
        prompt = (
            f"Redacta un borrador tipo '{content_type}' sobre: {topic}. "
            "Español, tono profesional Chain Industria."
        )
        result = self._llm.complete(prompt)
        return {
            "type": content_type,
            "topic": topic,
            "body": result.data.get("text", "") if result.success else "",
            "provider": result.provider,
        }

    def _run_memory_recall(self, task: Task) -> dict:
        query = task.payload.get("query", "")
        limit = int(task.payload.get("limit", 10))
        recalled = self._memory.recall(query, limit=limit)
        return {"entries": recalled.data, "count": recalled.metadata.get("count", 0)}

    def _run_search_index(self, task: Task) -> dict:
        limit = int(task.payload.get("limit", 50))
        index = self._memory.get_search_index(limit=limit)
        return {"searches": index.data, "count": index.metadata.get("count", 0)}

    def _run_notion_page(self, task: Task) -> dict:
        result = self._notion.create_page(
            task.payload.get("title", "Sin título"),
            content=task.payload.get("content", ""),
        )
        return _integration_response(result)

    def _run_notion_search(self, task: Task) -> dict:
        result = self._notion.search(
            task.payload.get("query", ""),
            page_size=int(task.payload.get("limit", 10)),
        )
        return _integration_response(result)

    def _run_notion_task(self, task: Task) -> dict:
        result = self._notion.create_task(
            task.payload.get("title", "Tarea"),
            status=task.payload.get("status", "Not started"),
            notes=task.payload.get("notes", ""),
        )
        return _integration_response(result)

    def _run_github_issues(self, task: Task) -> dict:
        result = self._github.list_issues(
            state=task.payload.get("state", "open"),
            per_page=int(task.payload.get("limit", 10)),
        )
        if result.success and isinstance(result.data, list):
            slim = [
                {
                    "number": i.get("number"),
                    "title": i.get("title"),
                    "state": i.get("state"),
                    "url": i.get("html_url"),
                }
                for i in result.data
            ]
            return {"issues": slim, "count": len(slim), "provider": result.provider}
        return _integration_response(result)

    def _run_github_issue_create(self, task: Task) -> dict:
        result = self._github.create_issue(
            task.payload.get("title", ""),
            body=task.payload.get("body", ""),
            labels=task.payload.get("labels"),
        )
        return _integration_response(result)

    def _run_github_repo(self, task: Task) -> dict:
        result = self._github.get_repo()
        if result.success and result.data:
            data = result.data
            return {
                "name": data.get("full_name"),
                "description": data.get("description"),
                "url": data.get("html_url"),
                "stars": data.get("stargazers_count"),
                "open_issues": data.get("open_issues_count"),
                "provider": result.provider,
            }
        return _integration_response(result)

    def _run_status(self, task: Task) -> dict:
        status = settings.integration_status()
        status["researcher"] = self._researcher.get_status() if self._researcher else None
        status["creative"] = self._creative.get_status() if self._creative else None
        return status

    def _run_configure(self, task: Task) -> dict:
        root = settings.project_root
        setup = root / "scripts" / "setup_env.py"
        subprocess.run([sys.executable, str(setup)], check=False, cwd=str(root))
        return settings.integration_status()


def _integration_response(result) -> dict:
    if result.success:
        return {"ok": True, "data": result.data, "provider": result.provider}
    return {"ok": False, "error": result.error, "provider": result.provider}
