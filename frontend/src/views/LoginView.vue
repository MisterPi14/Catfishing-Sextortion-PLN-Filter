<template>
  <div class="login-container">
    <div class="login-box">
      <h1>PLN Filter</h1>
      <p class="subtitle">Chat Seguro con Detección de Amenazas</p>

      <div class="auth-tabs">
        <button 
          type="button"
          :class="['tab-btn', { active: !isRegistering }]" 
          @click="isRegistering = false"
        >
          Iniciar Sesión
        </button>
        <button 
          type="button"
          :class="['tab-btn', { active: isRegistering }]" 
          @click="isRegistering = true"
        >
          Registrarse
        </button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">Usuario</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Ingresa tu usuario"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Ingresa tu contraseña"
            required
          />
        </div>

        <button type="submit" class="btn-login" :disabled="isLoading">
          {{ isLoading ? 'Procesando...' : (isRegistering ? 'Registrarse' : 'Iniciar Sesión') }}
        </button>
      </form>

      <div class="demo-section">
        <p>O prueba con usuarios de demostración:</p>
        <div class="demo-buttons">
          <button @click="demoLogin('user1')" class="btn-demo">
            Usuario 1
          </button>
          <button @click="demoLogin('user2')" class="btn-demo">
            Usuario 2
          </button>
        </div>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useChatStore } from '../stores/chatStore'
import authService from '../services/authService'
import websocketService from '../services/websocketService'

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')
const isRegistering = ref(false)
const store = useChatStore()

const handleSubmit = async () => {
  if (!username.value || !password.value) {
    error.value = 'Por favor completa todos los campos'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    let user
    if (isRegistering.value) {
      await authService.register(username.value, password.value)
      // Login automático tras registro exitoso
      user = await authService.login(username.value, password.value)
    } else {
      user = await authService.login(username.value, password.value)
    }
    
    store.setCurrentUser(user)

    // Conectar WebSocket
    await websocketService.connect(authService.getToken())
  } catch (err) {
    error.value = (isRegistering.value ? 'Error al registrar: ' : 'Error al iniciar sesión: ') + err.message
    isLoading.value = false
  }
}

const demoLogin = async (userId) => {
  isLoading.value = true
  error.value = ''

  try {
    const user = authService.mockLogin(userId, userId)
    store.setCurrentUser(user)
    await websocketService.connect(authService.getToken())
  } catch (err) {
    error.value = 'Error al conectar: ' + err.message
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 10px;
  font-size: 28px;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

.btn-login {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.3s;
}

.btn-login:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.demo-section {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid #eee;
  text-align: center;
}

.demo-section p {
  color: #666;
  margin-bottom: 15px;
  font-size: 14px;
}

.demo-buttons {
  display: flex;
  gap: 10px;
}

.btn-demo {
  flex: 1;
  padding: 10px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.btn-demo:hover {
  background: #e0e0e0;
}

.error-message {
  margin-top: 20px;
  padding: 12px;
  background: #fee;
  color: #c33;
  border-radius: 5px;
  font-size: 14px;
  text-align: center;
}

.auth-tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
}

.tab-btn {
  flex: 1;
  padding: 10px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-weight: 600;
  color: #888;
  margin-bottom: -2px;
  transition: all 0.3s;
}

.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.tab-btn:hover {
  color: #667eea;
}
</style>
