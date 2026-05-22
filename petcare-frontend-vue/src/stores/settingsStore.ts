import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  // --- CONTATOS DE EMERGÊNCIA ---
  const contacts = ref({ vet: '', emergency: '' })
  
  const savedContacts = localStorage.getItem('petcareplus_contacts')
  if (savedContacts) {
    contacts.value = JSON.parse(savedContacts)
  }

  function saveContacts(vet: string, emergency: string) {
    contacts.value = { vet, emergency }
    localStorage.setItem('petcareplus_contacts', JSON.stringify(contacts.value))
  }

  // --- ACESSIBILIDADE ---
  const a11y = ref({
    highContrast: false,
    largeText: false,
    dyslexiaFont: false,
    highlightLinks: false,
  })

  const savedA11y = localStorage.getItem('petcareplus_a11y')
  if (savedA11y) {
    a11y.value = JSON.parse(savedA11y)
  }

  // Aplica as classes no <body> do HTML
  function applyAccessibility() {
    document.body.classList.toggle('high-contrast', a11y.value.highContrast)
    document.documentElement.classList.toggle('large-text', a11y.value.largeText)
    document.body.classList.toggle('dyslexia-font', a11y.value.dyslexiaFont)
    document.body.classList.toggle('highlight-links', a11y.value.highlightLinks)
  }

  // Assiste mudanças no objeto a11y e salva automaticamente
  watch(a11y, (newVal) => {
    localStorage.setItem('petcareplus_a11y', JSON.stringify(newVal))
    applyAccessibility()
  }, { deep: true })

  return { contacts, saveContacts, a11y, applyAccessibility }
})