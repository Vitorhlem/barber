<template>
  <q-layout view="hHh lpR fFf">
    <q-header elevated class="bg-white text-primary">
      <q-toolbar class="q-px-lg q-py-sm">
        <q-avatar icon="content_cut" color="primary" text-color="white" size="40px" />
        <q-toolbar-title class="text-weight-bold">
          BarberBase
          <div class="text-caption text-grey-6 text-weight-regular">
            Olá, {{ authStore.userName || 'Utilizador' }}
          </div>
        </q-toolbar-title>
        <q-space />
        <div class="q-gutter-sm">
          <q-btn v-if="authStore.userType === 'cliente'" color="primary" icon="add" label="Novo Agendamento" unelevated @click="router.push('/agendamento/novo')" />
          <q-btn outline color="grey-8" icon="logout" label="Sair" @click="authStore.logout" />
          <q-btn 
  flat 
  round 
  icon="settings" 
  color="grey-7" 
  @click="router.push('/settings')" 
/>
        </div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page padding class="bg-grey-1">
        <div style="max-width: 1200px; margin: 0 auto;">
          
          <div class="row items-center q-mb-md q-mt-md">
            <div class="text-h5 text-weight-bold text-grey-9">A Sua Agenda</div>
          </div>

          <div v-if="agendamentoStore.carregando" class="flex flex-center q-pa-xl">
            <q-spinner-tail color="primary" size="3em" />
            <div class="text-grey-6 q-ml-md">A carregar os seus dados...</div>
          </div>

          <q-banner v-else-if="agendamentoStore.erro" class="bg-negative text-white q-mb-md rounded-borders">
            <template v-slot:avatar><q-icon name="error" /></template>
            {{ agendamentoStore.erro }}
          </q-banner>

          <template v-else>
            <div v-if="(authStore.userType === 'barbeiro' || authStore.userType === 'admin')" class="row q-col-gutter-md q-mb-lg">
              <div class="col-12 col-md-4">
                <q-card class="bg-primary text-white shadow-2 rounded-borders">
                  <q-card-section>
                    <div class="row items-center no-wrap">
                      <div class="col">
                        <div class="text-subtitle2 text-weight-medium text-blue-grey-2 text-uppercase">Faturação Total</div>
                        <div class="text-h3 text-weight-bold q-mt-sm">€ {{ calcularFaturacao() }}</div>
                      </div>
                      <div class="col-auto">
                        <q-icon name="account_balance_wallet" size="56px" color="white" class="opacity-50" />
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <q-tabs
              v-model="abaAtual"
              dense
              class="text-grey-7 q-mb-md"
              active-color="primary"
              indicator-color="primary"
              align="left"
              narrow-indicator
            >
              <q-tab name="proximos" label="Próximos Atendimentos" />
              <q-tab name="historico" label="Histórico" />
            </q-tabs>
            <q-separator class="q-mb-md" />

            <q-tab-panels v-model="abaAtual" animated class="bg-transparent">
              
              <q-tab-panel name="proximos" class="q-px-none q-pt-none">
                <div v-if="agendamentosProximos.length === 0" class="flex flex-center q-pa-xl bg-white rounded-borders shadow-1">
                  <q-icon name="event_available" size="64px" color="grey-4" />
                  <div class="text-h6 text-grey-5 q-mt-md full-width text-center">Não existem próximos agendamentos.</div>
                </div>
                <div v-else class="row q-col-gutter-md">
                  <div class="col-12 col-sm-6 col-md-4" v-for="agendamento in agendamentosProximos" :key="agendamento.id">
                    <q-card class="cursor-pointer transition-transform hover-scale" flat bordered @click="router.push(`/agendamento/${agendamento.id}`)">
                      <q-card-section>
                        <div class="row items-center justify-between q-mb-sm">
                          <div class="text-h6 text-weight-medium">{{ agendamento.servico }}</div>
                          <q-chip :color="corEstado(agendamento.status)" text-color="white" size="sm" class="text-weight-bold text-uppercase">
                            {{ agendamento.status }}
                          </q-chip>
                        </div>
                        <q-list dense class="text-grey-8">
  <q-item class="q-px-none">
    <q-item-section avatar min-width="32px"><q-icon name="schedule" color="grey-6" size="20px" /></q-item-section>
    <q-item-section>{{ formatarData(agendamento.data_hora) }}</q-item-section>
  </q-item>
  
  <q-item class="q-px-none">
    <q-item-section avatar min-width="32px"><q-icon name="payments" color="grey-6" size="20px" /></q-item-section>
    <q-item-section>€ {{ agendamento.preco?.toFixed(2) || '0.00' }}</q-item-section>
  </q-item>

  <q-item class="q-px-none">
  <q-item-section avatar min-width="32px">
    <q-icon :name="authStore.userType === 'barbeiro' || authStore.userType === 'admin' ? 'person' : 'badge'" color="grey-6" size="20px" />
  </q-item-section>
  <q-item-section>
    <span v-if="authStore.userType === 'barbeiro' || authStore.userType === 'admin'">
      <strong>Cliente:</strong> {{ agendamento.cliente?.nome || agendamento.cliente_nome || 'Desconhecido' }}
    </span>
    <span v-else>
      <strong>Barbeiro:</strong> {{ agendamento.barbeiro?.nome || agendamento.barbeiro_nome || 'Desconhecido' }}
    </span>
  </q-item-section>
