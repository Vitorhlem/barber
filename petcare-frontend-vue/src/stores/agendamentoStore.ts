import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './authStore'

// Definição da interface opcional para tipagem do Typescript
interface Usuario {
  id: number;
  nome: string;
  email?: string;
  telefone?: string;
}

export interface Agendamento {
  id: number;
  cliente_id: number;
  barbeiro_id: number;
  servico: string;
  data_hora: string;
  status: string;
  cliente_nome: string;
  barbeiro_nome: string;
  preco: number; 
  cliente?: Usuario;
  barbeiro?: Usuario;
}

export const useAgendamentoStore = defineStore('agendamentos', () => {
  const agendamentos = ref<Agendamento[]>([])
  const notifications = ref<string[]>([])
  const unreadCount = ref(0)
  const hasNewNotification = ref(false)
  
  // CORREÇÃO: Utilizando a rota /api configurada no Nginx do servidor
  const apiUrl = '/api'

  let socket: WebSocket | null = null
  const carregando = ref(false)
  const erro = ref('')
  
  async function fetchAgendamentos(slug: string) {
    const auth = useAuthStore()
    if (!auth.userId || !slug) return 

    try {
      const url = auth.userType === 'barbeiro' || auth.userType === 'admin'
        ? `/${slug}/agendamentos/barbeiro/${auth.userId}` 
        : `/${slug}/usuarios/${auth.userId}/agendamentos` 
        
      const response = await fetch(`${apiUrl}${url}`)
      if (response.ok) {
        agendamentos.value = await response.json()
      }
    } catch (error) {
      console.error("Erro ao carregar API:", error)
    }
  }

  function connectWebSocket(slug: string) {
    const auth = useAuthStore()
    if (!auth.userId) return
    
    // CORREÇÃO: Montagem dinâmica da URL do WebSocket para funcionar em Produção e Local
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsBaseUrl = `${protocol}//${host}/api`;
    
    socket = new WebSocket(`${wsBaseUrl}/ws/${auth.userId}`)
    
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.action === "UPDATE_AGENDAMENTOS") {
            notifications.value.push("Um agendamento foi atualizado!")
            unreadCount.value++
            hasNewNotification.value = true
            fetchAgendamentos(slug) 
        }
      } catch (e) {
        notifications.value.push(event.data)
        unreadCount.value++
        hasNewNotification.value = true
        fetchAgendamentos(slug)
      }
    }
    
    socket.onclose = () => {
      setTimeout(() => connectWebSocket(slug), 5000)
    }
  }

  function clearNotifications() {
    unreadCount.value = 0
    hasNewNotification.value = false
  }

  return { 
    carregando, 
    erro,
    agendamentos, 
    notifications, 
    unreadCount, 
    fetchAgendamentos,
    hasNewNotification,
    connectWebSocket, 
    clearNotifications, 
    apiUrl 
  }
})