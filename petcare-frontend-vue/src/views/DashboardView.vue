<template>
  <q-layout view="hHh lpR fFf" class="dashboard-layout">
    <q-header elevated class="dash-header">
      <q-toolbar class="q-px-lg q-py-sm">
        <div class="logo-circle-small q-mr-sm shadow-2" style="overflow: hidden; background-color: white;">
          <q-img v-if="sistemaStore.logoUrl" :src="sistemaStore.logoUrl" fit="cover" style="width: 100%; height: 100%;" />
          <q-icon v-else name="content_cut" class="logo-icon-small" color="primary" />
        </div>
        <q-toolbar-title class="text-weight-bold header-title">
          {{ sistemaStore.nomeBarbearia }}
          <div class="text-caption header-subtitle text-weight-medium">
            Olá, {{ authStore.userName || 'Utilizador' }}
            <q-badge v-if="wsConnected" color="positive" rounded class="q-ml-sm shadow-1" title="Conectado em tempo real" />
            <q-badge v-else color="negative" rounded class="q-ml-sm shadow-1" title="Desconectado" />
          </div>
        </q-toolbar-title>
        <q-space />
        <div class="q-gutter-sm">
          <q-btn v-if="authStore.userType === 'cliente'" color="primary" icon="add" label="Novo Agendamento" unelevated class="action-btn" no-caps @click="router.push(`/${slug}/agendamento/novo`)" />
          <q-btn v-if="authStore.userType === 'barbeiro' || authStore.userType === 'admin'" outline color="positive" icon="analytics" label="Estatísticas" class="action-btn-outline bg-white q-mr-sm" no-caps @click="router.push(`/${slug}/estatisticas`)" />
          <q-btn v-if="authStore.userType === 'barbeiro' || authStore.userType === 'admin'" outline color="warning" icon="block" label="Pausa/Bloqueio" class="action-btn-outline" no-caps @click="dialogBloqueio = true" />
          <q-btn outline color="grey-5" text-color="white" icon="logout" label="Sair" class="action-btn-outline text-grey-8" no-caps @click="authStore.logout" />
          <q-btn outline color="primary" icon="storefront" label="Loja Física" class="action-btn-outline bg-white q-mr-sm" no-caps @click="router.push(`/${slug}/produtos`)" />
          <q-btn flat round icon="settings" class="settings-btn" @click="router.push(`/${slug}/settings`)" />
        </div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page padding class="dashboard-page">
        <div style="max-width: 1200px; margin: 0 auto;">
          
          <div class="row items-center q-mb-lg q-mt-md">
            <div class="text-h4 text-weight-bolder page-title">A Sua Agenda</div>
          </div>

          <div v-if="agendamentoStore.carregando" class="flex flex-center q-pa-xl">
            <q-spinner-tail color="primary" size="3em" />
            <div class="text-grey-6 q-ml-md text-weight-medium">A carregar os seus dados...</div>
          </div>

          <q-banner v-else-if="agendamentoStore.erro" class="alert-banner q-mb-md rounded-borders shadow-2">
            <template v-slot:avatar><q-icon name="error" /></template>
            {{ agendamentoStore.erro }}
          </q-banner>

          <template v-else>
            <div v-if="(authStore.userType === 'barbeiro' || authStore.userType === 'admin')" class="row q-col-gutter-lg q-mb-xl">
              <div class="col-12 col-md-4">
                <q-card class="stat-card shadow-12 rounded-borders">
                  <q-card-section>
                    <div class="row items-center no-wrap">
                      <div class="col">
                        <div class="text-subtitle2 text-weight-bold stat-title text-uppercase">Faturação Total</div>
                        <div class="text-h3 text-weight-bolder q-mt-sm stat-value">R$ {{ calcularFaturacao() }}</div>
                      </div>
                      <div class="col-auto">
                        <div class="stat-icon-wrapper">
                          <q-icon name="account_balance_wallet" size="48px" class="stat-icon" />
                        </div>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <q-tabs
              v-model="abaAtual"
              dense
              class="custom-tabs q-mb-lg"
              active-color="primary"
              indicator-color="primary"
              align="left"
              narrow-indicator
            >
              <q-tab name="proximos" label="Próximos Atendimentos" no-caps class="text-weight-bold" />
              <q-tab v-if="authStore.userType !== 'cliente'" name="calendario" label="Visão de Calendário" no-caps class="text-weight-bold" />
              <q-tab v-if="authStore.userType !== 'cliente'" name="historico" label="Histórico" no-caps class="text-weight-bold" />
              <q-tab v-if="authStore.userType !== 'cliente'" name="servicos_manag" label="Gestão de Serviços" no-caps class="text-weight-bold" />
              <q-tab v-if="authStore.userType !== 'cliente'" name="produtos" label="Gestão de Produtos" no-caps class="text-weight-bold" />
            </q-tabs>
            <q-separator class="q-mb-lg separator-custom" />

            <q-tab-panels v-model="abaAtual" animated class="bg-transparent">
              
              <q-tab-panel name="proximos" class="q-px-none q-pt-none">
                <div v-if="agendamentosProximos.length === 0" class="flex flex-center q-pa-xl dash-card empty-state shadow-2">
                  <q-icon name="event_available" size="72px" color="grey-4" />
                  <div class="text-h6 text-grey-5 q-mt-md full-width text-center text-weight-medium">Não existem próximos agendamentos.</div>
                </div>
                <div v-else class="row q-col-gutter-lg">
                  <div class="col-12 col-sm-6 col-md-4" v-for="agendamento in agendamentosProximos" :key="agendamento.id">
                    <q-card class="dash-card item-card cursor-pointer shadow-3" bordered @click="router.push(`/${slug}/agendamento/${agendamento.id}`)">
                      <q-card-section>
                        <div class="row items-center justify-between q-mb-md">
                          <div class="text-h6 text-weight-bold item-title">{{ agendamento.servico }}</div>
                          <q-chip :color="corEstado(agendamento.status)" text-color="white" size="sm" class="text-weight-bolder text-uppercase shadow-1">
                            {{ agendamento.status }}
                          </q-chip>
                        </div>
                        <q-list dense class="item-list">
                          <q-item class="q-px-none">
                            <q-item-section avatar min-width="36px"><q-icon name="schedule" class="item-icon" size="22px" /></q-item-section>
                            <q-item-section class="item-text text-weight-medium">{{ formatarData(agendamento.data_hora) }}</q-item-section>
                          </q-item>
                          
                          <q-item class="q-px-none">
                            <q-item-section avatar min-width="36px"><q-icon name="payments" class="item-icon" size="22px" /></q-item-section>
                            <q-item-section class="item-text text-weight-medium">R$ {{ agendamento.preco?.toFixed(2) || '0.00' }}</q-item-section>
                          </q-item>

                          <q-item class="q-px-none">
                            <q-item-section avatar min-width="36px">
                              <q-icon :name="authStore.userType === 'barbeiro' || authStore.userType === 'admin' ? 'person' : 'badge'" class="item-icon" size="22px" />
                            </q-item-section>
                            <q-item-section class="item-text">
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
                    </q-card>
                  </div>
                </div>
              </q-tab-panel>

              <q-tab-panel v-if="authStore.userType !== 'cliente'" name="calendario" class="q-px-none q-pt-none">
                <q-card class="dash-card shadow-3" bordered>
                  <q-card-section class="q-pa-lg">
                    <div class="text-h5 q-mb-lg text-weight-bold page-title">Agenda de Hoje</div>
                    <q-timeline color="primary">
                      
                      <q-timeline-entry
                        v-for="bloqueio in bloqueios"
                        :key="'b-'+bloqueio.id"
                        :subtitle="formatarHora(bloqueio.inicio) + ' - ' + formatarHora(bloqueio.fim)"
                        icon="block"
                        color="negative"
                        class="timeline-entry"
                      >
                        <div class="text-weight-bold text-negative text-h6">BLOQUEADO: {{ bloqueio.motivo }}</div>
                        <q-btn flat dense color="negative" label="Remover" size="sm" class="q-mt-sm text-weight-bold" @click="removerBloqueio(bloqueio.id)" no-caps />
                      </q-timeline-entry>

                      <q-timeline-entry
                        v-for="agendamento in agendamentosDeHoje"
                        :key="'a-'+agendamento.id"
                        :subtitle="formatarHora(agendamento.data_hora)"
                        :color="corEstado(agendamento.status)"
                        icon="content_cut"
                        class="timeline-entry"
                      >
                        <div class="text-weight-bold text-h6 item-title">{{ agendamento.servico }}</div>
                        <div class="item-text text-weight-medium q-mt-xs">Cliente: {{ agendamento.cliente?.nome || agendamento.cliente_nome }}</div>
                      </q-timeline-entry>
                      
                    </q-timeline>
                  </q-card-section>
                </q-card>
              </q-tab-panel>

              <q-tab-panel v-if="authStore.userType !== 'cliente'" name="servicos_manag" class="q-px-none q-pt-none">
                <div class="row justify-between items-center q-mb-md">
                  <div class="text-h5 text-weight-bold page-title">Tabela de Preços e Serviços</div>
                  <q-btn color="primary" icon="add" label="Novo Serviço" unelevated class="action-btn shadow-3" no-caps @click="dialogServico = true" />
                </div>

                <div v-if="listaServicos.length === 0" class="flex flex-center q-pa-xl dash-card empty-state shadow-2">
                  <q-icon name="content_cut" size="72px" color="grey-4" />
                  <div class="text-h6 text-grey-5 q-mt-md full-width text-center text-weight-medium">Nenhum serviço cadastrado.</div>
                </div>
                
                <div v-else class="row q-col-gutter-lg">
                  <div class="col-12 col-sm-6 col-md-4" v-for="serv in listaServicos" :key="serv.id">
                    <q-card class="dash-card item-card shadow-3" bordered>
                      <q-card-section class="row items-center justify-between">
                        <div>
                          <div class="text-h6 text-weight-bold item-title q-mb-xs">{{ serv.nome }}</div>
                          <div class="text-h5 text-weight-bolder text-positive">R$ {{ serv.preco.toFixed(2) }}</div>
                        </div>
                        <q-btn flat round color="negative" icon="delete" size="sm" @click="deletarServico(serv.id)" />
                      </q-card-section>
                    </q-card>
                  </div>
                </div>
              </q-tab-panel>

              <q-tab-panel v-if="authStore.userType !== 'cliente'" name="historico" class="q-px-none q-pt-none">
                <div v-if="agendamentosHistorico.length === 0" class="flex flex-center q-pa-xl dash-card empty-state shadow-2">
                  <q-icon name="history" size="72px" color="grey-4" />
                  <div class="text-h6 text-grey-5 q-mt-md full-width text-center text-weight-medium">O histórico está vazio.</div>
                </div>
                <div v-else class="row q-col-gutter-lg">
                  <div class="col-12 col-sm-6 col-md-4" v-for="agendamento in agendamentosHistorico" :key="agendamento.id">
                    <q-card class="dash-card item-card cursor-pointer shadow-3" bordered @click="router.push(`/${slug}/agendamento/${agendamento.id}`)">
                      <q-card-section>
                        <div class="row items-center justify-between q-mb-md">
                          <div class="text-h6 text-weight-bold item-title">{{ agendamento.servico }}</div>
                          <q-chip :color="corEstado(agendamento.status)" text-color="white" size="sm" class="text-weight-bolder text-uppercase shadow-1">
                            {{ agendamento.status }}
                          </q-chip>
                        </div>
                        <q-list dense class="item-list">
                          <q-item class="q-px-none">
                            <q-item-section avatar min-width="36px"><q-icon name="schedule" class="item-icon" size="22px" /></q-item-section>
                            <q-item-section class="item-text text-weight-medium">{{ formatarData(agendamento.data_hora) }}</q-item-section>
                          </q-item>
                          <q-item class="q-px-none">
                            <q-item-section avatar min-width="36px">
                              <q-icon name="person" class="item-icon" size="22px" />
                            </q-item-section>
                            <q-item-section class="item-text">
                              <span><strong>Cliente:</strong> {{ agendamento.cliente?.nome || agendamento.cliente_nome }}</span>
                            </q-item-section>
                          </q-item>
                        </q-list>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>
              </q-tab-panel>

              <q-tab-panel v-if="authStore.userType !== 'cliente'" name="produtos" class="q-px-none q-pt-none">
                <div class="row justify-between items-center q-mb-md">
                  <div class="text-h5 text-weight-bold page-title">Catálogo da Loja</div>
                  <q-btn color="primary" icon="add" label="Novo Produto" unelevated class="action-btn shadow-3" no-caps @click="dialogProduto = true" />
                </div>

                <div v-if="produtos.length === 0" class="flex flex-center q-pa-xl dash-card empty-state shadow-2">
                  <q-icon name="inventory_2" size="72px" color="grey-4" />
                  <div class="text-h6 text-grey-5 q-mt-md full-width text-center text-weight-medium">Nenhum produto cadastrado na vitrine.</div>
                </div>
                <div v-else class="row q-col-gutter-lg">
                  <div class="col-12 col-sm-6 col-md-4" v-for="produto in produtos" :key="produto.id">
                    <q-card class="dash-card item-card shadow-3" bordered>
                      <q-card-section>
                        <div class="row items-center justify-between q-mb-sm">
                          <q-chip color="primary" text-color="white" size="sm" class="text-weight-bold text-uppercase shadow-1">
                            {{ produto.categoria }}
                          </q-chip>
                          <q-btn flat round color="negative" icon="delete" size="sm" @click="deletarProduto(produto.id)" title="Remover da Vitrine" />
                        </div>
                        <div class="text-h6 text-weight-bold item-title q-mb-xs ellipsis">{{ produto.nome }}</div>
                        <div class="text-body2 text-grey-7 q-mb-md" style="min-height: 40px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                          {{ produto.descricao || 'Sem descrição' }}
                        </div>
                        <div class="text-h5 text-weight-bolder text-positive">R$ {{ produto.preco.toFixed(2) }}</div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>
              </q-tab-panel>

            </q-tab-panels>
          </template>

        </div>
      </q-page>
    </q-page-container>
    
    <q-dialog v-model="dialogBloqueio">
      <q-card class="dialog-card shadow-12">
        <q-card-section class="dialog-header">
          <div class="text-h5 text-weight-bold text-white">Bloquear Horário</div>
        </q-card-section>

        <q-card-section class="q-pa-lg">
          <q-input v-model="novoBloqueio.inicio" type="datetime-local" label="Início" outlined color="primary" class="custom-input q-mb-md" />
          <q-input v-model="novoBloqueio.fim" type="datetime-local" label="Fim" outlined color="primary" class="custom-input q-mb-md" />
          <q-input v-model="novoBloqueio.motivo" label="Motivo (ex: Almoço)" outlined color="primary" class="custom-input" />
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancelar" color="grey-8" class="text-weight-bold" v-close-popup no-caps />
          <q-btn label="Salvar Bloqueio" color="negative" class="text-weight-bold action-btn shadow-2" @click="salvarBloqueio" v-close-popup unelevated no-caps />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogServico">
      <q-card class="dialog-card shadow-12">
        <q-card-section class="bg-primary text-white">
          <div class="text-h5 text-weight-bold">Adicionar / Modificar Serviço</div>
        </q-card-section>

        <q-card-section class="q-pa-lg q-gutter-y-md">
          <q-input v-model="novoServico.nome" label="Nome do Serviço (Ex: Corte + Pezinho)" outlined color="primary" class="custom-input" />
          <q-input v-model.number="novoServico.preco" type="number" label="Preço Cobrado (R$)" outlined color="primary" class="custom-input" />
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancelar" color="grey-8" class="text-weight-bold" v-close-popup no-caps />
          <q-btn label="Salvar Serviço" color="primary" class="text-weight-bold action-btn shadow-2" @click="salvarServico" v-close-popup unelevated no-caps />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogProduto">
      <q-card class="dialog-card shadow-12">
        <q-card-section class="bg-primary text-white">
          <div class="text-h5 text-weight-bold">Cadastrar Produto</div>
        </q-card-section>

        <q-card-section class="q-pa-lg q-gutter-y-md">
          <q-input v-model="novoProduto.nome" label="Nome do Produto (Ex: Pomada Efeito Mate)" outlined color="primary" class="custom-input" />
          <q-input v-model="novoProduto.descricao" label="Breve Descrição (Opcional)" type="textarea" rows="2" outlined color="primary" class="custom-input" />
          
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <q-file v-model="imagemUpload" label="Carregar Imagem do Computador" outlined color="primary" class="custom-input" accept="image/*" clearable>
                <template v-slot:prepend><q-icon name="attach_file" color="grey-6" /></template>
              </q-file>
            </div>
            <div class="col-12 col-md-6">
              <q-input v-model="novoProduto.imagem_url" label="Ou URL da Imagem" placeholder="https://..." outlined color="primary" class="custom-input" />
            </div>
          </div>
          
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <q-input v-model.number="novoProduto.preco" type="number" label="Preço (R$)" outlined color="primary" class="custom-input" />
            </div>
            <div class="col-6">
              <q-select v-model="novoProduto.categoria" :options="categoriasLoja" label="Categoria" outlined color="primary" class="custom-input" />
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancelar" color="grey-8" class="text-weight-bold" v-close-popup no-caps />
          <q-btn label="Salvar Produto" color="primary" class="text-weight-bold action-btn shadow-2" @click="salvarProduto" v-close-popup unelevated no-caps />
        </q-card-actions>
      </q-card>
    </q-dialog>

  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useAgendamentoStore } from '@/stores/agendamentoStore'
