#!/usr/bin/env bash

set -u

PROJECT_DIR="$HOME/agents"
REPORT_DIR="$PROJECT_DIR/reports"
REPORT_FILE="$REPORT_DIR/audit-chain-industria-agent-$(date +%Y%m%d-%H%M%S).md"

mkdir -p "$REPORT_DIR"

mask_secret() {
  sed -E 's/(sk-[A-Za-z0-9_-]{8})[A-Za-z0-9_-]+/\1********/g' \
  | sed -E 's/(ghp_[A-Za-z0-9]{8})[A-Za-z0-9]+/\1********/g' \
  | sed -E 's/(github_pat_[A-Za-z0-9_]{8})[A-Za-z0-9_]+/\1********/g'
}

run_cmd() {
  local title="$1"
  local cmd="$2"

  {
    echo ""
    echo "## $title"
    echo ""
    echo '```bash'
    echo "$ $cmd"
    echo '```'
    echo ""
    echo '```text'
    bash -lc "$cmd" 2>&1 | mask_secret
    echo '```'
    echo ""
  } >> "$REPORT_FILE"
}

write_section() {
  {
    echo ""
    echo "$1"
    echo ""
  } >> "$REPORT_FILE"
}

{
  echo "# Auditoría Chain Industria Agent"
  echo ""
  echo "**Fecha:** $(date)"
  echo "**Proyecto:** chain_industria_agent"
  echo "**Directorio esperado:** $PROJECT_DIR"
  echo ""
  echo "---"
} > "$REPORT_FILE"

write_section "# 1. Resumen inicial"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ No existe el directorio $PROJECT_DIR" >> "$REPORT_FILE"
  echo "No existe $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR"

echo "✅ Directorio del proyecto encontrado: $PROJECT_DIR" >> "$REPORT_FILE"

write_section "# 2. Diagnóstico del sistema"

run_cmd "Usuario actual" "whoami"
run_cmd "Directorio actual" "pwd"
run_cmd "Sistema operativo" "uname -a"
run_cmd "Versión Ubuntu" "lsb_release -a || cat /etc/os-release"
run_cmd "Fecha del sistema" "date"
run_cmd "Uso de disco" "df -h ."
run_cmd "Memoria" "free -h"
run_cmd "IP WSL" "hostname -I || true"

write_section "# 3. Herramientas instaladas"

run_cmd "Git" "git --version || true"
run_cmd "GitHub CLI" "gh --version || true"
run_cmd "GitHub Auth Status" "gh auth status || true"
run_cmd "Python" "python3 --version || true"
run_cmd "Pip" "python3 -m pip --version || true"
run_cmd "Node" "node -v || true"
run_cmd "NPM" "npm -v || true"
run_cmd "NVM" "command -v nvm || true"
run_cmd "PM2" "pm2 -v || true"
run_cmd "AgentMemory path" "which agentmemory || true"
run_cmd "AgentMemory version" "agentmemory --version || true"
run_cmd "Tree" "tree --version || true"

write_section "# 4. Estado del proyecto"

run_cmd "Archivos raíz" "ls -la"
run_cmd "Estructura del proyecto" "tree -L 4 -I 'venv|.venv|__pycache__|node_modules|.git' || find . -maxdepth 4 -type f | sort"
run_cmd "Tamaño del proyecto" "du -h -d 2 . 2>/dev/null | sort -h | tail -50"
run_cmd "Archivos Python" "find . -name '*.py' -not -path './venv/*' -not -path './.venv/*' -print | sort"
run_cmd "Archivos Markdown" "find . -name '*.md' -print | sort"
run_cmd "Scripts shell" "find . -name '*.sh' -print | sort"

write_section "# 5. Estado Git"

run_cmd "Git status" "git status || true"
run_cmd "Git branch" "git branch -vv || true"
run_cmd "Git remote" "git remote -v || true"
run_cmd "Últimos commits" "git log --oneline --decorate -10 || true"
run_cmd "Archivos trackeados" "git ls-files | sort || true"
run_cmd "Archivos ignorados relevantes" "git status --ignored -s | head -100 || true"

write_section "# 6. Revisión de archivos clave"

