<template>
  <q-layout view="hHh lpR fFf" class="details-layout">
    <q-page-container>
      <q-page padding class="flex flex-center details-page">
        
        <div style="width: 100%; max-width: 800px;">
          
          <div class="row items-center q-mb-lg">
            <q-btn 
              flat 
              icon="arrow_back" 
              label="Voltar ao Painel" 
              class="back-btn q-mr-md" 
              @click="router.push(`/${route.params.slug}/dashboard`)" 
              no-caps 
            />
            <q-breadcrumbs class="text-grey-6 text-weight-medium" active-color="primary">
              <q-breadcrumbs-el icon="home" class="cursor-pointer" @click="router.push(`/${route.params.slug}/dashboard`)" />
              <q-breadcrumbs-el label="Detalhes do Agendamento" />
            </q-breadcrumbs>
          </div>
          
          <q-card v-if="agendamento" class="details-card shadow-12">
            
            <q-card-section class="card-header q-pa-xl">
              <div class="row items-center justify-between">
                <div class="row items-center">
                  <div class="header-icon-wrapper shadow-4 q-mr-lg">
                    <q-icon name="content_cut" class="header-icon" />
                  </div>
                  <div>
                    <div class="text-caption text-white opacity-80 text-weight-bold letter-spacing text-uppercase">
                      Agendamento #{{ agendamento.id }}
                    </div>
                    <div class="text-h4 text-weight-bolder text-white q-mt-xs">
                      {{ agendamento.servico }}
                    </div>
                  </div>
                </div>
                
                <q-chip 
                  :color="corEstado(agendamento.status)" 
                  text-color="white" 
                  size="md"
                  class="status-chip shadow-2 text-weight-bolder text-uppercase q-px-md q-py-sm"
                >
                  {{ agendamento.status }}
                </q-chip>
              </div>
            </q-card-section>

            <q-card-section class="q-pa-xl bg-white">
              <div class="row q-col-gutter-xl">
                
                <div class="col-12 col-sm-4">
                  <div class="info-label">Data e Hora</div>
                  <div class="info-value q-mt-sm flex items-center">
                    <q-icon name="event" class="q-mr-sm text-primary" size="20px"/>
                    {{ formatarData(agendamento.data_hora) }}
                  </div>
                </div>
                
                <div class="col-12 col-sm-4">
                  <div class="info-label">Perfil do Cliente</div>
                  
                  <div class="info-value q-mt-sm flex items-center">
                    <q-icon name="person" class="q-mr-sm text-primary" size="20px" /> 
                    {{ agendamento.cliente?.nome || agendamento.cliente_nome }}
                  </div>
                  
                  <template v-if="authStore.userType === 'barbeiro' || authStore.userType === 'admin'">
                    <div v-if="agendamento.cliente?.telefone" class="q-mt-sm">
                      <a :href="'https://wa.me/' + formatarNumero(agendamento.cliente.telefone)" target="_blank" class="contact-link flex items-center">
                        <q-icon name="whatsapp" class="q-mr-sm text-positive" size="18px" /> 
                        {{ agendamento.cliente.telefone }}
                      </a>
                    </div>
                    <div v-if="agendamento.cliente?.email" class="text-body2 text-grey-8 q-mt-sm flex items-center">
                      <q-icon name="email" class="q-mr-sm text-grey-6" size="18px" /> 
                        {{ agendamento.cliente.email }}
                    </div>
                  </template>
                </div>
                
                <div class="col-12 col-sm-4">
                  <div class="info-label">Profissional Responsável</div>
                  <div class="info-value q-mt-sm flex items-center">
                    <q-icon name="badge" class="q-mr-sm text-primary" size="20px" />
                    {{ agendamento.barbeiro?.nome || agendamento.barbeiro_nome }}
                  </div>
                </div>
                
              </div>

              <q-separator class="separator-custom q-my-xl" />

              <div 
                v-if="(authStore.userType === 'barbeiro' || authStore.userType === 'admin') && agendamento.status !== 'Cancelado'" 
                class="management-section q-pa-lg"
              >
                <div class="text-h6 text-primary text-weight-bolder q-mb-md flex items-center">
                  <q-icon name="settings_suggest" class="q-mr-sm" size="24px"/> Gestão do Atendimento
                </div>
                <div class="row q-gutter-md">
                  <q-btn 
                    v-if="agendamento.status === 'Pendente'"
                    color="primary" 
                    icon="thumb_up" 
                    label="Confirmar Agendamento" 
                    class="action-btn shadow-3"
                    @click="alterarEstado('Confirmado')" 
                    unelevated
                    no-caps
                  />
                  <q-btn 
                    v-if="agendamento.status === 'Confirmado' || agendamento.status === 'Pendente'"
                    color="positive" 
                    icon="check_circle" 
                    label="Marcar como Concluído" 
                    class="action-btn shadow-3"
                    @click="alterarEstado('Concluído')" 
                    unelevated
                    no-caps
                  />
                </div>
              </div>

              <div 
                v-if="agendamento.status !== 'Cancelado' && agendamento.status !== 'Concluído'" 
                class="cancel-section q-pa-lg q-mt-lg"
              >
                <div class="text-h6 text-negative text-weight-bolder q-mb-xs flex items-center">
                  <q-icon name="warning" class="q-mr-sm" size="24px"/> Zona de Cancelamento
                </div>
                <div class="text-body2 text-grey-9 q-mb-md">
                  O horário será libertado na agenda imediatamente. Esta ação não poderá ser revertida.
                </div>
                <q-btn 
                  outline 
                  color="negative" 
                  label="Cancelar Agendamento" 
                  icon="cancel" 
                  class="action-btn-outline"
                  no-caps 
                  @click="confirmarCancelamento" 
                />
              </div>

            </q-card-section>
          </q-card>
          
          <div v-else class="flex flex-center q-pa-xl">
            <q-spinner-tail color="primary" size="3em" />
            <div class="text-grey-6 q-ml-md text-weight-medium">A carregar detalhes...</div>
          </div>

        </div>

      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAgendamentoStore } from '@/stores/agendamentoStore'