import { useSistemaStore } from '@/stores/sistemaStore'

const route = useRoute()
const router = useRouter()
const slug = route.params.slug as string

const sistemaStore = useSistemaStore()
const authStore = useAuthStore()
const agendamentoStore = useAgendamentoStore()

const dialogServico = ref(false)
const listaServicos = ref<any[]>([])
const novoServico = ref({ nome: '', preco: 0 })

// FUNÇÕES DE SERVIÇOS
const fetchServicos = async () => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/servicos/`)
    if (res.ok) listaServicos.value = await res.json()
  } catch (e) { console.error(e) }
}

const salvarServico = async () => {
  if (!novoServico.value.nome) return
  try {
    await fetch(`${import.meta.env.VITE_API_URL}/${slug}/servicos/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(novoServico.value)
    })
    fetchServicos()
    novoServico.value = { nome: '', preco: 0 }
  } catch (e) { console.error(e) }
}

const deletarServico = async (id: number) => {
  try {
    await fetch(`${import.meta.env.VITE_API_URL}/${slug}/servicos/${id}`, { method: 'DELETE' })
    fetchServicos()
  } catch (e) { console.error(e) }
}

const abaAtual = ref('proximos')
const wsConnected = ref(false)
let ws: WebSocket | null = null
const imagemUpload = ref<File | null>(null)

