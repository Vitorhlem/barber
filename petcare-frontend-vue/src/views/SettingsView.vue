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
              @click="router.push(`/${slug}/dashboard`)" 
              no-caps 
            />
            <q-breadcrumbs class="text-grey-6 text-weight-medium" active-color="primary">
              <q-breadcrumbs-el icon="home" class="cursor-pointer" @click="router.push(`/${slug}/dashboard`)" />
              <q-breadcrumbs-el label="Configurações" />
            </q-breadcrumbs>
          </div>

          <!-- Personalização do Sistema -->
          <q-card v-if="authStore.userType === 'admin' || authStore.userType === 'barbeiro'" class="settings-card shadow-12 border-warning q-mb-lg">
            <q-card-section class="q-pa-xl">
              <div class="text-h5 text-weight-bolder text-primary q-mb-md">Personalização do Sistema</div>
              <div class="row q-col-gutter-md">
                <div class="col-12">
                  <q-input v-model="configSistema.nome_barbearia" label="Nome da Barbearia" outlined color="primary" class="custom-input" />
                </div>
                <div class="col-12 col-sm-6">
                  <q-file v-model="logoUpload" label="Carregar Logo do Computador" outlined color="primary" class="custom-input" accept="image/*" clearable>
                    <template v-slot:prepend><q-icon name="attach_file" color="grey-6" /></template>
                  </q-file>
                </div>
                <div class="col-12 col-sm-6">
                  <q-input v-model="configSistema.logo_url" label="Ou URL da Logo" placeholder="https://..." outlined color="primary" class="custom-input" />
                </div>
              </div>
            </q-card-section>
            <q-card-actions align="right" class="q-pa-md bg-grey-1">
              <q-btn color="primary" label="Salvar Marca" class="action-btn shadow-2" @click="salvarMarca" unelevated no-caps />
            </q-card-actions>
          </q-card>

          <!-- Integrações -->
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

          <!-- Bloqueio de Dias Inteiros -->
          <q-card v-if="authStore.userType === 'barbeiro' || authStore.userType === 'admin'" class="settings-card shadow-12 q-mb-lg">
            <q-card-section class="q-pa-xl">
              <div class="row items-center q-mb-md">
                <div class="icon-wrapper shadow-4 q-mr-lg bg-negative text-white">
                  <q-icon name="event_busy" size="32px" />
                </div>
                <div>
                  <div class="text-h5 text-weight-bolder text-negative letter-spacing">Bloqueio de Dias Inteiros</div>
                  <div class="text-subtitle2 text-grey-6 q-mt-xs text-weight-medium">
                    Selecione datas específicas para fechar a sua agenda inteira (Feriados, Folgas pontuais, etc).
                  </div>
                </div>
              </div>

              <div class="row q-col-gutter-md items-center q-mb-xl bg-grey-1 q-pa-md rounded-borders">
                <div class="col-12 col-sm-5">
                  <q-input v-model="novaFolga.data" type="date" outlined dense color="primary" class="custom-input-dense" label="Data de Encerramento" />
                </div>
                <div class="col-12 col-sm-5">
                  <q-input v-model="novaFolga.motivo" outlined dense color="primary" class="custom-input-dense" label="Motivo (Ex: Natal, Férias)" />
                </div>
                <div class="col-12 col-sm-2 text-right">
                  <q-btn color="negative" icon="add" label="Bloquear" no-caps unelevated class="action-btn full-width" @click="adicionarFolga" />
                </div>
              </div>

              <div class="text-subtitle1 text-weight-bolder text-grey-8 q-mb-sm">Dias Bloqueados Ativos</div>
              <div v-if="listaFolgas.length === 0" class="text-body2 text-grey-5 q-pa-md text-center bg-grey-1 rounded-borders">
                Nenhuma folga ou feriado configurado para os próximos dias.
              </div>
              <div v-else class="schedule-container">
                <div v-for="folga in listaFolgas" :key="folga.id" class="schedule-row row items-center q-pa-md q-mb-sm rounded-borders justify-between">
                  <div class="row items-center">
                    <q-icon name="event_note" color="negative" size="20px" class="q-mr-md" />
                    <div>
                      <span class="text-weight-bold text-grey-9 q-mr-md">{{ formatarDataSimples(folga.data) }}</span>
                      <q-badge color="grey-7" class="text-weight-medium">{{ folga.motivo || 'Folga' }}</q-badge>
                    </div>
                  </div>
                  <q-btn flat round color="negative" icon="delete" size="sm" @click="removerFolga(folga.id)" />
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Expediente -->
          <q-card v-if="authStore.userType === 'barbeiro' || authStore.userType === 'admin'" class="settings-card shadow-12 q-mb-lg">
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
                      v-model="item.inicio" type="time" label="Abertura" outlined dense class="custom-input-dense" 
                      :disable="!item.trabalha" color="primary"
                    />
                  </div>
                  <div class="col-6 col-sm-4 q-pl-sm q-mt-sm q-mt-sm-none">
                    <q-input 
                      v-model="item.fim" type="time" label="Encerramento" outlined dense class="custom-input-dense" 
                      :disable="!item.trabalha" color="primary"
                    />
                  </div>
                </div>
              </div>
            </q-card-section>

            <q-card-actions align="right" class="q-pa-lg bg-grey-1" style="border-top: 1px solid #e2e8f0;">
              <q-btn 
                color="primary" label="Salvar Configurações" icon="save" class="action-btn shadow-4 q-px-lg" 
                size="lg" :loading="salvando" @click="salvarConfiguracao" unelevated no-caps
              />
            </q-card-actions>
          </q-card>

          <!-- Gestão de Equipe (Apenas Admin) -->
          <q-card v-if="authStore.userType === 'admin'" class="settings-card shadow-12 q-mb-lg">
            <q-card-section class="q-pa-xl">
              <div class="row items-center q-mb-md">
                <div class="icon-wrapper shadow-4 q-mr-lg bg-info text-white">
                  <q-icon name="content_cut" size="32px" />
                </div>
                <div>
                  <div class="text-h5 text-weight-bolder text-info letter-spacing">Gestão de Equipe</div>
                  <div class="text-subtitle2 text-grey-6 q-mt-xs text-weight-medium">
                    Adicione os barbeiros que terão acesso ao sistema e agenda nesta unidade.
                  </div>
                </div>
              </div>

              <div class="row q-col-gutter-md items-center q-mb-xl bg-grey-1 q-pa-md rounded-borders">
                <div class="col-12 col-sm-3">
                  <q-input v-model="novoBarbeiro.nome" outlined dense color="info" class="custom-input-dense" label="Nome do Barbeiro" />
                </div>
                <div class="col-12 col-sm-3">
                  <q-input v-model="novoBarbeiro.email" outlined dense color="info" class="custom-input-dense" label="E-mail (Login)" />
                </div>
                <div class="col-12 col-sm-2">
                  <q-input v-model="novoBarbeiro.senha" outlined dense color="info" class="custom-input-dense" label="Senha" />
                </div>
                <div class="col-12 col-sm-2">
                  <q-input v-model="novoBarbeiro.telefone" outlined dense color="info" class="custom-input-dense" label="Telefone" />
                </div>
                <div class="col-12 col-sm-2 text-right">
                  <q-btn color="info" icon="person_add" label="Adicionar" no-caps unelevated class="action-btn full-width" @click="adicionarBarbeiro" :loading="loadingBarbeiro" />
                </div>
              </div>

              <div class="text-subtitle1 text-weight-bolder text-grey-8 q-mb-sm">Equipe Atual</div>
              <div v-if="listaBarbeiros.length === 0" class="text-body2 text-grey-5 q-pa-md text-center bg-grey-1 rounded-borders">
                Nenhum barbeiro cadastrado nesta loja.
              </div>
              <div v-else class="schedule-container">
                <div v-for="barb in listaBarbeiros" :key="barb.id" class="schedule-row row items-center q-pa-md q-mb-sm rounded-borders justify-between">
                  <div class="row items-center">
                    <q-avatar color="info" text-color="white" icon="person" size="md" class="q-mr-md" />
                    <div>
                      <div class="text-weight-bold text-grey-9">{{ barb.nome }}</div>
                      <div class="text-caption text-grey-6">{{ barb.email }} • {{ barb.telefone || 'Sem telefone' }}</div>
                    </div>
                  </div>
                  <q-btn flat round color="negative" icon="delete" size="sm" @click="removerBarbeiro(barb.id)" title="Remover Barbeiro" />
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Alterar Senha de Acesso -->
          <q-card class="settings-card shadow-12 q-mb-lg">
            <q-card-section class="q-pa-xl">
              <div class="text-h5 text-weight-bolder text-primary q-mb-md">Alterar Senha de Acesso</div>
              <div class="text-subtitle2 text-grey-6 q-mb-lg text-weight-medium">Mantenha os seus dados seguros atualizando a sua senha periodicamente.</div>
              
              <div class="row q-col-gutter-md">
                <div class="col-12">
                  <q-input v-model="formSenha.senha_atual" type="password" label="Senha Atual" outlined color="primary" class="custom-input" />
                </div>
                <div class="col-12 col-sm-6">
                  <q-input v-model="formSenha.nova_senha" type="password" label="Nova Senha" outlined color="primary" class="custom-input" />
                </div>
                <div class="col-12 col-sm-6">
                  <q-input v-model="formSenha.confirmar_senha" type="password" label="Confirmar Nova Senha" outlined color="primary" class="custom-input" />
                </div>
              </div>
            </q-card-section>
            <q-card-actions align="right" class="q-pa-md bg-grey-1">
              <q-btn color="primary" label="Atualizar Senha" class="action-btn shadow-2" @click="handleAlterarSenha" :loading="loadingSenha" unelevated no-caps />
            </q-card-actions>
          </q-card>

          <!-- Endereço Exclusivo da Loja -->
          <q-card v-if="authStore.userType === 'admin'" class="settings-card shadow-12 border-warning q-mb-lg">
            <q-card-section class="bg-amber-1 text-black q-pa-xl" style="border-bottom: 1px solid #fcd34d;">
              <div class="text-h5 text-weight-bolder text-amber-9 letter-spacing">Endereço Exclusivo da Loja</div>
              <div class="text-subtitle2 text-amber-8 q-mt-xs text-weight-medium">Configure o link que identifica a sua barbearia no sistema.</div>
              
              <q-banner inline-actions class="bg-warning text-black q-mt-lg rounded-borders shadow-2">
                <template v-slot:avatar>
                  <q-icon name="warning" color="dark" size="md" />
                </template>
                <span class="text-weight-bold">Atenção ao alterar o link da sua loja!</span><br>
                Se alterar este endereço, o link atual deixará de funcionar imediatamente. Os seus clientes perderão o acesso através dos links antigos ou QR Codes impressos.
              </q-banner>
            </q-card-section>

            <q-card-section class="q-pa-xl">
              <div class="text-subtitle2 text-weight-bold text-grey-8 q-mb-sm">Link de acesso atual:</div>
              <code class="bg-grey-3 q-pa-sm rounded-borders text-secondary block q-mb-lg text-body1 text-weight-medium">
                localhost:5173/{{ authStore.barbeariaSlug }}/login
              </code>

              <q-input 
                v-model="novoSlug" 
                label="Novo Link Desejado (Ex: barbearia-do-bairro)" 
                outlined 
                color="amber-9"
                class="custom-input"
                hint="Evite espaços ou caracteres especiais. Eles serão convertidos em hifens."
              />
            </q-card-section>

            <q-card-actions align="right" class="q-pa-md bg-amber-1">
              <q-btn color="negative" label="Alterar Link da Loja" class="action-btn shadow-2" @click="confirmarAlteracaoSlug" :loading="loadingSlug" unelevated no-caps />
            </q-card-actions>
          </q-card>

        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useQuasar } from 'quasar'
