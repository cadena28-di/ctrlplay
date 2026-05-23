# Chain Industria — Fase 2: Integración, Automatización y Autoaprendizaje

> **Fase 1 (completada):** Infraestructura operativa — WSL2, AgentMemory (PM2), Cursor MCP, esqueleto multi-agente Python, memorias persistentes.
>
> **Fase 2 (actual):** Unificar memoria, implementar el núcleo agéntico (`planner → executor → memory`), automatizaciones e integraciones reales.

Documento padre: [`chain_industria_agent.md`](./chain_industria_agent.md)

---

## 1. Objetivo

Construir el **núcleo funcional del sistema agéntico**: que los agentes Python y los agentes de IDE (Cursor, Claude Code) lean y escriban en **un solo store** (AgentMemory), ejecuten tareas planificadas de forma repetible y dejen trazas que alimenten el autoaprendizaje.

### Objetivos específicos

| # | Objetivo | Criterio de éxito |
|---|----------|-------------------|
| O1 | **Memoria unificada** | `MemoryAgent` Python usa API AgentMemory (`:3111`); no duplica datos en `memory/notes` sin sincronizar |
| O2 | **Ciclo agéntico** | `planner → executor → memory` ejecuta al menos 3 tipos de tarea (investigar, generar, guardar) con logs |
| O3 | **Automatizaciones** | ≥2 jobs en `src/automations/` (cron o trigger manual) que invocan el coordinador |
| O4 | **Integraciones** | ≥1 conector en `src/integrations/` (HTTP/API o archivo) documentado y probado |
| O5 | **Autoaprendizaje** | Pipeline que llama `memory_lesson_save` / `memory_reflect` tras cada ciclo exitoso |
| O6 | **Multi-herramienta** | Cursor y Claude Code recuperan el mismo contexto vía AgentMemory sin divergencia |

### Fuera de alcance (Fase 2)

- UI web propia (solo viewer AgentMemory `:3113`)
- Despliegue en cloud / Kubernetes
- Fine-tuning de modelos propios
- Agentes de voz o multimodal

---

## 2. Arquitectura

### 2.1 Vista general Fase 2

```
┌──────────────────────────────────────────────────────────────────┐
│                        CAPA DE HERRAMIENTAS                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │   Cursor    │    │ Claude Code │    │  CLI / scripts      │ │
│  │  MCP tools  │    │  memoria    │    │  agentmemory-up.sh  │ │
│  └──────┬──────┘    └──────┬──────┘    └──────────┬──────────┘ │
└─────────┼──────────────────┼──────────────────────┼────────────┘
          │                  │                      │
          └──────────────────┼──────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│              AGENTMEMORY (PM2) — Store único :3111/:3113        │
│  memory_save │ memory_recall │ memory_smart_search │ reflect    │
└──────────────────────────────┬───────────────────────────────────┘
                               │ HTTP / MCP
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│           NÚCLEO PYTHON — /home/chainindustria/agents           │
│                                                                  │
│  ┌────────────┐    ┌────────────┐    ┌────────────────────┐   │
│  │ Coordinator│───►│   Planner    │───►│     Executor       │   │
│  └────────────┘    └────────────┘    └─────────┬──────────┘   │
│         │                    │                  │               │
│         │           ┌────────┴────────┐         │               │
│         │           ▼                 ▼         ▼               │
│         │    Researcher          Creative    Tools (MCP client) │
│         │           │                 │         │               │
│         └───────────┴─────────────────┴─────────┘               │
│                             │                                    │
│                    ┌────────┴────────┐                           │
│                    │  Memory Bridge  │◄── src/agent/memory/     │
│                    └────────┬────────┘                           │
│                             │                                    │
│  ┌──────────────────────────┴──────────────────────────────┐  │
│  │ src/automations/          src/integrations/               │  │
│  │  - daily_research.py       - agentmemory_client.py        │  │
│  │  - sync_memories.py        - notion / maps / files        │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Componentes nuevos (Fase 2)

| Módulo | Ruta | Responsabilidad |
|--------|------|-----------------|
| **Memory Bridge** | `src/agent/memory/bridge.py` | Cliente HTTP hacia AgentMemory; reemplaza escritura solo-local |
| **Planner** | `src/agent/planner/` | Descompone objetivo en pasos (`TaskPlan`) |
| **Executor** | `src/agent/executor/` | Ejecuta pasos, llama Researcher/Creative/Tools |
| **Tools** | `src/agent/tools/` | Wrappers: MCP, curl, archivos, búsqueda |
| **Automations** | `src/automations/` | Jobs programados o manuales |
| **Integrations** | `src/integrations/` | APIs externas (Maps, Notion, etc.) |
| **Utils** | `src/utils/` | Logging, config, validación |

### 2.3 Flujo de datos

```
Usuario / Automation
       │
       ▼