const dialogBloqueio = ref(false)
const bloqueios = ref<any[]>([])
const novoBloqueio = ref({ inicio: '', fim: '', motivo: 'Pausa' })

// VARIÁVEIS DE PRODUTOS
const dialogProduto = ref(false)
const produtos = ref<any[]>([])
const categoriasLoja = ['Bonés', 'Relógios', 'Perfumes', 'Camisas', 'Óleos e Cremes', 'Outros']
const novoProduto = ref({ nome: '', descricao: '', preco: 0, categoria: 'Outros', imagem_url: '' })

const inicializarWebSocket = () => {
  const userId = authStore.userId
  if (!userId) return

  let wsUrl = import.meta.env.VITE_API_URL.replace('http', 'ws').replace('https', 'wss')
  if (wsUrl.startsWith('/')) {
     const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
     wsUrl = `${protocol}//${window.location.host}${wsUrl}`
  }

  ws = new WebSocket(`${wsUrl}/ws/${userId}`)

  ws.onopen = () => {
    wsConnected.value = true
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.action === "UPDATE_AGENDAMENTOS") {
        agendamentoStore.fetchAgendamentos(slug)
      } else if (data.action === "UPDATE_BLOQUEIOS") {
        fetchBloqueios()
      }
    } catch (e) {
      console.log("Mensagem WebSocket recebida (não-JSON):", event.data)
    }
  }

  ws.onclose = () => {
    wsConnected.value = false
    setTimeout(inicializarWebSocket, 5000)
  }
}

