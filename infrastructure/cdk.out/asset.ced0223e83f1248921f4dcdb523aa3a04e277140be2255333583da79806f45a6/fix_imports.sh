#!/bin/bash

echo "🔧 Reparando estructura del proyecto..."

# Crear directorios si no existen
mkdir -p stack
mkdir -p ../lambda

# Crear archivos __init__.py necesarios
touch stack/__init__.py

# Verificar estructura
echo "📁 Estructura actual:"
find . -name "*.py" | head -20

# Verificar imports
echo "🔍 Probando imports de Python..."
python -c "
try:
    from stack.spacex_stack import SpaceXStack
    print('✅ Import de SpaceXStack: CORRECTO')
except ImportError as e:
    print('❌ Error en import:', e)
"

echo "✅ Reparación completada"
