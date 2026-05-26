<template>
  <q-layout view="hHh lpR fFf">
    
    <q-header elevated v-if="authStore.isSuperAdmin()" class="bg-dark text-white">
      <q-toolbar>
        <q-toolbar-title>
          Painel SaaS - Super Admin
        </q-toolbar-title>
        
        <q-btn 
          flat 
          v-if="authStore.barbeariaSlug" 
          :to="`/${authStore.barbeariaSlug}/dashboard`" 
          label="Ver Dashboard Local" 
        />
        
        <q-btn 
          flat 
          to="/admin/lojas" 
          label="Gerenciar Barbearias" 
          color="warning" 
          class="q-ml-sm"
        />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <NotificationToast :message="currentMsg" :visible="showToast" @close="showToast = false" />
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAgendamentoStore } from '@/stores/agendamentoStore'
import { useSistemaStore } from '@/stores/sistemaStore'
import NotificationToast from '@/components/NotificationToast.vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const route = useRoute()
const agendamentoStore = useAgendamentoStore()
const sistemaStore = useSistemaStore()

const currentMsg = ref('')
const showToast = ref(false)

// Vigia a mudança na URL para pegar o slug correto da loja
watch(
  () => route.params.slug,
  (newSlug) => {
    // Se a rota tiver um slug (Ex: /barbearia-do-ze/login), busca as configs daquela loja
    if (newSlug) {
      sistemaStore.fetchConfig(newSlug as string)
    }
  },
  { immediate: true }
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