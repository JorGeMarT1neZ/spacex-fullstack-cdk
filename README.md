# SpaceX FullStack Technical Test

aplicación FullStack que consume datos de la API de SpaceX, los procesa con AWS Lambda, almacena en DynamoDB y muestra a través de una aplicación web con Django y React.

## 🏗️ Arquitectura

![Arquitectura](docs/architecture.png)

## 🚀 Despliegue Rápido

### Prerrequisitos
- Python 3.12+
- Node.js 18+
- AWS CLI configurado
- Docker y Docker Compose

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd efRouting_technical_test


## 🌟 Infraestructura Desplegada

- **Región**: us-east-1
- **DynamoDB Table**: `spacex-launches`
- **Lambda Function**: `spacex-data-processor`
- **Frecuencia de ejecución**: Cada 6 horas
- **Stack CloudFormation**: `SpaceXFullStack`