for f in "main.py" "requirements.txt" "README.md" ".gitignore" "AGENTS.md" "chain_industria_agent.md"; do
  if [ -f "$f" ]; then
    run_cmd "Contenido de $f" "sed -n '1,220p' '$f'"
  else
    echo "## $f" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "❌ Archivo no encontrado." >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
  fi
done

write_section "# 7. Revisión de AgentMemory y PM2"

run_cmd "PM2 status" "pm2 status || true"
run_cmd "PM2 logs agentmemory" "pm2 logs agentmemory --lines 80 --nostream || true"
run_cmd "Puerto 3111" "ss -ltnp | grep 3111 || true"
run_cmd "Health AgentMemory" "curl -i http://localhost:3111/agentmemory/health || true"
run_cmd "Viewer AgentMemory" "ss -ltnp | grep -E '3113|3114' || true"

write_section "# 8. Revisión Cursor MCP"

run_cmd "Cursor MCP en WSL home" "cat ~/.cursor/mcp.json 2>/dev/null || true"
run_cmd "Cursor MCP en Windows si existe" "find /mnt/c/Users -maxdepth 3 -path '*/.cursor/mcp.json' -print -exec sed -n '1,200p' {} \\; 2>/dev/null || true"

write_section "# 9. Prueba del agente Python"

run_cmd "Ejecutar main.py" "python3 main.py || true"

write_section "# 10. Detección automática de deficiencias"

{
  echo "## Deficiencias detectadas"
  echo ""
} >> "$REPORT_FILE"

check_file() {
  local file="$1"
  if [ -f "$file" ]; then
    echo "- ✅ Existe \`$file\`." >> "$REPORT_FILE"
  else
    echo "- ❌ Falta \`$file\`." >> "$REPORT_FILE"
  fi
}

check_dir() {
  local dir="$1"
  if [ -d "$dir" ]; then
    echo "- ✅ Existe carpeta \`$dir/\`." >> "$REPORT_FILE"
  else
    echo "- ❌ Falta carpeta \`$dir/\`." >> "$REPORT_FILE"
  fi
}

check_file "main.py"
check_file "requirements.txt"
check_file "README.md"
check_file ".gitignore"
check_file "AGENTS.md"
check_file "chain_industria_agent.md"

check_dir "docs"
check_dir "scripts"
check_dir "src"
check_dir "memory"
check_dir "tests"
check_dir "coordinator"
check_dir "researcher"
check_dir "scraper"
check_dir "creative"

if [ -d "venv" ]; then
  if grep -q "^venv/" .gitignore 2>/dev/null; then
    echo "- ✅ \`venv/\` existe y está ignorado en .gitignore." >> "$REPORT_FILE"
  else
    echo "- ⚠️ \`venv/\` existe pero no parece estar ignorado en .gitignore." >> "$REPORT_FILE"
  fi
fi

if git remote -v 2>/dev/null | grep -q "URL_DE_TU_REPOSITORIO\\|usuario/repositorio"; then
  echo "- ❌ El remoto Git parece contener una URL de ejemplo incorrecta." >> "$REPORT_FILE"
else
  echo "- ✅ No se detectó URL de ejemplo obvia en remoto Git." >> "$REPORT_FILE"
fi

if pm2 status 2>/dev/null | grep -q "agentmemory"; then
  echo "- ✅ PM2 conoce el proceso agentmemory." >> "$REPORT_FILE"
else
  echo "- ⚠️ PM2 no muestra agentmemory." >> "$REPORT_FILE"
fi

if curl -s http://localhost:3111/agentmemory/health >/dev/null 2>&1; then
  echo "- ✅ AgentMemory responde en endpoint health." >> "$REPORT_FILE"
else
  echo "- ⚠️ AgentMemory no respondió en health." >> "$REPORT_FILE"
fi

write_section "# 11. Parches seguros aplicados"

echo "Aplicando parches seguros..."

# Crear .gitignore seguro si falta o reforzarlo.
touch .gitignore

append_ignore() {
  local line="$1"
  grep -qxF "$line" .gitignore || echo "$line" >> .gitignore
}

