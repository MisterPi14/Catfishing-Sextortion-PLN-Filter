import { useChatStore } from '../stores/chatStore'

class WebSocketService {
  constructor() {
    this.ws = null
    this.url = import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8080'
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
  }

  connect(token) {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${this.url}?token=${token}`)

        this.ws.onopen = () => {
          console.log('WebSocket conectado')
          const store = useChatStore()
          store.setConnected(true)
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          this.handleMessage(JSON.parse(event.data))
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('WebSocket desconectado')
          const store = useChatStore()
          store.setConnected(false)
          this.attemptReconnect(token)
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  handleMessage(data) {
    const store = useChatStore()
    const { action, data: payload } = data

    switch (action) {
      case 'messageReceived':
        // Determinar el ID real de la conversación desde el payload
        const realConversationId = payload.conversationId;
        
        // Determinar quién es la "otra persona" para mostrar en la lista
        // Si yo mandé el mensaje (Echo), el otro es el receiver. Si recibí (Inbound), es el sender.
        const otherParticipant = payload.senderId === store.currentUser?.userId 
            ? payload.receiverId 
            : payload.senderId;

        // Si la conversación no existe en el store local, crearla automáticamente
        if (realConversationId && !store.conversations[realConversationId]) {
             store.addConversation(realConversationId, otherParticipant);
        }

        // Agregar mensaje usando el ID correcto
        store.addMessage({
          ...payload,
          conversationId: realConversationId
        })
        
        // Actualizar la vista previa en la barra lateral
        if (realConversationId) {
            store.updateConversationLastMessage(realConversationId, payload)
        }
        break

      case 'messagesHistory':
        store.clearMessages()
        store.addMessages(payload.messages)
        break

      case 'riskAlert':
        store.addAlert({
          messageId: payload.messageId,
          threatType: payload.threatType,
          confidence: payload.confidence,
          riskLevel: payload.riskLevel,
          message: payload.message
        })
        break

      default:
        console.warn('Unknown action:', action)
    }
  }

  sendMessage(conversationId, receiverId, content) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket no está conectado')
      return false
    }

    this.ws.send(JSON.stringify({
      action: 'sendMessage',
      data: {
        conversationId,
        receiverId,
        content
      }
    }))

    return true
  }

  getMessages(conversationId, limit = 50, offset = 0) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket no está conectado')
      return false
    }

    this.ws.send(JSON.stringify({
      action: 'getMessages',
      data: {
        conversationId,
        limit,
        offset
      }
    }))

    return true
  }

  attemptReconnect(token) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Intentando reconectar... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      setTimeout(() => {
        this.connect(token).catch(error => {
          console.error('Reconexión fallida:', error)
        })
      }, this.reconnectDelay)
    } else {
      console.error('Máximo de intentos de reconexión alcanzado')
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

export default new WebSocketService()
