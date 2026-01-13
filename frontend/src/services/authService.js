class AuthService {
  constructor() {
    this.token = localStorage.getItem('authToken')
    this.user = JSON.parse(localStorage.getItem('user') || 'null')
    this.apiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:3000/dev').replace(/\/$/, '')
  }

  setToken(token) {
    this.token = token
    localStorage.setItem('authToken', token)
  }

  setUser(user) {
    this.user = user
    localStorage.setItem('user', JSON.stringify(user))
  }

  getToken() {
    return this.token
  }

  getUser() {
    return this.user
  }

  isAuthenticated() {
    return !!this.token && !!this.user
  }

  logout() {
    this.token = null
    this.user = null
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
  }

  async login(username, password) {
    try {
      const response = await fetch(`${this.apiUrl}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al iniciar sesión')
      }

      this.setToken(data.token)
      this.setUser(data.user)
      return data.user
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  async register(username, password) {
    try {
      const response = await fetch(`${this.apiUrl}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error al registrar usuario')
      }

      return data
    } catch (error) {
      console.error('Registration error:', error)
      throw error
    }
  }
}

export default new AuthService()
