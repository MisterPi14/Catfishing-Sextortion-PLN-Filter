<template>
  <div class="auth-container">
    <div class="background-blobs">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>
    
    <div class="auth-card glass">
      <div class="logo-section">
        <div class="logo-icon glass">
          <UserPlus :size="32" class="icon-vibrant" />
        </div>
        <h1>Crear Cuenta</h1>
        <p class="subtitle">Únete a la comunidad segura</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label for="username">Usuario</label>
          <div class="input-wrapper glass">
            <User :size="18" class="input-icon" />
            <input
              id="username"
              v-model="username"
              type="text"
              placeholder="Elige un nombre de usuario"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">Contraseña</label>
          <div class="input-wrapper glass">
            <Lock :size="18" class="input-icon" />
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="Crea una contraseña"
              required
            />
          </div>
        </div>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          <span v-if="!isLoading">Registrarse</span>
          <Loader2 v-else class="spin" />
        </button>
      </form>

      <div class="auth-footer">
        <p>¿Ya tienes cuenta? <router-link to="/login">Inicia Sesión</router-link></p>
      </div>

      <Transition name="fade">
        <div v-if="error" class="error-toast">
          <AlertCircle :size="16" /> {{ error }}
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '../stores/chatStore'
import authService from '../services/authService'
import websocketService from '../services/websocketService'
import { 
  UserPlus, 
  User, 
  Lock, 
  Loader2, 
  AlertCircle 
} from 'lucide-vue-next'

const router = useRouter()
const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')
const store = useChatStore()

const handleSubmit = async () => {
  if (!username.value || !password.value) {
    error.value = 'Por favor completa todos los campos'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    await authService.register(username.value, password.value)
    // Automáticamente loguear tras registro
    const user = await authService.login(username.value, password.value)
    store.setCurrentUser(user)
    await websocketService.connect(authService.getToken())
    router.push({ name: 'Home' })
  } catch (err) {
    error.value = 'Error al registrar: ' + err.message
    isLoading.value = false
  }
}
</script>

<style scoped>
/* Reutilizando estilos de LoginView.vue - En un proyecto real esto iría en un archivo CSS global o componente base */
.auth-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #0f172a;
  position: relative;
  overflow: hidden;
  padding: 20px;
}

.background-blobs {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.blob {
  position: absolute;
  filter: blur(80px);
  opacity: 0.4;
  border-radius: 50%;
  animation: move 20s infinite alternate;
}

.blob-1 {
  width: 400px;
  height: 400px;
  background: #3b82f6;
  top: -100px;
  left: -100px;
}

.blob-2 {
  width: 350px;
  height: 350px;
  background: #8b5cf6;
  bottom: -50px;
  right: -50px;
  animation-delay: -5s;
}

.blob-3 {
  width: 300px;
  height: 300px;
  background: #ec4899;
  top: 40%;
  left: 60%;
  animation-delay: -10s;
}

@keyframes move {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(100px, 50px) scale(1.1); }
}

.glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 40px;
  border-radius: 24px;
  z-index: 1;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.logo-section {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
}

.icon-vibrant {
  color: #10b981;
  filter: drop-shadow(0 0 8px rgba(16, 185, 129, 0.5));
}

h1 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
  letter-spacing: -0.02em;
}

.subtitle {
  color: #94a3b8;
  font-size: 14px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-size: 13px;
  font-weight: 500;
  color: #cbd5e1;
  margin-left: 4px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-radius: 12px;
  transition: all 0.3s;
}

.input-wrapper:focus-within {
  border-color: #10b981;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.input-icon {
  color: #64748b;
  margin-right: 12px;
}

input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 12px 0;
  color: #fff;
  font-size: 15px;
}

input:focus {
  outline: none;
}

input::placeholder {
  color: #475569;
}

.btn-primary {
  margin-top: 10px;
  padding: 14px;
  background: #10b981;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-primary:hover {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.auth-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #94a3b8;
}

.auth-footer a {
  color: #10b981;
  text-decoration: none;
  font-weight: 600;
}

.auth-footer a:hover {
  text-decoration: underline;
}

.error-toast {
  position: absolute;
  top: -60px;
  left: 0;
  right: 0;
  background: #ef4444;
  color: white;
  padding: 12px 20px;
  border-radius: 12px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.2);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
