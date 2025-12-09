# Guía de Despliegue - PLN Filter

Guía paso a paso para desplegar PLN Filter en AWS usando Serverless Framework.

## Requisitos

- Cuenta AWS activa
- AWS CLI configurado
- Node.js 16+
- Python 3.11+
- Serverless Framework instalado

## Paso 1: Preparar Credenciales AWS

```bash
# Instalar AWS CLI
pip install awscli

# Configurar credenciales
aws configure

# Ingresa:
# AWS Access Key ID: <tu_access_key>
# AWS Secret Access Key: <tu_secret_key>
# Default region: us-east-1
# Default output format: json
```

## Paso 2: Instalar Serverless Framework

```bash
# Instalar globalmente
npm install -g serverless

# Verificar
serverless --version
```

## Paso 3: Clonar y Configurar Proyecto

```bash
# Clonar repositorio
git clone <repo-url>
cd "PLN fIlter"

# Copiar variables de entorno
cp .env.example .env

# Editar .env con tus credenciales
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=<tu_access_key>
# AWS_SECRET_ACCESS_KEY=<tu_secret_key>
# STAGE=dev
```

## Paso 4: Desplegar Backend

```bash
cd backend

# Instalar dependencias Node
npm install --save-dev serverless-python-requirements

# Instalar dependencias Python
pip install -r requirements.txt

# Desplegar a AWS
serverless deploy

# Esperar a que termine (puede tomar 2-5 minutos)
```

### Salida Esperada

```
Service Information
service: pln-filter-backend
stage: dev
region: us-east-1
stack: pln-filter-backend-dev
resources: 15
endpoints:
  wss: wss://xxxxx.execute-api.us-east-1.amazonaws.com/dev
functions:
  receiveMessage: pln-filter-backend-dev-receiveMessage
  getMessages: pln-filter-backend-dev-getMessages
  notifyUser: pln-filter-backend-dev-notifyUser
```

**Guarda el endpoint WebSocket (wss://...)**

## Paso 5: Configurar Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install

# Crear archivo de configuración
cp .env.example .env.local

# Editar .env.local
# VITE_WEBSOCKET_URL=wss://xxxxx.execute-api.us-east-1.amazonaws.com/dev
# (Reemplaza xxxxx con tu endpoint)

# Ejecutar en desarrollo
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## Paso 6: Ejecutar Worker Local

```bash
cd ../worker

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo de configuración
cp ../.env .env

# Asegurar que Ollama está corriendo
# En otra terminal:
# ollama serve

# Ejecutar worker
python main.py
```

## Paso 7: Probar la Aplicación

1. Abre `http://localhost:5173` en el navegador
2. Usa los botones de demostración para login (user1 o user2)
3. Crea una conversación entre los dos usuarios
4. Envía mensajes
5. Verifica que los mensajes se reciben en tiempo real

## Verificar Despliegue

### Ver Logs

```bash
cd backend

# Ver logs de receiveMessage
serverless logs -f receiveMessage --tail

# Ver logs de getMessages
serverless logs -f getMessages --tail

# Ver logs de notifyUser
serverless logs -f notifyUser --tail
```

### Invocar Lambdas Manualmente

```bash
cd backend

# Invocar receiveMessage
serverless invoke local -f receiveMessage -d '{
  "requestContext": {
    "connectionId": "test-conn",
    "authorizer": {
      "claims": {
        "sub": "user1"
      }
    }
  },
  "body": "{\"action\": \"sendMessage\", \"data\": {\"conversationId\": \"conv_user1_user2\", \"receiverId\": \"user2\", \"content\": \"Hola\"}}"
}'
```

### Ver Recursos en AWS Console

1. **DynamoDB:** https://console.aws.amazon.com/dynamodb
   - Verifica que existan las tablas: ChatMessages, Users, Conversations

2. **SQS:** https://console.aws.amazon.com/sqs
   - Verifica que exista la cola: pln-filter-backend-dev-messages

3. **API Gateway:** https://console.aws.amazon.com/apigateway
   - Verifica que exista la API WebSocket: pln-filter-backend-dev-websocket

4. **Lambda:** https://console.aws.amazon.com/lambda
   - Verifica que existan las 3 funciones

## Despliegue en Producción

### Cambiar a Stage Producción

```bash
cd backend

# Desplegar a producción
serverless deploy --stage prod

# Esto crea recursos separados para prod
```

### Configurar Dominio Personalizado

```bash
# Instalar plugin
npm install --save-dev serverless-domain-manager

# Agregar a serverless.yml
custom:
  customDomain:
    domainName: api.tudominio.com
    certificateName: '*.tudominio.com'
    basePath: ''
    stage: prod
    createRoute53Record: true

# Desplegar
serverless create_domain
serverless deploy --stage prod
```

## Monitoreo y Mantenimiento

### Ver Métricas

```bash
# Ver información del stack
serverless info

# Ver información detallada
serverless info --verbose
```

### Actualizar Código

```bash
cd backend

# Actualizar solo una función (más rápido)
serverless deploy function -f receiveMessage

# Actualizar todo
serverless deploy
```

### Limpiar Recursos

```bash
cd backend

# Eliminar todo el stack
serverless remove

# Esto elimina:
# - Tablas DynamoDB
# - Cola SQS
# - API Gateway
# - Funciones Lambda
# - Roles IAM
```

## Troubleshooting

### Error: "No credentials found"

```bash
aws configure
# Ingresa tus credenciales
```

### Error: "Access Denied"

Verifica que tu usuario IAM tiene permisos para:
- Lambda
- DynamoDB
- SQS
- API Gateway
- IAM (para crear roles)

### Error: "Table already exists"

```bash
# Elimina el stack anterior
serverless remove

# Luego redeploy
serverless deploy
```

### Error: "Timeout"

Aumenta el timeout en `backend/serverless.yml`:
```yaml
functions:
  receiveMessage:
    timeout: 60
```

### WebSocket no conecta

1. Verifica que el endpoint en `.env.local` es correcto
2. Verifica que el frontend está en `http://localhost:5173` (no https)
3. Verifica los logs: `serverless logs -f receiveMessage --tail`

## Costos Estimados

Con la capa gratuita de AWS (suficiente para MVP):

| Servicio | Límite Gratuito | Costo Exceso |
|----------|-----------------|-------------|
| Lambda | 1M invocaciones/mes | $0.20 por 1M |
| DynamoDB | 25 GB + 25 RU/s | $1.25 por GB |
| SQS | 1M solicitudes/mes | $0.40 por 1M |
| API Gateway | 1M mensajes/mes | $3.50 por 1M |

**Costo total para MVP:** $0 (dentro de capa gratuita)

## Próximos Pasos

1. Configurar Cognito para autenticación real
2. Desplegar frontend en Amplify
3. Configurar dominio personalizado
4. Agregar monitoreo y alertas
5. Implementar CI/CD con GitHub Actions
6. Configurar backups automáticos
