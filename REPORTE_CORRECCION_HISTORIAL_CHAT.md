# Corrección de historial de mensajes al relogin

## Contexto del problema

Se observaba este comportamiento:

1. Usuario A envía mensaje a Usuario B.
2. Usuario B estaba desconectado.
3. Al cerrar sesión e iniciar con Usuario B, no se veía el mensaje previo de Usuario A.

## Causa raíz identificada

La causa principal estaba en una inconsistencia de autenticación entre handlers WebSocket:

- El authorizer WebSocket construye la identidad en `principalId`.
- `receive_message` sí soportaba `claims.sub` y `principalId`.
- `get_messages` **solo** intentaba leer `claims.sub`.

Resultado: `sendMessage` funcionaba, pero `getMessages` podía fallar al recuperar historial en sesiones nuevas (relogin), dependiendo del formato real del `requestContext.authorizer`.

Además, había una segunda causa funcional de UX/estado:

- El frontend limpiaba estado en logout (`resetState`).
- No existía carga inicial de conversaciones desde backend al entrar de nuevo.
- La lista de chats dependía de conversaciones creadas localmente en sesión actual.

## Cambios implementados

## 1) Backend: robustecer `getMessages`

Archivo modificado: `backend/handlers/get_messages.py`

Se implementó extracción robusta de usuario con este orden:

1. `authorizer.claims.sub`
2. `authorizer.principalId` o `authorizer.sub`
3. fallback por `connectionId` consultando DynamoDB (`get_user_by_connection_id`)

Si no se puede resolver usuario, responde `401 Unauthorized`.

También se agregó validación para bloquear acceso a conversaciones que no involucren al usuario autenticado (`403 Forbidden`).

## 2) Backend: nueva ruta WebSocket para cargar conversaciones

Archivo nuevo: `backend/handlers/get_conversations.py`

Se añadió handler `getConversations` que:

- Resuelve el usuario autenticado con la misma lógica robusta.
- Lee conversaciones del usuario.
- Devuelve respuesta WebSocket con:

```json
{
  "action": "conversationsList",
  "data": {
    "conversations": [...],
    "total": n
  }
}
```

## 3) Backend: acceso a conversaciones en DynamoDB

Archivo modificado: `backend/shared/dynamodb_client.py`

Se agregó método:

- `get_user_conversations(user_id)`

Este método:

- Hace `scan` de tabla de conversaciones.
- Filtra por `participant1` o `participant2` igual a `user_id`.
- Ordena por `lastMessageTime` descendente.

## 4) Backend: exponer la nueva ruta en Serverless

Archivo modificado: `backend/serverless.yml`

Se registró la función:

- `getConversations` -> `handlers/get_conversations.lambda_handler`
- Ruta WebSocket: `getConversations`

## 5) Frontend: consumir conversaciones y manejar errores

Archivo modificado: `frontend/src/services/websocketService.js`

Se agregó:

- Método `getConversations()` que envía acción WebSocket `getConversations`.
- Manejo de acción entrante `conversationsList` para poblar store.
- Manejo de acción `error` para guardar mensaje de error en store (`setLastError`).

## 6) Frontend: store actualizado para persistencia de lista

Archivo modificado: `frontend/src/stores/chatStore.js`

Se agregó:

- Estado `lastError`.
- Acción `setLastError(error)`.
- Acción `setConversationsFromServer(serverConversations)` para transformar y cargar la lista desde backend.

## 7) Frontend: carga inicial en pantalla principal

Archivo modificado: `frontend/src/views/ChatView.vue`

Se agregó:

- En `onMounted`, si WebSocket está conectado, solicitar `getConversations()`.
- Mensaje visual compacto de error en sidebar cuando exista `lastError`.

## Resultado esperado después de estos cambios

- Al relogin con Usuario B, la app solicita conversaciones existentes.
- La conversación A-B aparece en la barra lateral.
- Al seleccionar conversación, `getMessages` ya no falla por formato de authorizer y el historial se recupera.

## Segunda investigación (caso: mensaje duplicado en remitente)

Con la evidencia adicional (Roberto ve 2 mensajes iguales al enviar 1), se identificaron riesgos reales de duplicación:

1. **Reconexiones automáticas no intencionales** del cliente WebSocket al hacer logout.
2. **Sin deduplicación en store** cuando llega el mismo `messageId` por dos rutas/eventos cercanos.
3. **Estados stale de conexión** en backend (usuario marcado online aunque ya desconectó).
4. **Posible doble entrega al mismo `connectionId`** (si por estado stale remitente/receptor apuntan al mismo socket).

### Correcciones aplicadas en esta segunda ronda

#### A) Cliente WebSocket (frontend)

Archivo: `frontend/src/services/websocketService.js`

- Se agregó control de reconexión intencional con flags:
   - `shouldReconnect`
   - `activeToken`
