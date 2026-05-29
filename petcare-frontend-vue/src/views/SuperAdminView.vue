<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page class="flex flex-center admin-page q-pa-md">
        
        <q-card class="admin-card shadow-12">
          <q-card-section class="text-center q-pt-xl q-pb-sm">
            <q-icon name="admin_panel_settings" size="60px" color="primary" />
            <div class="text-h4 q-mt-md text-weight-bolder title-text">Super Admin</div>
            <div class="text-subtitle2 q-mt-sm subtitle-text text-weight-medium">Gestão de Inquilinos (SaaS)</div>
          </q-card-section>

          <q-card-section class="q-px-xl q-pb-xl">
            <div class="text-h6 q-mb-md text-center text-grey-8">Adicionar Nova Barbearia</div>
            
            <q-form @submit.prevent="criarLoja" class="q-gutter-y-md">
              
              <q-input 
                v-model="form.nome" 
                label="Nome da Barbearia" 
                outlined 
                color="primary" 
                class="custom-input" 
                :rules="[val => !!val || 'O nome é obrigatório']"
                @update:model-value="gerarSlug"
                hide-bottom-space
              >
                <template v-slot:prepend><q-icon name="storefront" color="grey-6" /></template>
              </q-input>

              <q-input 
                v-model="form.slug" 
                label="Link / Slug da Loja" 
                outlined 
                color="primary" 
                class="custom-input" 
                hint="Ex: barbearia-do-ze"
                :rules="[
                  val => !!val || 'O slug é obrigatório',
                  val => /^[a-z0-9-]+$/.test(val) || 'Apenas letras minúsculas, números e hifens permitidos'
                ]"
                hide-bottom-space
              >
                <template v-slot:prepend><q-icon name="link" color="grey-6" /></template>
              </q-input>

              <div v-if="linkGerado" class="success-box q-mt-md q-pa-md text-center shadow-2">
                <q-icon name="check_circle" color="positive" size="28px" />
                <div class="q-mt-sm text-weight-bold">Loja criada com sucesso!</div>
                <div class="text-caption q-mb-xs">Envie este link de acesso para o dono da barbearia:</div>
                <a :href="linkGerado" target="_blank" class="text-primary text-weight-bolder" style="word-break: break-all;">
                  {{ linkGerado }}
                </a>
              </div>

              <div v-if="erro" class="alert-box q-mt-md">
                <q-icon name="error" class="q-mr-xs" size="18px" /> {{ erro }}
              </div>

              <q-btn 
                type="submit" 
                color="primary" 
                class="full-width q-mt-lg submit-btn" 
                size="lg" 
                label="Registar Barbearia" 
                :loading="carregando" 
                unelevated 
                no-caps 
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
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/authStore' // Importa a Store de Autenticação

const $q = useQuasar()
const authStore = useAuthStore() // Inicializa a Store
const carregando = ref(false)
const erro = ref('')
const linkGerado = ref('')

const form = ref({
  nome: '',
  slug: ''
})

// Função inteligente que auto-preenche o slug criando uma URL amigável
// Ex: Se digitar "Barbearia do Zé", o slug vira "barbearia-do-ze"
const gerarSlug = (novoNome: string | number | null) => {
  if (typeof novoNome === 'string' && !linkGerado.value) { 
    form.value.slug = novoNome
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9 ]/g, "")
      .trim()
      .replace(/\s+/g, "-"); 
  }
}

const criarLoja = async () => {
  erro.value = ''
  linkGerado.value = ''
  carregando.value = true
  
  try {
    // Adicionado o usuario_logado_id conforme exigido pelo Backend
    const params = new URLSearchParams({
      nome: form.value.nome,
      slug: form.value.slug,
      usuario_logado_id: String(authStore.userId) 
    })

    const response = await fetch(`${import.meta.env.VITE_API_URL}/admin/barbearias/?${params.toString()}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Erro ao criar a barbearia. Verifique se o slug já existe.')
    }

    const data = await response.json()

    $q.notify({ type: 'positive', message: 'Barbearia criada com sucesso no sistema!', position: 'top' })
    
    linkGerado.value = data.link

    form.value.nome = ''
    form.value.slug = ''

  } catch (error: any) {
    erro.value = error.message
  } finally {
    carregando.value = false
  }
}
</script>

<style scoped>
.admin-page {
  /* Cores de fundo diferentes para diferenciar o painel de Admin do sistema normal */
  --cor-fundo-inicio: #0f172a; 
  --cor-fundo-fim: #334155;    
  --cor-cartao-bg: rgba(255, 255, 255, 0.98);
  
  background: linear-gradient(135deg, var(--cor-fundo-inicio) 0%, var(--cor-fundo-fim) 100%);
  min-height: 100vh;
}

.admin-card {
  width: 100%;
  max-width: 500px;
  background: var(--cor-cartao-bg);
  border-radius: 20px;
}

.title-text {
  color: #1e293b;
  letter-spacing: -1px;
}

.subtitle-text {
  color: #64748b;
}

.custom-input :deep(.q-field__control) {
  border-radius: 12px;
}

.submit-btn {
  border-radius: 12px;
  font-weight: bold;
  letter-spacing: 0.5px;
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

.success-box {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 12px;
}
</style>