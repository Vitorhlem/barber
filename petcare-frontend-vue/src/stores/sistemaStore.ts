import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSistemaStore = defineStore('sistema', () => {
  const nomeBarbearia = ref('BarberBase')
  const logoUrl = ref('')

  const fetchConfig = async () => {
    try {
      const res = await fetch('http://localhost:8000/sistema/config')
      if (res.ok) {
        const data = await res.json()
        nomeBarbearia.value = data.nome_barbearia
        logoUrl.value = data.logo_url || ''
        document.title = data.nome_barbearia // Muda o título da aba do navegador
      }
    } catch (e) {
      console.error('Erro ao buscar configuração do sistema', e)
    }
  }

  return { nomeBarbearia, logoUrl, fetchConfig }
})