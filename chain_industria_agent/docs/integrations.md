# Integraciones — Chain Industria Agent

## Configurar APIs

```bash
cp .env.example .env
# Edita .env con tus claves, o exporta variables y ejecuta:
python main.py configure
python scripts/check_config.py
python main.py status
```

### Dónde obtener cada clave

| Variable | Enlace |
|----------|--------|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/keys |
| `TAVILY_API_KEY` | https://app.tavily.com/ |
| `NOTION_API_KEY` | https://www.notion.so/my-integrations |
| `GITHUB_TOKEN` | https://github.com/settings/tokens (scope `repo`) |

### Notion

- Comparte la base de datos o página con la integración.
- `NOTION_DATABASE_ID` — ID de la base de tareas (opcional).
- `NOTION_PARENT_PAGE_ID` — ID de página padre si no usas base de datos.

## Fase 1 (implementada)

| Integración | Módulo |
|-------------|--------|
| Memoria local | `src/integrations/memory/` |
| Tavily / mock | `src/integrations/search/` |
| Anthropic / fallback | `src/integrations/llm/` |

## Fase 2 (implementada)

| Integración | Módulo | CLI |
|-------------|--------|-----|
| Notion | `src/integrations/notion/` | `notion-page`, `notion-search`, `notion-task` |
| GitHub | `src/integrations/github/` | `github-repo`, `github-issues`, `github-issue` |

## Comandos

```bash
python main.py configure
python main.py status
python main.py notion-search "Chain Industria"
python main.py notion-task "Revisar integraciones" --notes "Fase 2"
python main.py github-repo
python main.py github-issues --state open
python main.py github-issue "Nueva feature" --body "Descripción"
```

## Próxima fase

- Scraper (`scraper/`)
- API REST (FastAPI)
- Sincronización bidireccional Notion ↔ memoria local