- Antes de abrir una nueva conexión, se cierra cualquier socket previo activo/connecting.
- En `onclose`, solo reconecta si `shouldReconnect` es `true`.
- En `disconnect()`, ahora se desactiva reconexión y se resetean intentos.

Objetivo: evitar conexiones fantasma y eventos duplicados por múltiples sockets vivos.

#### B) Deduplicación de mensajes (frontend)

Archivo: `frontend/src/stores/chatStore.js`

- `addMessage()` ahora ignora mensajes cuyo `messageId` ya existe.
- `addMessages()` ahora fusiona mensajes de historial sin repetir `messageId` existentes.

Objetivo: impedir que el mismo mensaje se renderice dos veces en UI.

#### C) Entrega protegida en backend (receive_message)

Archivo: `backend/handlers/receive_message.py`

- Si `receiver_connection_id == sender_connection_id`, se omite entrega al receptor para evitar duplicado de eco.
- Si falla envío al receptor, se marca receptor offline (`mark_user_offline`) para limpiar estado stale.

Objetivo: evitar duplicación por mapeo de conexión incorrecto y limpiar estado de presencia inválido.

#### D) Desconexión real de usuario en backend

Archivos:

- `backend/handlers/connect.py`
- `backend/shared/dynamodb_client.py`

Se implementó:

- En `$disconnect`, resolver usuario por `connectionId` y marcarlo offline.
- Nuevo método `mark_user_offline(user_id)` en cliente DynamoDB para:
   - `isOnline = false`
   - `connectionId = ''`
   - actualización de `lastSeen`

Objetivo: mantener coherencia de presencia y reducir envíos a sockets muertos.

## Validación técnica realizada

Se validaron errores de los archivos modificados usando diagnóstico del entorno y no se detectaron errores en:

- `backend/handlers/get_messages.py`
- `backend/handlers/get_conversations.py`
- `backend/shared/dynamodb_client.py`
- `backend/serverless.yml`
- `frontend/src/services/websocketService.js`
- `frontend/src/stores/chatStore.js`
- `frontend/src/views/ChatView.vue`

## Pasos para aplicar y verificar en tu entorno

1. Desplegar backend local para incluir nueva ruta:
   - `1. Backend: Deploy`
   - `2. Backend: Offline Start`
2. Levantar frontend:
   - `3. Frontend: Dev Server`
3. Flujo de prueba:
   - Login con Usuario A.
   - Crear chat con Usuario B y enviar mensaje.
   - Verificar que Usuario A ve **1 solo mensaje** por envío.
   - Logout.
   - Login con Usuario B.
   - Verificar que conversación aparezca y que el historial cargue.

## Nota operativa importante

En tu consola hubo un comando con orden invertido:

- Incorrecto: `npx sls start offline --stage local`
- Correcto: `npx sls offline start --stage local`

Ese detalle por sí solo puede impedir levantar backend y hacer parecer que falló la lógica de mensajería.

## Tercera corrección (consistencia remitente-token)

Con el análisis de tablas en caliente se observó un caso donde el mensaje persistido no coincidía con la expectativa del flujo manual de prueba (aparecía `senderId=roberto` cuando se esperaba `diegoPi`).

Para blindar este punto se aplicó:

- `backend/handlers/receive_message.py`
   - Se eliminó el fallback inseguro de remitente (`user_dev` / body trust sin auth).
   - Si no hay identidad autenticada en WebSocket, devuelve `401`.
   - Si llega `senderId` en payload y no coincide con el usuario autenticado, devuelve `403`.

- `frontend/src/services/websocketService.js`
   - Ahora el cliente envía `senderId` explícito desde `store.currentUser.userId` en `sendMessage`.

Con esto, cualquier desalineación entre sesión real y emisor declarado se detecta y bloquea de forma explícita en backend.

## Cuarta corrección (respuesta WebSocket real)

Se identificó que `getMessages` y `getConversations` estaban **retornando** JSON pero no lo enviaban por el canal WebSocket. En API Gateway WebSocket, el `return` del Lambda no llega al cliente; es necesario usar `ApiGatewayManagementApi`.

Se corrigió:

- `backend/handlers/get_messages.py`
   - Envío de `messagesHistory` usando `WebSocketClient.send_message(connectionId, ...)`
   - Retorno `200` simple luego del envío
   - En caso de error, se envía `action: error` al cliente

- `backend/handlers/get_conversations.py`
   - Envío de `conversationsList` usando `WebSocketClient`
   - Retorno `200` simple
   - En caso de error, se envía `action: error` al cliente

Esto garantiza que la lista de conversaciones y el historial lleguen realmente al frontend.

## Nota de diseño (mejora futura recomendada)

Actualmente `get_user_conversations` usa `scan`, suficiente para entorno local/MVP.
Para escalar en producción, conviene modelar un índice (GSI) por participante para consulta eficiente sin `scan`.