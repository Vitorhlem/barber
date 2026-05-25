<template>
  <q-page padding>
    <q-card style="max-width: 400px; margin: auto;">
      <q-card-section>
        <div class="text-h6">Integrações</div>
      </q-card-section>
      <q-card-section>
        <q-btn 
          color="primary" 
          icon="calendar_month" 
          label="Conectar Google Agenda" 
          @click="iniciarAuthGoogle" 
          unelevated
        />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/authStore'
const authStore = useAuthStore()

const iniciarAuthGoogle = async () => {
  // 1. Pede a URL de login ao backend passando o ID do barbeiro logado
  const response = await fetch(`http://localhost:8000/auth/google/login?user_id=${authStore.userId}`)
  const data = await response.json()
  
  // 2. Redireciona para o Google
  if (data.url) {
    window.location.href = data.url
  }
}
</script>