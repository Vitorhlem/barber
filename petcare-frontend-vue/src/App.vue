<script setup lang="ts">
import { ref } from 'vue'
import { useAgendamentoStore } from '@/stores/agendamentoStore'
import NotificationToast from '@/components/NotificationToast.vue'

const agendamentoStore = useAgendamentoStore()
const currentMsg = ref('')
const showToast = ref(false)

// Escuta mudanças na store para disparar o toast
agendamentoStore.$subscribe((mutation, state) => {
  // Verifique se a estrutura da store é exatamente essa (unreadCount/notifications)
  if (state.unreadCount > 0) {
    currentMsg.value = state.notifications[state.notifications.length - 1] ?? ''
    showToast.value = true
    setTimeout(() => showToast.value = false, 6000)
  }
})
</script>

<template>
  <q-layout view="hHh lpR fFf">
    
    <q-page-container>
      
      <NotificationToast :message="currentMsg" :visible="showToast" @close="showToast = false" />
      
      <router-view />
      
    </q-page-container>
    
  </q-layout>
</template>