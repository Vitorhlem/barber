import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const contacts = ref({ barbearia: '', suporte: '' })
  
  const savedContacts = localStorage.getItem('barberbase_contacts')
  if (savedContacts) {
    contacts.value = JSON.parse(savedContacts)
  }

  function saveContacts(barbearia: string, suporte: string) {
    contacts.value = { barbearia, suporte }
    localStorage.setItem('barberbase_contacts', JSON.stringify(contacts.value))
  }

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

  return { contacts, saveContacts, a11y, applyAccessibility }
})