<script setup lang="ts">
import { ref } from 'vue'
import { usePetStore } from '@/stores/petStore'
import NotificationToast from '@/components/NotificationToast.vue'

const petStore = usePetStore()
const currentMsg = ref('')
const showToast = ref(false)

// Escuta mudanças na store para disparar o toast
petStore.$subscribe((mutation, state) => {
  if (state.unreadCount > 0) {
    currentMsg.value = state.notifications[state.notifications.length - 1] ?? ''
    showToast.value = true
    setTimeout(() => showToast.value = false, 6000)
  }
})
</script>

<template>
  <NotificationToast :message="currentMsg" :visible="showToast" @close="showToast = false" />
  <router-view />
</template>