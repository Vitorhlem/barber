<template>
  <q-layout view="hHh lpR fFf" class="settings-layout">
    <q-page-container>
      <q-page padding class="flex flex-center settings-page">
        
        <div style="width: 100%; max-width: 768px;">
          
          <div class="row items-center q-mb-lg">
            <q-btn 
              flat 
              icon="arrow_back" 
              label="Voltar ao Painel" 
              class="back-btn q-mr-md" 
              @click="router.push('/dashboard')" 
              no-caps 
            />
            <q-breadcrumbs class="text-grey-6 text-weight-medium" active-color="primary">
              <q-breadcrumbs-el icon="home" class="cursor-pointer" @click="router.push('/dashboard')" />
              <q-breadcrumbs-el label="Configurações" />
            </q-breadcrumbs>
          </div>

          <q-card class="settings-card shadow-12 q-mb-lg">
            <q-card-section class="q-pa-xl row items-center justify-between">
              <div class="row items-center">
                <div class="icon-wrapper shadow-4 q-mr-lg bg-primary text-white">
                  <q-icon name="extension" size="32px" />
                </div>
                <div>
                  <div class="text-h5 text-weight-bolder text-primary letter-spacing">Integrações</div>
                  <div class="text-subtitle2 text-grey-6 q-mt-xs text-weight-medium">
                    Conecte com serviços externos para sincronizar a sua agenda.
                  </div>
                </div>
              </div>
              <q-btn 
                color="primary" 
                icon="calendar_month" 
                label="Conectar Google Agenda" 
                class="action-btn shadow-3 q-mt-md q-mt-sm-none"
                @click="iniciarAuthGoogle" 
                unelevated
                no-caps
              />
            </q-card-section>
          </q-card>

          <q-card v-if="authStore.userType === 'barbeiro' || authStore.userType === 'admin'" class="settings-card shadow-12">
            
            <q-card-section class="card-header q-pa-xl">
              <div class="row items-center">
                <div class="icon-wrapper-header shadow-4 q-mr-lg">
                  <q-icon name="schedule" size="32px" />
                </div>
                <div>
                  <div class="text-h4 text-weight-bolder text-white letter-spacing">Expediente</div>
                  <div class="text-subtitle1 text-white opacity-80 text-weight-medium q-mt-sm">
                    Defina o seu ritmo de trabalho e os horários da semana.
                  </div>
                </div>
              </div>
            </q-card-section>

            <q-card-section class="q-pa-xl bg-white">
              
              <div :class="['store-status-banner q-pa-lg rounded-borders q-mb-xl shadow-1 flex items-center justify-between', config.loja_aberta ? 'store-open' : 'store-closed']">
                <div>
                  <div class="text-h6 text-weight-bold flex items-center">
                    <q-icon :name="config.loja_aberta ? 'storefront' : 'remove_shopping_cart'" size="28px" class="q-mr-sm" />
                    {{ config.loja_aberta ? 'A Barbearia está Aberta' : 'A Barbearia está Fechada' }}
                  </div>
                  <div class="text-body2 q-mt-xs opacity-80 text-weight-medium">
                    {{ config.loja_aberta ? 'Os clientes podem ver os seus horários e realizar agendamentos normalmente.' : 'O aplicativo está bloqueado para clientes e não aceita novos agendamentos.' }}
                  </div>
                </div>
                <q-toggle
                  v-model="config.loja_aberta"
                  size="lg"
                  checked-icon="check"
                  color="positive"
                  unchecked-icon="clear"
                  keep-color
                />
              </div>

              <div class="text-subtitle1 text-weight-bolder text-primary q-mb-md">Ritmo de Atendimento</div>
              <q-select
                v-model="config.intervalo_minutos"
                :options="opcoesIntervalo"
                emit-value
                map-options
                label="Duração padrão de cada bloco de horário"
                outlined
                color="primary"
                class="custom-input q-mb-xl"
              >
                <template v-slot:prepend><q-icon name="timer" color="grey-6" /></template>
              </q-select>

              <div class="text-subtitle1 text-weight-bolder text-primary q-mb-md">Dias e Horários de Trabalho</div>
              
              <div class="schedule-container">
                <div v-for="item in horariosLista" :key="item.dia" class="schedule-row row items-center q-pa-md q-mb-sm rounded-borders">
                  
                  <div class="col-12 col-sm-3 text-weight-bold text-grey-9 text-body1 flex items-center">
                    <q-checkbox v-model="item.trabalha" color="primary" class="q-mr-sm" />
                    <span :class="{'text-grey-5': !item.trabalha}">{{ item.nome }}</span>
                  </div>
                  
                  <div class="col-6 col-sm-4 q-pr-sm q-mt-sm q-mt-sm-none">
                    <q-input 
                      v-model="item.inicio" 
                      type="time" 
                      label="Abertura" 
                      outlined 
                      dense 
                      class="custom-input-dense" 
                      :disable="!item.trabalha" 
                      color="primary"
                    />
                  </div>
                  
                  <div class="col-6 col-sm-4 q-pl-sm q-mt-sm q-mt-sm-none">
                    <q-input 
                      v-model="item.fim" 
                      type="time" 
                      label="Encerramento" 
                      outlined 
                      dense 
                      class="custom-input-dense" 
                      :disable="!item.trabalha" 
                      color="primary"
                    />
                  </div>

                </div>
              </div>
            </q-card-section>

            <q-card-actions align="right" class="q-pa-lg bg-grey-1" style="border-top: 1px solid #e2e8f0;">
              <q-btn 
                color="primary" 
                label="Salvar Configurações" 
                icon="save" 
                class="action-btn shadow-4 q-px-lg" 
                size="lg"
                :loading="salvando" 
                @click="salvarConfiguracao" 
                unelevated 
                no-caps
              />
            </q-card-actions>
          </q-card>

        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useQuasar } from 'quasar'

