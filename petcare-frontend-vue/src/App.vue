<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <NotificationToast :message="currentMsg" :visible="showToast" @close="showToast = false" />
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue' // <-- Importado 'watch'
import { useRoute } from 'vue-router' // <-- Importado 'useRoute'
import { useAgendamentoStore } from '@/stores/agendamentoStore'
import { useSistemaStore } from '@/stores/sistemaStore'
import NotificationToast from '@/components/NotificationToast.vue'

const route = useRoute() // <-- Inicializado
const agendamentoStore = useAgendamentoStore()
const sistemaStore = useSistemaStore()

const currentMsg = ref('')
const showToast = ref(false)

// NOVO: Vigia a mudança na URL para pegar o slug correto da loja
watch(
  () => route.params.slug,
  (newSlug) => {
    // Se a rota tiver um slug (Ex: /barbearia-do-ze/login), busca as configs daquela loja
    if (newSlug) {
      sistemaStore.fetchConfig(newSlug as string)
    }
  },
  { immediate: true } // Dispara assim que o componente for criado
)

// Escuta mudanças na store para disparar o toast
agendamentoStore.$subscribe((mutation, state) => {
  if (state.unreadCount > 0) {
    currentMsg.value = state.notifications[state.notifications.length - 1] ?? ''
    showToast.value = true
    setTimeout(() => showToast.value = false, 6000)
  }
})
</script>