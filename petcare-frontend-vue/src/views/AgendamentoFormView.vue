<template>
  <q-layout view="hHh lpR fFf" class="form-layout">
    <q-page-container>
      <q-page padding class="flex flex-center form-page">
        
        <div style="width: 100%; max-width: 600px;">
          <q-btn 
            flat 
            icon="arrow_back" 
            label="Voltar" 
            class="q-mb-md back-btn" 
            @click="router.back()" 
            no-caps 
            ripple
          />

          <q-card class="form-card shadow-12">
            
            <q-card-section class="form-header text-center q-pa-xl">
              <div v-if="sistemaStore.logoUrl" class="q-mx-auto q-mb-md flex flex-center">
                <q-img 
                  :src="sistemaStore.logoUrl" 
                  style="max-height: 90px; max-width: 200px; border-radius: 8px;" 
                  fit="contain" 
                />
              </div>
              <div v-else class="header-icon-wrapper shadow-3 q-mx-auto q-mb-md">
                <q-icon name="calendar_month" class="header-icon" />
              </div>

              <div class="text-h4 text-weight-bolder text-white letter-spacing">
                {{ sistemaStore.nomeBarbearia || 'Nossa Barbearia' }}
              </div>
              
              <div class="text-subtitle1 text-white text-weight-medium q-mt-sm opacity-80">
                Reserve um Horário
              </div>
            </q-card-section>

            <q-card-section class="q-pa-xl">
              <q-form @submit.prevent="submeterAgendamento" class="q-gutter-y-lg">
                
                <div class="row q-col-gutter-lg">
                  <div class="col-12 col-sm-6">
                    <div class="text-subtitle2 text-weight-bold q-mb-sm text-grey-8">Profissional</div>
                    <q-select
                      v-model="form.barbeiro_id"
                      :options="listaBarbeiros"
                      option-value="id"
                      option-label="nome"
                      emit-value
                      map-options
                      label="Escolha quem o vai atender"
                      outlined
                      color="primary"
                      class="custom-input"
                      hide-bottom-space
                      :loading="carregandoBarbeiros"
                      :rules="[val => !!val || 'Obrigatório']"
                    >
                      <template v-slot:prepend><q-icon name="badge" color="grey-6" /></template>
                    </q-select>
                  </div>
                  
                  <div class="col-12 col-sm-6">
                    <div class="text-subtitle2 text-weight-bold q-mb-sm text-grey-8">Serviço</div>
                    <q-select
                      v-model="form.servico"
                      :options="Object.keys(tabelaPrecos)"
                      label="Selecione o serviço"
                      outlined
                      color="primary"
                      class="custom-input"
                      hide-bottom-space
                      :rules="[val => !!val || 'Obrigatório']"
                    >
                      <template v-slot:prepend><q-icon name="content_cut" color="grey-6" /></template>
                      <template v-slot:append v-if="form.servico">
  <q-badge class="price-badge shadow-1">{{ formatarPreco(tabelaPrecos[form.servico] || 0) }}</q-badge>
