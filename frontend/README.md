# Frontend - PLN Filter

Aplicación Vue 3 + Vite para el sistema de chat con detección de amenazas.

## Estructura

```
src/
├── components/      # Componentes reutilizables
├── views/          # Vistas principales (Login, Chat)
├── stores/         # Pinia stores (estado global)
├── services/       # Servicios (WebSocket, Auth)
├── assets/         # Recursos estáticos
├── App.vue         # Componente raíz
└── main.js         # Punto de entrada
```

## Instalación

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## Build

```bash
npm run build
```

## Características

- **Autenticación:** Mock login para desarrollo
- **Chat en tiempo real:** WebSocket para mensajería instantánea
- **Alertas de riesgo:** Visualización de amenazas detectadas
- **Historial:** Recuperación de mensajes anteriores
- **Responsive:** Interfaz adaptable a diferentes tamaños

## Variables de Entorno

Crear archivo `.env.local`:

```env
VITE_WEBSOCKET_URL=ws://localhost:8080
VITE_API_URL=http://localhost:3000
```

## Usuarios de Demostración

- **user1** / cualquier contraseña
- **user2** / cualquier contraseña

O usar los botones de demostración en la pantalla de login.
