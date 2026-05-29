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
  
  const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  const apiUrl = isLocalhost 
    ? 'http://localhost:8000' 
    : 'https://barberbase-api-backend.onrender.com'

  let socket: WebSocket | null = null
  const carregando = ref(false)
  const erro = ref('')
  // NOVO: Adicionado 'slug' como parâmetro
  async function fetchAgendamentos(slug: string) {
    const auth = useAuthStore()
    if (!auth.userId || !slug) return // Garante que temos o ID do usuário e o link da loja

    try {
      // Injeta o slug no início da rota da API
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

  // NOVO: Passa o slug também para a conexão WebSocket para que, quando ele receber msg,
  // consiga atualizar os agendamentos chamando fetchAgendamentos(slug)
  function connectWebSocket(slug: string) {
    const auth = useAuthStore()
    if (!auth.userId) return
    
    const wsUrl = apiUrl.replace('http', 'ws').replace('https', 'wss')
    socket = new WebSocket(`${wsUrl}/ws/${auth.userId}`)
    
    socket.onmessage = (event) => {
      // Usando JSON.parse para tratar ações
      try {
        const data = JSON.parse(event.data)
        if (data.action === "UPDATE_AGENDAMENTOS") {
            notifications.value.push("Um agendamento foi atualizado!")
            unreadCount.value++
            hasNewNotification.value = true
            fetchAgendamentos(slug) // Passa o slug na hora de atualizar
        }
      } catch (e) {
        // Fallback caso a msg seja um texto simples
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
    carregando, // <-- Adicionado
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