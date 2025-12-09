# Setup Inicial - PLN Filter

## Requisitos Previos

- Cuenta AWS activa
- Python 3.9+
- Node.js 16+
- Git
- Ollama instalado localmente

## Paso 1: Configurar AWS CLI

```bash
# Instalar AWS CLI
pip install awscli

# Configurar credenciales
aws configure
# Ingresa: Access Key ID, Secret Access Key, región (ej: us-east-1), formato (json)
```

## Paso 2: Crear Tabla DynamoDB

```bash
# Crear tabla ChatMessages
aws dynamodb create-table \
  --table-name ChatMessages \
  --attribute-definitions \
    AttributeName=conversationId,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=conversationId,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

## Paso 3: Crear Cola SQS

```bash
# Crear cola para mensajes a analizar
aws sqs create-queue \
  --queue-name pln-filter-messages \
  --region us-east-1
```

## Paso 4: Crear User Pool en Cognito

```bash
# Crear user pool
aws cognito-idp create-user-pool \
  --pool-name PLNFilterUsers \
  --policies PasswordPolicy='{MinimumLength=8,RequireUppercase=false,RequireLowercase=false,RequireNumbers=false,RequireSymbols=false}' \
  --region us-east-1
```

## Paso 5: Crear API Gateway WebSocket

```bash
# Crear API WebSocket (se hace desde consola AWS por ahora)
# Ir a: API Gateway > Create API > WebSocket API
# Nombre: pln-filter-websocket
```

## Paso 6: Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<tu_access_key>
AWS_SECRET_ACCESS_KEY=<tu_secret_key>

# DynamoDB
DYNAMODB_TABLE=ChatMessages

# SQS
SQS_QUEUE_URL=<url_de_tu_cola_sqs>

# API Gateway WebSocket
WEBSOCKET_API_ENDPOINT=<tu_endpoint_websocket>

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral  # o el modelo que uses
```

## Próximos Pasos

1. **Definir modelo de datos DynamoDB** → Estructura exacta de tablas
2. **Crear esquemas de eventos** → Formato JSON de mensajes
3. **Desarrollar Lambdas** → ReceiveMessage, GetMessages, NotifyUser
4. **Crear frontend Vue** → Interfaz de chat
5. **Implementar Worker local** → Integración con Ollama

## Comandos Útiles

```bash
# Ver tablas DynamoDB
aws dynamodb list-tables --region us-east-1

# Ver colas SQS
aws sqs list-queues --region us-east-1

# Probar conexión a Ollama
curl http://localhost:11434/api/tags
```
