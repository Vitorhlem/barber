import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSistemaStore = defineStore('sistema', () => {
  const nomeBarbearia = ref('BarberBase')
  const logoUrl = ref('')

  // NOVO: A função agora exige que você passe o slug da barbearia
  const fetchConfig = async (slug: string) => {
    if (!slug) return; // Evita requisições quebradas
    
    try {
      // API com o prefixo dinâmico do slug
      const res = await fetch(`/api/${slug}/sistema/config`)
      
      if (res.ok) {
        const data = await res.json()
        nomeBarbearia.value = data.nome_barbearia
        logoUrl.value = data.logo_url || ''
        document.title = data.nome_barbearia // Muda o título da aba do navegador
      }
    } catch (e) {
      console.error('Erro ao buscar configuração do sistema para a loja: ' + slug, e)
    }
  }

  return { nomeBarbearia, logoUrl, fetchConfig }
})