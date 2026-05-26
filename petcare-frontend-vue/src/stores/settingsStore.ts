import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const contacts = ref({ barbearia: '', suporte: '' })
  
  // NOVO: Função para carregar contatos específicos daquela barbearia (slug)
  function loadContacts(slug: string) {
    if (!slug) return
    const savedContacts = localStorage.getItem(`barberbase_contacts_${slug}`)
    if (savedContacts) {
      contacts.value = JSON.parse(savedContacts)
    } else {
      contacts.value = { barbearia: '', suporte: '' } // Limpa se não houver dados desta loja
    }
  }

  // NOVO: Função para salvar contatos vinculados à barbearia (slug)
  function saveContacts(slug: string, barbearia: string, suporte: string) {
    if (!slug) return
    contacts.value = { barbearia, suporte }
    localStorage.setItem(`barberbase_contacts_${slug}`, JSON.stringify(contacts.value))
  }

  // Acessibilidade permanece GLOBAL (se o cliente tem problema de visão, vale para todas as lojas)
  const a11y = ref({
    highContrast: false,
    largeText: false,
    dyslexiaFont: false,
    highlightLinks: false,
  })

  const savedA11y = localStorage.getItem('barberbase_a11y')
  if (savedA11y) {
    a11y.value = JSON.parse(savedA11y)
  }

  function applyAccessibility() {
    document.body.classList.toggle('high-contrast', a11y.value.highContrast)
    document.documentElement.classList.toggle('large-text', a11y.value.largeText)
    document.body.classList.toggle('dyslexia-font', a11y.value.dyslexiaFont)
    document.body.classList.toggle('highlight-links', a11y.value.highlightLinks)
  }

  watch(a11y, (newVal) => {
    localStorage.setItem('barberbase_a11y', JSON.stringify(newVal))
    applyAccessibility()
  }, { deep: true })

  return { contacts, loadContacts, saveContacts, a11y, applyAccessibility }
})