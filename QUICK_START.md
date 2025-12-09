# Quick Start - PLN Filter

Guía rápida para empezar en 5 minutos.

## Requisitos

- AWS CLI configurado: `aws configure`
- Node.js 16+
- Python 3.11+
- Serverless Framework: `npm install -g serverless`

## 1. Desplegar Backend (2 min)

```bash
cd backend
npm install --save-dev serverless-python-requirements
pip install -r requirements.txt
serverless deploy
```

**Guarda el endpoint WebSocket que aparece en la salida**

## 2. Configurar Frontend (1 min)

```bash
cd ../frontend
npm install
cp .env.example .env.local

# Edita .env.local y reemplaza el endpoint WebSocket
# VITE_WEBSOCKET_URL=wss://xxxxx.execute-api.us-east-1.amazonaws.com/dev

npm run dev
```

Abre `http://localhost:5173`

## 3. Ejecutar Worker (1 min)

```bash
cd ../worker
pip install -r requirements.txt
cp ../.env .env

# En otra terminal, asegúrate que Ollama está corriendo:
# ollama serve

python main.py
```

## 4. Probar

1. Abre `http://localhost:5173`
2. Haz click en "Usuario 1" o "Usuario 2"
3. Crea una conversación
4. Envía mensajes

## Comandos Útiles

```bash
# Ver logs del backend
cd backend
serverless logs -f receiveMessage --tail

# Eliminar todo
serverless remove

# Información del stack
serverless info
```

## Troubleshooting

| Problema | Solución |
|----------|----------|
| "No credentials found" | Ejecuta `aws configure` |
| WebSocket no conecta | Verifica el endpoint en `.env.local` |
| "Table already exists" | Ejecuta `serverless remove` y luego `serverless deploy` |
| Ollama no funciona | Asegúrate que `ollama serve` está corriendo |

## Próximos Pasos

- Leer [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) para despliegue en producción
- Leer [backend/README.md](./backend/README.md) para más detalles del backend
- Leer [frontend/README.md](./frontend/README.md) para más detalles del frontend
