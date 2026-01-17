<template>
  <div class="general-view">
    <div class="welcome-container">
      <div class="icon-blob glass">
        <MessageSquare :size="48" class="icon-pulse" />
      </div>
      <h2>Bienvenido a PLN Filter</h2>
      <p>Selecciona un contacto de la barra lateral para comenzar a chatear con protección en tiempo real.</p>
      
      <div class="features-grid">
        <div class="feature-card glass">
          <ShieldCheck :size="24" class="text-emerald" />
          <span>Filtro de Amenazas</span>
        </div>
        <div class="feature-card glass">
          <Zap :size="24" class="text-amber" />
          <span>Análisis IA Profundo</span>
        </div>
        <div class="feature-card glass">
          <Lock :size="24" class="text-blue" />
          <span>Privacidad Total</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { MessageSquare, ShieldCheck, Zap, Lock } from 'lucide-vue-next'
</script>

<style scoped>
.general-view {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  background: radial-gradient(circle at center, rgba(59, 130, 246, 0.05) 0%, transparent 70%);
}

.welcome-container {
  max-width: 480px;
  text-align: center;
}

.icon-blob {
  width: 100px;
  height: 100px;
  margin: 0 auto 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 30px;
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1) !important;
  border-color: rgba(59, 130, 246, 0.2);
}

.icon-pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); filter: drop-shadow(0 0 0px rgba(59, 130, 246, 0)); }
  50% { transform: scale(1.1); filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.5)); }
  100% { transform: scale(1); filter: drop-shadow(0 0 0px rgba(59, 130, 246, 0)); }
}

h2 {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}

p {
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 40px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.feature-card {
  padding: 20px 12px;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  font-weight: 600;
  color: #cbd5e1;
}

.text-emerald { color: #10b981; }
.text-amber { color: #f59e0b; }
.text-blue { color: #3b82f6; }

.glass {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}
</style>
