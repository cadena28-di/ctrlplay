"""
Chain Industria Agent — punto de entrada principal.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import reload_settings

reload_settings()

from coordinator.coordinator import Coordinator
from creative.creative import Creative
from researcher.researcher import Researcher


def _print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def _coordinator() -> Coordinator:
    return Coordinator(researcher=Researcher(), creative=Creative())


def run_demo() -> None:
    _print_header("INICIANDO CHAIN INDUSTRIA AGENT")
    coordinator = _coordinator()

    status = coordinator.run()
    print("\n📋 Estado de integraciones:")
    print(json.dumps(status, indent=2, ensure_ascii=False, default=str))

    print("\n" + "-" * 70)
    print("INVESTIGACIÓN")
    print("-" * 70)
    research_task = coordinator.research("Chain Industria", ["web", "api"])
    if research_task.result:
        web = next(
            (r for r in research_task.result.get("results", []) if r.get("source") == "web"),
            {},
        )
        print(f"🔍 Web ({web.get('provider', '?')}): {web.get('results_found', 0)} resultados")

    print("\n" + "-" * 70)
    print("CREATIVIDAD")
    print("-" * 70)
    ideas_task = coordinator.creative_ideas("automatización industrial", 2)
    for idea in (ideas_task.result or {}).get("ideas", [])[:2]:
        print(f"  💡 {str(idea.get('idea', ''))[:120]}")

    print("\n" + "-" * 70)
    print("FASE 2 — NOTION / GITHUB")
    print("-" * 70)
    repo_task = coordinator.github_repo()
    if repo_task.result and repo_task.result.get("name"):
        print(f"  🐙 Repo: {repo_task.result.get('name')} — {repo_task.result.get('url')}")
    elif repo_task.result:
        print(f"  🐙 GitHub: {repo_task.result.get('error', 'no configurado')}")

    issues_task = coordinator.github_issues(limit=3)
    issues = (issues_task.result or {}).get("issues", [])
    print(f"  📌 Issues abiertos (muestra): {len(issues)}")

    print("\n" + "-" * 70)
    print("ÍNDICE DE BÚSQUEDAS")
    print("-" * 70)
    index_task = coordinator.search_index(limit=10)
    searches = (index_task.result or {}).get("searches", [])
    print(f"📚 Entradas: {len(searches)}")

    _print_header("✅ AGENTE LISTO")


def run_cli(args: argparse.Namespace) -> None:
    from src.agent.task import TaskType

    coordinator = _coordinator()

    if args.command == "configure":
        task = coordinator.configure()
        print(json.dumps(task.result, indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "status":
        task = coordinator.planner.plan(TaskType.STATUS, {})
        result = coordinator.execute(task)
        print(json.dumps(result.result, indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "research":
        task = coordinator.research(args.query, args.sources.split(",") if args.sources else None)
        print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "ideas":
        task = coordinator.creative_ideas(args.topic, args.quantity)
        print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "recall":
        task = coordinator.recall_memory(args.query, args.limit)
        print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "search-index":
        task = coordinator.search_index(args.limit)
        print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "notion-page":
        task = coordinator.notion_page(args.title, args.content or "")
        print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "notion-search":
        task = coordinator.notion_search(args.query, args.limit)
        print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "notion-task":
        task = coordinator.notion_task(args.title, args.notes or "", args.status)
        print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "github-issues":
        task = coordinator.github_issues(args.state, args.limit)
        print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "github-issue":
        labels = args.labels.split(",") if args.labels else None
        task = coordinator.github_create_issue(args.title, args.body or "", labels)
        print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "github-repo":
        task = coordinator.github_repo()
        print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False, default=str))
        return

    if args.command == "repair":
        import subprocess

        subprocess.run([sys.executable, str(ROOT / "scripts" / "repair_env.py")], check=False)
        reload_settings()
        return

    if args.command == "validate":
        import subprocess

        subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_all.py")], check=False)
        return

    if args.command == "doctor":
        import subprocess

        subprocess.run([sys.executable, str(ROOT / "scripts" / "repair_env.py")], check=False)
        reload_settings()
        subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_all.py")], check=False)
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chain Industria Agent")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("demo", help="Demostración completa")
    sub.add_parser("status", help="Estado de integraciones")
    sub.add_parser("configure", help="Crear/actualizar .env desde plantilla")

    p_research = sub.add_parser("research", help="Investigar un tema")
    p_research.add_argument("query")
    p_research.add_argument("--sources", default="web,api")

    p_ideas = sub.add_parser("ideas", help="Generar ideas")
    p_ideas.add_argument("topic")
    p_ideas.add_argument("-n", "--quantity", type=int, default=3)

    p_recall = sub.add_parser("recall", help="Recuperar memoria")
    p_recall.add_argument("query")
    p_recall.add_argument("-l", "--limit", type=int, default=10)

    p_index = sub.add_parser("search-index", help="Índice de búsquedas")
    p_index.add_argument("-l", "--limit", type=int, default=50)

    p_np = sub.add_parser("notion-page", help="Crear página en Notion")
    p_np.add_argument("title")
    p_np.add_argument("--content", default="")

    p_ns = sub.add_parser("notion-search", help="Buscar en Notion")
    p_ns.add_argument("query")
    p_ns.add_argument("-l", "--limit", type=int, default=10)

    p_nt = sub.add_parser("notion-task", help="Crear tarea en Notion")
    p_nt.add_argument("title")
    p_nt.add_argument("--notes", default="")
    p_nt.add_argument("--status", default="Not started")

    p_gi = sub.add_parser("github-issues", help="Listar issues")
    p_gi.add_argument("--state", default="open")
    p_gi.add_argument("-l", "--limit", type=int, default=10)

    p_gic = sub.add_parser("github-issue", help="Crear issue")
    p_gic.add_argument("title")
    p_gic.add_argument("--body", default="")
    p_gic.add_argument("--labels", default="")

    sub.add_parser("github-repo", help="Info del repositorio")

    sub.add_parser("repair", help="Reparar archivo .env")
    sub.add_parser("validate", help="Validar integraciones y GitHub")
    sub.add_parser("doctor", help="Reparar .env + validar todo")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command or args.command == "demo":
        run_demo()
        return

    run_cli(args)


if __name__ == "__main__":
    main()