Coordinator.run(goal)
       │
       ▼
Planner.plan(goal) ──► [step1, step2, step3]
       │
       ▼
Executor.run(steps)
       ├──► Researcher.research(query)
       ├──► Creative.generate(prompt)
       └──► Tools.call(name, args)
       │
       ▼
MemoryBridge.save(content, type, concepts)
       │
       ▼
AgentMemory (:3111) ──► visible en Cursor / Claude Code
       │
       ▼
LearningPipeline.reflect() ──► memory_lesson_save (MCP o API)
```

### 2.4 Contratos de memoria

| Tipo AgentMemory | Cuándo usar | Ejemplo |
|------------------|-------------|---------|
| `architecture` | Decisiones de stack, diseño | "Memory Bridge usa puerto 3111" |
| `workflow` | Procesos repetibles | "Ciclo diario de investigación a las 08:00" |
| `pattern` | Código reutilizable | "Patrón planner→executor" |
| `fact` | Datos de negocio | "Chain Industria — Bucaramanga" |
| `bug` | Errores conocidos | "PM2 cae si systemd compite" |
| `preference` | Preferencias del usuario | "Documentación en español" |

---

## 3. Reglas

### 3.1 Reglas de arquitectura

1. **Un solo store de verdad:** AgentMemory es la fuente canónica; `memory/notes/` solo como caché o borrador, nunca como única copia.
2. **Sin secretos en repo:** API keys en `/home/chainindustria/.agentmemory/.env` o variables de entorno; nunca en `agents/`.
3. **WSL como runtime:** Todo proceso persistente corre en Ubuntu WSL; Cursor solo orquesta vía `wsl.exe`.
4. **PM2 para daemons:** AgentMemory y futuros servicios Node van bajo PM2; Python se invoca por cron o coordinador.
5. **Idempotencia:** Automatizaciones deben poder re-ejecutarse sin duplicar memorias (usar `concepts` + hash de contenido).

### 3.2 Reglas de agentes

1. **Planner no ejecuta:** Solo planifica; el Executor tiene los side-effects.
2. **Executor no planifica:** Recibe pasos; si falla, reporta al Coordinator sin re-planificar en silencio.
3. **Toda salida relevante se persiste:** Investigación, ideas y errores van a AgentMemory con `type` correcto.
4. **Contexto antes de actuar:** Cada ciclo inicia con `memory_recall` / `memory_smart_search` sobre el objetivo.
5. **Lección al cerrar:** Ciclo exitoso → `memory_lesson_save`; ciclo fallido → `memory_save` tipo `bug`.

### 3.3 Reglas de herramientas (Cursor / Claude Code)

1. **Consultar memoria primero** en tareas sobre Chain Industria.
2. **Guardar decisiones** con `memory_save` al cerrar cambios de arquitectura o workflow.
3. **No contradecir memorias** sin actualizar o superseder la entrada anterior.
4. **Documentar en `docs/`** cambios que afecten Fase 2 o posteriores.
5. **Allowlist MCP** recomendado: `agentmemory:*` en `~/.cursor/permissions.json`.

### 3.4 Reglas operativas

1. Tras cambiar IP de WSL → ejecutar `~/scripts/update-cursor-mcp-ip.sh` y reiniciar Cursor.
2. Antes de debug MCP → `curl :3111/health` y `pm2 status`.
3. No correr `systemctl agentmemory` y PM2 a la vez (conflicto de puerto).
4. Commits atómicos por módulo (`planner`, `bridge`, `automations`, etc.).
5. Tests mínimos en `tests/` para Memory Bridge y Planner antes de marcar entregable hecho.

---

## 4. Comandos

### 4.1 Infraestructura (diario)

```bash
# Arranque completo AgentMemory + health + IP MCP
~/scripts/agentmemory-up.sh