append_ignore "venv/"
append_ignore ".venv/"
append_ignore "__pycache__/"
append_ignore "*.py[cod]"
append_ignore ".env"
append_ignore ".env.*"
append_ignore "!.env.example"
append_ignore "node_modules/"
append_ignore "*.log"
append_ignore ".agentmemory/"
append_ignore "server.log"
append_ignore "*.key"
append_ignore "*.pem"
append_ignore "*.token"

# Crear estructura base si falta.
mkdir -p docs scripts src/agent/planner src/agent/executor src/agent/memory src/agent/tools src/automations src/integrations src/utils memory/notes memory/summaries tests coordinator researcher scraper creative reports

# Crear __init__.py seguros.
touch src/__init__.py
touch src/agent/__init__.py
touch src/agent/planner/__init__.py
touch src/agent/executor/__init__.py
touch src/agent/memory/__init__.py
touch src/agent/tools/__init__.py
touch src/automations/__init__.py
touch src/integrations/__init__.py
touch src/utils/__init__.py
touch coordinator/__init__.py
touch researcher/__init__.py
touch scraper/__init__.py
touch creative/__init__.py
touch tests/__init__.py

# .gitkeep en carpetas.
find docs scripts src memory tests coordinator researcher scraper creative -type d -exec touch {}/.gitkeep \; 2>/dev/null || true

# Crear requirements si falta.
if [ ! -f requirements.txt ]; then
cat > requirements.txt <<'REQ'
requests
python-dotenv
REQ
echo "- ✅ Creado requirements.txt." >> "$REPORT_FILE"
else
echo "- ✅ requirements.txt ya existía." >> "$REPORT_FILE"
fi

# Crear script de diagnóstico si falta.
if [ ! -f scripts/check-agentmemory.sh ]; then
cat > scripts/check-agentmemory.sh <<'SH'
#!/usr/bin/env bash

echo "=============================="
echo " Diagnóstico AgentMemory"
echo "=============================="

echo ""
echo "PM2:"
pm2 status || true

echo ""
echo "Health:"
curl -i http://localhost:3111/agentmemory/health || true

echo ""
echo "Puerto 3111:"
ss -ltnp | grep 3111 || true

echo ""
echo "Logs:"
pm2 logs agentmemory --lines 40 --nostream || true
SH
chmod +x scripts/check-agentmemory.sh
echo "- ✅ Creado scripts/check-agentmemory.sh." >> "$REPORT_FILE"
else
chmod +x scripts/check-agentmemory.sh
echo "- ✅ scripts/check-agentmemory.sh ya existía y se aseguró permiso ejecutable." >> "$REPORT_FILE"
fi

write_section "# 12. Estado después de parches"

run_cmd "Git status después de parches" "git status || true"
run_cmd "Estructura después de parches" "tree -L 4 -I 'venv|.venv|__pycache__|node_modules|.git' || true"
run_cmd "Prueba final main.py" "python3 main.py || true"
run_cmd "Prueba final AgentMemory" "curl -i http://localhost:3111/agentmemory/health || true"

write_section "# 13. Recomendaciones iniciales"

{
  echo "- Revisar el reporte completo."
  echo "- Corregir errores de importación si \`python3 main.py\` falla."
  echo "- Confirmar que \`git remote -v\` apunta al repositorio real de GitHub."
  echo "- Confirmar que \`gh auth status\` está autenticado."
  echo "- Confirmar que Cursor MCP sigue mostrando \`agentmemory\` con herramientas habilitadas."
  echo "- Hacer commit de los cambios generados si el reporte es correcto."
  echo ""
  echo "Comandos sugeridos:"
  echo ""
  echo '```bash'
  echo "git status"
  echo "git add ."
  echo "git commit -m \"chore: audit and patch chain industria agent base\""
  echo "git push"
  echo '```'
} >> "$REPORT_FILE"

echo ""
echo "=============================================="
echo " Auditoría terminada"
echo " Reporte generado en:"
echo "$REPORT_FILE"
echo "=============================================="
echo ""
echo "Para ver el reporte:"
echo "cat \"$REPORT_FILE\""
echo ""
echo "Para abrir el reporte en Cursor:"
echo "cursor \"$REPORT_FILE\" 2>/dev/null || code \"$REPORT_FILE\" 2>/dev/null || true"
