#!/bin/bash

# Chain Industria Agent - Setup Script
# Este script clona, configura e instala el proyecto

echo "===================================="
echo "Chain Industria Agent - Setup"
echo "===================================="

# 1. Clona el repositorio
echo ""
echo "1. Clonando repositorio..."
git clone https://github.com/chaiindustriaceoempresa-gif/chain_industria_agent.git
cd chain_industria_agent

# 2. Verifica que estamos en el directorio correcto
echo ""
echo "2. Directorio actual:"
pwd

# 3. Instala las dependencias
echo ""
echo "3. Instalando dependencias..."
pip install -r requirements.txt

# 4. Verifica la estructura
echo ""
echo "4. Estructura del proyecto:"
ls -la

# 5. Muestra instrucciones finales
echo ""
echo "===================================="
echo "✅ Setup completado"
echo "===================================="
echo ""
echo "Para ejecutar el agente:"
echo "  python main.py"
echo ""
echo "Para ver el estado de git:"
echo "  git status"
echo ""
echo "Para actualizar cambios:"
echo "  git pull origin main"
echo ""
