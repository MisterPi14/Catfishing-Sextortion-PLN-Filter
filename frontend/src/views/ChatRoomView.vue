<template>
  <div class="chat-room">
    <header class="chat-header glass">
      <div class="chat-title">
        <div class="status-dot"></div>
        <h2>{{ currentConversation?.participant }}</h2>
      </div>
      <div class="chat-actions">
        <button class="btn-icon glass"><Phone :size="18" /></button>
        <button class="btn-icon glass"><Video :size="18" /></button>
        <button class="btn-icon glass"><Info :size="18" /></button>
      </div>
    </header>

    <div class="messages-area" ref="messagesRef">
      <div v-if="isLoading" class="loader-overlay">
        <Loader2 class="spin" :size="32" />
      </div>

      <div class="alerts-stack">
        <TransitionGroup name="slide-up">
          <div
            v-for="alert in alerts"
            :key="alert.messageId"
            class="risk-alert glass"
            :class="`risk-${alert.riskLevel}`"
          >
            <div class="alert-icon">
              <AlertTriangle v-if="alert.riskLevel === 'high'" />
              <AlertCircle v-else />
            </div>
            <div class="alert-content">
              <strong>{{ alert.threatType }} Detectado</strong>
              <p>{{ alert.message }}</p>
            </div>
            <button @click="removeAlert(alert.messageId)" class="btn-close">
              <X :size="14" />
            </button>
          </div>
        </TransitionGroup>
      </div>

      <div class="messages-list">
        <div
          v-for="msg in currentMessages"
          :key="msg.messageId"
          class="message-wrapper"
          :class="{ sent: msg.senderId === currentUser?.userId }"
        >
          <div 
            class="message-bubble glass"
            :class="[
              msg.riskAnalysis?.riskLevel ? `risk-${msg.riskAnalysis.riskLevel}` : '',
              { blurred: msg.riskAnalysis?.riskLevel === 'high' && !revealedMessages.has(msg.messageId) }
            ]"
          >
            <div v-if="msg.riskAnalysis?.riskLevel === 'high' && !revealedMessages.has(msg.messageId)" class="blur-overlay">
              <ShieldAlert :size="20" />
              <span>Contenido Sensible</span>
              <button @click="revealMessage(msg.messageId)" class="btn-reveal">Ver</button>
            </div>
            
            <p class="content">{{ msg.content }}</p>
            <div class="meta">
              <span class="time">{{ formatTime(msg.timestamp) }}</span>
              <div v-if="msg.riskAnalysis?.analyzed" class="risk-indicator">
                <CheckCheck :size="14" v-if="msg.riskAnalysis.riskLevel === 'low'" class="text-emerald" />
                <AlertCircle :size="14" v-else-if="msg.riskAnalysis.riskLevel === 'medium'" class="text-amber" />
                <ShieldAlert :size="14" v-else-if="msg.riskAnalysis.riskLevel === 'high'" class="text-rose" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <footer class="chat-input-area glass">
      <div class="input-container glass">
        <button class="btn-extra"><Paperclip :size="20" /></button>
        <input
          v-model="messageContent"
          type="text"
          placeholder="Escribe un mensaje..."
          @keyup.enter="sendMessage"
        />
        <button class="btn-extra"><Smile :size="20" /></button>
      </div>
      <button 
        @click="sendMessage" 
        class="btn-send" 
        :disabled="!messageContent || !isConnected"
      >
        <Send :size="20" />
      </button>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useChatStore } from '../stores/chatStore'
import websocketService from '../services/websocketService'
import { 
  Phone, 
  Video, 
  Info, 
  Send, 
  Paperclip, 
  Smile, 
  Loader2,
  AlertTriangle,
  AlertCircle,
  ShieldAlert,
  CheckCheck,
  X
} from 'lucide-vue-next'

const props = defineProps(['id'])
const store = useChatStore()
const messageContent = ref('')
const messagesRef = ref(null)
const revealedMessages = ref(new Set())

