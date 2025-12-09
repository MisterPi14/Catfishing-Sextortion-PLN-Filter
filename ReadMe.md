# PLN Filter - Sistema de Detección de Amenazas en Chat

Sistema de mensajería instantánea con detección de amenazas (sextorsión, catfishing) usando AWS serverless + LLM local (Ollama).

## Stack Tecnológico

- **Frontend:** Vue 3 + Vite
- **Backend:** Python + AWS Lambda
- **Base de Datos:** DynamoDB
- **Colas:** SQS
- **Comunicación:** API Gateway WebSocket
- **Autenticación:** Cognito
- **Hosting:** Amplify
- **Worker Local:** Python + Ollama

## Estructura del Proyecto

```
PLN fIlter/
├── frontend/          # Aplicación Vue
├── backend/           # Funciones Lambda (Python)
├── worker/            # Worker local (Python + Ollama)
├── Arquitectura/      # Documentación
├── SETUP.md           # Guía de configuración inicial
└── PROJECT_STRUCTURE.md
```

## Primeros Pasos

### 1. Clonar y Configurar

```bash
# Clonar repositorio
git clone <repo-url>
cd "PLN fIlter"

# Copiar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales AWS
```

### 2. Configurar AWS

Seguir la guía en [SETUP.md](./SETUP.md):

```bash
# Instalar AWS CLI
pip install awscli

# Configurar credenciales
aws configure

# Crear tablas DynamoDB
aws dynamodb create-table ...

# Crear cola SQS
aws sqs create-queue ...
```

### 3. Desplegar Backend (Lambdas)

```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Empaquetar y desplegar cada Lambda
# (Instrucciones detalladas en backend/deploy.sh)
```

### 4. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local

# Ejecutar en desarrollo
npm run dev
```

### 5. Ejecutar Worker Local

```bash
cd worker

# Instalar dependencias
pip install -r requirements.txt

# Asegurar que Ollama está corriendo
# ollama serve

# Ejecutar worker
python main.py
```

## Documentación

- [DATA_MODEL.md](./backend/DATA_MODEL.md) - Estructura de DynamoDB
- [EVENT_SCHEMAS.md](./backend/EVENT_SCHEMAS.md) - Esquemas de eventos JSON
- [SETUP.md](./SETUP.md) - Configuración inicial
- [Arquitectura.txt](./Arquitectura/Arquitectura.txt) - Descripción detallada

## Flujo de Datos

1. **Usuario envía mensaje** → WebSocket → API Gateway
2. **Lambda ReceiveMessage** → Guarda en DynamoDB + Encola en SQS
3. **Worker Local** → Lee de SQS → Analiza con Ollama
4. **Si hay riesgo** → Invoca Lambda NotifyUser → Alerta por WebSocket
5. **Usuario recibe alerta** → Visualiza en tiempo real

## Capa Gratuita AWS

- DynamoDB: 25 GB + 25 RU/s
- Lambda: 1M invocaciones/mes
- API Gateway: 1M mensajes/mes
- SQS: 1M solicitudes/mes
- Cognito: 50k MAU

**Suficiente para MVP con 2 usuarios.**

## Próximos Pasos

- [ ] Crear tablas DynamoDB
- [ ] Desplegar Lambdas
- [ ] Crear API Gateway WebSocket
- [ ] Configurar Cognito
- [ ] Desarrollar frontend Vue
- [ ] Integrar Ollama
- [ ] Desplegar en Amplify

## Soporte

Para preguntas o problemas, revisar la documentación en `Arquitectura/` o contactar al equipo de desarrollo.
