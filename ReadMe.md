# PLN Filter — Sistema de mensajería instantánea con detección de catfishing y sextorsión

PLN Filter es una aplicación web de mensajería instantánea uno a uno que incorpora un
componente de análisis semántico de las conversaciones para identificar mensajes
asociados a **catfishing** y **sextorsión**, y alertar de manera preventiva al usuario
antes de que se consolide el fraude.

La clasificación se realiza mediante un **modelo largo de lenguaje (LLM) ejecutado en
entorno local** a través de Ollama, refinado con técnicas de *prompt engineering*
(zero-shot y few-shot). El resto del sistema se apoya en una arquitectura híbrida
nube-local basada en servicios administrados de AWS.

> Este repositorio corresponde a la implementación del reporte técnico
> **"Diseño de un Detector de Catfishing y Sextorsión Orientado a Aplicaciones de
> Mensajería Instantánea Mediante Refinamiento de un Modelo Largo de Lenguaje"**.
>
> - Autor: Edgar Diego Piña Vargas
> - Asesores: Dr. José Portillo Portillo · Dr. Olalekan Tolulope Abiola

---

## 1. Contexto y objetivos

### Problema

La masificación de las aplicaciones de mensajería instantánea ha generado un entorno
propicio para la proliferación de fraudes digitales, entre ellos el catfishing (creación
de una identidad falsa para generar confianza y explotarla) y la sextorsión (coerción
sexual a partir de material íntimo obtenido de la víctima). Ambas modalidades presentan
una dependencia directa entre sí y afectan a usuarios de cualquier edad.

### Objetivo general

Diseñar un sistema de mensajería con detección de catfishing y sextorsión, fundamentado
en la integración y el refinamiento de un modelo largo de lenguaje, delimitado al idioma
español.

### Objetivos del sistema

- Analizar de forma asíncrona cada mensaje intercambiado en una conversación.
- Clasificar el contenido escrito en una de tres etiquetas: `catfishing`, `sextorsion`
  o `inofensivo`.
- Notificar al usuario en tiempo cercano al interactivo cuando se identifique un patrón
  de riesgo, con orientación sobre cómo reportar y bloquear.
- Mantener la persistencia de mensajes, conversaciones y del resultado del análisis.
- Operar dentro de los límites de las capas gratuitas de los servicios empleados.

### Límites y alcances

| Dentro del alcance | Fuera del alcance |
|---|---|
| Conversaciones uno a uno | Chat grupal |
| Contenido exclusivamente escrito | Procesamiento de imagen o audio |
| Refinamiento por técnicas de prompting | Entrenamiento o *fine tuning* de pesos |
| Modelos de 0.25 B a 8 B de parámetros | Modelos de mayor escala |
| Idioma español | Otros idiomas |
| Inferencia en entorno local | Inferencia gestionada en la nube |
| Alertamiento preventivo al usuario | Cadena de custodia o valor probatorio |

El conjunto de datos utilizado para el refinamiento y la evaluación del clasificador se
construyó a partir de ejemplos reales anonimizados y de datos sintéticos generados con
modelos de gran escala. **Este repositorio no contiene datos personales ni conversaciones
de usuarios reales.**

---

## 2. Arquitectura de la solución

La solución es **híbrida nube-local**: el cómputo de la aplicación de mensajería se apoya
en servicios administrados de AWS, mientras que la inferencia del LLM se ejecuta en un
worker local. Este desacoplamiento hace que la ejecución del modelo no retrase el envío
ni la recepción de mensajes.

### 2.1 Componentes