</template>
                    </q-select>
                  </div>
                </div>

                <q-separator class="separator-custom q-my-md" />

                <div>
                  <div class="text-subtitle2 text-weight-bold q-mb-sm text-grey-8">Data do Atendimento</div>
                  <q-input
                    v-model="dataSelecionada"
                    type="date"
                    outlined
                    color="primary"
                    class="custom-input"
                    hide-bottom-space
                    :min="dataMinima"
                    :rules="[val => !!val || 'A data é obrigatória']"
                  />
                </div>

                <div v-if="dataSelecionada && form.barbeiro_id && (!configuracaoBarbeiroSelecionado || configuracaoBarbeiroSelecionado.loja_aberta)" class="time-slots-container q-pa-lg rounded-borders shadow-1">
                  <div class="text-subtitle1 text-weight-bold text-primary q-mb-md flex items-center">
                    <q-icon name="schedule" class="q-mr-sm" size="24px"/> 
                    Horários Disponíveis
                  </div>
                  
                  <div class="row q-gutter-sm">
                    <q-btn
                      v-for="hora in horariosDisponiveis"
                      :key="hora"
                      :label="hora"
                      :color="horaSelecionada === hora ? 'primary' : 'white'"
                      :text-color="horaSelecionada === hora ? 'white' : 'grey-9'"
                      :outline="horaSelecionada !== hora"
                      class="time-btn col-auto text-weight-bold"
                      style="min-width: 80px;"
                      @click="horaSelecionada = hora"
                      unelevated
                    />
                    
                    <div v-if="horariosDisponiveis.length === 0" class="empty-time-state q-pa-md flex items-center rounded-borders full-width justify-center">
                      <q-icon name="event_busy" size="28px" class="q-mr-sm text-grey-6"/> 
                      <span class="text-grey-7 text-weight-medium">Sem horários livres neste dia.</span>
                    </div>
                  </div>
                </div>

                <div v-if="configuracaoBarbeiroSelecionado && !configuracaoBarbeiroSelecionado.loja_aberta" class="store-closed-banner q-pa-xl text-center shadow-2">
                  <q-icon name="storefront" size="64px" color="negative" class="q-mb-md" />
                  <div class="text-h5 text-negative text-weight-bolder letter-spacing">Barbearia Fechada</div>
                  <div class="text-body1 text-grey-9 q-mt-md text-weight-medium">
                    Este profissional não está a aceitar agendamentos de momento. Por favor, tente selecionar outro profissional ou volte mais tarde.
                  </div>
                </div>

                <div class="q-mt-xl">
                  <q-btn 
                    type="submit" 
                    color="primary" 
                    class="full-width submit-btn shadow-4" 
                    size="xl" 
                    label="Confirmar Agendamento" 
                    :loading="submetendo" 
                    :disabled="!formularioValido || (configuracaoBarbeiroSelecionado && !configuracaoBarbeiroSelecionado.loja_aberta)"
                    unelevated 
                    no-caps
                  />
                </div>
              </q-form>
            </q-card-section>
          </q-card>
        </div>

      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useSistemaStore } from '@/stores/sistemaStore' // Importado o sistemaStore
import { useQuasar } from 'quasar'

const route = useRoute() 
const router = useRouter()
const authStore = useAuthStore()
const sistemaStore = useSistemaStore() // Instanciado o sistemaStore
const $q = useQuasar()

const listaServicosBD = ref<any[]>([])

const tabelaPrecos = computed(() => {
  const mapa: Record<string, number> = {}
  listaServicosBD.value.forEach(s => {
    mapa[s.nome] = s.preco
  })
  return mapa
})
const submetendo = ref(false)
const carregandoBarbeiros = ref(true)
const listaBarbeiros = ref<any[]>([])

const form = ref({
  barbeiro_id: null,
  servico: ''
})

const dataSelecionada = ref('')
const horaSelecionada = ref('')
const horariosOcupados = ref<string[]>([])
const bloqueiosDoProfissional = ref<any[]>([])
const folgasDoProfissional = ref<any[]>([])
const configuracaoBarbeiroSelecionado = ref<any>(null)

const obterDataAtualLocal = () => {
  const agora = new Date()
  const ano = agora.getFullYear()
  const mes = String(agora.getMonth() + 1).padStart(2, '0')
  const dia = String(agora.getDate()).padStart(2, '0')
  return `${ano}-${mes}-${dia}`
}
const dataMinima = ref(obterDataAtualLocal())

