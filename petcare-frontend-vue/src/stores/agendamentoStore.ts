import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './authStore'

export interface Agendamento {
  id: number;
  cliente_id: number;
  barbeiro_id: number;
  servico: string;
  data_hora: string;
  status: string;
  cliente_nome: string;
  barbeiro_nome: string;
  preco: number; // <--- NOVO
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

  async function fetchAgendamentos() {
    const auth = useAuthStore()
    if (!auth.userId) return

    try {
      const url = auth.userType === 'barbeiro' 
        ? `/agendamentos/barbeiro/${auth.userId}` 
        : `/usuarios/${auth.userId}/agendamentos` 
        
      const response = await fetch(`${apiUrl}${url}`)
      if (response.ok) {
        agendamentos.value = await response.json()
      }
    } catch (error) {
      console.error("Erro ao carregar API:", error)
    }
  }

  function connectWebSocket() {
    const auth = useAuthStore()
    if (!auth.userId) return
    
    const wsUrl = apiUrl.replace('http', 'ws').replace('https', 'wss')
    socket = new WebSocket(`${wsUrl}/ws/${auth.userId}`)
    
    socket.onmessage = (event) => {
      notifications.value.push(event.data)
      unreadCount.value++
      hasNewNotification.value = true
      
      fetchAgendamentos()
    }
    
    socket.onclose = () => {
      setTimeout(connectWebSocket, 5000)
    }
  }

  function clearNotifications() {
    unreadCount.value = 0
    hasNewNotification.value = false
  }

  return { 
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