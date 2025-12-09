# PLN Filter - Sistema de Detección de Amenazas en Chat

Sistema de mensajería instantánea con detección de amenazas (sextorsión, catfishing) usando AWS serverless + LLM local (Ollama).

## Stack Tecnológico

- **Frontend:** Vue 3 + Vite
- **Backend:** Python + AWS Lambda (gestionado con Serverless Framework)
- **Base de Datos:** DynamoDB
- **Colas:** SQS
- **Comunicación:** API Gateway WebSocket
- **Autenticación:** Cognito (futuro)
- **Hosting:** Amplify (futuro)
- **Worker Local:** Python + Ollama

## Estructura del Proyecto

```
PLN fIlter/
├── frontend/          # Aplicación Vue 3 + Vite
├── backend/           # Funciones Lambda (Python) + Serverless
├── worker/            # Worker local (Python + Ollama)
├── Arquitectura/      # Documentación de arquitectura
├── SETUP.md           # Guía de configuración con Serverless
├── README.md          # Este archivo
└── .env.example       # Variables de entorno
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

### 2. Desplegar Backend con Serverless

```bash
cd backend

# Instalar dependencias
npm install --save-dev serverless-python-requirements
pip install -r requirements.txt

# Desplegar a AWS
serverless deploy
```

Serverless Framework crea automáticamente:
- Tablas DynamoDB (ChatMessages, Users, Conversations)
- Cola SQS para análisis de mensajes
- API Gateway WebSocket para comunicación en tiempo real
- Roles IAM con permisos necesarios

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Crear archivo de configuración
cp .env.example .env.local

# Editar .env.local con el endpoint WebSocket del backend
# Obtén el endpoint de la salida de: serverless deploy

# Ejecutar en desarrollo
npm run dev
```

### 4. Ejecutar Worker Local

```bash
cd worker

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo de configuración
cp ../.env .env

# Asegurar que Ollama está corriendo
# ollama serve

# Ejecutar worker
python main.py
```

## Documentación

- [SETUP.md](./SETUP.md) - Guía detallada de configuración con Serverless
- [backend/DATA_MODEL.md](./backend/DATA_MODEL.md) - Estructura de DynamoDB
- [backend/EVENT_SCHEMAS.md](./backend/EVENT_SCHEMAS.md) - Esquemas de eventos JSON
- [frontend/README.md](./frontend/README.md) - Documentación del frontend
- [Arquitectura/Arquitectura.txt](./Arquitectura/Arquitectura.txt) - Descripción detallada de la arquitectura

## Flujo de Datos

1. **Usuario envía mensaje** → WebSocket → API Gateway
2. **Lambda ReceiveMessage** → Guarda en DynamoDB + Encola en SQS
3. **Worker Local** → Lee de SQS → Analiza con Ollama
4. **Si hay riesgo** → Invoca Lambda NotifyUser → Alerta por WebSocket
5. **Usuario recibe alerta** → Visualiza en tiempo real

## Capa Gratuita AWS

- **DynamoDB:** 25 GB almacenamiento + 25 RU/s
- **Lambda:** 1M invocaciones/mes
- **API Gateway:** 1M mensajes/mes
- **SQS:** 1M solicitudes/mes
- **Cognito:** 50k MAU

**Suficiente para MVP con 2 usuarios.**

## Comandos Principales

### Backend (Serverless)

```bash
cd backend

# Desplegar
serverless deploy

# Ver logs
serverless logs -f receiveMessage --tail

# Invocar localmente
serverless invoke local -f receiveMessage

# Eliminar stack
serverless remove

# Ver información
serverless info
```

### Frontend

```bash
cd frontend

# Desarrollo
npm run dev

# Build
npm run build

# Preview
npm run preview
```

### Worker

```bash
cd worker

# Ejecutar
python main.py
```

## Próximos Pasos

- [ ] Configurar Cognito para autenticación real
- [ ] Desplegar frontend en Amplify
- [ ] Integrar modelo de Ollama específico
- [ ] Agregar tests unitarios
- [ ] Configurar CI/CD con GitHub Actions
- [ ] Implementar logging centralizado

## Soporte

Para preguntas o problemas:
1. Revisar la documentación en `Arquitectura/`
2. Consultar logs con: `serverless logs -f <function-name>`
3. Verificar variables de entorno en `.env`
