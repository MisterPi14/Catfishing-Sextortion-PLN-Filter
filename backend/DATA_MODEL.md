# Modelo de Datos - DynamoDB

## Tabla 1: ChatMessages

Almacena todos los mensajes del sistema.

**Clave Primaria:**
- Partition Key (PK): `conversationId` (String)
- Sort Key (SK): `timestamp` (Number - Unix timestamp en ms)

**Atributos:**

```json
{
  "conversationId": "conv_user1_user2",
  "timestamp": 1704067200000,
  "messageId": "msg_12345",
  "senderId": "user1",
  "receiverId": "user2",
  "content": "Hola, ¿cómo estás?",
  "status": "delivered",
  "riskAnalysis": {
    "analyzed": false,
    "riskLevel": null,
    "threatType": null,
    "confidence": null
  },
  "createdAt": "2024-01-01T12:00:00Z"
}
```

**Índices Secundarios:**
- GSI: `senderId-timestamp` → Para consultar mensajes por remitente
- GSI: `receiverId-timestamp` → Para consultar mensajes por destinatario

---

## Tabla 2: Users

Almacena información de usuarios y sus conexiones activas.

**Clave Primaria:**
- Partition Key (PK): `userId` (String)

**Atributos:**

```json
{
  "userId": "user1",
  "email": "<email>",
  "username": "username1",
  "connectionId": "conn_abc123xyz",
  "isOnline": true,
  "lastSeen": 1704067200000,
  "createdAt": "2024-01-01T12:00:00Z"
}
```

**Notas:**
- `connectionId` se actualiza cada vez que el usuario se conecta por WebSocket
- `isOnline` se usa para saber si el usuario está activo

---

## Tabla 3: Conversations

Metadatos de conversaciones (opcional pero útil).

**Clave Primaria:**
- Partition Key (PK): `conversationId` (String)

**Atributos:**

```json
{
  "conversationId": "conv_user1_user2",
  "participant1": "user1",
  "participant2": "user2",
  "lastMessage": "Hola, ¿cómo estás?",
  "lastMessageTime": 1704067200000,
  "messageCount": 42,
  "createdAt": "2024-01-01T12:00:00Z",
  "updatedAt": "2024-01-01T12:30:00Z"
}
```

---

## Flujo de Datos

### Envío de Mensaje

1. Usuario envía mensaje por WebSocket
2. Lambda `ReceiveMessage` recibe el evento
3. Guarda en `ChatMessages` con `status: "pending"` y `analyzed: false`
4. Encola en SQS para análisis
5. Envía al destinatario por WebSocket

### Análisis de Mensaje

1. Worker local lee de SQS
2. Procesa con Ollama (LLM)
3. Actualiza `ChatMessages` con resultado de análisis
4. Si hay riesgo, invoca Lambda `NotifyUser`

### Recuperación de Historial

1. Usuario solicita historial
2. Lambda `GetMessages` consulta `ChatMessages` con `conversationId`
3. Retorna mensajes ordenados por `timestamp`

---

## Consideraciones de Costo (Capa Gratuita)

- **DynamoDB:** 25 GB almacenamiento + 25 unidades de lectura/escritura por segundo (gratis)
- Para 2 usuarios con ~100 mensajes/día: **Dentro de límites gratuitos**
- Usar `PAY_PER_REQUEST` para no preocuparse por provisioning

---

## Comandos para Crear Tablas

```bash
# ChatMessages
aws dynamodb create-table \
  --table-name ChatMessages \
  --attribute-definitions \
    AttributeName=conversationId,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=conversationId,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Users
aws dynamodb create-table \
  --table-name Users \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
  --key-schema \
    AttributeName=userId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Conversations
aws dynamodb create-table \
  --table-name Conversations \
  --attribute-definitions \
    AttributeName=conversationId,AttributeType=S \
  --key-schema \
    AttributeName=conversationId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```