| # | Componente | Rol dentro del sistema |
|---|---|---|
| 1 | **AWS Amplify** | Hosting del frontend estático (HTML, CSS, JS) con soporte SSL/TLS y despliegue desde repositorio Git. |
| 2 | **Amazon Cognito User Pool** | Autenticación de usuarios basada en OAuth 2.0 / OpenID Connect y emisión de JWT para autorizar peticiones. |
| 3 | **API Gateway (WebSocket API)** | Conexión bidireccional y persistente con cada cliente; asigna un `connectionId` por sesión y enruta las acciones (`sendMessage`, `getMessages`, etc.) hacia las funciones Lambda. |
| 4 | **Lambda `receiveMessage`** | Almacena el mensaje entrante en DynamoDB, lo encola en SQS para su análisis y lo reenvía al destinatario por WebSocket. |
| 5 | **Lambda `getMessages`** | Recupera el historial de conversaciones y sus metadatos (estado del análisis, alertas emitidas), con paginación para conversaciones largas. |
| 6 | **Lambda `notifyUser`** | Invocada por el worker cuando la predicción es `catfishing` o `sextorsion`; resuelve el `connectionId` del destinatario y emite la alerta por WebSocket. |
| 7 | **Amazon DynamoDB** | Persistencia NoSQL de mensajes, usuarios y conversaciones. La tabla de mensajes usa `conversationId` como clave de partición y `timestamp` como clave de ordenamiento. |
| 8 | **Amazon SQS — cola de análisis** | Búfer entre el sistema de mensajería y el worker local, configurado con *long polling*. Garantiza que ningún mensaje quede sin analizar aunque el equipo local esté apagado o sin conexión. |
| 9 | **Amazon SQS — Dead Letter Queue** | Recibe los mensajes cuyo análisis falló tras varios intentos, evitando ciclos infinitos de reintento que bloquearían la cola principal. |
| 10 | **Worker local + Ollama** | Aplicación Python que consume la cola, envía el mensaje al LLM mediante el cliente de Ollama, actualiza el estado del análisis en DynamoDB, invoca `notifyUser` en caso de riesgo y elimina el mensaje de la cola. |

### 2.2 Flujo de datos

1. El usuario envía un mensaje → WebSocket → API Gateway.
2. `receiveMessage` persiste el mensaje en DynamoDB, lo encola en SQS y lo entrega al
   destinatario.
3. El worker local lee la cola y ejecuta la inferencia del LLM sobre el contenido.
4. El worker actualiza el resultado del análisis en DynamoDB.
5. Si la etiqueta predicha es `catfishing` o `sextorsion`, el worker invoca `notifyUser`.
6. `notifyUser` envía la alerta al cliente conectado, que la muestra en tiempo real.
7. El mensaje se elimina de la cola una vez confirmadas todas las operaciones.

Diagramas: [`Arquitectura/diagramaArquitectonico.svg`](./Arquitectura/diagramaArquitectonico.svg)
y [`diagrams/`](./diagrams).

### 2.3 Consideraciones de diseño

- **Desacoplamiento asíncrono:** la cola SQS aísla la latencia de la inferencia del flujo
  de mensajería.
- **Tolerancia a fallos:** el sistema sigue operando aunque el worker local deje de estar
  disponible; los mensajes pendientes se analizan al reconectarse.
- **Modularidad:** cada función Lambda concentra una responsabilidad, lo que permite
  ampliarlas por separado (por ejemplo, escalamiento de notificaciones según el riesgo).
- **Costo:** la inferencia local evita el gasto de servicios administrados de inferencia y
  mantiene la información en infraestructura propia.

---

## 3. Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | Vue 3 + Vite |
| Backend | Python 3.11 sobre AWS Lambda, orquestado con Serverless Framework 4 |
| Base de datos | Amazon DynamoDB |
| Mensajería asíncrona | Amazon SQS (+ DLQ) |
| Comunicación en tiempo real | API Gateway WebSocket API |
| Autenticación | Amazon Cognito User Pool |
| Hosting | AWS Amplify |
| Worker de inferencia | Python + Ollama |
| Entorno de desarrollo | Docker + LocalStack + Serverless Offline |

### Hardware de referencia del worker

La ejecución local se validó sobre un equipo con CPU Intel Core i7 de 4.ª generación, GPU
NVIDIA GeForce GTX 1060 (6 GB de VRAM) y 16 GB de RAM, capaz de operar modelos de hasta
8 B de parámetros.

---

## 4. Estructura del proyecto

```
PLN-filter/
├── frontend/            # Aplicación Vue 3 + Vite
│   └── src/
├── backend/             # Funciones Lambda (Python) + Serverless Framework
│   ├── handlers/        # auth, connect, receive_message, get_messages,
│   │                    # notify_user, get_conversations, user_management
│   ├── shared/          # Utilidades compartidas
│   ├── scripts/         # Automatización posterior al despliegue (update-env.js)
│   └── serverless.yml   # Infraestructura como código
├── worker/              # Worker local de inferencia
│   ├── main.py          # Ciclo principal
│   ├── sqs_listener.py  # Consumo de la cola de análisis
│   ├── llm_processor.py # Cliente de Ollama y clasificación
│   └── aws_notifier.py  # Invocación de notifyUser
├── Arquitectura/        # Diagramas y descripción arquitectónica
├── diagrams/            # Diagramas complementarios
└── .env.example         # Plantilla de variables de entorno
```

---

## 5. Puesta en marcha

### 5.1 Requisitos

