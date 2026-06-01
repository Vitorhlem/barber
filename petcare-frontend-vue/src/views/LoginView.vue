<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page class="flex flex-center login-page q-pa-md">
        
        <q-card class="login-card shadow-12">
          <q-card-section class="text-center q-pt-xl q-pb-sm">
            <div class="logo-circle shadow-3" style="overflow: hidden; background-color: white;">
              <q-img v-if="sistemaStore.logoUrl" :src="sistemaStore.logoUrl" fit="cover" style="width: 100%; height: 100%;" />
              <q-icon v-else name="content_cut" class="logo-icon" color="primary" />
            </div>
            <div class="text-h4 q-mt-lg text-weight-bolder title-text">{{ sistemaStore.nomeBarbearia }}</div>
            <div class="text-subtitle2 q-mt-sm subtitle-text text-weight-medium">O seu estilo, o nosso tempo.</div>
          </q-card-section>

          <q-tabs
            v-model="aba"
            dense
            class="custom-tabs q-mx-lg q-mt-sm q-mb-md"
            active-color="primary"
            indicator-color="primary"
            align="justify"
            narrow-indicator
          >
            <q-tab name="login" label="Iniciar Sessão" no-caps class="text-weight-bold" />
            <q-tab name="registo" label="Criar Conta" no-caps class="text-weight-bold" />
          </q-tabs>

          <q-tab-panels v-model="aba" animated class="bg-transparent">
            
            <q-tab-panel name="login" class="q-px-xl q-pb-xl q-pt-none">
              <q-form @submit.prevent="efetuarLogin" class="q-gutter-y-md q-mt-sm">
                
                <q-input v-model="emailLogin" label="E-mail" type="email" outlined color="primary" class="custom-input" :rules="[val => !!val || 'O e-mail é obrigatório']" hide-bottom-space>
                  <template v-slot:prepend><q-icon name="email" color="grey-6" /></template>
                </q-input>

                <q-input v-model="senhaLogin" label="Palavra-passe" type="password" outlined color="primary" class="custom-input" :rules="[val => !!val || 'A palavra-passe é obrigatória']" hide-bottom-space>
                  <template v-slot:prepend><q-icon name="lock" color="grey-6" /></template>
                </q-input>

                <div v-if="authStore.erro && aba === 'login'" class="alert-box">
                  <q-icon name="error" class="q-mr-xs" size="18px" /> {{ authStore.erro }}
                </div>

                <q-btn type="submit" color="primary" class="full-width q-mt-lg submit-btn" size="lg" label="Entrar" :loading="carregando" unelevated no-caps />
              
              </q-form>
            </q-tab-panel>

            <q-tab-panel name="registo" class="q-px-xl q-pb-xl q-pt-none">
              <q-form @submit.prevent="efetuarRegisto" class="q-gutter-y-md q-mt-xs">
                
                <q-input v-model="formRegisto.nome" label="Nome Completo" outlined color="primary" class="custom-input" :rules="[val => !!val || 'O nome é obrigatório']" hide-bottom-space>
                  <template v-slot:prepend><q-icon name="person" color="grey-6" /></template>
                </q-input>

                <q-input v-model="formRegisto.telefone" label="Telemóvel / WhatsApp" type="tel" outlined color="primary" class="custom-input" hint="Para recebermos o seu contacto" hide-bottom-space>
                  <template v-slot:prepend><q-icon name="phone" color="grey-6" /></template>
                </q-input>

                <q-input v-model="formRegisto.email" label="E-mail" type="email" outlined color="primary" class="custom-input" :rules="[val => !!val || 'O e-mail é obrigatório']" hide-bottom-space>
                  <template v-slot:prepend><q-icon name="email" color="grey-6" /></template>
                </q-input>

                <q-input v-model="formRegisto.senha" label="Criar Palavra-passe" type="password" outlined color="primary" class="custom-input" :rules="[val => val.length >= 6 || 'Mínimo de 6 caracteres']" hide-bottom-space>
                  <template v-slot:prepend><q-icon name="lock" color="grey-6" /></template>
                </q-input>

                <div v-if="erroRegisto" class="alert-box">
                  <q-icon name="error" class="q-mr-xs" size="18px" /> {{ erroRegisto }}
                </div>

                <q-btn type="submit" color="primary" class="full-width q-mt-lg submit-btn" size="lg" label="Registar e Entrar" :loading="carregando" unelevated no-caps />
              
              </q-form>
            </q-tab-panel>
          </q-tab-panels>

        </q-card>

      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router' // <-- IMPORTADO PARA LER O SLUG DA URL