const currentUser = computed(() => store.currentUser)
const currentMessages = computed(() => store.currentMessages)
const currentConversation = computed(() => store.conversations[props.id])
const alerts = computed(() => store.alerts)
const isConnected = computed(() => store.isConnected)
const isLoading = computed(() => store.isLoading)

const sendMessage = () => {
  if (!messageContent.value || !isConnected.value) return

  websocketService.sendMessage(
    props.id,
    currentConversation.value.participant,
    messageContent.value
  )

  messageContent.value = ''
}

const revealMessage = (id) => {
  revealedMessages.value.add(id)
}

const removeAlert = (id) => {
  store.alerts = store.alerts.filter(a => a.messageId !== id)
}

const formatTime = (ts) => {
  return new Date(ts).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

watch(currentMessages, () => {
  scrollToBottom()
}, { deep: true })

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-room {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.03) 0%, transparent 60%);
}

.chat-header {
  height: 80px;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  z-index: 5;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

h2 {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.chat-actions {
  display: flex;
  gap: 12px;
}

.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.05) !important;
  color: #fff;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 40px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
}

.loader-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(15, 23, 42, 0.5);
  z-index: 10;
}

.alerts-stack {
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 10;
  pointer-events: none;
}

.risk-alert {
  pointer-events: auto;
  padding: 16px 20px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.alert-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.alert-content {
  flex: 1;
}

.alert-content strong {
  display: block;
  font-size: 14px;
}

.alert-content p {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 2px;
}

.risk-high {
  background: rgba(244, 63, 94, 0.1) !important;
  border-color: rgba(244, 63, 94, 0.2);
}
.risk-high .alert-icon { background: rgba(244, 63, 94, 0.2); color: #fb7185; }
.risk-high strong { color: #fb7185; }

.risk-medium {
  background: rgba(245, 158, 11, 0.1) !important;
  border-color: rgba(245, 158, 11, 0.2);
}
.risk-medium .alert-icon { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.risk-medium strong { color: #fbbf24; }

.btn-close {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 70%;
}

.message-wrapper.sent {
  align-self: flex-end;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
  overflow: hidden;
}

.sent .message-bubble {
  background: #3b82f6 !important;
  color: white;
  border-bottom-right-radius: 4px;
  border-color: rgba(255, 255, 255, 0.1);
}

.message-wrapper:not(.sent) .message-bubble {
  border-bottom-left-radius: 4px;
}

.content {
  font-size: 14px;
  line-height: 1.5;
}

.meta {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.time {
  font-size: 11px;
  opacity: 0.6;
}

.risk-indicator {
  display: flex;
  align-items: center;
}

/* Specific Risk UI */
.message-bubble.risk-high {
  background: rgba(244, 63, 94, 0.05) !important;
  border: 1px solid rgba(244, 63, 94, 0.2);
}

.message-bubble.risk-medium {
  border-left: 3px solid #f59e0b;
}

.blurred .content {
  filter: blur(8px);
  user-select: none;
}

.blur-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.8);
  z-index: 2;
  gap: 4px;
  color: #94a3b8;
}

.blur-overlay span {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.btn-reveal {
  background: white;
  color: #0f172a;
  border: none;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 4px;
}

.message-bubble.risk-high:not(.blurred) {
  background: rgba(244, 63, 94, 0.1) !important;
  border: 1px solid rgba(244, 63, 94, 0.5);
}

.chat-input-area {
  height: 90px;
  padding: 0 40px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.input-container {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-radius: 16px;
}

.input-container input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 12px;
  color: white;
  font-size: 15px;
}

.input-container input:focus {
  outline: none;
}

.btn-extra {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-radius: 8px;
}

.btn-extra:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.btn-send {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: #3b82f6;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-send:hover:not(:disabled) {
  background: #2563eb;
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.glass {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
