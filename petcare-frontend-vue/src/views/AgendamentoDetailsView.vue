<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-page padding class="flex flex-center bg-grey-1">
        
        <div style="width: 100%; max-width: 768px;">
          <q-breadcrumbs class="q-mb-lg text-grey-8" active-color="primary">
            <q-breadcrumbs-el icon="home" label="Painel" class="cursor-pointer" @click="router.push('/dashboard')" />
            <q-breadcrumbs-el label="Detalhes do Agendamento" />
          </q-breadcrumbs>
          
          <q-card v-if="agendamento" flat bordered class="rounded-borders shadow-1">
            <q-card-section class="bg-white q-pa-lg">
              <div class="row items-center justify-between">
                <div>
                  <div class="text-caption text-grey-6 text-weight-bold letter-spacing">
                    AGENDAMENTO #{{ agendamento.id }}
                  </div>
                  <div class="text-h4 text-weight-bold text-grey-9 q-mt-sm">
                    {{ agendamento.servico }}
                  </div>
                </div>
                <q-chip :color="corEstado(agendamento.status)" text-color="white" class="text-weight-bold text-uppercase">
                  {{ agendamento.status }}
                </q-chip>
              </div>
            </q-card-section>

            <q-separator />

            <q-card-section class="q-pa-lg bg-grey-1">
              <div class="row q-col-gutter-md">
                <div class="col-12 col-sm-4">
                  <div class="text-caption text-grey-6 text-weight-bold text-uppercase">Data e Hora</div>
                  <div class="text-body1 text-weight-medium q-mt-xs">
                    {{ formatarData(agendamento.data_hora) }}
                  </div>
                </div>
                
                <div class="col-12 col-sm-4">
                  <div class="text-caption text-grey-6 text-weight-bold text-uppercase">Cliente</div>
                  <div class="text-body1 text-weight-medium q-mt-xs">
                    {{ agendamento.cliente_nome }}
                  </div>
                </div>
                
                <div class="col-12 col-sm-4">
                  <div class="text-caption text-grey-6 text-weight-bold text-uppercase">Profissional / Barbeiro</div>
                  <div class="text-body1 text-weight-medium q-mt-xs">
                    {{ agendamento.barbeiro_nome }}
                  </div>
                </div>
              </div>
            </q-card-section>

            <q-card-section v-if="(authStore.userType === 'barbeiro' || authStore.userType === 'admin') && agendamento.status !== 'Cancelado'" class="bg-blue-grey-1 q-pa-lg" style="border-top: 1px solid #e0e0e0;">
              <div class="text-h6 text-primary text-weight-bold q-mb-md">Gestão do Atendimento</div>
              <div class="row q-gutter-md">
                <q-btn 
                  v-if="agendamento.status === 'Pendente'"
                  color="primary" 
                  icon="thumb_up" 
                  label="Confirmar Agendamento" 
                  @click="alterarEstado('Confirmado')" 
                  unelevated
                />
                <q-btn 
                  v-if="agendamento.status === 'Confirmado' || agendamento.status === 'Pendente'"
                  color="positive" 
                  icon="check_circle" 
                  label="Marcar como Concluído" 
                  @click="alterarEstado('Concluído')" 
                  unelevated
                />
              </div>
            </q-card-section>

            <q-card-section v-if="agendamento.status !== 'Cancelado' && agendamento.status !== 'Concluído'" class="bg-red-1 q-pa-lg" style="border-top: 1px solid #fecaca;">
              <div class="text-h6 text-negative text-weight-bold q-mb-sm">Cancelar Agendamento</div>
              <div class="text-body2 text-grey-8 q-mb-md">O horário será libertado e a ação não poderá ser revertida.</div>
              <q-btn 
                outline 
                color="negative" 
                label="Cancelar Agendamento" 
                icon="cancel" 
                no-caps 
                @click="confirmarCancelamento" 
              />
            </q-card-section>
          </q-card>
          
          <div v-else class="flex flex-center q-pa-xl">
            <q-spinner-dots color="primary" size="40px" />
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

onMounted(() => {
  const idAgendamento = Number(route.params.id)
  agendamento.value = agendamentoStore.agendamentos.find((a: any) => a.id === idAgendamento)
  
  if (!agendamento.value) {
    router.push('/dashboard')
  }
})

const formatarData = (dataStr: string) => {
  return new Date(dataStr).toLocaleString('pt-PT', { dateStyle: 'full', timeStyle: 'short' })
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
    // Envia apenas o novo estado esperado pelo AgendamentoUpdate
    const response = await fetch(`http://localhost:8000/agendamentos/${agendamento.value.id}`, { 
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: novoEstado })
    })
    
    if (!response.ok) throw new Error('Falha ao atualizar')
    
    agendamento.value.status = novoEstado
    
    await agendamentoStore.fetchAgendamentos() 
    
    $q.notify({ type: 'positive', message: `Agendamento alterado para ${novoEstado}`, position: 'top' })
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Erro ao atualizar o estado.', position: 'top' })
  }
}
const confirmarCancelamento = () => {
  $q.dialog({
    title: 'Confirmar Cancelamento',
    message: 'Tem a certeza que pretende cancelar este agendamento?',
    cancel: true,
    persistent: true,
    ok: { color: 'negative', label: 'Sim, cancelar', noCaps: true },
    cancel: { flat: true, color: 'grey-8', label: 'Não, recuar', noCaps: true }
  }).onOk(async () => {
    try {
      await fetch(`http://localhost:8000/agendamentos/${agendamento.value.id}`, { method: 'DELETE' })
      $q.notify({ type: 'positive', message: 'Cancelado com sucesso.', position: 'top' })
      router.push('/dashboard')
    } catch (error) {
      $q.notify({ type: 'negative', message: 'Erro ao cancelar o agendamento.', position: 'top' })
    }
  })
}

onMounted(async () => {
  const idAgendamento = Number(route.params.id)
  
  // Tente buscar da API para garantir que tem todos os campos (cliente e barbeiro)
  try {
    const response = await fetch(`http://localhost:8000/agendamentos/${idAgendamento}`)
    if (!response.ok) throw new Error('Não encontrado')
    agendamento.value = await response.json()
  } catch (error) {
    // Se falhar, volta para o dashboard
    router.push('/dashboard')
  }
})
</script>

<style scoped>
.letter-spacing { letter-spacing: 1px; }
</style>