const fetchBloqueios = async () => {
  if (authStore.userType === 'cliente') return
  try {
    const userId = authStore.userId 
    if (!userId) return

    const res = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/bloqueios/barbeiro/${userId}`)
    if (res.ok) {
      const data = await res.json()
      const agora = new Date()
      // Filtra os bloqueios: só mostra aqueles cujo horário de fim ainda não passou
      bloqueios.value = data.filter((b: any) => new Date(b.fim) >= agora)
    }
  } catch (error) {
    console.error("Erro ao buscar bloqueios", error)
  }
}

// FUNÇÃO PARA REMOVER A PAUSA/BLOQUEIO
const removerBloqueio = async (id: number) => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/bloqueios/${id}`, { method: 'DELETE' })
    if (res.ok) {
      // Atualiza a lista de bloqueios após apagar com sucesso
      fetchBloqueios()
    }
  } catch (e) {
    console.error("Erro ao remover bloqueio", e)
  }
}

const salvarBloqueio = async () => {
  try {
    const payload = {
      barbeiro_id: authStore.userId, 
      inicio: new Date(novoBloqueio.value.inicio).toISOString(),
      fim: new Date(novoBloqueio.value.fim).toISOString(),
      motivo: novoBloqueio.value.motivo
    }
    
    await fetch(`${import.meta.env.VITE_API_URL}/${slug}/bloqueios/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    fetchBloqueios()
    novoBloqueio.value = { inicio: '', fim: '', motivo: 'Pausa' }
  } catch (e) {
    console.error(e)
  }
}

// FUNÇÕES DE PRODUTOS
const fetchProdutos = async () => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/produtos/`)
    if (res.ok) produtos.value = await res.json()
  } catch (e) { console.error(e) }
}