import { useSistemaStore } from '@/stores/sistemaStore'

const sistemaStore = useSistemaStore()
const configSistema = ref({ nome_barbearia: '', logo_url: '' })

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const $q = useQuasar()

const slug = route.params.slug as string 

// Estados Base
const logoUpload = ref<File | null>(null)
const salvando = ref(false)
const listaFolgas = ref<any[]>([])
const novaFolga = ref({ data: '', motivo: '' })

// Estados de Segurança
const loadingSenha = ref(false)
const formSenha = ref({ senha_atual: '', nova_senha: '', confirmar_senha: '' })

// Estados do Slug
const loadingSlug = ref(false)
const novoSlug = ref(authStore.barbeariaSlug)

// --- ESTADOS DE GESTÃO DE EQUIPE ---
const listaBarbeiros = ref<any[]>([])
const loadingBarbeiro = ref(false)
const novoBarbeiro = ref({ nome: '', email: '', senha: '', telefone: '' })

const fetchBarbeiros = async () => {
  if (authStore.userType !== 'admin') return
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/barbeiros/`)
    if (res.ok) listaBarbeiros.value = await res.json()
  } catch (e) { console.error(e) }
}

const adicionarBarbeiro = async () => {
  if (!novoBarbeiro.value.nome || !novoBarbeiro.value.email || !novoBarbeiro.value.senha) {
    $q.notify({ color: 'warning', message: 'Preencha o Nome, E-mail e Senha do barbeiro.', position: 'top' })
    return
  }
  loadingBarbeiro.value = true
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/barbeiros/?usuario_logado_id=${authStore.userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nome: novoBarbeiro.value.nome,
        email: novoBarbeiro.value.email,
        senha: novoBarbeiro.value.senha,
        telefone: novoBarbeiro.value.telefone,
        tipo: 'barbeiro'
      })
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(errorData.detail || 'Erro ao criar barbeiro.')
    }
    $q.notify({ color: 'positive', message: 'Barbeiro adicionado à equipe!', position: 'top' })
    novoBarbeiro.value = { nome: '', email: '', senha: '', telefone: '' }
    fetchBarbeiros() 
  } catch (err: any) {
    $q.notify({ color: 'negative', message: err.message, position: 'top' })
  } finally {
    loadingBarbeiro.value = false
  }
}

const removerBarbeiro = async (id: number) => {
  $q.dialog({
    title: 'Remover Barbeiro',
    message: 'Tem certeza? Ele não poderá mais acessar o sistema desta barbearia.',
    cancel: true,
    persistent: true,
    ok: { label: 'Sim, remover', color: 'negative', unelevated: true }
  }).onOk(async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/barbeiros/${id}?usuario_logado_id=${authStore.userId}`, {
        method: 'DELETE'
      })
      if (res.ok) {
        $q.notify({ color: 'positive', message: 'Barbeiro removido com sucesso.', position: 'top' })
        fetchBarbeiros()
      }
    } catch (e) { console.error(e) }
  })
}

