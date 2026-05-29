<template>
  <q-layout view="hHh lpR fFf" class="stats-layout">
    <q-header elevated class="stats-header">
      <q-toolbar class="q-px-lg q-py-sm">
        <q-btn flat round icon="arrow_back" color="white" @click="router.push(`/${slug}/dashboard`)" />
        <q-toolbar-title class="text-weight-bold header-title q-ml-sm">
          Painel de Estatísticas
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page padding class="stats-page">
        <div style="max-width: 1200px; margin: 0 auto;">
          
          <div class="row items-center justify-between q-mb-xl q-mt-md">
            <div>
              <div class="text-h4 text-weight-bolder text-primary letter-spacing">Visão Geral</div>
              <div class="text-subtitle1 text-grey-7 q-mt-xs">Acompanhe o desempenho da sua barbearia.</div>
            </div>
            
            <div style="width: 250px;">
              <q-select
                v-model="filtroTempo"
                :options="opcoesFiltro"
                emit-value
                map-options
                outlined
                dense
                color="primary"
                class="bg-white shadow-1"
                style="border-radius: 8px;"
              >
                <template v-slot:prepend><q-icon name="filter_alt" color="primary" /></template>
              </q-select>
            </div>
          </div>

          <div class="row q-col-gutter-lg q-mb-xl">
            <div class="col-12 col-sm-6 col-md-3">
              <q-card class="kpi-card shadow-4 bg-primary text-white">
                <q-card-section>
                  <div class="row items-center justify-between">
                    <div class="text-subtitle2 text-weight-bold text-uppercase opacity-80">Faturação</div>
                    <q-icon name="payments" size="24px" class="opacity-80" />
                  </div>
                  <div class="text-h4 text-weight-bolder q-mt-sm">R$ {{ kpis.faturacao.toFixed(2) }}</div>
                </q-card-section>
              </q-card>
            </div>
            
            <div class="col-12 col-sm-6 col-md-3">
              <q-card class="kpi-card shadow-4 bg-white">
                <q-card-section>
                  <div class="row items-center justify-between">
                    <div class="text-subtitle2 text-weight-bold text-uppercase text-grey-6">Atendimentos</div>
                    <q-icon name="content_cut" size="24px" color="primary" />
                  </div>
                  <div class="text-h4 text-weight-bolder text-grey-9 q-mt-sm">{{ kpis.atendimentos }}</div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <q-card class="kpi-card shadow-4 bg-white">
                <q-card-section>
                  <div class="row items-center justify-between">
                    <div class="text-subtitle2 text-weight-bold text-uppercase text-grey-6">Ticket Médio</div>
                    <q-icon name="receipt_long" size="24px" color="positive" />
                  </div>
                  <div class="text-h4 text-weight-bolder text-grey-9 q-mt-sm">R$ {{ kpis.ticketMedio.toFixed(2) }}</div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-sm-6 col-md-3">
              <q-card class="kpi-card shadow-4 bg-white">
                <q-card-section>
                  <div class="row items-center justify-between">
                    <div class="text-subtitle2 text-weight-bold text-uppercase text-grey-6">Faltas / Cancel.</div>
                    <q-icon name="cancel" size="24px" color="negative" />
                  </div>
                  <div class="text-h4 text-weight-bolder text-grey-9 q-mt-sm">{{ kpis.taxaCancelamento.toFixed(1) }}%</div>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <div class="row q-col-gutter-lg">
            
            <div class="col-12 col-md-6">
              <q-card class="chart-card shadow-4">
                <q-card-section class="q-pa-lg">
                  <div class="text-h6 text-weight-bold text-grey-9 q-mb-lg">Serviços Mais Realizados</div>
                  
                  <div v-if="servicosAgrupados.length === 0" class="text-grey-5 text-center q-pa-md">Sem dados no período.</div>
                  
                  <div v-for="(servico, index) in servicosAgrupados" :key="index" class="q-mb-md">
                    <div class="row justify-between text-caption text-weight-bold text-grey-8 q-mb-xs">
                      <span>{{ servico.nome }}</span>
                      <span>{{ servico.quantidade }} ({{ servico.porcentagem }}%)</span>
                    </div>
                    <div class="progress-bg">
                      <div class="progress-bar bg-primary" :style="{ width: servico.porcentagem + '%' }"></div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-md-6">
              <q-card class="chart-card shadow-4">
                <q-card-section class="q-pa-lg">
                  <div class="text-h6 text-weight-bold text-grey-9 q-mb-lg flex items-center">
                    <q-icon name="workspace_premium" color="warning" size="28px" class="q-mr-sm" />
                    Top 5 Clientes (Fidelidade)
                  </div>
                  
                  <div v-if="topClientes.length === 0" class="text-grey-5 text-center q-pa-md">Sem dados no período.</div>

                  <q-list separator>
                    <q-item v-for="(cliente, index) in topClientes" :key="index" class="q-py-md">
                      <q-item-section avatar>
                        <q-avatar :color="index === 0 ? 'warning' : 'grey-3'" :text-color="index === 0 ? 'white' : 'grey-8'" font-size="16px" class="text-weight-bold">
                          {{ index + 1 }}º
                        </q-avatar>
                      </q-item-section>
                      <q-item-section>
                        <q-item-label class="text-weight-bold text-grey-9">{{ cliente.nome }}</q-item-label>
                        <q-item-label caption>{{ cliente.visitas }} visitas no período</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <div class="text-weight-bolder text-positive">R$ {{ cliente.gastoTotal.toFixed(2) }}</div>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>

          </div>

        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAgendamentoStore } from '@/stores/agendamentoStore'

