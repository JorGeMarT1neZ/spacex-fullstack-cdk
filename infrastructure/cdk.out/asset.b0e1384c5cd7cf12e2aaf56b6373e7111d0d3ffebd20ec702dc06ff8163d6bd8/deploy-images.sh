#!/bin/bash

set -e

echo "🚀 Iniciando construcción y despliegue de imágenes..."

# Configuración
AWS_ACCOUNT="946253857446"
AWS_REGION="us-east-1"
ECR_REGISTRY="${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Login a ECR
echo "🔐 Autenticando en ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Construir y subir Backend
echo "🐍 Construyendo Backend..."
cd backend
docker build -t $ECR_REGISTRY/spacex-backend:latest .
docker push $ECR_REGISTRY/spacex-backend:latest
echo "✅ Backend subido exitosamente"

# Construir y subir Frontend
echo "⚛️ Construyendo Frontend..."
cd ../frontend

# Verificar que los archivos necesarios existen
if [ ! -f "package.json" ]; then
    echo "❌ package.json no encontrado"
    exit 1
fi

# Instalar dependencias localmente primero para verificar
echo "📦 Instalando dependencias del frontend..."
npm install

# Construir la aplicación
echo "🏗️ Construyendo aplicación React..."
npm run build

# Construir imagen Docker
docker build -t $ECR_REGISTRY/spacex-frontend:latest .

# Subir imagen
docker push $ECR_REGISTRY/spacex-frontend:latest
echo "✅ Frontend subido exitosamente"

echo "🎉 Todas las imágenes han sido construidas y subidas exitosamente"
echo "📦 Backend:  $ECR_REGISTRY/spacex-backend:latest"
echo "📦 Frontend: $ECR_REGISTRY/spacex-frontend:latest"