// --- MÉTODOS ORIGINAIS ---
const formatarDataSimples = (dataStr: string) => {
  const parts = dataStr.split('-')
  return `${parts[2]}/${parts[1]}/${parts[0]}`
}

const fetchFolgas = async () => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/folgas/barbeiro/${authStore.userId}`)
    if (res.ok) {
      listaFolgas.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  }
}

const adicionarFolga = async () => {
  if (!novaFolga.value.data) return
  try {
    const payload = {
      barbeiro_id: authStore.userId,
      data: novaFolga.value.data,
      motivo: novaFolga.value.motivo
    }
    const res = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/folgas/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      fetchFolgas()
      novaFolga.value = { data: '', motivo: '' }
      $q.notify({ type: 'positive', message: 'Dia bloqueado com sucesso!' })
    }
  } catch (e) { console.error(e) }
}

const removerFolga = async (id: number) => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/folgas/${id}`, { method: 'DELETE' })
    if (res.ok) {
      fetchFolgas()
      $q.notify({ type: 'positive', message: 'Bloqueio de dia removido!' })
    }
  } catch (e) { console.error(e) }
}

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
  const response = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/auth/google/login?user_id=${authStore.userId}`)
  const data = await response.json()
  if (data.url) {
    window.location.href = data.url
  }
}

const fetchConfiguracao = async () => {
  if (authStore.userType === 'cliente') return
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/configuracao/${authStore.userId}`)
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