const router = useRouter()
const route = useRoute()
const agendamentoStore = useAgendamentoStore()

// Captura o slug da loja atual (ex: 'barbearia-do-ze')
const slug = route.params.slug as string 

const filtroTempo = ref('mes_atual')
const opcoesFiltro = [
  { label: 'Últimos 7 Dias', value: '7_dias' },
  { label: 'Este Mês', value: 'mes_atual' },
  { label: 'Mês Passado', value: 'mes_passado' },
  { label: 'Este Ano', value: 'ano_atual' },
  { label: 'Todo o Período', value: 'tudo' }
]

onMounted(async () => {
  // Passa o slug para a Store para ela baixar apenas os agendamentos desta loja
  await agendamentoStore.fetchAgendamentos(slug)
})

// Filtragem de Dados por Data
const agendamentosFiltrados = computed(() => {
  const agora = new Date()
  return agendamentoStore.agendamentos.filter(a => {
    const dataAgendamento = new Date(a.data_hora)
    
    if (filtroTempo.value === '7_dias') {
      const seteDiasAtras = new Date()
      seteDiasAtras.setDate(agora.getDate() - 7)
      return dataAgendamento >= seteDiasAtras && dataAgendamento <= agora
    }
    if (filtroTempo.value === 'mes_atual') {
      return dataAgendamento.getMonth() === agora.getMonth() && dataAgendamento.getFullYear() === agora.getFullYear()
    }
    if (filtroTempo.value === 'mes_passado') {
      const mesPassado = new Date()
      mesPassado.setMonth(agora.getMonth() - 1)
      return dataAgendamento.getMonth() === mesPassado.getMonth() && dataAgendamento.getFullYear() === mesPassado.getFullYear()
    }
    if (filtroTempo.value === 'ano_atual') {
      return dataAgendamento.getFullYear() === agora.getFullYear()
    }
    return true // 'tudo'
  })
})

// Cálculo de KPIs
const kpis = computed(() => {
  const concluidos = agendamentosFiltrados.value.filter(a => a.status?.toLowerCase() === 'concluído' || a.status?.toLowerCase() === 'concluido')
  const cancelados = agendamentosFiltrados.value.filter(a => a.status?.toLowerCase() === 'cancelado')
  
  const faturacao = concluidos.reduce((sum, a) => sum + (a.preco || 0), 0)
  const atendimentos = concluidos.length
  const ticketMedio = atendimentos > 0 ? faturacao / atendimentos : 0
  
  const totalGeral = agendamentosFiltrados.value.length
  const taxaCancelamento = totalGeral > 0 ? (cancelados.length / totalGeral) * 100 : 0

  return { faturacao, atendimentos, ticketMedio, taxaCancelamento }
})

// Gráfico de Barras: Serviços Populares
const servicosAgrupados = computed(() => {
  const concluidos = agendamentosFiltrados.value.filter(a => a.status?.toLowerCase() === 'concluído' || a.status?.toLowerCase() === 'concluido')
  const contagem: Record<string, number> = {}
  
  concluidos.forEach(a => {
    const nome = a.servico || 'Outros'
    contagem[nome] = (contagem[nome] || 0) + 1
  })

  const total = concluidos.length
  return Object.keys(contagem)
    .map(key => ({
      nome: key,
      quantidade: contagem[key] || 0,
      porcentagem: total > 0 ? Math.round(((contagem[key] || 0) / total) * 100) : 0
    }))
    .sort((a, b) => (b.quantidade || 0) - (a.quantidade || 0))
})

// Ranking: Top 5 Clientes
const topClientes = computed(() => {
  const concluidos = agendamentosFiltrados.value.filter(a => a.status?.toLowerCase() === 'concluído' || a.status?.toLowerCase() === 'concluido')
  const clientes: Record<string, { nome: string, visitas: number, gastoTotal: number }> = {}

  concluidos.forEach(a => {
    const idNome = a.cliente?.nome || a.cliente_nome || 'Cliente Desconhecido'
    if (!clientes[idNome]) {
      clientes[idNome] = { nome: idNome, visitas: 0, gastoTotal: 0 }
    }
    clientes[idNome].visitas += 1
    clientes[idNome].gastoTotal += (a.preco || 0)
  })

  return Object.values(clientes)
    .sort((a, b) => b.gastoTotal - a.gastoTotal)
    .slice(0, 5)
})
</script>

<style scoped>
/* O seu estilo CSS permanece inalterado */
.stats-layout {
  --cor-fundo-pagina: #f8fafc;
  --cor-header-inicio: #1e293b;
  --cor-header-fim: #0f172a;
}
.stats-page { background-color: var(--cor-fundo-pagina); min-height: 100vh; }
.stats-header { background: linear-gradient(135deg, var(--cor-header-inicio) 0%, var(--cor-header-fim) 100%); }
.letter-spacing { letter-spacing: -1px; }
.opacity-80 { opacity: 0.8; }

.kpi-card {
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-5px); }

.chart-card {
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  background-color: white;
  height: 100%;
}

.progress-bg {
  width: 100%;
  height: 12px;
  background-color: #f1f5f9;
  border-radius: 6px;
  overflow: hidden;
}
.progress-bar {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease-in-out;
}
</style>