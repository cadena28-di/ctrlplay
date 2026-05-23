# Chain Industria — Agente de IA con Memoria Persistente

Documento de referencia del proyecto. Sincronizado con AgentMemory (memorias `mem_mphhlflu`, `mem_mphhw4qu`).

---

## Objetivo

Desarrollar un **sistema de IA agéntica** para Chain Industria con:

- Automatizaciones
- Autoaprendizaje
- **Memoria compartida** entre herramientas (Cursor, Claude Code, AgentMemory, agentes Python)

---

## Stack técnico

| Componente | Detalle |
|------------|---------|
| SO | WSL2 — Ubuntu (usuario `chainindustria`) |
| Runtime | Node.js v24.15.0 vía NVM (`/home/chainindustria/.nvm`) |
| Memoria persistente | AgentMemory (`@agentmemory/mcp`) |
| Proceso | PM2 — servicio `agentmemory` |
| IDE principal | Cursor — MCP vía `wsl.exe` |
| Segundo agente | Claude Code (CLI en WSL) |
| Agentes locales | Python — `/home/chainindustria/agents` |

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     Windows (host)                          │
│  ┌──────────────┐         wsl.exe          ┌─────────────┐ │
│  │    Cursor    │ ─────── MCP ────────────►│  WSL2 Ubuntu │ │
│  │  (agente 1)  │                          │              │ │
│  └──────────────┘                          │  AgentMemory │ │
│  ┌──────────────┐                          │  :3111 /mcp  │ │
│  │ Claude Code  │ ──── memoria compartida ►│  :3113 viewer│ │
│  │  (agente 2)  │                          │              │ │
│  └──────────────┘                          │  PM2         │ │
│                                             │  agentmemory │ │
│                                             └──────┬───────┘ │
└────────────────────────────────────────────────────┼─────────┘
                                                     │
                     ┌───────────────────────────────┼───────────────┐
                     │  /home/chainindustria/agents  │               │
                     │  ┌─────────────┐  ┌──────────┴──┐  ┌────────┐ │
                     │  │ Coordinator │──│ Researcher  │  │Creative│ │
                     │  └──────┬──────┘  └─────────────┘  └────────┘ │
                     │         │         MemoryAgent (Python, local)  │
                     │         └────────► notes / summaries           │
                     └────────────────────────────────────────────────┘
```

---

## Rutas importantes

| Ruta | Uso |
|------|-----|
| `/home/chainindustria/agents` | Proyecto multi-agente Python |
| `/home/chainindustria/agents/docs` | Documentación (este archivo) |
| `/home/chainindustria/agents/main.py` | Coordinador multi-agente |
| `/home/chainindustria/.agentmemory` | Datos y estado de AgentMemory |
| `/home/chainindustria/scripts/start-agentmemory.sh` | Script PM2 |
| `/home/chainindustria/scripts/agentmemory-up.sh` | Arranque completo + health |
| `C:\Users\USUARIO\.cursor\mcp.json` | MCP de Cursor (Windows) |

---

## AgentMemory (PM2)

**Estado esperado:**

```bash
pm2 status   # agentmemory → online
```

| Puerto | Servicio |
|--------|----------|
| 3111 | MCP + health (`/health`, `/mcp`) |
| 3113 | Viewer web |

**Comandos útiles:**

```bash
# Arranque completo (IP MCP + PM2 + health)
~/scripts/agentmemory-up.sh

# Solo PM2
pm2 restart agentmemory
pm2 logs agentmemory

# Health (reemplaza IP con la de WSL)
curl http://$(hostname -I | awk '{print $1}'):3111/health
```

---

## Cursor MCP (Windows)

Archivo: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "wsl.exe",
      "args": [
        "bash", "-lc",
        "export NVM_DIR=/home/chainindustria/.nvm; source /home/chainindustria/.nvm/nvm.sh; /home/chainindustria/.nvm/versions/node/v24.15.0/bin/npx -y @agentmemory/mcp"
      ]
    }
  }
}
```

**Herramientas MCP disponibles:**

| Herramienta | Uso |
|-------------|-----|
| `memory_save` | Guardar decisión, patrón o arquitectura |
| `memory_recall` | Recuperar memorias por consulta |
| `memory_smart_search` | Búsqueda híbrida semántica + keywords |
| `memory_lesson_save` | Lecciones aprendidas |
| `memory_reflect` | Reflexión sobre sesiones |
| `memory_consolidate` | Consolidar memorias |
| `memory_sessions` | Historial de sesiones |
| `memory_diagnose` | Diagnóstico del motor |

**Allowlist recomendada** (`~/.cursor/permissions.json`):

```json
{
  "mcpAllowlist": ["agentmemory:*"]
}
```

---

## Agentes Python (proyecto local)

Estructura en `/home/chainindustria/agents`:

```
agents/
├── main.py              # CoordinatorAgent
├── coordinator/
├── researcher/          # agent_researcher.py
├── creative/            # agent_creative.py
├── memory/              # agent_memory.py, notes/, summaries/
├── src/
│   ├── agent/
│   ├── automations/
│   ├── integrations/
│   └── utils/
├── scripts/
├── tests/
└── docs/
    └── chain_industria_agent.md   # ← este archivo
```

**Flujo actual** (`main.py`):

1. Researcher investiga (ej. "Chain Industria Bucaramanga Google Maps")
2. Creative genera ideas (ej. "estrategias de crecimiento industrial")
3. MemoryAgent guarda resultados en notas locales
4. Coordinador reporta fin del ciclo

> El `MemoryAgent` Python es **local** (archivos en `memory/notes`). La memoria **persistente compartida** entre Cursor y Claude Code es **AgentMemory** (Node/PM2/MCP).

---

## Memorias en AgentMemory

| ID | Contenido |
|----|-----------|
| `mem_mphhlflu_c3d0dbf9bdb1` | Stack: WSL2, AgentMemory+PM2, Cursor MCP |
| `mem_mphhw4qu_7621e25c14a0` | Objetivo: IA agéntica, autoaprendizaje, memoria compartida |

**Consultar desde Cursor:**

```
Usa agentmemory memory_recall con query "Chain Industria"
```

---

## Fases del proyecto

| Fase | Estado | Documento |
|------|--------|-----------|
| **Fase 1** | Completada | Este archivo — infraestructura, MCP, esqueleto multi-agente |
| **Fase 2** | En curso | [`chain_industria_agent_fase2.md`](./chain_industria_agent_fase2.md) — objetivo, arquitectura, reglas, comandos, roadmap, entregables |

---

## Referencias rápidas

```bash
# Proyecto Python
cd ~/agents && source venv/bin/activate && python main.py

# AgentMemory
~/scripts/agentmemory-up.sh

# PM2
pm2 status && pm2 logs agentmemory --lines 50
```

*Última actualización: 2026-05-22*