# Estado PM2
export NVM_DIR=~/.nvm && source ~/.nvm/nvm.sh && pm2 status

# Logs AgentMemory
pm2 logs agentmemory --lines 100

# Health y MCP
IP=$(hostname -I | awk '{print $1}')
curl -s "http://${IP}:3111/health" | jq .
curl -s "http://${IP}:3111/mcp" -o /dev/null -w "%{http_code}\n"

# Viewer
echo "http://${IP}:3113"
```

### 4.2 Proyecto Python (Fase 2)

```bash
cd ~/agents
source venv/bin/activate

# Ciclo coordinador (Fase 1 — evoluciona en Fase 2)
python main.py

# Cuando existan módulos Fase 2:
python -m src.agent.planner --goal "investigar competencia industrial Bucaramanga"
python -m src.automations.daily_research
python -m src.automations.sync_memories

# Tests
pytest tests/ -v
pytest tests/test_memory_bridge.py -v
```

### 4.3 AgentMemory desde terminal (WSL)

```bash
# Guardar vía CLI si está instalado
agentmemory save --content "..." --type workflow --concepts "Chain Industria,automation"

# Diagnóstico
agentmemory diagnose 2>/dev/null || curl -s "http://${IP}:3111/health"
```

### 4.4 Cursor (Windows — PowerShell)

```powershell
# Abrir doc Fase 2
code "\\wsl$\Ubuntu\home\chainindustria\agents\docs\chain_industria_agent_fase2.md"

# Ver MCP config
notepad $env:USERPROFILE\.cursor\mcp.json
```

### 4.5 Prompts útiles en Cursor

```
Usa agentmemory memory_recall con query "Chain Industria Fase 2"
```

```
Usa agentmemory memory_save para registrar la lección aprendida de esta sesión
```

### 4.6 Troubleshooting

| Síntoma | Comando / acción |
|---------|------------------|
| MCP rojo en Cursor | `~/scripts/agentmemory-up.sh` → reiniciar Cursor |
| Puerto ocupado | `pm2 stop agentmemory`; `sudo systemctl stop agentmemory` |
| IP WSL cambió | `~/scripts/update-cursor-mcp-ip.sh` |
| Memoria no aparece | `memory_smart_search` con conceptos exactos |
| Python no encuentra módulos | `export PYTHONPATH=~/agents` |

---

## 5. Roadmap

### Sprint 1 — Memory Bridge (semana 1)

| Tarea | Estado |
|-------|--------|
| Cliente HTTP `AgentMemoryClient` en `src/integrations/agentmemory_client.py` | ⬜ |
| `MemoryBridge` reemplaza `MemoryAgent.save()` local | ⬜ |
| Tests: save + recall round-trip | ⬜ |
| Migrar notas existentes de `memory/notes/` al store | ⬜ |

### Sprint 2 — Núcleo agéntico (semana 2)

| Tarea | Estado |
|-------|--------|
| `Planner` genera `TaskPlan` desde string goal | ⬜ |
| `Executor` ejecuta pasos secuenciales | ⬜ |
| Refactor `main.py` → usa Planner + Executor | ⬜ |
| Logging estructurado en `src/utils/logger.py` | ⬜ |

### Sprint 3 — Automatizaciones (semana 3)

| Tarea | Estado |
|-------|--------|
| `daily_research.py` — investigación + guardado automático | ⬜ |
| `sync_memories.py` — reconcilia local vs AgentMemory | ⬜ |
| Cron o systemd timer documentado | ⬜ |
| Alerta si health falla 3 veces seguidas | ⬜ |

### Sprint 4 — Autoaprendizaje y multi-agente IDE (semana 4)

| Tarea | Estado |
|-------|--------|
| `LearningPipeline` post-ciclo (reflect + lesson_save) | ⬜ |
| Claude Code configurado con mismo endpoint AgentMemory | ⬜ |
| Reglas Cursor en `.cursor/rules/` para Chain Industria | ⬜ |
| Documentación y memorias Fase 2 en AgentMemory | ⬜ |

### Hitos

```
Fase 1 ✅  Infra + MCP + esqueleto
    │
    ▼