import { useAuthStore } from '@/stores/authStore'
import { useQuasar } from 'quasar'

const route = useRoute()
const router = useRouter()
const agendamentoStore = useAgendamentoStore()
const authStore = useAuthStore()
const $q = useQuasar()

const agendamento = ref<any>(null)

const formatarData = (dataStr: string) => {
  return new Date(dataStr).toLocaleString('pt-PT', { dateStyle: 'full', timeStyle: 'short' })
}

const formatarNumero = (numero: string) => {
  return numero.replace(/\D/g, '')
}

const corEstado = (status: string) => {
  const s = status?.toLowerCase() || ''
  if (s === 'pendente') return 'warning'
  if (s === 'confirmado' || s === 'concluido' || s === 'concluído') return 'positive'
  if (s === 'cancelado') return 'negative'
  return 'grey'
}

const alterarEstado = async (novoEstado: string) => {
  try {
    const response = await fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${route.params.slug}/agendamentos/${agendamento.value.id}`, { 
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: novoEstado })
    })
    
    if (!response.ok) throw new Error('Falha ao atualizar')
    
    agendamento.value.status = novoEstado
    await agendamentoStore.fetchAgendamentos(route.params.slug as string)
    
    $q.notify({ type: 'positive', message: `Agendamento alterado para ${novoEstado}`, position: 'top' })
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Erro ao atualizar o estado.', position: 'top' })
  }
}

const confirmarCancelamento = () => {
  $q.dialog({
  title: 'Confirmar Cancelamento',
  message: 'Tem a certeza que pretende cancelar este agendamento?',
  persistent: true,
  ok: { color: 'negative', label: 'Sim, cancelar', noCaps: true },
  cancel: { flat: true, color: 'grey-8', label: 'Não, recuar', noCaps: true }
}).onOk(async () => {
    try {
      await fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${route.params.slug}/agendamentos/${agendamento.value.id}`, { method: 'DELETE' })
      $q.notify({ type: 'positive', message: 'Cancelado com sucesso.', position: 'top' })
      router.push(`/${route.params.slug}/dashboard`)
    } catch (error) {
      $q.notify({ type: 'negative', message: 'Erro ao cancelar o agendamento.', position: 'top' })
    }
  })
}

onMounted(async () => {
  const idAgendamento = Number(route.params.id)
  
  try {
    const response = await fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${route.params.slug}/agendamentos/${idAgendamento}`)
    if (!response.ok) throw new Error('Não encontrado')
    agendamento.value = await response.json()
  } catch (error) {
    router.push(`/${route.params.slug}/dashboard`)
  }
})
</script>

<style scoped>
/* O seu estilo original não foi alterado */
.details-layout {
  --cor-fundo-pagina: #f1f5f9;
  --cor-cartao-bg: #ffffff;
  --cor-header-inicio: var(--q-primary);
  --cor-header-fim: #1e3a8a; 
  --cor-texto-primario: #0f172a;
  --cor-texto-secundario: #64748b;
  --borda-raio: 20px;
  --borda-raio-pequeno: 12px;
  --borda-cor: #e2e8f0;
}
.details-page {
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
  letter-spacing: 1px;
}
.opacity-80 {
  opacity: 0.8;
}
.details-card {
  background: var(--cor-cartao-bg);
  border-radius: var(--borda-raio);
  overflow: hidden;
  border: none;
}
.card-header {
  background: linear-gradient(135deg, var(--cor-header-inicio) 0%, var(--cor-header-fim) 100%);
}
.header-icon-wrapper {
  width: 64px;
  height: 64px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(5px);
}
.header-icon {
  font-size: 32px;
  color: white;
}
.status-chip {
  border-radius: 8px;
  font-size: 14px;
}
.info-label {
  color: var(--cor-texto-secundario);
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}
.info-value {
  color: var(--cor-texto-primario);
  font-size: 1.1rem;
  font-weight: 600;
}
.separator-custom {
  background-color: var(--borda-cor);
}
.contact-link {
  display: inline-flex;
  padding: 6px 12px;
  background-color: #f0fdf4;
  color: #166534;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: background-color 0.2s;
}
.contact-link:hover {
  background-color: #dcfce7;
}
.management-section {
  background-color: #f8fafc;
  border: 1px solid var(--borda-cor);
  border-radius: var(--borda-raio-pequeno);
}
.cancel-section {
  background-color: #fef2f2;
  border: 1px dashed #fca5a5;
  border-radius: var(--borda-raio-pequeno);
}
.action-btn {
  border-radius: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  transition: transform 0.2s;
}
.action-btn:hover {
  transform: translateY(-2px);
}
.action-btn-outline {
  border-radius: 10px;
  font-weight: 700;
  border-width: 2px;
  background-color: white;
}
</style>