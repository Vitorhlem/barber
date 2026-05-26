<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <NotificationToast :message="currentMsg" :visible="showToast" @close="showToast = false" />
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAgendamentoStore } from '@/stores/agendamentoStore'
import { useSistemaStore } from '@/stores/sistemaStore'
import NotificationToast from '@/components/NotificationToast.vue'

const agendamentoStore = useAgendamentoStore()
const sistemaStore = useSistemaStore()

const currentMsg = ref('')
const showToast = ref(false)

onMounted(() => {
  sistemaStore.fetchConfig()
})

// Escuta mudanças na store para disparar o toast
agendamentoStore.$subscribe((mutation, state) => {
  if (state.unreadCount > 0) {
    currentMsg.value = state.notifications[state.notifications.length - 1] ?? ''
    showToast.value = true
    setTimeout(() => showToast.value = false, 6000)
  }
})
</script>