- Node.js 18+
- Python 3.11+
- Docker (para el entorno local con LocalStack)
- [Ollama](https://ollama.com) en ejecución (`ollama serve`)
- Serverless Framework 4 (`npm install -g serverless`)
- AWS CLI configurado, únicamente si se despliega a una cuenta real

### 5.2 Configuración inicial

```bash
git clone <repo-url>
cd PLN-filter
cp .env.example .env
```

Las variables relevantes son las de conexión a AWS o LocalStack (`AWS_REGION`,
`AWS_ENDPOINT_URL`, `SQS_QUEUE_URL`, `DYNAMODB_TABLE`), el nombre de la función de
notificación (`NOTIFY_USER_LAMBDA_NAME`) y las del modelo (`OLLAMA_BASE_URL`,
`OLLAMA_MODEL`). El archivo `.env` no debe versionarse.

### 5.3 Entorno local (LocalStack)

El *stage* `local` apunta todos los servicios de AWS al endpoint de LocalStack
(`http://localhost:4566`), según lo definido en `backend/serverless.yml`.

```bash
# 1. Levantar LocalStack
docker run --rm -d -p 4566:4566 --name localstack localstack/localstack

# 2. Desplegar la infraestructura simulada
cd backend
npm install
pip install -r requirements.txt
serverless deploy --stage local
```

El hook `deploy:finalize` ejecuta `scripts/update-env.js`, que propaga los endpoints
generados a los archivos de configuración del frontend y del worker.

### 5.4 Despliegue en AWS

```bash
cd backend
serverless deploy --stage dev
```

Serverless Framework aprovisiona automáticamente las tablas de DynamoDB (mensajes,
usuarios y conversaciones), la cola SQS de análisis, la API WebSocket y los roles IAM con
los permisos necesarios. El endpoint WebSocket se obtiene de la salida del despliegue o
con `serverless info`.

### 5.5 Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # definir VITE_WEBSOCKET_URL con el endpoint del backend
npm run dev                  # http://localhost:5173
```

### 5.6 Worker de inferencia

```bash
cd worker
pip install -r requirements.txt
cp ../.env .env

ollama pull <modelo>   # el definido en OLLAMA_MODEL
python main.py
```

---

## 6. Comandos principales

### Backend

```bash
serverless deploy --stage local        # Desplegar contra LocalStack
serverless deploy --stage dev          # Desplegar a AWS
serverless info                        # Endpoints y recursos del stack
serverless logs -f receiveMessage --tail
serverless invoke local -f receiveMessage --path mock-receive-messages.json
serverless remove                      # Eliminar el stack
```

Los archivos `mock-*.json` de `backend/` sirven como cargas útiles de prueba para la
invocación local de cada función.

### Frontend

```bash
npm run dev       # Servidor de desarrollo
npm run build     # Build de producción
npm run preview   # Previsualización del build
```

### Worker

```bash
python main.py
```

---

## 7. Capa gratuita de AWS

El diseño se ajusta a los límites de la capa gratuita de los servicios empleados:

| Servicio | Límite |
|---|---|
| DynamoDB | 25 GB de almacenamiento + 25 unidades de capacidad |
| Lambda | 1 M de invocaciones/mes |
| API Gateway | 1 M de mensajes/mes |
| SQS | 1 M de solicitudes/mes |
| Cognito | 50 k usuarios activos mensuales |
| Amplify | 15 GB de almacenamiento |

---

## 8. Documentación complementaria

- [SETUP.md](./SETUP.md) — Configuración detallada con Serverless Framework
- [QUICK_START.md](./QUICK_START.md) — Guía rápida de arranque
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) — Guía de despliegue
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) — Estructura del repositorio
- [backend/DATA_MODEL.md](./backend/DATA_MODEL.md) — Modelo de datos de DynamoDB
- [backend/EVENT_SCHEMAS.md](./backend/EVENT_SCHEMAS.md) — Esquemas de eventos JSON
- [frontend/README.md](./frontend/README.md) — Documentación del frontend
- [Arquitectura/Arquitectura.txt](./Arquitectura/Arquitectura.txt) — Descripción arquitectónica

---

## 9. Diagnóstico

1. Revisar los diagramas y la descripción en `Arquitectura/`.
2. Consultar los registros de una función: `serverless logs -f <función> --tail`.
3. Verificar que el worker está consumiendo la cola y que Ollama responde en
   `OLLAMA_BASE_URL`.
4. Inspeccionar la Dead Letter Queue para identificar mensajes cuyo análisis falló de
   forma reiterada.
5. Confirmar que las variables de entorno de `.env` corresponden al *stage* en uso.
