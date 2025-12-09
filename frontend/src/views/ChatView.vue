<template>
  <div class="chat-container">
    <div class="sidebar">
      <div class="user-info">
        <div class="user-avatar">{{ currentUser?.username?.[0]?.toUpperCase() }}</div>
        <div class="user-details">
          <p class="username">{{ currentUser?.username }}</p>
          <p class="status" :class="{ online: isConnected }">
            {{ isConnected ? '● En línea' : '● Desconectado' }}
          </p>
        </div>
        <button @click="handleLogout" class="btn-logout">Salir</button>
      </div>

      <div class="conversations-list">
        <h3>Conversaciones</h3>
        <div class="add-conversation">
          <input
            v-model="newConversationUser"
            type="text"
            placeholder="ID del usuario"
            @keyup.enter="startConversation"
          />
          <button @click="startConversation" class="btn-add">+</button>
        </div>

        <div
          v-for="(conv, id) in conversations"
          :key="id"
          class="conversation-item"
          :class="{ active: currentConversationId === id }"
          @click="selectConversation(id)"
        >
          <div class="conv-avatar">{{ conv.participant?.[0]?.toUpperCase() }}</div>
          <div class="conv-info">
            <p class="conv-name">{{ conv.participant }}</p>
            <p class="conv-last-msg">{{ conv.lastMessage || 'Sin mensajes' }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="main-chat">
      <div v-if="!currentConversationId" class="empty-state">
        <p>Selecciona una conversación para comenzar</p>
      </div>

      <div v-else class="chat-content">
        <div class="chat-header">
          <h2>{{ conversations[currentConversationId]?.participant }}</h2>
        </div>

        <div class="alerts-container">
          <div
            v-for="alert in alerts"
            :key="alert.messageId"
            class="alert"
            :class="`alert-${alert.riskLevel}`"
          >
            <strong>⚠️ {{ alert.threatType }}</strong>
            <p>{{ alert.message }}</p>
            <small>Confianza: {{ (alert.confidence * 100).toFixed(0) }}%</small>
          </div>
        </div>

        <div class="messages-container">
          <div
            v-for="msg in currentMessages"
            :key="msg.messageId"
            class="message"
            :class="{ sent: msg.senderId === currentUser?.userId }"
          >
            <div class="message-content">
              <p>{{ msg.content }}</p>
              <small>{{ formatTime(msg.timestamp) }}</small>
            </div>
            <div
              v-if="msg.riskAnalysis?.analyzed && msg.riskAnalysis?.threatType"
              class="risk-badge"
              :class="`risk-${msg.riskAnalysis.riskLevel}`"
            >
              {{ msg.riskAnalysis.threatType }}
            </div>
          </div>
        </div>

        <div class="message-input">
          <input
            v-model="messageContent"
            type="text"
            placeholder="Escribe un mensaje..."
            @keyup.enter="sendMessage"
          />
          <button @click="sendMessage" class="btn-send" :disabled="!messageContent || !isConnected">
            Enviar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '../stores/chatStore'
import authService from '../services/authService'
import websocketService from '../services/websocketService'

const store = useChatStore()
const messageContent = ref('')
const newConversationUser = ref('')

const currentUser = computed(() => store.currentUser)
const conversations = computed(() => store.conversations)
const currentConversationId = computed(() => store.currentConversationId)
const currentMessages = computed(() => store.currentMessages)
const alerts = computed(() => store.alerts)
const isConnected = computed(() => store.isConnected)

const selectConversation = (conversationId) => {
  store.setCurrentConversation(conversationId)
  store.clearMessages()
  websocketService.getMessages(conversationId)
}

const startConversation = () => {
  if (!newConversationUser.value) return

  const receiverId = newConversationUser.value
  const conversationId = [currentUser.value.userId, receiverId].sort().join('_')

  store.addConversation(conversationId, receiverId)
  store.setCurrentConversation(conversationId)
  newConversationUser.value = ''
  store.clearMessages()
}

const sendMessage = () => {
  if (!messageContent.value || !isConnected.value) return

  websocketService.sendMessage(
    currentConversationId.value,
    conversations.value[currentConversationId.value].participant,
    messageContent.value
  )

  messageContent.value = ''
}

const handleLogout = () => {
  authService.logout()
  websocketService.disconnect()
  store.$reset()
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  // Agregar conversación de demostración
  const otherUser = currentUser.value.userId === 'user1' ? 'user2' : 'user1'
  const conversationId = [currentUser.value.userId, otherUser].sort().join('_')
  store.addConversation(conversationId, otherUser)
})

onUnmounted(() => {
  websocketService.disconnect()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  background: #fff;
}

.sidebar {
  width: 300px;
  background: #f8f9fa;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.user-info {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  font-weight: 600;
  color: #333;
  margin: 0;
  font-size: 14px;
}

.status {
  color: #999;
  font-size: 12px;
  margin: 4px 0 0 0;
}

.status.online {
  color: #4caf50;
}

.btn-logout {
  padding: 6px 12px;
  background: #fee;
  color: #c33;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  flex-shrink: 0;
}

.conversations-list {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

.conversations-list h3 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #666;
  text-transform: uppercase;
}

.add-conversation {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.add-conversation input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
}

.btn-add {
  padding: 8px 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.conversation-item {
  display: flex;
  gap: 10px;
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.conversation-item:hover {
  background: #f0f0f0;
}

.conversation-item.active {
  background: #e8eaf6;
  border-left: 3px solid #667eea;
}

.conv-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.conv-info {
  flex: 1;
  min-width: 0;
}

.conv-name {
  font-weight: 600;
  color: #333;
  margin: 0;
  font-size: 14px;
}

.conv-last-msg {
  color: #999;
  font-size: 12px;
  margin: 4px 0 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.main-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 16px;
}

.chat-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
}

.chat-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.alerts-container {
  padding: 10px 20px;
  max-height: 150px;
  overflow-y: auto;
}

.alert {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  font-size: 13px;
  border-left: 4px solid;
}

.alert strong {
  display: block;
  margin-bottom: 4px;
}

.alert p {
  margin: 4px 0;
}

.alert small {
  display: block;
  margin-top: 4px;
  opacity: 0.8;
}

.alert-high {
  background: #ffebee;
  border-left-color: #f44336;
  color: #c62828;
}

.alert-medium {
  background: #fff3e0;
  border-left-color: #ff9800;
  color: #e65100;
}

.alert-low {
  background: #f1f8e9;
  border-left-color: #8bc34a;
  color: #558b2f;
}

.messages-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.message.sent {
  justify-content: flex-end;
}

.message-content {
  max-width: 60%;
  padding: 12px 16px;
  background: #f0f0f0;
  border-radius: 12px;
  word-wrap: break-word;
}

.message.sent .message-content {
  background: #667eea;
  color: white;
}

.message-content p {
  margin: 0;
  font-size: 14px;
}

.message-content small {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  opacity: 0.7;
}

.risk-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.risk-high {
  background: #ffcdd2;
  color: #c62828;
}

.risk-medium {
  background: #ffe0b2;
  color: #e65100;
}

.risk-low {
  background: #c8e6c9;
  color: #2e7d32;
}

.message-input {
  padding: 20px;
  background: white;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 10px;
}

.message-input input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.message-input input:focus {
  outline: none;
  border-color: #667eea;
}

.btn-send {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s;
}

.btn-send:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