</q-item>
</q-list>
                      </q-card-section>
                      <q-separator />
                      <q-card-actions align="right" class="q-pa-sm text-primary">
                        <q-btn flat no-caps label="Ver detalhes" icon-right="arrow_forward" size="sm" />
                      </q-card-actions>
                    </q-card>
                  </div>
                </div>
              </q-tab-panel>

              <q-tab-panel name="historico" class="q-px-none q-pt-none">
                <div v-if="agendamentosHistorico.length === 0" class="flex flex-center q-pa-xl bg-white rounded-borders shadow-1">
                  <q-icon name="history" size="64px" color="grey-4" />
                  <div class="text-h6 text-grey-5 q-mt-md full-width text-center">O histórico está vazio.</div>
                </div>
                <div v-else class="row q-col-gutter-md">
                  <div class="col-12 col-sm-6 col-md-4" v-for="agendamento in agendamentosHistorico" :key="agendamento.id">
                    <q-card class="cursor-pointer transition-transform hover-scale" flat bordered @click="router.push(`/agendamento/${agendamento.id}`)">
                      <q-card-section>
                        <div class="row items-center justify-between q-mb-sm">
                          <div class="text-h6 text-weight-medium">{{ agendamento.servico }}</div>
                          <q-chip :color="corEstado(agendamento.status)" text-color="white" size="sm" class="text-weight-bold text-uppercase">
                            {{ agendamento.status }}
                          </q-chip>
                        </div>
                        <q-list dense class="text-grey-8">
                          <q-item class="q-px-none">
                            <q-item-section avatar min-width="32px"><q-icon name="schedule" color="grey-6" size="20px" /></q-item-section>
                            <q-item-section>{{ formatarData(agendamento.data_hora) }}</q-item-section>
                          </q-item>
                          <q-item class="q-px-none">
                            <q-item-section avatar min-width="32px">
                              <q-icon :name="authStore.userType === 'barbeiro' || authStore.userType === 'admin' ? 'person' : 'badge'" color="grey-6" size="20px" />
                            </q-item-section>
                            <q-item-section>
                              <span v-if="authStore.userType === 'barbeiro' || authStore.userType === 'admin'"><strong>Cliente:</strong> {{ agendamento.cliente_nome }}</span>
                              <span v-else><strong>Barbeiro:</strong> {{ agendamento.barbeiro_nome }}</span>
                            </q-item-section>
                          </q-item>
                        </q-list>
                      </q-card-section>
                      <q-separator />
                      <q-card-actions align="right" class="q-pa-sm text-primary">
                        <q-btn flat no-caps label="Ver detalhes" icon-right="arrow_forward" size="sm" />
                      </q-card-actions>
                    </q-card>
                  </div>
                </div>
              </q-tab-panel>

            </q-tab-panels>
          </template>

        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useAgendamentoStore } from '@/stores/agendamentoStore'

const router = useRouter()
const authStore = useAuthStore()
const agendamentoStore = useAgendamentoStore()

const abaAtual = ref('proximos')

onMounted(() => {
  if (authStore.isAuthenticated()) {
    agendamentoStore.fetchAgendamentos()
  }
})

const agendamentosProximos = computed(() => {
  return agendamentoStore.agendamentos.filter(a => {
    const s = a.status?.toLowerCase() || ''
    return s === 'pendente' || s === 'confirmado'
  })
})

const agendamentosHistorico = computed(() => {
  return agendamentoStore.agendamentos.filter(a => {
    const s = a.status?.toLowerCase() || ''
    return s === 'concluido' || s === 'concluído' || s === 'cancelado'
  })
})

const formatarData = (dataStr: string) => {
  return new Date(dataStr).toLocaleString('pt-PT', { dateStyle: 'long', timeStyle: 'short' })
}

const corEstado = (status: string) => {
  const s = status?.toLowerCase() || ''
  if (s === 'pendente') return 'warning'
  if (s === 'confirmado' || s === 'concluido' || s === 'concluído') return 'positive'
  if (s === 'cancelado') return 'negative'
  return 'grey'
}

const calcularFaturacao = () => {
  const total = agendamentoStore.agendamentos
    .filter(a => {
      const s = a.status?.toLowerCase() || ''
      return s === 'concluído' || s === 'concluido'
    })
    .reduce((sum, a) => sum + (a.preco || 0), 0)
  return total.toFixed(2)
}
</script>

<style scoped>
.opacity-50 { opacity: 0.5; }
.hover-scale { transition: transform 0.2s ease, box-shadow 0.2s ease; }
.hover-scale:hover { transform: translateY(-3px); box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important; border-color: var(--q-primary); }
</style>