const horariosDisponiveis = computed(() => {
  if (!dataSelecionada.value || !configuracaoBarbeiroSelecionado.value) return []
  if (folgasDoProfissional.value.some(f => f.data === dataSelecionada.value)) {
    return [] 
  }
  const dataObj = new Date(dataSelecionada.value + 'T00:00:00')
  const diaSemana = dataObj.getDay()
  
  let listaDias = []
  try {
    listaDias = JSON.parse(configuracaoBarbeiroSelecionado.value.horarios_json)
  } catch (e) {
    return []
  }
  
  const configDia = listaDias.find((d: any) => d.dia === diaSemana)
  if (!configDia || !configDia.trabalha) return []
  
  const slotsDoDia: string[] = []
  const [startH, startM] = configDia.inicio.split(':').map(Number)
  const [endH, endM] = configDia.fim.split(':').map(Number)
  const intervalo = configuracaoBarbeiroSelecionado.value.intervalo_minutos || 30
  
  let atualMinutos = startH * 60 + startM
  const fimMinutos = endH * 60 + endM
  
  while (atualMinutos < fimMinutos) {
    const h = Math.floor(atualMinutos / 60).toString().padStart(2, '0')
    const m = (atualMinutos % 60).toString().padStart(2, '0')
    slotsDoDia.push(`${h}:${m}`)
    atualMinutos += intervalo
  }
  
  const agora = new Date()
  const hojeLocal = obterDataAtualLocal()
  
  return slotsDoDia.filter(hora => {
    if (horariosOcupados.value.includes(hora)) return false
    
    const slotTime = new Date(`${dataSelecionada.value}T${hora}:00`)
    for (const bloqueio of bloqueiosDoProfissional.value) {
      const bInicio = new Date(bloqueio.inicio)
      const bFim = new Date(bloqueio.fim)
      if (slotTime >= bInicio && slotTime < bFim) {
        return false
      }
    }
    
    if (dataSelecionada.value === hojeLocal) {
      const [h, m] = hora.split(':').map(Number) as [number, number]
      const horaAtual = agora.getHours()
      const minutoAtual = agora.getMinutes()
      
      if (h < horaAtual || (h === horaAtual && m <= minutoAtual)) {
        return false
      }
    }
    return true
  })
})

const formularioValido = computed(() => {
  return dataSelecionada.value && horaSelecionada.value && form.value.servico && form.value.barbeiro_id
})

const formatarPreco = (valor: number) => new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'BRL' }).format(valor)

onMounted(async () => {
  const slug = route.params.slug as string
  try {
    const response = await fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${slug}/barbeiros/`)
    if (response.ok) listaBarbeiros.value = await response.json()

    const resServicos = await fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${slug}/servicos/`)
    if (resServicos.ok) listaServicosBD.value = await resServicos.json()
    
  } catch (error) {
    console.error("Erro no carregamento inicial do formulário", error)
  } finally {
    carregandoBarbeiros.value = false
  }
})

watch([() => form.value.barbeiro_id, dataSelecionada], async ([novoProfissionalId, novaData]) => {
  horaSelecionada.value = '' 
  const idReal = typeof novoProfissionalId === 'object' ? (novoProfissionalId as any)?.id : novoProfissionalId
  const slug = route.params.slug as string

  if (!idReal || !novaData) {
    horariosOcupados.value = []
    bloqueiosDoProfissional.value = []
    folgasDoProfissional.value = []
    configuracaoBarbeiroSelecionado.value = null
    return
  }
  
  try {
    const [resAgendamentos, resBloqueios, resConfig, resFolgas] = await Promise.all([
      fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${slug}/agendamentos/barbeiro/${idReal}`),
      fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${slug}/bloqueios/barbeiro/${idReal}`),
      fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${slug}/configuracao/${idReal}`),
      fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${slug}/folgas/barbeiro/${idReal}`) 
    ])
    
    if (resFolgas.ok) {
      folgasDoProfissional.value = await resFolgas.json()
    } else {
      folgasDoProfissional.value = []
    }

    if (resConfig.ok) {
      configuracaoBarbeiroSelecionado.value = await resConfig.json()
    }

    if (resBloqueios.ok) {
      bloqueiosDoProfissional.value = await resBloqueios.json()
    } else {
      bloqueiosDoProfissional.value = []
    }

    if (resAgendamentos.ok) {
      const agendamentos = await resAgendamentos.json()
      const ocupados: string[] = []
      
      agendamentos.forEach((a: any) => {
        if (a.status?.toLowerCase() !== 'cancelado') {
          const dataNormalizada = a.data_hora.replace('Z', '').replace(' ', 'T')
          const partes = dataNormalizada.split('T')
          
          if (partes.length === 2) {
            const dataAgendamento = partes[0]
            const horaAgendamento = partes[1].substring(0, 5) 
            
            if (dataAgendamento === novaData) {
              ocupados.push(horaAgendamento)
            }
          }
        }
      })
      horariosOcupados.value = ocupados
    }
  } catch (err) {
    console.error("Erro ao verificar disponibilidade ou bloqueios:", err)
  }
})