import { useAuthStore } from '@/stores/authStore'
import { useQuasar } from 'quasar'
import { useSistemaStore } from '@/stores/sistemaStore'

const route = useRoute() // <-- INICIALIZADO
const sistemaStore = useSistemaStore()
const authStore = useAuthStore()
const $q = useQuasar()

const aba = ref('login')
const carregando = ref(false)

// Campos de Login
const emailLogin = ref('')
const senhaLogin = ref('')

// Campos de Registo
const erroRegisto = ref('')
const formRegisto = ref({
  nome: '',
  telefone: '',
  email: '',
  senha: '',
  tipo: 'cliente'
})

const efetuarLogin = async () => {
  carregando.value = true
  const slug = route.params.slug as string // Pega o slug da URL atual
  await authStore.login(slug, emailLogin.value, senhaLogin.value) // Envia o slug
  carregando.value = false
}

const efetuarRegisto = async () => {
  erroRegisto.value = ''
  carregando.value = true
  const slug = route.params.slug as string // Pega o slug da URL atual
  
  try {
    // API atualizada para apontar para a barbearia correta
    const response = await fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${slug}/usuarios/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formRegisto.value)
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Erro ao criar conta.')
    }

    $q.notify({ type: 'positive', message: 'Conta criada com sucesso!', position: 'top' })
    
    // Autentica o usuário recém-criado na barbearia correta
    await authStore.login(slug, formRegisto.value.email, formRegisto.value.senha)

  } catch (error: any) {
    erroRegisto.value = error.message
  } finally {
    carregando.value = false
  }
}
</script>

<style scoped>
/* O seu estilo original não foi alterado */
.login-page {
  --cor-fundo-inicio: #1a1a2e; 
  --cor-fundo-fim: #16213e;    
  --cor-cartao-bg: rgba(255, 255, 255, 0.97);
  --borda-cartao: 24px;
  --cor-texto-titulo: #1f2937;
  --cor-texto-subtitulo: #6b7280;
  --cor-destaque: var(--q-primary); 
  --cor-destaque-hover: #155bb5;

  background: linear-gradient(135deg, var(--cor-fundo-inicio) 0%, var(--cor-fundo-fim) 100%);
  min-height: 100vh;
}
.login-card {
  width: 100%;
  max-width: 440px;
  background: var(--cor-cartao-bg);
  border-radius: var(--borda-cartao);
  backdrop-filter: blur(10px);
}
.logo-circle {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  background-color: var(--cor-destaque);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}
.logo-circle:hover {
  transform: scale(1.05);
}
.logo-icon {
  font-size: 40px;
  color: white;
}
.title-text {
  color: var(--cor-texto-titulo);
  letter-spacing: -1px;
}
.subtitle-text {
  color: var(--cor-texto-subtitulo);
}
.custom-tabs {
  border-bottom: 2px solid #f1f5f9;
  color: #94a3b8;
}
.custom-input :deep(.q-field__control) {
  border-radius: 12px;
}
.submit-btn {
  border-radius: 12px;
  font-weight: bold;
  letter-spacing: 0.5px;
  transition: background-color 0.3s ease;
}
.alert-box {
  background-color: #fee2e2;
  color: #b91c1c;
  border: 1px solid #f87171;
  padding: 10px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>