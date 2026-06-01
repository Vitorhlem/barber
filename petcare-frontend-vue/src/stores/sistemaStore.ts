import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSistemaStore = defineStore('sistema', () => {
  const nomeBarbearia = ref('BarberBase')
  const logoUrl = ref('')

  const fetchConfig = async (slug: string) => {
    if (!slug) return; 
    
    try {
      const res = await fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${slug}/sistema/config`)
      
      if (res.ok) {
        const data = await res.json()
        nomeBarbearia.value = data.nome_barbearia
        logoUrl.value = data.logo_url || ''
        document.title = data.nome_barbearia 
      }
    } catch (e) {
      console.error('Erro ao buscar configuração do sistema para a loja: ' + slug, e)
    }
  }

  return { nomeBarbearia, logoUrl, fetchConfig }
})