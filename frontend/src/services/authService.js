class AuthService {
  constructor() {
    this.token = localStorage.getItem('authToken')
    this.user = JSON.parse(localStorage.getItem('user') || 'null')
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

  // Mock login para desarrollo
  mockLogin(userId, username) {
    const mockToken = `mock_token_${userId}_${Date.now()}`
    const mockUser = {
      userId,
      username,
      email: `${username}@example.com`
    }
    this.setToken(mockToken)
    this.setUser(mockUser)
    return mockUser
  }
}

export default new AuthService()