const salvarProduto = async () => {
  try {
    // 1. Se o utilizador selecionou um ficheiro, faz o upload primeiro
    // A rota de upload da imagem é global (sem slug)
    if (imagemUpload.value) {
      const formData = new FormData()
      formData.append('file', imagemUpload.value)
      
      const uploadRes = await fetch(`${import.meta.env.VITE_API_URL}/upload/imagem`, {
        method: 'POST',
        body: formData
      })
      
      if (uploadRes.ok) {
        const uploadData = await uploadRes.json()
        novoProduto.value.imagem_url = uploadData.url // Preenche a URL com o link local gerado
      }
    }

    // 2. Grava o produto no banco de dados da loja
    await fetch(`${import.meta.env.VITE_API_URL}/${slug}/produtos/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(novoProduto.value)
    })
    
    // 3. Limpa o formulário e atualiza a lista
    fetchProdutos()
    novoProduto.value = { nome: '', descricao: '', preco: 0, categoria: 'Outros', imagem_url: '' }
    imagemUpload.value = null
    
  } catch (e) { 
    console.error(e) 
  }
}

const deletarProduto = async (id: number) => {
  try {
    await fetch(`${import.meta.env.VITE_API_URL}/${slug}/produtos/${id}`, { method: 'DELETE' })
    fetchProdutos()
  } catch (e) { console.error(e) }
}

onMounted(() => {
  if (authStore.isAuthenticated()) {
    agendamentoStore.fetchAgendamentos(slug) // Aqui o slug será enviado para a Store
    fetchBloqueios()
    fetchProdutos()
    inicializarWebSocket()
    fetchServicos()
  }
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})

const agendamentosProximos = computed(() => {
  return agendamentoStore.agendamentos.filter(a => {
    const s = a.status?.toLowerCase() || ''
    return s === 'pendente' || s === 'confirmado'
  }).sort((a, b) => new Date(a.data_hora).getTime() - new Date(b.data_hora).getTime())
})

const agendamentosDeHoje = computed(() => {
  const hoje = new Date().toDateString()
  return agendamentosProximos.value.filter(a => {
    return new Date(a.data_hora).toDateString() === hoje
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

const formatarHora = (dataStr: string) => {
  return new Date(dataStr).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })
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
/* Os seus estilos não foram alterados */
.dashboard-layout {
  --cor-fundo-dash: #f8fafc;
  --cor-cartao-bg: #ffffff;
  --cor-header-bg: #1e293b;
  --cor-header-texto: #ffffff;
  --cor-texto-primario: #0f172a;
  --cor-texto-secundario: #64748b;
  --cor-texto-icone: #94a3b8;
  --cor-gradiente-stat-inicio: #2563eb;
  --cor-gradiente-stat-fim: #1d4ed8;
  --borda-raio: 16px;
  --borda-raio-pequeno: 10px;
  --borda-cor: #e2e8f0;
}
.dashboard-page {
  background-color: var(--cor-fundo-dash);
  min-height: 100vh;
}
.page-title {
  color: var(--cor-texto-primario);
  letter-spacing: -0.5px;
}
.dash-header {
  background-color: var(--cor-header-bg);
  color: var(--cor-header-texto);
}
.logo-circle-small {
  width: 40px;
  height: 40px;
  background-color: var(--q-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.logo-icon-small {
  font-size: 20px;
  color: white;
}
.header-title {
  font-size: 1.25rem;
  letter-spacing: 0.5px;
}
.header-subtitle {
  color: #cbd5e1;
}
.action-btn {
  border-radius: var(--borda-raio-pequeno);
  font-weight: 600;
  letter-spacing: 0.3px;
}
.action-btn-outline {
  border-radius: var(--borda-raio-pequeno);
  font-weight: 600;
  border-color: rgba(255, 255, 255, 0.2);
}
.settings-btn {
  color: #cbd5e1;
  transition: transform 0.3s ease, color 0.3s ease;
}
.settings-btn:hover {
  transform: rotate(45deg);
  color: white;
}
.dash-card {
  background: var(--cor-cartao-bg);
  border-radius: var(--borda-raio);
  border-color: var(--borda-cor);
}
.stat-card {
  background: linear-gradient(135deg, var(--cor-gradiente-stat-inicio) 0%, var(--cor-gradiente-stat-fim) 100%);
  color: white;
  border: none;
}
.stat-title {
  color: rgba(255, 255, 255, 0.8);
  letter-spacing: 1px;
}
.stat-value {
  letter-spacing: -1px;
}
.stat-icon-wrapper {
  background: rgba(255, 255, 255, 0.15);
  padding: 12px;
  border-radius: 50%;
  backdrop-filter: blur(5px);
}
.stat-icon {
  color: white;
  opacity: 0.9;
}
.custom-tabs {
  color: var(--cor-texto-secundario);
  font-size: 1.1rem;
}
.separator-custom {
  background-color: var(--borda-cor);
}
.empty-state {
  border: 1px dashed var(--borda-cor);
  background-color: rgba(255, 255, 255, 0.5);
}
.item-card {
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.15) !important;
  border-color: var(--q-primary);
}
.item-title {
  color: var(--cor-texto-primario);
}
.item-list {
  color: var(--cor-texto-secundario);
}
.item-icon {
  color: var(--cor-texto-icone);
}
.item-text {
  font-size: 0.95rem;
}
.alert-banner {
  background-color: #fee2e2;
  color: #b91c1c;
  border-left: 6px solid #ef4444;
  font-weight: 600;
}
.dialog-card {
  min-width: 380px;
  border-radius: var(--borda-raio);
  overflow: hidden;
}
.dialog-header {
  background-color: #ef4444; 
  padding: 16px 24px;
}
.custom-input :deep(.q-field__control) {
  border-radius: 8px;
}
.timeline-entry :deep(.q-timeline__title) {
  color: var(--cor-texto-primario);
}
.timeline-entry :deep(.q-timeline__subtitle) {
  color: var(--cor-texto-secundario);
  font-weight: 600;
}
</style>