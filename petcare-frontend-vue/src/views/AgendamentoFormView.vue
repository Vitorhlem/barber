<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-page padding class="flex flex-center bg-grey-1">
        
        <div style="width: 100%; max-width: 540px;">
          <q-btn flat color="grey-8" icon="arrow_back" label="Voltar" class="q-mb-md" @click="router.back()" no-caps />

          <q-card flat bordered class="rounded-borders shadow-2">
            <q-card-section class="bg-white q-pa-lg">
              <div class="text-h5 text-weight-bold text-grey-9">Marcar Horário</div>
              <div class="text-subtitle2 text-grey-6">Selecione o profissional e o horário disponível.</div>
            </q-card-section>

            <q-separator />

            <q-card-section class="q-pa-lg">
              <q-form @submit.prevent="submeterAgendamento" class="q-gutter-y-lg">
                
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-sm-6">
                    <q-select
                      v-model="form.barbeiro_id"
                      :options="listaBarbeiros"
                      option-value="id"
                      option-label="nome"
                      emit-value
                      map-options
                      label="Profissional"
                      outlined
                      color="primary"
                      hide-bottom-space
                      :loading="carregandoBarbeiros"
                      :rules="[val => !!val || 'Obrigatório']"
                    >
                      <template v-slot:prepend><q-icon name="badge" /></template>
                    </q-select>
                  </div>
                  
                  <div class="col-12 col-sm-6">
                    <q-select
                      v-model="form.servico"
                      :options="Object.keys(tabelaPrecos)"
                      label="Serviço"
                      outlined
                      color="primary"
                      hide-bottom-space
                      :rules="[val => !!val || 'Obrigatório']"
                    >
                      <template v-slot:prepend><q-icon name="content_cut" /></template>
                      <template v-slot:append v-if="form.servico">
                        <q-badge color="positive">{{ formatarPreco(tabelaPrecos[form.servico]) }}</q-badge>
                      </template>
                    </q-select>
                  </div>
                </div>

                <div>
                  <q-input
                    v-model="dataSelecionada"
                    type="date"
                    label="Data do Atendimento"
                    outlined
                    color="primary"
                    hide-bottom-space
                    :min="dataMinima"
                    :rules="[val => !!val || 'A data é obrigatória']"
                  />
                </div>

                <div v-if="dataSelecionada && form.barbeiro_id" class="q-pa-md bg-blue-grey-1 rounded-borders" style="border: 1px solid #eceff1;">
                  <div class="text-subtitle2 text-grey-9 text-weight-bold q-mb-md">
                    <q-icon name="schedule" class="q-mr-xs" size="20px"/> Horários Disponíveis
                  </div>
                  
                  <div class="row q-gutter-sm">
                    <q-btn
                      v-for="hora in horariosDisponiveis"
                      :key="hora"
                      :label="hora"
                      :color="horaSelecionada === hora ? 'primary' : 'white'"
                      :text-color="horaSelecionada === hora ? 'white' : 'grey-9'"
                      :outline="horaSelecionada !== hora"
                      class="col-auto text-weight-bold shadow-1"
                      style="min-width: 75px;"
                      @click="horaSelecionada = hora"
                    />
                    
                    <div v-if="horariosDisponiveis.length === 0" class="text-negative text-body2 q-pa-sm flex items-center">
                      <q-icon name="event_busy" size="24px" class="q-mr-sm"/> Sem horários livres neste dia (ou encerrado).
                    </div>
                  </div>
                </div>

                <div class="q-mt-md">
                  <q-btn 
                    type="submit" 
                    color="primary" 
                    class="full-width" 
                    size="large" 
                    label="Confirmar Agendamento" 
                    :loading="submetendo" 
                    :disabled="!formularioValido"
                    unelevated 
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
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useQuasar } from 'quasar'

const router = useRouter()
const authStore = useAuthStore()
const $q = useQuasar()

const submetendo = ref(false)
const carregandoBarbeiros = ref(true)
const listaBarbeiros = ref<any[]>([])

const tabelaPrecos: Record<string, number> = {
  'Corte de Cabelo': 15.00,
  'Barba': 10.00,
  'Corte + Barba': 23.00
}

const form = ref({
  barbeiro_id: null,
  servico: ''
})

const dataSelecionada = ref('')
const horaSelecionada = ref('')
const horariosOcupados = ref<string[]>([])