Fase 2 ──► M1: Memory Bridge operativo
    │      M2: Planner + Executor en producción local
    │      M3: 2 automatizaciones corriendo
    │      M4: Pipeline autoaprendizaje + Claude Code sync
    ▼
Fase 3     Integraciones externas (Notion, Maps, CRM)
           UI dashboard propio
           Métricas y observabilidad
```

---

## 6. Entregables

### 6.1 Código

| Entregable | Ruta | Definición de hecho |
|------------|------|---------------------|
| **E1** Memory Bridge | `src/integrations/agentmemory_client.py` + `src/agent/memory/bridge.py` | save/recall funcionan contra `:3111` |
| **E2** Planner | `src/agent/planner/planner.py` | Genera ≥3 pasos desde un goal |
| **E3** Executor | `src/agent/executor/executor.py` | Ejecuta plan sin excepciones no manejadas |
| **E4** Tools base | `src/agent/tools/` | ≥2 tools (file_read, http_get) |
| **E5** Coordinator v2 | `main.py` refactorizado | Usa E1–E4 en un solo comando |
| **E6** Automations | `src/automations/daily_research.py`, `sync_memories.py` | Ejecutables manualmente; cron opcional |
| **E7** Tests | `tests/test_memory_bridge.py`, `tests/test_planner.py` | `pytest` verde |

### 6.2 Documentación

| Entregable | Archivo |
|------------|---------|
| **D1** Este documento | `docs/chain_industria_agent_fase2.md` |
| **D2** Actualización doc padre | `docs/chain_industria_agent.md` — enlace Fase 2 |
| **D3** README del repo | `agents/README.md` — quick start |
| **D4** Reglas Cursor | `.cursor/rules/chain-industria.mdc` (opcional) |

### 6.3 Memorias AgentMemory (obligatorias al cerrar Fase 2)

| Entregable | Contenido a guardar |
|------------|---------------------|
| **M1** | Arquitectura Memory Bridge + puertos |
| **M2** | Workflows de automatización activos |
| **M3** | Lecciones aprendidas (errores PM2, MCP, WSL IP) |
| **M4** | Preferencias y convenciones del proyecto |

### 6.4 Operación

| Entregable | Verificación |
|------------|--------------|
| **O1** PM2 `agentmemory` online 24/7 | `pm2 status` → online |
| **O2** Health check automatizable | script retorna 0 si `:3111/health` OK |
| **O3** `agentmemory-up.sh` documentado en runbook | probado tras reinicio WSL |

### 6.5 Criterios de cierre de Fase 2

Fase 2 se considera **cerrada** cuando:

- [ ] E1–E7 completados y tests en verde
- [ ] D1–D3 publicados en `docs/`
- [ ] M1–M4 guardados en AgentMemory
- [ ] O1–O3 verificados tras reinicio completo de WSL
- [ ] Un ciclo `Coordinator → Planner → Executor → AgentMemory` demostrado en logs
- [ ] Cursor y Claude Code recuperan la misma memoria de prueba sin edición manual

---

## Referencias

- Doc Fase 1: [`chain_industria_agent.md`](./chain_industria_agent.md)
- Memorias: `mem_mphhlflu`, `mem_mphhw4qu`
- Scripts: `~/scripts/agentmemory-up.sh`, `~/scripts/start-agentmemory.sh`

*Versión: 1.0 — 2026-05-22*
