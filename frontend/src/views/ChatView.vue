<template>
  <div class="chat-layout">
    <aside class="sidebar glass">
      <div class="sidebar-header">
        <div class="user-profile">
          <div class="avatar glass">
            {{ currentUser?.username?.[0]?.toUpperCase() }}
            <div class="status-indicator" :class="{ connected: isConnected }"></div>
          </div>
          <div class="user-info">
            <span class="user-name">{{ currentUser?.username }}</span>
            <span class="connection-status">{{ isConnected ? 'En línea' : 'Desconectado' }}</span>
          </div>
        </div>
        <button @click="handleLogout" class="btn-icon glass" title="Cerrar Sesión">
          <LogOut :size="18" />
        </button>
      </div>

      <div class="search-section">
        <div class="search-wrapper glass">
          <Search :size="16" />
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Buscar chats..." 
          />
        </div>
      </div>

      <div class="conversations-nav">
        <div class="nav-header">
          <span>MENSAJES</span>
          <button @click="showAddModal = true" class="btn-add glass">
            <Plus :size="16" />
          </button>
        </div>

        <div class="conversations-list">
          <div
            v-for="(conv, id) in filteredConversations"
            :key="id"
            class="conversation-item"
            :class="{ active: currentConversationId === id }"
            @click="selectConversation(id)"
          >
            <div class="conv-avatar glass">
              {{ conv.participant?.[0]?.toUpperCase() }}
            </div>
            <div class="conv-details">
              <div class="conv-top">
                <span class="conv-name">{{ conv.participant }}</span>
                <span class="conv-time">{{ formatTime(conv.lastMessageTime) }}</span>
              </div>
              <p class="conv-last-msg">{{ conv.lastMessage || 'Empieza a chatear...' }}</p>
            </div>
            <div v-if="conv.unreadCount" class="unread-badge">
              {{ conv.unreadCount }}
            </div>
          </div>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade-slide" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Modal para nueva conversación -->
    <Transition name="fade">
      <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
        <div class="modal-content glass">
          <h3>Nueva Conversación</h3>
          <p>Introduce el nombre de usuario del destinatario.</p>
          <div class="input-wrapper glass">
            <User :size="18" />
            <input 
              v-model="newUserId" 
              type="text" 
              placeholder="Username" 
              @keyup.enter="startConversation"
            />
          </div>
          <div class="modal-actions">
            <button @click="showAddModal = false" class="btn-text">Cancelar</button>
            <button @click="startConversation" class="btn-primary" :disabled="!newUserId">Crear Chat</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '../stores/chatStore'
import authService from '../services/authService'
import websocketService from '../services/websocketService'
import { 
  LogOut, 
  Search, 
  Plus, 
  User,
  MessageSquare
} from 'lucide-vue-next'

const store = useChatStore()
const router = useRouter()
const searchQuery = ref('')
const showAddModal = ref(false)
const newUserId = ref('')

const currentUser = computed(() => store.currentUser)
const conversations = computed(() => store.conversations)
const currentConversationId = computed(() => store.currentConversationId)
const isConnected = computed(() => store.isConnected)

const filteredConversations = computed(() => {
  const list = Object.values(conversations.value)
  if (!searchQuery.value) return list
  return list.filter(c => 
    c.participant.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const selectConversation = (id) => {
  store.setCurrentConversation(id)
  router.push({ name: 'ChatRoom', params: { id } })
  websocketService.getMessages(id)
}

const startConversation = () => {
  if (!newUserId.value) return
  
  const receiverId = newUserId.value
  const conversationId = [currentUser.value.userId, receiverId].sort().join('_')
  
  store.addConversation(conversationId, receiverId)
  showAddModal.value = false
  newUserId.value = ''
  selectConversation(conversationId)
}

const handleLogout = () => {
  authService.logout()
  websocketService.disconnect()
  store.$reset()
  router.push({ name: 'Login' })
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  // Logic after mounting if needed
})
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  background: #0f172a;
  color: #f8fafc;
}

.sidebar {
  width: 340px;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  z-index: 10;
}

.glass {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(20px);
}

.sidebar-header {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  color: #3b82f6;
  position: relative;
  background: rgba(59, 130, 246, 0.1) !important;
  border-color: rgba(59, 130, 246, 0.2);
}

.status-indicator {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #64748b;
  border: 2px solid #0f172a;
}

.status-indicator.connected {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  font-size: 15px;
}

.connection-status {
  font-size: 11px;
  color: #94a3b8;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.2s;
  border: none;
}

.btn-icon:hover {
  background: rgba(239, 68, 68, 0.1) !important;
  color: #ef4444;
}

.search-section {
  padding: 0 24px 20px;
}

.search-wrapper {
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-radius: 12px;
  color: #64748b;
}

.search-wrapper input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 10px 12px;
  color: #fff;
  font-size: 14px;
}

.search-wrapper input:focus {
  outline: none;
}

.conversations-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.nav-header {
  padding: 0 24px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #475569;
}

.btn-add {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #3b82f6;
  border: none;
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 4px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.conversation-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.conversation-item.active {
  background: rgba(59, 130, 246, 0.1);
  box-shadow: inset 0 0 0 1px rgba(59, 130, 246, 0.2);
}

.conv-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
  color: #e2e8f0;
  flex-shrink: 0;
}

.conv-details {
  flex: 1;
  min-width: 0;
}

.conv-top {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 4px;
}

.conv-name {
  font-weight: 600;
  font-size: 14px;
  color: #f1f5f9;
}

.conv-time {
  font-size: 11px;
  color: #64748b;
}

.conv-last-msg {
  font-size: 13px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.active .conv-name {
  color: #3b82f6;
}

.main-content {
  flex: 1;
  height: 100%;
  position: relative;
}

/* Modal styles */
.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.modal-content {
  width: 360px;
  padding: 32px;
  border-radius: 24px;
  text-align: center;
}

.modal-content h3 {
  margin-bottom: 8px;
}

.modal-content p {
  font-size: 14px;
  color: #94a3b8;
  margin-bottom: 24px;
}

.btn-text {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-weight: 600;
  cursor: pointer;
  padding: 10px 20px;
}

.btn-primary {
  padding: 10px 24px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
