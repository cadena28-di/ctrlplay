# Chain Industria Agent

`chain_industria_agent` es el agente principal del proyecto Chain Industria.

## Objetivo

Chain Industria pretende construir un agente de IA que sea el apoyo más fiable para la organización.

El agente debe tener la capacidad de:

- Crear soluciones.
- Analizar información.
- Implementar procesos.
- Automatizar tareas.
- Recordar decisiones importantes.
- Adaptarse y diversificarse en diferentes entornos.
- Apoyar la evolución continua de Chain Industria.

## Estado actual

- WSL2 Ubuntu como entorno principal.
- Cursor conectado mediante MCP.
- Claude Code como agente complementario.
- AgentMemory ejecutándose con PM2.
- GitHub como repositorio central.
- Arquitectura modular inicial.

## Capacidades iniciales

- Memoria persistente.
- Organización del proyecto.
- Documentación técnica.
- Automatizaciones base.
- Módulos iniciales para coordinación, investigación, scraping y creatividad.
- Preparación para flujos agenticos.

## Estructura inicial

```
.
├── chain_industria_agent.md
├── AGENTS.md
├── README.md
├── requirements.txt
├── main.py
├── docs/
├── scripts/
├── src/
├── memory/
├── tests/
├── coordinator/
├── researcher/
├── scraper/
└── creative/
```

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py configure     # Crea/actualiza .env
# Edita .env con tus API keys (ver docs/integrations.md)
```

## Ejecución

```bash
python main.py configure     # Sincroniza .env
python main.py status        # Estado de integraciones
python main.py demo

# Fase 1
python main.py research "Chain Industria"
python main.py ideas "automatización" -n 3
python main.py recall "Chain"
python main.py search-index

# Fase 2 — Notion
python main.py notion-search "proyecto"
python main.py notion-page "Informe" --content "Resumen..."
python main.py notion-task "Implementar API" --notes "Fase 2"

# Fase 2 — GitHub
python main.py github-repo
python main.py github-issues
python main.py github-issue "Título" --body "Descripción"
```

## Integraciones

| Fase | Servicios |
|------|-----------|
| 1 | Memoria local, Tavily, Anthropic |
| 2 | Notion, GitHub |

Ver `docs/integrations.md` para claves y configuración.

## Tests

```bash
pytest tests/ -q
```

## Licencia

Copyright © Chain Industria. Todos los derechos reservados.