# Análisis Técnico del Código - PLN Filter

**Fecha:** 06 de Enero 2026  
**Propósito:** Documento de consulta técnica para desarrollo sin ejecutar cambios

## Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Análisis de Componentes](#análisis-de-componentes)
4. [Flujo de Datos Detallado](#flujo-de-datos-detallado)
5. [Preguntas Frecuentes Técnicas](#preguntas-frecuentes-técnicas)
6. [Decisiones de Diseño](#decisiones-de-diseño)
7. [Consideraciones de Seguridad](#consideraciones-de-seguridad)
8. [Escalabilidad y Rendimiento](#escalabilidad-y-rendimiento)

---

## Resumen Ejecutivo

### ¿Qué es este sistema?

PLN Filter es un sistema de mensajería instantánea con detección automática de amenazas (catfishing y sextorsión) utilizando procesamiento de lenguaje natural (PLN). El sistema combina:

- **Cloud Services (AWS):** Backend serverless para alta disponibilidad y bajo costo
- **Local Processing:** Modelo LLM (Ollama) ejecutado localmente para análisis de contenido
- **Real-time Communication:** WebSockets para chat instantáneo

### Tecnologías Principales

| Componente | Tecnología | Versión/Especificación |
|------------|-----------|----------------------|
| Frontend | Vue 3 + Vite | Modern SPA |
| Backend | AWS Lambda + Python | 3.11 |
| Database | DynamoDB | NoSQL serverless |
| Message Queue | SQS | Fully managed |
| Communication | API Gateway WebSocket | Real-time bidirectional |
| LLM | Ollama (Mistral) | Local inference |
| IaC | Serverless Framework | v4 |

### Características Clave

1. **Arquitectura Híbrida:** Combina servicios cloud con procesamiento local
2. **Serverless:** Sin gestión de servidores, auto-escalable
3. **Asíncrono:** Análisis de mensajes desacoplado del flujo principal
4. **Tiempo Real:** Mensajería y alertas instantáneas vía WebSocket
5. **Bajo Costo:** Diseñado para operar en capa gratuita de AWS

---

## Arquitectura del Sistema

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS CLOUD                                │
│                                                                   │
│  ┌──────────────┐         ┌─────────────────────────────────┐  │
│  │   Amplify    │         │    API Gateway WebSocket         │  │
│  │   Hosting    │◄────────┤  wss://xxxxx.amazonaws.com       │  │
│  │  (Frontend)  │         └──────────┬──────────────┬────────┘  │
│  └──────────────┘                    │              │            │
│                                      │              │            │
│                         ┌────────────▼───┐    ┌────▼──────────┐ │
│                         │  Lambda        │    │  Lambda       │ │
│                         │  receiveMessage│    │  getMessages  │ │
│                         └────┬───────┬───┘    └───────────────┘ │
│                              │       │                           │
│                              │       │                           │
│                    ┌─────────▼───┐   └──────────┐               │
│                    │  DynamoDB   │              │               │
│                    │  Messages   │              │               │
│                    │  Users      │              │               │
│                    │  Convs      │              │               │
│                    └─────────────┘              │               │
│                                                 │               │
│                                    ┌────────────▼─────┐         │
│                                    │      SQS         │         │
│                                    │  Message Queue   │         │
│                                    └────────┬─────────┘         │
│                                             │                   │
└─────────────────────────────────────────────┼───────────────────┘
                                              │ (Poll)
                                              │
                      ┌───────────────────────▼──────────────────┐
                      │      LOCAL ENVIRONMENT                   │
                      │                                           │
                      │  ┌──────────────────────────────────┐   │
                      │  │  Worker Python                    │   │
                      │  │  - SQS Listener                   │   │
                      │  │  - LLM Processor                  │   │
                      │  │  - AWS Notifier                   │   │
                      │  └───────────┬──────────────────────┘   │
                      │              │                            │
                      │  ┌───────────▼──────────────────────┐   │
                      │  │  Ollama Server                    │   │
                      │  │  Model: Mistral (0.5-8B params)   │   │
                      │  │  Port: 11434                      │   │
                      │  └───────────────────────────────────┘   │
                      │                                           │
                      └───────────────────────────────────────────┘
```

### Flujo de Comunicación

**Envío de Mensaje:**
```
Usuario → WebSocket → Lambda:receiveMessage → [DynamoDB + SQS] → WebSocket → Destinatario
                                               ↓
                                           Worker Local → Ollama → Análisis
                                               ↓ (si riesgo)
                                           Lambda:notifyUser → WebSocket → Usuario
```

---

## Análisis de Componentes

### 1. Backend - AWS Lambda Functions

#### 1.1 Lambda: receiveMessage

**Ubicación:** `/backend/handlers/receive_message.py`

**Responsabilidades:**
1. Recibir mensajes del cliente vía WebSocket
2. Validar datos de entrada
3. Persistir mensaje en DynamoDB
4. Encolar mensaje en SQS para análisis asíncrono
5. Entregar mensaje al destinatario en tiempo real

**Código Crítico:**

```python
def lambda_handler(event, context):
    # 1. Extraer información de contexto
    connection_id = event['requestContext']['connectionId']
    sender_id = event['requestContext']['authorizer']['claims']['sub']
    
    # 2. Validación
    body = json.loads(event.get('body', '{}'))
    action = body.get('action')
    if action != 'sendMessage':
        return {'statusCode': 400}
    
    # 3. Generar IDs únicos
    message_id = f"msg_{uuid.uuid4().hex[:12]}"
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    
    # 4. Guardar en DynamoDB (persistencia inmediata)
    dynamodb.save_message(conversation_id, timestamp, message_data)
    
    # 5. Encolar en SQS (análisis asíncrono)
    sqs.send_message(sqs_message)
    
    # 6. Enviar al destinatario vía WebSocket (entrega instantánea)
    websocket.send_message(receiver_connection_id, websocket_message)
```

**Preguntas Frecuentes:**

**P: ¿Por qué se guarda en DynamoDB antes de encolar en SQS?**  
**R:** Para garantizar que ningún mensaje se pierda. Si SQS falla, el mensaje ya está persistido. Esto implementa el patrón "write-through" asegurando durabilidad.

**P: ¿Qué pasa si el destinatario no está conectado?**  
**R:** El mensaje se guarda en DynamoDB de todas formas. Cuando el destinatario se conecte y solicite el historial (vía `getMessages`), recibirá todos los mensajes pendientes.

**P: ¿Por qué usar WebSocket en lugar de HTTP polling?**  
**R:** WebSocket mantiene una conexión persistente bidireccional, eliminando la latencia de establecer nuevas conexiones HTTP. Esto permite:
- Entrega instantánea de mensajes (< 100ms)
- Menor consumo de recursos
- Mejor experiencia de usuario (similar a WhatsApp)

**P: ¿Cómo se garantiza el orden de los mensajes?**  
**R:** DynamoDB usa `timestamp` como Sort Key en la clave compuesta `(conversationId, timestamp)`. Las consultas automáticamente retornan mensajes ordenados cronológicamente.

#### 1.2 Lambda: notifyUser

**Ubicación:** `/backend/handlers/notify_user.py`

**Responsabilidades:**
1. Recibir alertas del Worker local
2. Obtener connectionId del usuario
3. Enviar alerta por WebSocket

**Código Crítico:**

```python
def lambda_handler(event, context):
    # 1. Parsear evento
    body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
    
    # 2. Verificar que usuario está online
    user = dynamodb.get_user(user_id)
    if not user or not user.get('isOnline'):
        return {'statusCode': 404}
    
    # 3. Construir y enviar alerta
    alert_message = {
        'action': 'riskAlert',
        'data': {
            'messageId': message_id,
            'threatType': threat_type,
            'confidence': confidence,
            'riskLevel': risk_level,
            'message': f'Alerta: Se detectó posible intento de {threat_type}'
        }
    }
    
    websocket.send_message(connection_id, alert_message)
```

**Preguntas Frecuentes:**

**P: ¿Por qué solo se notifica si el usuario está online?**  
**R:** Las alertas WebSocket requieren una conexión activa. Si el usuario está offline, verá la alerta cuando consulte el historial de mensajes (el campo `riskAnalysis` estará presente).

**P: ¿Puede un usuario recibir múltiples alertas para el mismo mensaje?**  
**R:** No debería, porque el Worker elimina el mensaje de SQS solo después de completar todo el procesamiento, incluyendo la notificación.

### 2. Worker Local - Procesamiento LLM

#### 2.1 Main Worker Loop

**Ubicación:** `/worker/main.py`

**Clase PLNFilterWorker:**

```python
class PLNFilterWorker:
    def run(self):
        """Loop principal infinito"""
        while self.running:
            # 1. Long-polling: espera hasta 20 segundos por mensajes
            messages = self.sqs_listener.receive_messages(
                max_messages=1, 
                wait_time=20
            )
            
            if not messages:
                continue
            
            for message in messages:
                # 2. Parsear
                parsed = self.sqs_listener.parse_message(message)
                
                # 3. Procesar con LLM
                if self.process_message(parsed['data']):
                    # 4. Eliminar SOLO si procesamiento exitoso
                    self.sqs_listener.delete_message(parsed['receipt_handle'])
                else:
                    # El mensaje volverá a la cola después del VisibilityTimeout
                    logger.warning("Failed to process, will retry")
```

**Preguntas Frecuentes:**

**P: ¿Por qué usar long-polling con 20 segundos?**  
**R:** Long-polling reduce costos y latencia:
- Sin long-polling: El Worker hace peticiones cada segundo aunque no haya mensajes
- Con long-polling: SQS mantiene la conexión abierta hasta 20 segundos, retornando inmediatamente si llega un mensaje

**P: ¿Qué pasa si el Worker se detiene mientras procesa un mensaje?**  
**R:** El mensaje volverá automáticamente a la cola después de 5 minutos (VisibilityTimeout), permitiendo que otro Worker lo reprocese.

#### 2.2 LLM Processor

**Ubicación:** `/worker/llm_processor.py`

**Análisis con Ollama:**

```python
class LLMProcessor:
    def analyze_message(self, message_content):
        """Analiza mensaje con Ollama"""
        # 1. Construir prompt especializado
        prompt = self._build_prompt(message_content)
        
        # 2. Llamar a Ollama API
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,  # "mistral"
                "prompt": prompt,
                "stream": False  # Esperar respuesta completa
            },
            timeout=30
        )
        
        # 3. Parsear respuesta JSON
        analysis = self._parse_response(result.get('response', ''))
        
        return analysis
```

**Prompt Engineering:**

```python
def _build_prompt(self, message_content):
    return f"""Analiza el siguiente mensaje de chat para detectar amenazas de seguridad.

Mensaje: "{message_content}"

Responde en JSON con el siguiente formato:
{{
    "threat_detected": true/false,
    "threat_type": "sextorsion" | "catfishing" | "scam" | "harassment" | "none",
    "confidence": 0.0-1.0,
    "reasoning": "breve explicación"
}}

Solo responde con el JSON, sin explicaciones adicionales."""
```

**Preguntas Frecuentes:**

**P: ¿Por qué Ollama en lugar de OpenAI o Claude?**  
**R:** Requisito del proyecto: reducir costos operativos. Ollama permite:
1. Ejecución 100% local (sin costos de API)
2. Control total sobre el modelo y datos
3. Sin límites de rate limiting
4. Privacidad: los mensajes nunca salen del entorno local

**P: ¿Qué modelo se usa por defecto?**  
**R:** Mistral (configurado en `worker/config.py`). Se pueden usar otros:
- `llama2:7b` (más rápido, menos preciso)
- `mixtral:8x7b` (más lento, más preciso)
- Modelos custom fine-tuned

**P: ¿Cómo se maneja si Ollama está offline?**  
**R:** El código captura excepciones de conexión y retorna un análisis por defecto (sin amenaza). El mensaje NO se elimina de SQS, por lo que se reintentará cuando Ollama vuelva.

**P: ¿Qué es el RISK_THRESHOLD?**  
**R:** Configurado en `config.py` como 0.7 (70%). Solo se marcan como amenazas los mensajes donde el LLM tiene ≥70% de confianza. Esto reduce falsos positivos.

---

## Flujo de Datos Detallado

### Escenario 1: Usuario Envía Mensaje Normal

**Paso a Paso:**

1. **Usuario A escribe mensaje en el frontend**
   ```javascript
   websocket.send(JSON.stringify({
     action: 'sendMessage',
     data: {
       conversationId: 'conv_userA_userB',
       receiverId: 'userB',
       content: 'Hola, ¿cómo estás?'
     }
   }))
   ```

2. **Lambda receiveMessage procesa:**
   - Genera messageId único: `msg_a1b2c3d4e5f6`
   - Timestamp: `1704067200000`
   - Guarda en DynamoDB con `riskAnalysis.analyzed = false`
   - Encola en SQS
   - Envía a Usuario B vía WebSocket

3. **Usuario B recibe el mensaje instantáneamente (< 1 segundo)**

4. **Worker Local procesa (2-25 segundos después):**
   - Recibe de SQS
   - Llama Ollama para análisis
   - Ollama responde: `{threat_detected: false, confidence: 0.05}`
   - Actualiza DynamoDB: `riskAnalysis.analyzed = true, riskLevel = 'low'`
   - NO invoca notifyUser (no hay amenaza)
   - Elimina mensaje de SQS

**Tiempos Estimados:**
- Envío → Recepción: **< 1 segundo**
- Análisis completo: **2-25 segundos**

### Escenario 2: Mensaje con Amenaza Detectada

**Diferencia en paso 4:**

4. **Worker Local detecta amenaza:**
   - Ollama responde: `{threat_detected: true, threat_type: 'sextorsion', confidence: 0.95}`
   - Actualiza DynamoDB con `riskLevel = 'high'`
   - **Invoca Lambda notifyUser**

5. **Lambda notifyUser:**
   - Obtiene connectionId de Usuario B
   - Envía alerta por WebSocket:
   ```json
   {
     "action": "riskAlert",
     "data": {
       "threatType": "sextorsion",
       "confidence": 0.95,
       "riskLevel": "high",
       "message": "Alerta: Se detectó posible intento de sextorsion"
     }
   }
   ```

6. **Usuario B ve alerta en UI:**
   - Mensaje se resalta en rojo
   - Aparece modal de advertencia
   - Se recomienda precaución

---

## Preguntas Frecuentes Técnicas

### Arquitectura General

**P: ¿Por qué arquitectura serverless en lugar de servidores tradicionales?**  
**R:** Ventajas para este proyecto:
1. **Costo:** Pago por uso real, no por servidores 24/7
2. **Escalabilidad:** Auto-escalado automático
3. **Mantenimiento:** Cero gestión de servidores
4. **Capa Gratuita:** 1M invocaciones Lambda/mes gratis

Para un MVP con 2 usuarios, el costo es $0/mes.

**P: ¿Qué pasa si el Worker local está offline?**  
**R:** El sistema sigue funcionando:
- Mensajes se envían y reciben normalmente
- Mensajes se acumulan en SQS (hasta 14 días de retención)
- Cuando el Worker vuelva, procesa todos los pendientes
- No se pierden datos

**P: ¿Se puede ejecutar el Worker en la nube?**  
**R:** Sí, pero con costos:
- EC2 con GPU: ~$0.90/hora (g4dn.xlarge)
- SageMaker: ~$0.14/hora + costos de inferencia

Para producción, se podría usar EC2 Spot Instances (70% descuento).

### DynamoDB

**P: ¿Por qué NoSQL (DynamoDB) en lugar de SQL (RDS)?**  
**R:** Ventajas para este caso de uso:
1. **Escalabilidad:** Auto-escalado horizontal
2. **Latencia:** < 10ms en operaciones
3. **Costo:** Capa gratuita de 25 GB
4. **Serverless:** No requiere gestión de servidores
5. **Schema flexible:** Fácil agregar campos

**P: ¿Cómo se modelan las conversaciones?**  
**R:** Clave compuesta:
- **Partition Key:** `conversationId = 'conv_userA_userB'`
- **Sort Key:** `timestamp = 1704067200000`

Todos los mensajes de una conversación están en la misma partición, ordenados automáticamente.

**P: ¿Cuánto cuesta DynamoDB para 2 usuarios?**  
**R:** Con 100 mensajes/día:
```
Escrituras: 6,000/mes
Lecturas: ~10,000/mes

Capa gratuita: 25 GB + 200M reads + 25M writes
Costo: $0.00 (dentro de capa gratuita)
```

### SQS

**P: ¿Por qué usar SQS en lugar de procesar directamente?**  
**R:** Desacoplamiento asíncrono:
1. **Latencia:** Análisis LLM toma 2-25 segundos. Usuarios no deben esperar
2. **Escalabilidad:** Si hay burst de mensajes, la cola los bufferea
3. **Resiliencia:** Si Worker falla, mensajes permanecen seguros
4. **Reintentos:** Procesamiento automático hasta que tenga éxito

**P: ¿Qué es el VisibilityTimeout?**  
**R:** Configurado como 300 segundos (5 minutos). Cuando un Worker recibe un mensaje, este se vuelve invisible para otros consumidores durante 5 minutos. Si el Worker no lo elimina, vuelve a estar disponible.

**P: ¿Cuántos mensajes puede tener la cola?**  
**R:** Prácticamente ilimitado. SQS soporta millones de mensajes con 14 días de retención máxima.

---

## Decisiones de Diseño

### 1. ¿Por qué usar WebSocket en lugar de HTTP REST?

**Decisión:** API Gateway WebSocket  
**Alternativa:** HTTP REST con polling

**Razones:**
- **Latencia:** WebSocket permite entrega instantánea (< 100ms)
- **Eficiencia:** Una conexión persistente vs múltiples HTTP requests
- **Bidireccional:** El servidor puede enviar alertas sin que el cliente pregunte
- **Experiencia:** Similar a apps de mensajería modernas (WhatsApp, Telegram)

**Trade-off:** WebSocket es más complejo de implementar y debuggear que REST.

### 2. ¿Por qué separar el análisis LLM del flujo principal?

**Decisión:** Cola SQS + Worker asíncrono  
**Alternativa:** Lambda procesa con LLM directamente

**Razones:**
- **Latencia:** Los usuarios ven mensajes inmediatamente (< 1s), no esperan 25s
- **Costo:** Ollama local gratis vs SageMaker/Bedrock ($0.02-0.10/1K tokens)
- **Flexibilidad:** Cambiar modelo sin tocar infraestructura AWS
- **Hardware:** Aprovechar GPU local existente

**Trade-off:** Requiere computadora local siempre encendida.

### 3. ¿Por qué guardar en DynamoDB antes de encolar?

**Decisión:** DynamoDB write → SQS enqueue  
**Alternativa:** SQS enqueue → DynamoDB write después

**Razones:**
- **Durabilidad:** Si SQS falla, el mensaje ya está guardado
- **Consistencia:** El destinatario puede ver mensajes inmediatamente
- **Historial:** Aunque SQS pierda un mensaje, está en DynamoDB

**Trade-off:** Dos operaciones en lugar de una (aumenta latencia ~20ms).

### 4. ¿Por qué serverless en lugar de contenedores (ECS/EKS)?

**Decisión:** AWS Lambda serverless  
**Alternativa:** Docker en ECS/EKS

**Razones:**
- **Costo:** $0 para MVP (capa gratuita) vs $20-50/mes mínimo para ECS
- **Escalabilidad:** Automática de 0 a miles de usuarios
- **Mantenimiento:** Cero gestión de servidores/clusters
- **Desarrollo:** Serverless Framework simplifica despliegue

**Trade-off:** Lambda tiene límites (15 min timeout, 10 GB RAM).

---

## Consideraciones de Seguridad

### 1. Autenticación y Autorización

**Actual (MVP):**
- Autenticador simple en `handlers/auth.py`
- Valida tokens JWT de Cognito
- `claims.sub` identifica al usuario

**Mejoras Recomendadas:**
1. Implementar Cognito User Pool completo
2. Validar refresh tokens
3. Agregar MFA (Multi-Factor Authentication)
4. Rate limiting por usuario

### 2. Validación de Entrada

**Actual:**
```python
if not all([receiver_id, content, conversation_id]):
    return {'statusCode': 400, 'body': json.dumps({'error': 'Missing fields'})}
```

**Mejoras Recomendadas:**
1. Validar longitud de mensaje (max 10KB)
2. Sanitizar HTML/scripts en contenido
3. Validar formato de IDs
4. Prevenir SQL/NoSQL injection

### 3. Datos Sensibles

**Actual:**
- Mensajes en texto plano en DynamoDB
- Sin encriptación adicional

**Mejoras Recomendadas:**
1. Encriptación en reposo (DynamoDB encryption at rest)
2. Encriptación en tránsito (TLS 1.2+ - ya implementado)
3. Encriptación end-to-end entre usuarios
4. KMS para gestión de llaves

### 4. Control de Acceso

**Actual:**
- Lambda tiene permisos amplios via IAM Role

**Mejoras Recomendadas:**
1. Principio de mínimo privilegio
2. Separar roles por Lambda
3. VPC para lambdas que acceden a recursos privados
4. WAF (Web Application Firewall) en API Gateway

---

## Escalabilidad y Rendimiento

### Límites Actuales

| Componente | Límite MVP | Límite AWS | Cuello de Botella |
|-----------|-----------|------------|-------------------|
| Lambda | 10 invocaciones/seg | 1000/seg | Threshold bajo |
| DynamoDB | 25 RCU/WCU | Ilimitado | Capa gratuita |
| SQS | 100 msg/seg | 3000/seg | Worker local |
| WebSocket | 500 conexiones | 500K | API Gateway |
| Ollama Local | 1 mensaje/5seg | Variable | GPU local |

### Estrategias de Escalamiento

**Horizontal (más instancias):**
1. **Worker:** Ejecutar múltiples Workers en paralelo
2. **Lambda:** Auto-escalado automático (ya implementado)
3. **DynamoDB:** Aumentar RCU/WCU o usar On-Demand

**Vertical (más recursos):**
1. **Worker:** GPU más potente (RTX 3090, A100)
2. **Lambda:** Aumentar memoria (aumenta CPU proporcionalmente)
3. **Ollama:** Modelo más pequeño (llama2:7b vs mixtral:8x7b)

**Optimizaciones:**
1. **Batch processing:** Worker procesa 10 mensajes a la vez
2. **Caching:** Resultados de análisis comunes
3. **CDN:** CloudFront para assets estáticos
4. **Índices:** GSI en DynamoDB para queries frecuentes

### Benchmark Estimado

**10 usuarios activos:**
- 500 mensajes/día = 15,000/mes
- Análisis: ~2 min/mensaje
- Worker: Procesa en ~5 horas/día
- Costo: $0 (capa gratuita)

**100 usuarios activos:**
- 5,000 mensajes/día = 150,000/mes
- Análisis: Requiere 3-4 Workers en paralelo
- Costo: ~$5-10/mes (DynamoDB + Lambda fuera de capa gratuita)

**1000 usuarios activos:**
- 50,000 mensajes/día = 1.5M/mes
- Análisis: Requiere 30-40 Workers o migrar a EC2 GPU
- Costo: ~$50-100/mes + $200-400/mes GPU

---

## Conclusión

Este sistema implementa una arquitectura híbrida cloud-local que balancea:
- **Costo:** $0 para MVP, escalable con crecimiento
- **Performance:** Mensajería instantánea (< 1s) con análisis asíncrono
- **Privacidad:** Procesamiento LLM 100% local
- **Escalabilidad:** Serverless auto-escalable + Workers horizontales

**Fortalezas:**
✅ Bajo costo operativo  
✅ Alta disponibilidad (AWS 99.99%)  
✅ Fácil de mantener (serverless)  
✅ Análisis con LLM local (privado y flexible)

**Áreas de Mejora:**
⚠️ Seguridad (agregar encriptación E2E)  
⚠️ Autenticación (implementar Cognito completo)  
⚠️ Monitoreo (agregar CloudWatch Alarms)  
⚠️ Testing (cobertura < 20%)

---

**Documento generado para consulta técnica - No requiere ejecución de cambios**
