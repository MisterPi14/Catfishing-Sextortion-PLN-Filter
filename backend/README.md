# Backend - PLN Filter con Serverless Framework

Backend serverless con Python + AWS Lambda, gestionado completamente con Serverless Framework.

## Estructura

```
backend/
├── serverless.yml              # Configuración de Serverless
├── requirements.txt            # Dependencias Python
├── handlers/                   # Funciones Lambda
│   ├── receive_message.py      # Procesa mensajes entrantes
│   ├── get_messages.py         # Recupera historial
│   └── notify_user.py          # Envía alertas de riesgo
├── shared/                     # Código compartido
│   ├── dynamodb_client.py      # Cliente DynamoDB
│   ├── sqs_client.py           # Cliente SQS
│   └── websocket_client.py     # Cliente WebSocket
└── README.md                   # Este archivo
```

## Instalación

```bash
# Instalar Serverless Framework globalmente
npm install -g serverless

# Instalar dependencias del proyecto
npm install --save-dev serverless-python-requirements

# Instalar dependencias Python
pip install -r requirements.txt
```

## Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<tu_access_key>
AWS_SECRET_ACCESS_KEY=<tu_secret_key>
STAGE=dev
```

### Serverless.yml

El archivo `serverless.yml` define:

- **Funciones Lambda:** receiveMessage, getMessages, notifyUser
- **Tablas DynamoDB:** ChatMessages, Users, Conversations
- **Cola SQS:** Para análisis asincrónico de mensajes
- **API Gateway WebSocket:** Para comunicación en tiempo real
- **Roles IAM:** Permisos necesarios para cada servicio

## Despliegue

### Desplegar a AWS

```bash
# Despliegue básico
serverless deploy

# Despliegue con stage específico
serverless deploy --stage prod

# Despliegue con región específica
serverless deploy --region eu-west-1
```

Serverless Framework automáticamente:
1. Empaqueta el código Python con dependencias
2. Crea un bucket S3 para almacenar el código
3. Crea las tablas DynamoDB
4. Crea la cola SQS
5. Crea el API Gateway WebSocket
6. Configura los roles IAM
7. Sube las Lambdas

### Salida del Despliegue

```
Service Information
service: pln-filter-backend
stage: dev
region: us-east-1
stack: pln-filter-backend-dev
resources: 15
api keys:
  None
endpoints:
  wss: wss://xxxxx.execute-api.us-east-1.amazonaws.com/dev
functions:
  receiveMessage: pln-filter-backend-dev-receiveMessage
  getMessages: pln-filter-backend-dev-getMessages
  notifyUser: pln-filter-backend-dev-notifyUser
```

## Comandos Útiles

### Logs

```bash
# Ver logs de una función
serverless logs -f receiveMessage

# Ver logs en tiempo real
serverless logs -f receiveMessage --tail

# Ver logs de los últimos 10 minutos
serverless logs -f receiveMessage --startTime 10m
```

### Invocación Local

```bash
# Invocar una función localmente
serverless invoke local -f receiveMessage -d '{"test": "data"}'

# Invocar con archivo de datos
serverless invoke local -f receiveMessage -p event.json
```

### Información

```bash
# Ver información del stack desplegado
serverless info

# Ver recursos creados
serverless info --verbose
```

### Actualización

```bash
# Actualizar solo el código (más rápido)
serverless deploy function -f receiveMessage

# Actualizar todo el stack
serverless deploy
```

### Eliminación

```bash
# Eliminar todo el stack (tablas, colas, Lambdas, etc.)
serverless remove

# Eliminar con confirmación
serverless remove --force
```

## Funciones Lambda

### receiveMessage

**Ruta WebSocket:** `sendMessage`

Procesa mensajes entrantes:
1. Guarda en DynamoDB
2. Encola en SQS para análisis
3. Envía al destinatario por WebSocket

**Evento:**
```json
{
  "action": "sendMessage",
  "data": {
    "conversationId": "conv_user1_user2",
    "receiverId": "user2",
    "content": "Hola"
  }
}
```

### getMessages

**Ruta WebSocket:** `getMessages`

Recupera historial de mensajes:
1. Consulta DynamoDB
2. Retorna mensajes ordenados por timestamp

**Evento:**
```json
{
  "action": "getMessages",
  "data": {
    "conversationId": "conv_user1_user2",
    "limit": 50,
    "offset": 0
  }
}
```

### notifyUser

**Invocación:** Desde Worker local

Envía alertas de riesgo:
1. Obtiene connectionId del usuario
2. Envía alerta por WebSocket

**Evento:**
```json
{
  "userId": "user2",
  "messageId": "msg_12345",
  "threatType": "sextorsion",
  "confidence": 0.95,
  "riskLevel": "high"
}
```

## Recursos Creados

### DynamoDB

- **ChatMessages:** Almacena todos los mensajes
- **Users:** Información de usuarios y conexiones
- **Conversations:** Metadatos de conversaciones

### SQS

- **pln-filter-backend-dev-messages:** Cola para análisis de mensajes

### API Gateway WebSocket

- Endpoint: `wss://xxxxx.execute-api.us-east-1.amazonaws.com/dev`
- Rutas: `sendMessage`, `getMessages`

## Troubleshooting

### Error: "No credentials found"

```bash
aws configure
# Ingresa tus credenciales AWS
```

### Error: "Plugin not found"

```bash
npm install --save-dev serverless-python-requirements
```

### Error: "Table already exists"

```bash
serverless remove
serverless deploy
```

### Error: "Timeout"

Aumentar timeout en `serverless.yml`:
```yaml
functions:
  receiveMessage:
    timeout: 60  # Aumentar de 30 a 60 segundos
```

### Error: "Permission denied"

Verificar que el rol IAM tiene permisos para:
- DynamoDB (Query, Scan, GetItem, PutItem, UpdateItem)
- SQS (SendMessage, ReceiveMessage, DeleteMessage)
- API Gateway (ManageConnections)

## Desarrollo Local

### Emular DynamoDB localmente

```bash
# Instalar DynamoDB local
npm install -g dynamodb-local

# Ejecutar
dynamodb-local

# Usar en serverless.yml
dynamodb:
  stages:
    - dev
  start:
    port: 8000
    inMemory: true
    migrate: true
```

### Ejecutar Lambdas localmente

```bash
serverless invoke local -f receiveMessage -d '{"test": "data"}'
```

## Monitoreo

### CloudWatch

Ver logs en AWS Console:
1. CloudWatch > Logs > `/aws/lambda/pln-filter-backend-dev-*`

### Métricas

Serverless Framework proporciona:
- Duración de ejecución
- Errores
- Invocaciones
- Throttling

## Costos

Con la capa gratuita de AWS:
- **Lambda:** 1M invocaciones/mes (gratis)
- **DynamoDB:** 25 GB + 25 RU/s (gratis)
- **SQS:** 1M solicitudes/mes (gratis)
- **API Gateway:** 1M mensajes/mes (gratis)

**Costo estimado para MVP:** $0 (dentro de capa gratuita)

## Próximos Pasos

- [ ] Agregar autenticación con Cognito
- [ ] Implementar tests unitarios
- [ ] Configurar CI/CD
- [ ] Agregar logging centralizado
- [ ] Implementar rate limiting
- [ ] Agregar validación de entrada