const dataMinima = new Date().toISOString().split('T')[0]

const gerarTodosHorarios = () => {
  const slots = []
  for (let h = 8; h <= 18; h++) {
    const horaStr = h.toString().padStart(2, '0')
    slots.push(`${horaStr}:00`)
    slots.push(`${horaStr}:30`)
  }
  return slots
}
const todosHorariosBase = gerarTodosHorarios()

// Filtro de disponibilidade à prova de timezone
const horariosDisponiveis = computed(() => {
  if (!dataSelecionada.value) return []
  
  const dataObj = new Date(dataSelecionada.value + 'T00:00:00')
  if (dataObj.getDay() === 0) return [] 
  
  const agora = new Date()
  const ano = agora.getFullYear()
  const mes = String(agora.getMonth() + 1).padStart(2, '0')
  const dia = String(agora.getDate()).padStart(2, '0')
  const hojeLocal = `${ano}-${mes}-${dia}`
  
  return todosHorariosBase.filter(hora => {
    // 1. Oculta horários reservados com base na string exata do banco
    if (horariosOcupados.value.includes(hora)) return false
    
    // 2. Oculta horas que já passaram se for o dia de hoje
    if (dataSelecionada.value === hojeLocal) {
      const [h, m] = hora.split(':').map(Number)
      if (h < agora.getHours() || (h === agora.getHours() && m <= agora.getMinutes())) {
        return false
      }
    }
    return true
  })
})

const formularioValido = computed(() => {
  return dataSelecionada.value && horaSelecionada.value && form.value.servico && form.value.barbeiro_id
})

const formatarPreco = (valor: number) => new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(valor)

onMounted(async () => {
  try {
    const response = await fetch('http://localhost:8000/barbeiros/')
    if (response.ok) listaBarbeiros.value = await response.json()
  } finally {
    carregandoBarbeiros.value = false
  }
})

// Busca a agenda do profissional e separa as datas e horas usando extração de strings (sem new Date)
watch([() => form.value.barbeiro_id, dataSelecionada], async ([novoProfissionalId, novaData]) => {
  horaSelecionada.value = '' 
  const idReal = typeof novoProfissionalId === 'object' ? (novoProfissionalId as any)?.id : novoProfissionalId
  
  if (!idReal || !novaData) {
    horariosOcupados.value = []
    return
  }
  
  try {
    const res = await fetch(`http://localhost:8000/agendamentos/barbeiro/${idReal}`)
    if (res.ok) {
      const agendamentos = await res.json()
      const ocupados: string[] = []
      
      agendamentos.forEach((a: any) => {
        if (a.status?.toLowerCase() !== 'cancelado') {
          // Ex: "2026-05-26T11:00:00" ou "2026-05-26 11:00:00"
          const dataNormalizada = a.data_hora.replace('Z', '').replace(' ', 'T')
          const partes = dataNormalizada.split('T')
          
          if (partes.length === 2) {
            const dataAgendamento = partes[0]
            const horaAgendamento = partes[1].substring(0, 5) // HH:MM
            
            if (dataAgendamento === novaData) {
              ocupados.push(horaAgendamento)
            }
          }
        }
      })
      horariosOcupados.value = ocupados
    }
  } catch (err) {
    console.error("Erro ao verificar disponibilidade:", err)
  }
})

const submeterAgendamento = async () => {
  if (!authStore.userId) return
  submetendo.value = true
  
  try {
    const idProfissional = typeof form.value.barbeiro_id === 'object' 
      ? (form.value.barbeiro_id as any)?.id 
      : Number(form.value.barbeiro_id);

    const dados = {
      barbeiro_id: idProfissional,
      servico: form.value.servico,
      preco: Number(tabelaPrecos[form.value.servico]) || 0,
      // Envia estritamente o texto escolhido, ignorando timezones do navegador
      data_hora: `${dataSelecionada.value}T${horaSelecionada.value}:00`
    }
    
    const response = await fetch(`http://localhost:8000/usuarios/${authStore.userId}/agendamentos/`, {
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
    router.push('/dashboard')
    
  } catch (error: any) {
    $q.notify({ type: 'negative', message: `Erro ao agendar: ${error.message}`, position: 'top', timeout: 5000 })
  } finally {
    submetendo.value = false
  }
}
</script>