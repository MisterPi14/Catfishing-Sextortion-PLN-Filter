# Setup Inicial - PLN Filter con Serverless Framework

## Requisitos Previos

- Cuenta AWS activa
- Python 3.11+
- Node.js 16+
- Git
- Ollama instalado localmente
- Serverless Framework instalado globalmente

## Paso 1: Instalar Serverless Framework

```bash
# Instalar Serverless Framework globalmente
npm install -g serverless

# Verificar instalación
serverless --version
```

## Paso 2: Configurar AWS CLI

```bash
# Instalar AWS CLI
pip install awscli

# Configurar credenciales
aws configure
# Ingresa: Access Key ID, Secret Access Key, región (ej: us-east-1), formato (json)
```

## Paso 3: Instalar Dependencias del Backend

```bash
cd backend

# Instalar dependencias Python
pip install -r requirements.txt

# Instalar plugin de Serverless para Python
npm install --save-dev serverless-python-requirements
```

## Paso 4: Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<tu_access_key>
AWS_SECRET_ACCESS_KEY=<tu_secret_key>
STAGE=dev

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

## Paso 5: Desplegar Backend con Serverless

```bash
cd backend

# Desplegar a AWS
serverless deploy

# O con variables de entorno específicas
serverless deploy --stage dev --region us-east-1
```

Serverless Framework automáticamente:
- Crea las tablas DynamoDB
- Crea la cola SQS
- Crea el API Gateway WebSocket
- Configura los roles IAM necesarios
- Empaqueta y sube las Lambdas

## Paso 6: Obtener Endpoints

Después del despliegue, Serverless mostrará:

```
endpoints:
  wss: wss://xxxxx.execute-api.us-east-1.amazonaws.com/dev
```

Guarda este endpoint para configurar el frontend.

## Paso 7: Configurar Frontend

```bash
cd frontend

# Crear .env.local
cp .env.example .env.local

# Editar con el endpoint WebSocket obtenido
VITE_WEBSOCKET_URL=wss://xxxxx.execute-api.us-east-1.amazonaws.com/dev
```

## Paso 8: Ejecutar Worker Local

```bash
cd worker

# Instalar dependencias
pip install -r requirements.txt

# Crear .env
cp ../.env .env

# Ejecutar worker
python main.py
```

## Comandos Útiles de Serverless

```bash
# Ver logs de una Lambda
serverless logs -f receiveMessage --tail

# Invocar una Lambda localmente
serverless invoke local -f receiveMessage -d '{"test": "data"}'

# Eliminar stack completo
serverless remove

# Ver información del stack desplegado
serverless info
```

## Estructura del Proyecto

```
backend/
├── serverless.yml          # Configuración de Serverless
├── requirements.txt        # Dependencias Python
├── handlers/              # Funciones Lambda
│   ├── receive_message.py
│   ├── get_messages.py
│   └── notify_user.py
└── shared/               # Código compartido
    ├── dynamodb_client.py
    ├── sqs_client.py
    └── websocket_client.py
```

## Troubleshooting

### Error: "No credentials found"
```bash
# Asegúrate de haber ejecutado aws configure
aws configure
```

### Error: "Plugin not found"
```bash
# Instala el plugin de Python
npm install --save-dev serverless-python-requirements
```

### Error: "Table already exists"
```bash
# Elimina el stack anterior
serverless remove

# Luego redeploy
serverless deploy
```
