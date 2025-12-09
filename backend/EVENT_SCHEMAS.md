# Esquemas de Eventos - PLN Filter

## 1. Evento WebSocket: Enviar Mensaje

**Cliente → API Gateway WebSocket**

```json
{
  "action": "sendMessage",
  "data": {
    "conversationId": "conv_user1_user2",
    "receiverId": "user2",
    "content": "Hola, ¿cómo estás?"
  }
}
```

---

## 2. Evento WebSocket: Obtener Historial

**Cliente → API Gateway WebSocket**

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

---

## 3. Evento Lambda: ReceiveMessage

**API Gateway → Lambda ReceiveMessage**

```json
{
  "requestContext": {
    "connectionId": "conn_abc123xyz",
    "authorizer": {
      "claims": {
        "sub": "user1"
      }
    }
  },
  "body": {
    "action": "sendMessage",
    "data": {
      "conversationId": "conv_user1_user2",
      "receiverId": "user2",
      "content": "Hola, ¿cómo estás?"
    }
  }
}
```

---

## 4. Evento SQS: Mensaje para Análisis

**Lambda ReceiveMessage → SQS**

```json
{
  "messageId": "msg_12345",
  "conversationId": "conv_user1_user2",
  "senderId": "user1",
  "receiverId": "user2",
  "content": "Hola, ¿cómo estás?",
  "timestamp": 1704067200000
}
```

---

## 5. Evento WebSocket: Mensaje Recibido

**Lambda ReceiveMessage → API Gateway WebSocket → Cliente**

```json
{
  "action": "messageReceived",
  "data": {
    "messageId": "msg_12345",
    "senderId": "user1",
    "content": "Hola, ¿cómo estás?",
    "timestamp": 1704067200000,
    "status": "delivered"
  }
}
```

---

## 6. Evento Lambda: NotifyUser (Alerta de Riesgo)

**Worker Local → Lambda NotifyUser**

```json
{
  "userId": "user2",
  "messageId": "msg_12345",
  "threatType": "sextorsion",
  "confidence": 0.95,
  "riskLevel": "high",
  "message": "Alerta: Se detectó posible intento de sextorsión"
}
```

---

## 7. Evento WebSocket: Alerta de Riesgo

**Lambda NotifyUser → API Gateway WebSocket → Cliente**

```json
{
  "action": "riskAlert",
  "data": {
    "messageId": "msg_12345",
    "threatType": "sextorsion",
    "confidence": 0.95,
    "riskLevel": "high",
    "message": "Alerta: Se detectó posible intento de sextorsión"
  }
}
```

---

## 8. Evento Lambda: GetMessages

**API Gateway → Lambda GetMessages**

```json
{
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "user1"
      }
    }
  },
  "body": {
    "action": "getMessages",
    "data": {
      "conversationId": "conv_user1_user2",
      "limit": 50,
      "offset": 0
    }
  }
}
```

---

## 9. Respuesta Lambda: GetMessages

**Lambda GetMessages → API Gateway → Cliente**

```json
{
  "action": "messagesHistory",
  "data": {
    "conversationId": "conv_user1_user2",
    "messages": [
      {
        "messageId": "msg_12345",
        "senderId": "user1",
        "content": "Hola, ¿cómo estás?",
        "timestamp": 1704067200000,
        "status": "delivered",
        "riskAnalysis": {
          "analyzed": true,
          "riskLevel": "low",
          "threatType": null,
          "confidence": 0.05
        }
      }
    ],
    "total": 42
  }
}
```

---

## Notas Importantes

1. **Todos los eventos incluyen timestamps en milisegundos (Unix)**
2. **Los IDs se generan con prefijos para identificar tipo:** `msg_`, `conv_`, `conn_`, etc.
3. **El `conversationId` se genera como:** `conv_{userId1}_{userId2}` (ordenado alfabéticamente)
4. **Los tokens JWT se envían en headers HTTP, no en WebSocket**
5. **Las alertas de riesgo se envían de forma asincrónica** (no bloquean el flujo de mensajería)
