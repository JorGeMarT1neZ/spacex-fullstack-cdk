# SpaceX FullStack Technical Test

Sistema FullStack que consume datos de la API pública de SpaceX, los
procesa con AWS Lambda, almacena en Amazon DynamoDB y muestra a través
de una aplicación web con Django (backend) y React (frontend).

### Servicios AWS Utilizados

-   AWS Lambda: Procesamiento de datos de SpaceX cada 6 horas
-   Amazon DynamoDB: Almacenamiento de datos de lanzamientos
-   Amazon EventBridge: Programación de ejecuciones automáticas
-   AWS ECS Fargate: Contenerización de aplicaciones (pendiente)
-   Amazon ECR: Registry de imágenes Docker
-   AWS IAM: Gestión de permisos y seguridad
-   AWS CloudFormation: Infraestructura como código

### 🟡 En Progreso:

-   🔄 ECS Fargate: Despliegue en proceso (validación de recursos)

## 🚀 Despliegue Rápido

### Clonar el repositorio

``` bash
git clone https://github.com/JorGeMarT1neZ/spacex-fullstack-cdk.git
cd efRouting_technical_test
```

### Configurar Entorno

``` bash
# Backend Django
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend React
cd ../frontend
npm install
```

### Desplegar Infraestructura

``` bash
cd infrastructure
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Bootstrap CDK (primera vez)
cdk bootstrap

# Desplegar
cdk deploy
```

## Ejecutar Localmente

``` bash
# Backend
cd backend
docker build -t spacex-backend .
docker run -p 8000:8000 -e TABLE_NAME=spacex-launches spacex-backend

# Frontend
cd frontend
npm start
```

## Probar Lambda Manualmente

``` bash
aws lambda invoke --function-name spacex-data-processor output.json
cat output.json
```

## Verificar Datos en DynamoDB

``` bash
aws dynamodb scan --table-name spacex-launches --max-items 5
```

## Probar API backend

``` bash
curl http://localhost:8000/api/statistics/
curl http://localhost:8000/api/launches/?limit=3
```

## Estructura del proyecto

    efRouting_technical_test01/
    ├── infrastructure/
    │   ├── stack/
    │   │   └── spacex_stack.py
    │   ├── app.py
    │   └── requirements.txt
    ├── lambda/
    │   ├── lambda_function.py
    │   ├── requirements.txt
    │   └── test_lambda_function.py
    ├── backend/
    │   ├── spacex_site/
    │   ├── launches/
    │   ├── manage.py
    │   ├── requirements.txt
    │   └── Dockerfile
    ├── frontend/
    │   ├── src/
    │   │   ├── components/
    │   │   └── App.js
    │   ├── public/
    │   ├── package.json
    │   └── Dockerfile
    └── .github/workflows/

## Comandos útiles

``` bash
# Backend development
cd backend && python manage.py runserver

# Frontend development  
cd frontend && npm start

# Ejecutar pruebas
cd lambda && python -m pytest
cd backend && python manage.py test
```

## Infraestructura

``` bash
# Sintetizar template CloudFormation
cdk synth

# Ver diferencias
cdk diff

# Destruir recursos
cdk destroy
```

## Docker

``` bash
docker build -t spacex-backend ./backend
docker build -t spacex-frontend ./frontend
docker-compose up
```

## 🌟 Infraestructura Desplegada

-   Región: us-east-1
-   DynamoDB Table: spacex-launches
-   Lambda Function: spacex-data-processor
-   Frecuencia: cada 6 horas
-   Stack CloudFormation: SpaceXFullStack
-   IAM Roles configurados

### Comandos de verificación

``` bash
aws lambda invoke --function-name spacex-data-processor output.json
aws dynamodb scan --table-name spacex-launches --max-items 3
```

### 🌐 URLs y Endpoints

-   http://localhost:8000/api/launches/
-   http://localhost:8000/api/statistics/
-   http://localhost:8000/api/launches/{id}/
-   http://localhost:8000/swagger/
-   http://localhost:8000/health/

### Frontend React

-   http://localhost:3000/
-   http://localhost:3000/statistics