const salvarMarca = async () => {
  try {
    if (logoUpload.value) {
      const formData = new FormData()
      formData.append('file', logoUpload.value)
      
      const uploadRes = await fetch(`${import.meta.env.VITE_API_URL}/upload/imagem`, {
        method: 'POST',
        body: formData
      })
      
      if (uploadRes.ok) {
        const uploadData = await uploadRes.json()
        configSistema.value.logo_url = uploadData.url 
      }
    }

    await fetch(`${import.meta.env.VITE_API_URL}/${slug}/sistema/config`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(configSistema.value)
    })
    
    await sistemaStore.fetchConfig(slug)
    logoUpload.value = null
    
    $q.notify({ type: 'positive', message: 'Marca atualizada com sucesso!', position: 'top' })
  } catch (e) {
    console.error(e)
    $q.notify({ type: 'negative', message: 'Erro ao salvar modificações da marca.', position: 'top' })
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
    
    const response = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/configuracao/${authStore.userId}`, {
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

// --- NOVOS MÉTODOS: SEGURANÇA E IDENTIDADE ---
async function handleAlterarSenha() {
  if (!formSenha.value.senha_atual || !formSenha.value.nova_senha) {
    $q.notify({ color: 'negative', message: 'Preencha todos os campos de senha.', position: 'top' })
    return
  }

  if (formSenha.value.nova_senha !== formSenha.value.confirmar_senha) {
    $q.notify({ color: 'negative', message: 'A nova senha e a confirmação não coincidem.', position: 'top' })
    return
  }

  loadingSenha.value = true
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/usuarios/${authStore.userId}/alterar-senha`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        senha_atual: formSenha.value.senha_atual,
        nova_senha: formSenha.value.nova_senha
      })
    })

    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'Erro ao alterar senha.')

    $q.notify({ color: 'positive', message: 'Senha atualizada com sucesso!', position: 'top' })
    formSenha.value = { senha_atual: '', nova_senha: '', confirmar_senha: '' }
  } catch (err: any) {
    $q.notify({ color: 'negative', message: err.message, position: 'top' })
  } finally {
    loadingSenha.value = false
  }
}

