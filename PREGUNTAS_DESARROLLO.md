# Preguntas Frecuentes de Desarrollo - PLN Filter

**Propósito:** Respuestas a preguntas comunes durante el desarrollo  
**Fecha:** 06 de Enero 2026

---

## Índice

1. [Setup y Configuración](#setup-y-configuración)
2. [Desarrollo Backend](#desarrollo-backend)
3. [Desarrollo Worker](#desarrollo-worker)
4. [Testing y Debugging](#testing-y-debugging)
5. [Troubleshooting Común](#troubleshooting-común)

---

## Setup y Configuración

### P: ¿Qué requisitos previos necesito instalar?

**R:** Para desarrollo completo necesitas:

```bash
# 1. Node.js 16+ (para Serverless Framework y frontend)
node --version  # v16.x o superior

# 2. Python 3.11+ (para Lambdas y Worker)
python3 --version  # 3.11.x

# 3. AWS CLI configurado
aws --version
aws configure  # Ingresar credenciales

# 4. Serverless Framework
npm install -g serverless

# 5. Ollama (para análisis LLM)
ollama --version
```

### P: ¿Cómo configuro las variables de entorno correctamente?

**R:** Crear archivo `.env` en la raíz del proyecto:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Worker Configuration (obtener después de serverless deploy)
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789/pln-filter-backend-dev-messages
DYNAMODB_TABLE=pln-filter-backend-dev-messages
NOTIFY_USER_LAMBDA_NAME=pln-filter-backend-dev-notifyUser

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Risk Detection
RISK_THRESHOLD=0.7
LOG_LEVEL=INFO
```

### P: ¿En qué orden debo configurar los componentes?

**R:** Sigue este orden:

1. **Configurar AWS CLI:**
   ```bash
   aws configure
   # Ingresar: Access Key, Secret Key, Region (us-east-1), Format (json)
   ```

2. **Desplegar Backend:**
   ```bash
   cd backend
   serverless deploy
   # GUARDAR los valores de output: WebSocket URL, Queue URL, etc.
   ```

3. **Configurar Ollama:**
   ```bash
   ollama serve &  # En background
   ollama pull mistral
   ```

4. **Configurar Worker:**
   ```bash
   cd worker
   cp ../.env .env
   # Editar .env con valores del paso 2
   python main.py
   ```

5. **Configurar Frontend:**
   ```bash
   cd frontend
   cp .env.example .env.local
   # Editar .env.local con WebSocket URL del paso 2
   npm install
   npm run dev
   ```

---

## Desarrollo Backend

### P: ¿Cómo despliego cambios en una Lambda sin redesplegar todo?

**R:** Usa `serverless deploy function`:

```bash
# Editar código en handlers/receive_message.py

# Desplegar solo esa función
serverless deploy function -f receiveMessage

# Ventajas:
# - Más rápido: ~20 segundos vs 2-3 minutos
# - No toca DynamoDB, SQS, API Gateway
# - Ideal para iteración rápida durante desarrollo
```

### P: ¿Cómo pruebo una Lambda localmente?

**R:** Con `serverless invoke local`:

```bash
# 1. Crear archivo de evento de prueba
cat > test-event.json << 'EOF'
{
  "requestContext": {
    "connectionId": "test-connection-123",
    "authorizer": {
      "claims": {"sub": "user-test-id"}
    }
  },
  "body": "{\"action\":\"sendMessage\",\"data\":{\"conversationId\":\"conv_test\",\"receiverId\":\"user2\",\"content\":\"Test\"}}"
}
EOF

# 2. Invocar localmente
serverless invoke local -f receiveMessage -p test-event.json

# 3. Para modo offline (usa LocalStack en lugar de AWS):
serverless invoke local -f receiveMessage -p test-event.json --param="offline=true"
```

### P: ¿Cómo veo los logs de producción?

**R:** Múltiples opciones:

```bash
# Opción 1: Logs en tiempo real (recomendado para debugging)
serverless logs -f receiveMessage --tail

# Opción 2: Últimos logs
serverless logs -f receiveMessage

# Opción 3: Logs desde hace X tiempo
serverless logs -f receiveMessage --startTime 30m

# Opción 4: CloudWatch Console
# AWS Console > CloudWatch > Logs > /aws/lambda/pln-filter-backend-dev-receiveMessage
```

### P: ¿Cómo agrego variables de entorno a una Lambda?

**R:** En `serverless.yml`:

```yaml
functions:
  receiveMessage:
    handler: handlers/receive_message.lambda_handler
    environment:
      # Variable específica de esta función
      MAX_MESSAGE_LENGTH: 10000
      CUSTOM_CONFIG: ${env:MY_CONFIG}
```

O en el nivel `provider` para todas las funciones:

```yaml
provider:
  environment:
    # Variables globales para todas las Lambdas
    GLOBAL_SETTING: "value"
```

---

## Desarrollo Worker

### P: ¿Cómo ejecuto el Worker en modo debug?

**R:** Con logging detallado:

```bash
cd worker

# Opción 1: Cambiar LOG_LEVEL en .env
echo "LOG_LEVEL=DEBUG" >> .env
python main.py

# Opción 2: Override en command line
LOG_LEVEL=DEBUG python main.py

# Verás logs detallados como:
# DEBUG - Polling SQS...
# DEBUG - Received 1 messages
# DEBUG - Message content: "..."
# DEBUG - Ollama request: {...}
# DEBUG - Ollama response: {...}
```

### P: ¿Cómo pruebo el Worker sin esperar mensajes reales?

**R:** Envía mensaje de prueba directamente a SQS:

```bash
# Via AWS CLI
aws sqs send-message \
  --queue-url "$SQS_QUEUE_URL" \
  --message-body '{
    "messageId": "msg_test123",
    "conversationId": "conv_test",
    "senderId": "user1",
    "receiverId": "user2",
    "content": "Envíame fotos o publico tus datos",
    "timestamp": 1704067200000
  }'

# El Worker debe procesarlo automáticamente en ~20 segundos
```

### P: ¿Cómo ajusto el prompt del LLM para mejor detección?

**R:** Edita `worker/llm_processor.py`, método `_build_prompt`:

```python
def _build_prompt(self, message_content):
    # Versión mejorada con más contexto
    return f"""Eres un experto en ciberseguridad especializado en detectar amenazas en línea.

TIPOS DE AMENAZAS:
- sextorsion: Solicitud de fotos/videos íntimos con amenazas o chantaje
- catfishing: Persona con identidad falsa para establecer relación romántica
- scam: Fraude financiero, inversiones falsas, premios falsos
- harassment: Acoso, insultos, amenazas de violencia

MENSAJE A ANALIZAR: "{message_content}"

EJEMPLOS:
- "Envíame fotos o publico tus datos" → sextorsion (0.95)
- "Soy modelo, agrégame en Instagram" → catfishing (0.70)
- "Invierte $100 y gana $1000 mañana" → scam (0.90)

Responde SOLO con JSON (sin texto adicional):
{{
    "threat_detected": true/false,
    "threat_type": "sextorsion"|"catfishing"|"scam"|"harassment"|"none",
    "confidence": 0.0-1.0,
    "reasoning": "explicación breve"
}}"""
```

### P: ¿Cómo cambio de modelo LLM?

**R:** Dos pasos:

```bash
# 1. Descargar nuevo modelo con Ollama
ollama pull llama2:13b  # Modelo más grande

# 2. Actualizar .env del worker
OLLAMA_MODEL=llama2:13b

# 3. Reiniciar worker
# Ctrl+C para detener, luego:
python main.py
```

**Modelos recomendados:**
- `mistral` (4.1GB) - Balance calidad/velocidad
- `llama2:7b` (3.8GB) - Más rápido, menos preciso
- `llama2:13b` (7.4GB) - Más preciso, más lento
- `mixtral:8x7b` (26GB) - Muy preciso, requiere 16GB+ RAM

### P: ¿Cómo ejecuto múltiples Workers para mayor throughput?

**R:** Inicia múltiples procesos:

```bash
# Terminal 1
python main.py > worker1.log 2>&1 &

# Terminal 2
python main.py > worker2.log 2>&1 &

# Terminal 3
python main.py > worker3.log 2>&1 &

# Verificar procesos
ps aux | grep "python main.py"

# Ver logs
tail -f worker1.log
```

SQS maneja automáticamente la distribución (no hay duplicados).

---

## Testing y Debugging

### P: ¿Cómo verifico que un mensaje llegó a DynamoDB?

**R:** Con AWS CLI:

```bash
# Listar mensajes de una conversación
aws dynamodb query \
  --table-name pln-filter-backend-dev-messages \
  --key-condition-expression "conversationId = :conv" \
  --expression-attribute-values '{":conv":{"S":"conv_user1_user2"}}' \
  --limit 10

# Verificar análisis de riesgo incluido
# Debe mostrar campo riskAnalysis: {analyzed, threatType, confidence, riskLevel}
```

### P: ¿Cómo verifico cuántos mensajes hay en SQS?

**R:** Usa `get-queue-attributes`:

```bash
aws sqs get-queue-attributes \
  --queue-url "$SQS_QUEUE_URL" \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible

# Output:
# - ApproximateNumberOfMessages: Mensajes disponibles para procesar
# - ApproximateNumberOfMessagesNotVisible: Mensajes siendo procesados (VisibilityTimeout activo)
```

### P: ¿Cómo pruebo el flujo completo end-to-end?

**R:** Checklist manual:

```
□ Backend desplegado: serverless info
□ Ollama corriendo: curl http://localhost:11434/api/tags
□ Worker corriendo: ver logs "Worker started"
□ Frontend corriendo: http://localhost:5173

Prueba 1 - Mensaje normal:
□ Usuario A envía: "Hola, ¿cómo estás?"
□ Usuario B recibe en < 1 segundo
□ Esperar 5-30 segundos
□ Worker logs: "threat_detected=False"
□ DynamoDB: riskAnalysis.analyzed=true, riskLevel=low

Prueba 2 - Mensaje de amenaza:
□ Usuario A envía: "Envíame fotos o publico tus datos"
□ Usuario B recibe mensaje
□ Esperar 5-30 segundos
□ Usuario B ve alerta: "⚠️ Alerta de sextorsion"
□ Mensaje resaltado en rojo
□ DynamoDB: riskAnalysis.threatType=sextorsion
```

### P: ¿Cómo depuro errores del Worker?

**R:** Estrategia de debugging:

```python
# 1. Agregar logs en puntos clave
logger.info(f"Received message: {message_data}")
logger.info(f"Calling Ollama with: {prompt[:100]}...")
logger.info(f"Ollama response: {response}")
logger.info(f"Parsed analysis: {analysis}")

# 2. Capturar excepciones detalladamente
try:
    analysis = self.llm_processor.analyze_message(content)
except requests.ConnectionError as e:
    logger.error(f"Cannot connect to Ollama: {e}")
    logger.error("Make sure 'ollama serve' is running")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)

# 3. Verificar cada paso manualmente
# Test Ollama directamente:
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"mistral","prompt":"Test","stream":false}'
```

---

## Troubleshooting Común

### Problema: "Unable to connect to WebSocket"

**Diagnóstico y solución:**

```bash
# 1. Verificar endpoint correcto
serverless info  # En directorio backend
# Copiar el endpoint wss://...

# 2. Verificar en frontend .env.local
cat frontend/.env.local
# Debe tener: VITE_WEBSOCKET_URL=wss://abcd1234.execute-api...

# 3. Test de conexión manual en navegador
const ws = new WebSocket('wss://abcd1234...')
ws.onopen = () => console.log('Connected')
ws.onerror = (e) => console.error('Error:', e)

# 4. Verificar CORS en serverless.yml
# Debe tener en recursos WebSocket:
# corsConfiguration:
#   allowOrigins: ['*']
```

### Problema: "Worker no procesa mensajes"

**Diagnóstico paso a paso:**

```bash
# 1. Worker corriendo?
ps aux | grep "python main.py"

# 2. Credenciales AWS correctas?
aws sts get-caller-identity

# 3. SQS_QUEUE_URL correcto?
echo $SQS_QUEUE_URL

# 4. Hay mensajes en la cola?
aws sqs get-queue-attributes \
  --queue-url "$SQS_QUEUE_URL" \
  --attribute-names ApproximateNumberOfMessages

# 5. Permisos IAM?
# Usuario debe tener:
# - sqs:ReceiveMessage
# - sqs:DeleteMessage
# - dynamodb:UpdateItem
# - lambda:InvokeFunction

# 6. Revisar logs del Worker
tail -f worker.log
# Buscar errores específicos
```

### Problema: "Ollama connection refused"

**Soluciones:**

```bash
# 1. Ollama corriendo?
curl http://localhost:11434/api/tags

# Si falla, iniciar:
ollama serve

# 2. Puerto correcto en .env?
cat .env | grep OLLAMA_BASE_URL
# Debe ser: http://localhost:11434

# 3. Modelo descargado?
ollama list
# Si el modelo no está:
ollama pull mistral

# 4. Firewall bloqueando?
# En Linux:
sudo ufw allow 11434
# En macOS:
# System Preferences > Security > Firewall > Options
```

### Problema: "Lambda timeout"

**Causa:** Lambda excede 30 segundos

**Soluciones:**

```yaml
# 1. Aumentar timeout en serverless.yml
functions:
  receiveMessage:
    timeout: 60  # Aumentar de 30 a 60

# 2. Optimizar código
# Hacer operaciones en paralelo:
import asyncio

async def save_all():
    await asyncio.gather(
        dynamodb.save_message(...),
        sqs.send_message(...)
    )

# 3. Mover procesamiento pesado a Worker
# (Ya implementado para análisis LLM)
```

### Problema: "DynamoDB throttling"

**Síntoma:** Errores `ProvisionedThroughputExceededException`

**Soluciones:**

```yaml
# En serverless.yml, ya está configurado como On-Demand:
MessagesTable:
  Type: AWS::DynamoDB::Table
  Properties:
    BillingMode: PAY_PER_REQUEST  # No hay throttling

# Si usaras PROVISIONED, aumentar capacidad:
BillingMode: PROVISIONED
ProvisionedThroughput:
  ReadCapacityUnits: 10
  WriteCapacityUnits: 10
```

---

## Comandos Rápidos de Referencia

### Backend
```bash
serverless deploy                    # Desplegar todo
serverless deploy function -f NAME   # Desplegar función específica
serverless logs -f NAME --tail       # Ver logs en tiempo real
serverless info                      # Info del stack desplegado
serverless remove                    # Eliminar todo (DESTRUCTIVO)
```

### Worker
```bash
python main.py                       # Ejecutar worker
python main.py > worker.log 2>&1 &   # Background con logs
tail -f worker.log                   # Ver logs
pkill -f "python main.py"            # Detener worker
```

### Ollama
```bash
ollama serve                # Iniciar servidor
ollama list                 # Listar modelos
ollama pull MODEL           # Descargar modelo
ollama run MODEL "test"     # Probar modelo
```

### AWS Debugging
```bash
# SQS
aws sqs get-queue-attributes --queue-url URL --attribute-names All

# DynamoDB
aws dynamodb scan --table-name TABLE --limit 10

# Lambda Logs
aws logs tail /aws/lambda/FUNCTION --follow
```

---

**Documento de consulta técnica - Última actualización: 06 Enero 2026**