const router = useRouter()
const authStore = useAuthStore()
const $q = useQuasar()

const salvando = ref(false)
const config = ref({
  intervalo_minutos: 30,
  horarios_json: '[]',
  loja_aberta: true
})

const horariosLista = ref<any[]>([])

const opcoesIntervalo = [
  { label: 'De 15 em 15 minutos', value: 15 },
  { label: 'De 30 em 30 minutos', value: 30 },
  { label: 'De 45 em 45 minutos', value: 45 },
  { label: 'De 1 em 1 hora (60 min)', value: 60 }
]

const iniciarAuthGoogle = async () => {
  const response = await fetch(`http://localhost:8000/auth/google/login?user_id=${authStore.userId}`)
  const data = await response.json()
  if (data.url) {
    window.location.href = data.url
  }
}

const fetchConfiguracao = async () => {
  if (authStore.userType === 'cliente') return
  try {
    const response = await fetch(`http://localhost:8000/configuracao/${authStore.userId}`)
    if (response.ok) {
      const data = await response.json()
      config.value.intervalo_minutos = data.intervalo_minutos
      config.value.horarios_json = data.horarios_json
      config.value.loja_aberta = data.loja_aberta !== undefined ? data.loja_aberta : true
      horariosLista.value = JSON.parse(data.horarios_json)
    }
  } catch (e) {
    console.error("Erro ao carregar configurações", e)
  }
}

const salvarConfiguracao = async () => {
  salvando.value = true
  try {
    const payload = {
      intervalo_minutos: config.value.intervalo_minutos,
      horarios_json: JSON.stringify(horariosLista.value),
      loja_aberta: config.value.loja_aberta
    }
    
    const response = await fetch(`http://localhost:8000/configuracao/${authStore.userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    if (response.ok) {
      $q.notify({ type: 'positive', message: 'Configurações atualizadas com sucesso!', position: 'top' })
    } else {
      throw new Error()
    }
  } catch (e) {
    $q.notify({ type: 'negative', message: 'Erro ao salvar modificações.', position: 'top' })
  } finally {
    salvando.value = false
  }
}

onMounted(() => {
  fetchConfiguracao()
})
</script>

<style scoped>
/* =======================================================
   VARIÁVEIS DE COR E ESTILO (FÁCEIS DE ALTERAR)
======================================================= */
.settings-layout {
  --cor-fundo-pagina: #f1f5f9;
  --cor-cartao-bg: #ffffff;
  
  /* Gradiente do Cabeçalho de Expediente */
  --cor-header-inicio: var(--q-primary);
  --cor-header-fim: #1e3a8a; /* Azul Escuro */
  
  /* Cores de Texto */
  --cor-texto-primario: #0f172a;
  --cor-texto-secundario: #64748b;
  
  /* Bordas e Sombras */
  --borda-raio: 20px;
  --borda-raio-input: 12px;
  --borda-cor: #e2e8f0;
}

/* =======================================================
   ESTILOS GERAIS DA PÁGINA
======================================================= */
.settings-page {
  background-color: var(--cor-fundo-pagina);
  min-height: 100vh;
}

.back-btn {
  color: var(--cor-texto-secundario) !important;
  font-weight: 700;
  border-radius: 8px;
  background-color: rgba(100, 116, 139, 0.1);
  transition: all 0.2s;
}
.back-btn:hover {
  background-color: rgba(100, 116, 139, 0.2);
  color: var(--cor-texto-primario) !important;
}

.letter-spacing {
  letter-spacing: -0.5px;
}
.opacity-80 {
  opacity: 0.8;
}

/* =======================================================
   CARTÕES PRINCIPAIS
======================================================= */
.settings-card {
  background: var(--cor-cartao-bg);
  border-radius: var(--borda-raio);
  overflow: hidden;
  border: none;
}

.icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-wrapper-header {
  width: 64px;
  height: 64px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(5px);
  color: white;
}

/* Cabeçalho do Cartão de Expediente */
.card-header {
  background: linear-gradient(135deg, var(--cor-header-inicio) 0%, var(--cor-header-fim) 100%);
}

/* =======================================================
   BANNER DE STATUS DA LOJA
======================================================= */
.store-status-banner {
  transition: all 0.3s ease;
  border: 1px solid transparent;
}
.store-open {
  background-color: #f0fdf4;
  border-color: #bbf7d0;
  color: #166534;
}
.store-closed {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

/* =======================================================
   INPUTS E FORMULÁRIOS
======================================================= */
.custom-input :deep(.q-field__control) {
  border-radius: var(--borda-raio-input);
  background-color: #f8fafc;
}

.custom-input-dense :deep(.q-field__control) {
  border-radius: 8px;
  background-color: #ffffff;
}

/* =======================================================
   LISTA DE HORÁRIOS (SEMANA)
======================================================= */
.schedule-container {
  background-color: #f8fafc;
  border: 1px solid var(--borda-cor);
  border-radius: var(--borda-raio-input);
  padding: 12px;
}

.schedule-row {
  background-color: #ffffff;
  border: 1px solid var(--borda-cor);
  transition: all 0.2s ease;
}
.schedule-row:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* Botões de Ação */
.action-btn {
  border-radius: var(--borda-raio-input);
  font-weight: 700;
  letter-spacing: 0.5px;
  transition: transform 0.2s;
}
.action-btn:hover {
  transform: translateY(-2px);
}
</style>