function confirmarAlteracaoSlug() {
  if (!novoSlug.value || novoSlug.value === authStore.barbeariaSlug) {
    $q.notify({ color: 'warning', message: 'Informe um link novo diferente do atual.', position: 'top' })
    return
  }

  $q.dialog({
    title: 'Confirmar Alteração de Link?',
    message: 'Tem a certeza absoluta? Todos os links antigos enviados a clientes pararão de funcionar imediatamente.',
    cancel: true,
    persistent: true,
    ok: { label: 'Sim, desejo alterar', color: 'negative', unelevated: true }
  }).onOk(() => {
    handleAlterarSlug()
  })
}

async function handleAlterarSlug() {
  loadingSlug.value = true
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/${slug}/sistema/alterar-slug?usuario_logado_id=${authStore.userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ novo_slug: novoSlug.value })
    })

    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'Erro ao alterar endereço da loja.')

    $q.notify({ color: 'positive', message: 'Endereço da barbearia alterado com sucesso!', position: 'top' })
    
    if(authStore.atualizarSlugLocal) {
      authStore.atualizarSlugLocal(data.novo_slug)
    }
    
    router.push(`/${data.novo_slug}/settings`)
  } catch (err: any) {
    $q.notify({ color: 'negative', message: err.message, position: 'top' })
  } finally {
    loadingSlug.value = false
  }
}

onMounted(() => {
  sistemaStore.fetchConfig(slug).then(() => {
    configSistema.value.nome_barbearia = sistemaStore.nomeBarbearia
    configSistema.value.logo_url = sistemaStore.logoUrl
  })
  fetchConfiguracao()
  fetchFolgas()
  fetchBarbeiros() 
})
</script>

<style scoped>
.settings-layout {
  --cor-fundo-pagina: #f1f5f9;
  --cor-cartao-bg: #ffffff;
  --cor-header-inicio: var(--q-primary);
  --cor-header-fim: #1e3a8a;
  --cor-texto-primario: #0f172a;
  --cor-texto-secundario: #64748b;
  --borda-raio: 20px;
  --borda-raio-input: 12px;
  --borda-cor: #e2e8f0;
}
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
.settings-card {
  background: var(--cor-cartao-bg);
  border-radius: var(--borda-raio);
  overflow: hidden;
  border: none;
}
.border-warning {
  border: 1px solid #f2c037;
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
.card-header {
  background: linear-gradient(135deg, var(--cor-header-inicio) 0%, var(--cor-header-fim) 100%);
}
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
.custom-input :deep(.q-field__control) {
  border-radius: var(--borda-raio-input);
  background-color: #f8fafc;
}
.custom-input-dense :deep(.q-field__control) {
  border-radius: 8px;
  background-color: #ffffff;
}
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