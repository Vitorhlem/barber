import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const userId = ref<number | null>(Number(sessionStorage.getItem('barberbase_user_id')) || null)
  const userType = ref<string>(sessionStorage.getItem('barberbase_user_tipo') || '')
  const userName = ref<string>(sessionStorage.getItem('barberbase_user_nome') || '')
  
  // NOVO: Adicionado para guardar de qual barbearia esse usuário é
  const barbeariaSlug = ref<string>(sessionStorage.getItem('barberbase_slug') || '') 
  
  const erro = ref<string | null>(null)
  
  const router = useRouter()

  // NOVO: Recebe o slug como primeiro parâmetro
  async function login(slug: string, email: string, senha: string) {
    erro.value = null
    try {
      // API agora recebe o slug dinamicamente
      const response = await fetch(`http://localhost:8000/${slug}/login/`, {
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
      barbeariaSlug.value = slug // Atualiza o state
      
      sessionStorage.setItem('barberbase_user_id', String(userData.id))
      sessionStorage.setItem('barberbase_user_tipo', userData.tipo)
      sessionStorage.setItem('barberbase_user_nome', userData.nome)
      sessionStorage.setItem('barberbase_slug', slug) // Salva o slug na sessão
      
      // Redireciona para o dashboard correto
      router.push(`/${slug}/dashboard`)
    } catch (e: any) {
      erro.value = e.message
    }
  }

  function logout() {
    const slugAtual = barbeariaSlug.value // Salva o slug temporariamente para saber para onde mandar
    
    userId.value = null
    userType.value = ''
    userName.value = ''
    barbeariaSlug.value = ''
    
    sessionStorage.removeItem('barberbase_user_id')
    sessionStorage.removeItem('barberbase_user_tipo')
    sessionStorage.removeItem('barberbase_user_nome')
    sessionStorage.removeItem('barberbase_slug')
    
    // Volta para o login DAQUELA barbearia específica
    if (slugAtual) {
      router.push(`/${slugAtual}/login`)
    } else {
      router.push('/admin/lojas') // Fallback caso não tenha slug
    }
  }

  const isAuthenticated = () => !!userId.value

  return { userId, userType, userName, barbeariaSlug, erro, login, logout, isAuthenticated }
})