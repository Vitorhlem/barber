import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const userId = ref<number | null>(Number(sessionStorage.getItem('barberbase_user_id')) || null)
  const userType = ref<string>(sessionStorage.getItem('barberbase_user_tipo') || '')
  const userName = ref<string>(sessionStorage.getItem('barberbase_user_nome') || '')
  
  const barbeariaSlug = ref<string>(sessionStorage.getItem('barberbase_slug') || '') 
  
  const erro = ref<string | null>(null)
  
  const router = useRouter()

  async function login(slug: string, email: string, senha: string) {
    erro.value = null
    try {
      const response = await fetch(`/api/${slug}/login/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, senha })
})
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'E-mail ou senha incorretos para esta barbearia')
      }
      
      const userData = await response.json()
      
      userId.value = userData.id
      userType.value = userData.tipo
      userName.value = userData.nome
      barbeariaSlug.value = slug 
      
      sessionStorage.setItem('barberbase_user_id', String(userData.id))
      sessionStorage.setItem('barberbase_user_tipo', userData.tipo)
      sessionStorage.setItem('barberbase_user_nome', userData.nome)
      sessionStorage.setItem('barberbase_slug', slug) 
      
      router.push(`/${slug}/dashboard`)
    } catch (e: any) {
      erro.value = e.message
    }
  }

  function atualizarSlugLocal(novoSlug: string) {
    barbeariaSlug.value = novoSlug
    sessionStorage.setItem('barberbase_slug', novoSlug)
  }

  function logout() {
    const slugAtual = barbeariaSlug.value 
    
    userId.value = null
    userType.value = ''
    userName.value = ''
    barbeariaSlug.value = ''
    
    sessionStorage.removeItem('barberbase_user_id')
    sessionStorage.removeItem('barberbase_user_tipo')
    sessionStorage.removeItem('barberbase_user_nome')
    sessionStorage.removeItem('barberbase_slug')
    
    if (slugAtual) {
      router.push(`/${slugAtual}/login`)
    } else {
      router.push('/admin/lojas') 
    }
  }

  const isAuthenticated = () => !!userId.value
  
  // NOVO: Função para o router saber se é o dono do sistema
  const isSuperAdmin = () => userType.value === 'admin' 

  return { userId, userType, userName, barbeariaSlug, erro, atualizarSlugLocal, login, logout, isAuthenticated, isSuperAdmin }
})

  