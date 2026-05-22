import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './authStore'

export interface RecordItem {
  id: number;
  name: string;
  date: string;
  nextDate?: string;
  vet?: string;
  weight?: number;
  notes?: string;
  type: string;
}

export interface Pet {
  id: number;
  name: string;
  species: string;
  breed: string | null;
  microchip: string | null;
  birthdate: string | null;
  sex: string;
  photo: string | null;
  vaccines: RecordItem[];
  parasites: RecordItem[];
  consults: RecordItem[];
  weights: RecordItem[];
  documents: RecordItem[];
}

export const usePetStore = defineStore('pets', () => {
  const pets = ref<Pet[]>([])
  const notifications = ref<string[]>([])
  const unreadCount = ref(0)
  
  // Detecção automática de ambiente
  const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const apiUrl = isLocalhost 
    ? 'http://localhost:8000' 
    : 'https://petcare-api-backend.onrender.com';

  let socket: WebSocket | null = null

  async function fetchPets() {
    const auth = useAuthStore()
    if (!auth.userId) return

    try {
      const url = auth.userType === 'veterinario' ? '/pets/' : `/usuarios/${auth.userId}/pets/`
      const response = await fetch(`${apiUrl}${url}`)
      if (response.ok) {
        const data = await response.json()
        
        pets.value = data.map((p: any) => ({
          id: p.id,
          name: p.nome,
          species: p.especie,
          breed: p.raca,
          microchip: p.microchip,
          birthdate: p.data_nascimento,
          sex: p.sexo,
          photo: p.foto,
          vaccines: p.registros.filter((r: any) => r.tipo === 'vacina').map(mapRecord),
          parasites: p.registros.filter((r: any) => r.tipo === 'parasita').map(mapRecord),
          consults: p.registros.filter((r: any) => r.tipo === 'consulta').map(mapRecord),
          weights: p.registros.filter((r: any) => r.tipo === 'peso').map(mapRecord),
          documents: p.registros.filter((r: any) => r.tipo === 'documento').map(mapRecord),
        }))
      }
    } catch (error) {
      console.error("Erro ao carregar API:", error)
    }
  }

  function mapRecord(r: any): RecordItem {
    return { 
      id: r.id, 
      name: r.nome, 
      date: r.data, 
      nextDate: r.proxima_data, 
      vet: r.anotacoes, 
      weight: r.peso, 
      notes: r.anotacoes, 
      type: r.tipo 
    }
  }

  function connectWebSocket() {
    const auth = useAuthStore()
    if (!auth.userId) return
    
    // Converte http para ws ou https para wss
    const wsUrl = apiUrl.replace('http', 'ws')
    socket = new WebSocket(`${wsUrl}/ws/${auth.userId}`)
    
    socket.onmessage = (event) => {
      // Adiciona na lista de notificações e incrementa o contador
      notifications.value.push(event.data)
      unreadCount.value++
      
      // Atualiza os dados automaticamente após receber notificação
      fetchPets()
    }
    
    socket.onclose = () => {
      // Tenta reconectar após 5 segundos se cair
      setTimeout(connectWebSocket, 5000)
    }
  }

  function clearNotifications() {
    unreadCount.value = 0
  }

  return { 
    pets, 
    notifications, 
    unreadCount, 
    fetchPets, 
    connectWebSocket, 
    clearNotifications, 
    apiUrl 
  }
})