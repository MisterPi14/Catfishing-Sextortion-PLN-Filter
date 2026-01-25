import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useChatStore = defineStore('chat', () => {
  // Estado
  const currentUser = ref(null)
  const conversations = ref({})
  const currentConversationId = ref(null)
  const messages = ref([])
  const alerts = ref([])
  const isConnected = ref(false)
  const isLoading = ref(false)

  // Computed
  const currentMessages = computed(() => {
    if (!currentConversationId.value) return []
    return messages.value.filter(m => m.conversationId === currentConversationId.value)
  })

  const hasUnreadAlerts = computed(() => alerts.value.length > 0)

  // Acciones
  const setCurrentUser = (user) => {
    currentUser.value = user
  }

  const setConnected = (connected) => {
    isConnected.value = connected
  }

  const setCurrentConversation = (conversationId) => {
    currentConversationId.value = conversationId
  }

  const addMessage = (message) => {
    messages.value.push(message)
  }

  const addMessages = (newMessages) => {
    messages.value = [...messages.value, ...newMessages]
  }

  const clearMessages = () => {
    messages.value = []
  }

  const addAlert = (alert) => {
    alerts.value.push(alert)
    // Auto-remover después de 5 segundos
    setTimeout(() => {
      alerts.value = alerts.value.filter(a => a.messageId !== alert.messageId)
    }, 5000)
  }

  const addConversation = (conversationId, participant) => {
    if (!conversations.value[conversationId]) {
      conversations.value[conversationId] = {
        id: conversationId,
        participant,
        lastMessage: null,
        lastMessageTime: null
      }
    }
  }

  const updateConversationLastMessage = (conversationId, message) => {
    if (conversations.value[conversationId]) {
      conversations.value[conversationId].lastMessage = message.content
      conversations.value[conversationId].lastMessageTime = message.timestamp
    }
  }

  const setLoading = (loading) => {
    isLoading.value = loading
  }

  const resetState = () => {
    currentUser.value = null
    conversations.value = {}
    currentConversationId.value = null
    messages.value = []
    alerts.value = []
    isConnected.value = false
    isLoading.value = false
  }

  return {
    // Estado
    currentUser,
    conversations,
    currentConversationId,
    messages,
    alerts,
    isConnected,
    isLoading,
    // Computed
    currentMessages,
    hasUnreadAlerts,
    // Acciones
    setCurrentUser,
    setConnected,
    setCurrentConversation,
    addMessage,
    addMessages,
    clearMessages,
    addAlert,
    addConversation,
    updateConversationLastMessage,
    setLoading,
    resetState
  }
})