const submeterAgendamento = async () => {
  if (!authStore.userId) return
  submetendo.value = true
  const slug = route.params.slug as string
  
  try {
    const idProfissional = typeof form.value.barbeiro_id === 'object' 
      ? (form.value.barbeiro_id as any)?.id 
      : Number(form.value.barbeiro_id);

    const dados = {
      barbeiro_id: idProfissional,
      servico: form.value.servico,
      preco: Number(tabelaPrecos.value[form.value.servico]) || 0,
      data_hora: `${dataSelecionada.value}T${horaSelecionada.value}:00`
    }
    
    const response = await fetch(`${(import.meta.env.DEV ? 'http://localhost:8000' : '/api')}/${slug}/usuarios/${authStore.userId}/agendamentos/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })

    if (!response.ok) {
      const erroApi = await response.json()
      const mensagemErro = Array.isArray(erroApi.detail) 
        ? erroApi.detail.map((e: any) => `${e.loc[1]}: ${e.msg}`).join(', ')
        : erroApi.detail;
      throw new Error(mensagemErro || 'Falha na validação')
    }

    $q.notify({ type: 'positive', message: 'Agendamento criado com sucesso!', position: 'top' })
    router.push(`/${slug}/dashboard`)
    
  } catch (error: any) {
    $q.notify({ type: 'negative', message: `Erro ao agendar: ${error.message}`, position: 'top', timeout: 5000 })
  } finally {
    submetendo.value = false
  }
}
</script>

<style scoped>
.form-layout {
  --cor-fundo-pagina: #f1f5f9;
  --cor-cartao-bg: #ffffff;
  --cor-header-inicio: var(--q-primary);
  --cor-header-fim: #1e1f20;
  --borda-raio: 20px;
  --borda-raio-input: 12px;
  --borda-cor: #e2e8f0;
}
.form-page {
  background-color: var(--cor-fundo-pagina);
  min-height: 100vh;
}
.back-btn {
  color: #64748b !important;
  font-weight: 600;
  border-radius: 8px;
  transition: background-color 0.2s;
}
.back-btn:hover {
  background-color: rgba(100, 116, 139, 0.1);
}
.letter-spacing {
  letter-spacing: -0.5px;
}
.opacity-80 {
  opacity: 0.8;
}
.form-card {
  background: var(--cor-cartao-bg);
  border-radius: var(--borda-raio);
  overflow: hidden;
  border: none;
}
.form-header {
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
.custom-input :deep(.q-field__control) {
  border-radius: var(--borda-raio-input);
  background-color: #f8fafc;
}
.separator-custom {
  background-color: var(--borda-cor);
}
.price-badge {
  font-size: 14px;
  font-weight: bold;
  padding: 6px 10px;
  border-radius: 8px;
}
.time-slots-container {
  background-color: #f8fafc;
  border: 1px solid var(--borda-cor);
}
.time-btn {
  border-radius: 10px;
  transition: all 0.2s ease;
}
.time-btn:not(.q-btn--outline) {
  box-shadow: 0 4px 6px -1px rgba(13, 13, 15, 0.2), 0 2px 4px -1px rgba(7, 7, 8, 0.1);
}
.time-btn:hover {
  transform: translateY(-2px);
}
.empty-time-state {
  background-color: #f1f5f9;
  border: 1px dashed #cbd5e1;
}
.store-closed-banner {
  background-color: #fef2f2;
  border: 2px dashed #fecaca;
  border-radius: var(--borda-raio-input);
}
.submit-btn {
  border-radius: var(--borda-raio-input);
  font-weight: 700;
  letter-spacing: 0.5px;
  transition: transform 0.2s;
}
.submit-btn:not(:disabled):hover {
  transform: translateY(-2px);
}
</style>