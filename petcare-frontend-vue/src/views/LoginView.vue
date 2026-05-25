<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page class="flex flex-center bg-grey-2">
        
        <q-card class="q-pa-lg shadow-2 rounded-borders" style="width: 100%; max-width: 420px;">
          <q-card-section class="text-center">
            <q-avatar size="64px" color="primary" text-color="white" icon="content_cut" />
            <div class="text-h5 q-mt-md text-weight-bold">BarberBase</div>
            <div class="text-subtitle2 text-grey-7">Inicie sessão para gerir a sua agenda</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit.prevent="efetuarLogin" class="q-gutter-md">
              <q-input
                v-model="email"
                label="E-mail"
                type="email"
                outlined
                color="primary"
                :rules="[val => !!val || 'O e-mail é obrigatório']"
              >
                <template v-slot:prepend>
                  <q-icon name="email" />
                </template>
              </q-input>

              <q-input
                v-model="senha"
                label="Palavra-passe"
                type="password"
                outlined
                color="primary"
                :rules="[val => !!val || 'A palavra-passe é obrigatória']"
              >
                <template v-slot:prepend>
                  <q-icon name="lock" />
                </template>
              </q-input>

              <div v-if="authStore.erro" class="text-negative text-center text-weight-medium">
                {{ authStore.erro }}
              </div>

              <q-btn
                type="submit"
                color="primary"
                class="full-width q-mt-md"
                size="large"
                label="Iniciar Sessão"
                :loading="carregando"
                unelevated
              />
            </q-form>
          </q-card-section>
        </q-card>

      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const email = ref('')
const senha = ref('')
const carregando = ref(false)

const efetuarLogin = async () => {
  carregando.value = true
  await authStore.login(email.value, senha.value)
  carregando.value = false
}
</script>

<style scoped>
/* O Quasar remove a necessidade de 90% do CSS manual! */
</style>