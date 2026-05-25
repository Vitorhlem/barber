import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const userId = ref<number | null>(Number(localStorage.getItem('barberbase_user_id')) || null)
  const userType = ref<string>(localStorage.getItem('barberbase_user_tipo') || '')
  const userName = ref<string>(localStorage.getItem('barberbase_user_nome') || '') // <--- NOVO
  const erro = ref<string | null>(null)
  
  const router = useRouter()

  async function login(email: string, senha: string) {
    erro.value = null
    try {
      const response = await fetch('http://localhost:8000/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'E-mail ou senha incorretos')
      }
      
      const userData = await response.json()
      
      userId.value = userData.id
      userType.value = userData.tipo
      userName.value = userData.nome // <--- NOVO
      
      localStorage.setItem('barberbase_user_id', String(userData.id))
      localStorage.setItem('barberbase_user_tipo', userData.tipo)
      localStorage.setItem('barberbase_user_nome', userData.nome) // <--- NOVO
      
      router.push('/dashboard')
    } catch (e: any) {
      erro.value = e.message
    }
  }

  function logout() {
    userId.value = null
    userType.value = ''
    userName.value = '' // <--- NOVO
    localStorage.removeItem('barberbase_user_id')
    localStorage.removeItem('barberbase_user_tipo')
    localStorage.removeItem('barberbase_user_nome') // <--- NOVO
    router.push('/login')
  }

  const isAuthenticated = () => !!userId.value

  return { userId, userType, userName, erro, login, logout, isAuthenticated }
})