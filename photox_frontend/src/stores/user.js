import { defineStore } from 'pinia'
import api from '@/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    isLoggedIn: false
  }),
  actions: {
    setUser(userData) {
      this.user = userData
      this.isLoggedIn = true
      localStorage.setItem('user', JSON.stringify(userData))
    },
    logout() {
      this.user = null
      this.isLoggedIn = false
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    },
    async initialize() {
      const token = localStorage.getItem('token')
      if (!token) {
        this.user = null
        this.isLoggedIn = false
        return
      }
      
      try {
        const response = await api.auth.getCurrentUser()
        this.user = response.data
        this.isLoggedIn = true
        localStorage.setItem('user', JSON.stringify(response.data))
      } catch (error) {
        console.error('Token 验证失败:', error)
        this.logout()
      }
    }
  }
})  