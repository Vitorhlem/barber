import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const userId = ref<string | null>(localStorage.getItem('petcareplus_user_id'))
  const userType = ref<string>(localStorage.getItem('petcareplus_user_tipo') || 'tutor')
  const router = useRouter()

  function login(id: string, type: string) {
    userId.value = id
    userType.value = type
    localStorage.setItem('petcareplus_user_id', id)
    localStorage.setItem('petcareplus_user_tipo', type)
  }

  function logout() {
    userId.value = null
    userType.value = 'tutor'
    localStorage.removeItem('petcareplus_user_id')
    localStorage.removeItem('petcareplus_user_tipo')
    router.push('/login')
  }

  const isAuthenticated = () => !!userId.value

  return { userId, userType, login, logout, isAuthenticated }
})