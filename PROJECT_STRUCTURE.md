# Estructura del Proyecto - PLN Filter

```
PLN fIlter/
├── frontend/                    # Aplicación Vue
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/             # Pinia stores (estado global)
│   │   ├── services/           # Servicios (WebSocket, API)
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
├── backend/                     # Funciones Lambda (Python)
│   ├── lambdas/
│   │   ├── receive_message/
│   │   │   └── lambda_function.py
│   │   ├── get_messages/
│   │   │   └── lambda_function.py
│   │   └── notify_user/
│   │       └── lambda_function.py
│   ├── shared/                 # Código compartido entre lambdas
│   │   ├── dynamodb_client.py
│   │   ├── sqs_client.py
│   │   └── websocket_client.py
│   ├── requirements.txt
│   └── deploy.sh               # Script para desplegar lambdas
│
├── worker/                      # Worker local (Python + Ollama)
│   ├── main.py                 # Punto de entrada
│   ├── sqs_listener.py         # Escucha SQS
│   ├── llm_processor.py        # Procesa con Ollama
│   ├── aws_notifier.py         # Invoca NotifyUser Lambda
│   ├── requirements.txt
│   └── config.py               # Configuración (credenciales AWS, Ollama)
│
├── Arquitectura/
│   └── Arquitectura.txt         # Documentación de arquitectura
│
├── README.md                    # Instrucciones generales
└── .env.example                 # Variables de entorno (plantilla)
```
