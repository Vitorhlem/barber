<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePetStore } from '@/stores/petStore'
import { useAuthStore } from '@/stores/authStore'
import placeholderImg from '@/assets/placeholder.svg'

const route = useRoute()
const router = useRouter()
const petStore = usePetStore()
const authStore = useAuthStore()

// Pega o ID da URL (ex: /pet/1)
const petId = Number(route.params.id)

// Computed Property: Acha o pet atual e atualiza automaticamente se os dados mudarem
const pet = computed(() => petStore.pets.find(p => p.id === petId))

// Controle das Abas (Substitui as classes .active do antigo CSS)
const activeTab = ref<'vaccines' | 'parasites' | 'consults' | 'weights' | 'documents'>('vaccines')

onMounted(async () => {
  // Se o usuário atualizou a página com F5 e os pets sumiram da memória, busca de novo
  if (petStore.pets.length === 0) {
    await petStore.fetchPets()
  }
  // Se o pet não existir ou a pessoa digitou URL errada, volta pra home
  if (!pet.value) {
    router.push('/')
  }
})

function goBack() {
  router.push('/')
}

function getPetAge(birthdate: string | null) {
  if (!birthdate) return 'Idade não informada'
  const birthDate = new Date(birthdate)
  const today = new Date()
  let years = today.getFullYear() - birthDate.getFullYear()
  let months = today.getMonth() - birthDate.getMonth()
  if (months < 0 || (months === 0 && today.getDate() < birthDate.getDate())) {
    years--
    months += 12
  }
  return `${years} ano(s) e ${months} mes(es)`
}

function formatDate(dateString: string) {
  return new Date(dateString + 'T00:00:00').toLocaleDateString('pt-BR')
}

// ==========================================
// LÓGICA DO MODAL DE REGISTROS (Vacina, Peso, etc)
// ==========================================
const showRecordModal = ref(false)
const isEditing = ref(false)
const recordForm = ref({ id: null as number | null, name: '', date: '', nextDate: '', vet: '', weight: '', notes: '' })

function openRecordModal(record: any = null) {
  if (record) {
    isEditing.value = true
    recordForm.value = {
      id: record.id,
      name: record.name || '',
      date: record.date || '',
      nextDate: record.nextDate || '',
      vet: record.vet || '',
      weight: record.weight?.toString() || '',
      notes: record.notes || ''
    }
  } else {
    isEditing.value = false
    recordForm.value = { 
    id: null, 
    name: '', 
    date: new Date().toISOString().split('T')[0] || '', 
    nextDate: '', 
    vet: '', 
    weight: '', 
    notes: '' 
}
  }
  showRecordModal.value = true
}

async function saveRecord() {
  const typeMap: Record<string, string> = {
    vaccines: 'vacina',
    parasites: 'parasita',
    consults: 'consulta',
    weights: 'peso'
  }

  let anotacoesFinais = null
  if (['vaccines', 'parasites'].includes(activeTab.value)) {
    anotacoesFinais = recordForm.value.vet || null
  } else if (activeTab.value === 'consults') {
    anotacoesFinais = [recordForm.value.vet, recordForm.value.notes].filter(Boolean).join(' | ') || null
  }

  const payload = {
    tipo: typeMap[activeTab.value],
    nome: recordForm.value.name || (activeTab.value === 'weights' ? 'Registro de Peso' : ''),
    data: recordForm.value.date,
    proxima_data: recordForm.value.nextDate || null,
    peso: recordForm.value.weight ? parseFloat(recordForm.value.weight) : null,
    anotacoes: anotacoesFinais
  }

  try {
    let url = `${petStore.apiUrl}/pets/${petId}/registros/`
    let method = 'POST'
    
    if (isEditing.value && recordForm.value.id) {
      url = `${petStore.apiUrl}/registros/${recordForm.value.id}`
      method = 'PUT'
    }

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (response.ok) {
      await petStore.fetchPets() 
      showRecordModal.value = false
    } else {
      alert("Erro ao salvar registro da API.")
    }
  } catch (e) {
    alert("Erro de conexão com o servidor.")
  }
}

async function deleteRecord(recordId: number) {
  if(!confirm("Tem certeza que deseja excluir este registro?")) return
  try {
    const response = await fetch(`${petStore.apiUrl}/registros/${recordId}`, { method: 'DELETE' })
    if (response.ok) await petStore.fetchPets()
  } catch (e) {
    console.error(e)
  }
}

// ==========================================
// LÓGICA DO MODAL DE DOCUMENTOS MÉDICOS
// ==========================================
const showDocModal = ref(false)
const docForm = ref({ type: 'Receituário', date: new Date().toISOString().split('T')[0], vetName: '', content: '' })

function openDocModal() {
  docForm.value = { type: 'Receituário', date: new Date().toISOString().split('T')[0], vetName: '', content: '' }
  showDocModal.value = true
}

async function saveDoc() {
  const payload = {
    tipo: 'documento',
    nome: `${docForm.value.type} - ${docForm.value.vetName}`,
    data: docForm.value.date,
    proxima_data: null,
    peso: null,
    anotacoes: docForm.value.content
  }
  try {
    const response = await fetch(`${petStore.apiUrl}/pets/${petId}/registros/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (response.ok) {
      await petStore.fetchPets()
      showDocModal.value = false
    }
  } catch (e) {
    console.error(e)
  }
}

async function deletePet() {
  if(!confirm("Tem certeza que deseja excluir este pet e todos os seus registros?")) return
  try {
    const response = await fetch(`${petStore.apiUrl}/pets/${petId}`, { method: 'DELETE' })
    if (response.ok) {
      await petStore.fetchPets()
      router.push('/')
    }
  } catch(e) {
    console.error(e)
  }
}
</script>

<template>
  <div v-if="pet" class="page active">
    <header class="header">
      <button @click="goBack" class="back-btn">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
      </button>
      <h1>Detalhes</h1>
      <div style="width: 24px;"></div>
    </header>

    <main class="details-main-container">
      <div id="details-content">
        <img :src="pet.photo || placeholderImg" id="details-photo" />
        <div id="details-info">
          <h2>{{ pet.name }}</h2>
          <p><strong>Espécie:</strong> {{ pet.species }} | <strong>Raça:</strong> {{ pet.breed || 'Não informada' }}</p>
          <p><strong>Microchip:</strong> {{ pet.microchip || 'Não informado' }}</p>
          <p class="pet-age">{{ getPetAge(pet.birthdate) }}</p>
        </div>
        
        <div class="details-actions" v-if="authStore.userType === 'tutor'">
          <button class="btn btn-danger" @click="deletePet">Excluir Pet</button>
        </div>
      </div>

      <div class="tabs-container">
        <div class="tabs-nav">
          <button class="tab-link" :class="{ active: activeTab === 'vaccines' }" @click="activeTab = 'vaccines'">Vacinas</button>
          <button class="tab-link" :class="{ active: activeTab === 'parasites' }" @click="activeTab = 'parasites'">Parasitas</button>
          <button class="tab-link" :class="{ active: activeTab === 'consults' }" @click="activeTab = 'consults'">Consultas</button>
          <button class="tab-link" :class="{ active: activeTab === 'weights' }" @click="activeTab = 'weights'">Peso</button>
          <button class="tab-link" :class="{ active: activeTab === 'documents' }" @click="activeTab = 'documents'">Doc. Médicos</button>
        </div>

        <div class="tab-content active">
          <div v-if="!pet[activeTab] || pet[activeTab].length === 0" class="empty-state">
            <p>Nenhum registro encontrado.</p>
          </div>

          <div v-for="record in pet[activeTab]" :key="record.id" class="record-card" :style="activeTab === 'documents' ? 'align-items: flex-start' : ''">
            
            <div style="flex-grow:1; width:100%;">
              <div v-if="activeTab === 'documents'">
                <h4 style="color: var(--primary-dark); font-size: 1.15rem; margin-bottom: 8px;">📄 {{ record.name }}</h4>
                <p style="font-size: 0.9rem; margin-bottom: 12px; color: var(--text-light)"><strong>Emitido em:</strong> {{ formatDate(record.date) }}</p>
                <div style="background: var(--bg-color); padding: 16px; border-radius: 8px; border-left: 4px solid var(--primary-color); white-space: pre-wrap; font-family: monospace;">{{ record.notes }}</div>
              </div>
              
              <div v-else-if="activeTab === 'weights'">
                <h4>{{ record.weight }} kg</h4>
                <p><strong>Data:</strong> {{ formatDate(record.date) }}</p>
              </div>
              
              <div v-else>
                <h4>{{ record.name }}</h4>
                <p><strong>Data:</strong> {{ formatDate(record.date) }}</p>
                <p v-if="record.vet"><strong>Local/Vet:</strong> {{ record.vet }}</p>
                <p v-if="activeTab === 'consults' && record.notes"><strong>Anotações:</strong> {{ record.notes }}</p>
                <p v-if="record.nextDate" class="next-due">Próxima dose: {{ formatDate(record.nextDate) }}</p>
              </div>
            </div>

            <div class="record-actions" v-if="!(activeTab === 'documents' && authStore.userType === 'tutor')">
              <button v-if="activeTab !== 'documents'" @click="openRecordModal(record)">✏️</button>
              <button @click="deleteRecord(record.id)">🗑️</button>
            </div>
          </div>

          <button v-if="activeTab !== 'documents'" class="btn btn-primary btn-block mt-4" @click="openRecordModal()">
            + Novo Registro
          </button>
          
          <button v-if="activeTab === 'documents' && authStore.userType === 'veterinario'" class="btn btn-primary btn-block mt-4" style="background: var(--primary-dark);" @click="openDocModal">
            👩‍⚕️ Emitir Prescrição / Atestado
          </button>
        </div>
      </div>
    </main>

    <div v-if="showRecordModal" class="modal-overlay visible" @click.self="showRecordModal = false">
      <div class="modal-content">
        <h2>{{ isEditing ? 'Editar Registro' : 'Adicionar Registro' }}</h2>
        <form @submit.prevent="saveRecord">
          <div class="form-group" v-if="activeTab !== 'weights'">
            <label>Nome / Motivo / Produto *</label>
            <input type="text" v-model="recordForm.name" required />
          </div>
          
          <div class="form-group">
            <label>Data *</label>
            <input type="date" v-model="recordForm.date" required />
          </div>

          <div class="form-group" v-if="['vaccines', 'parasites'].includes(activeTab)">
            <label>Próxima Aplicação</label>
            <input type="date" v-model="recordForm.nextDate" />
          </div>

          <div class="form-group" v-if="['vaccines', 'parasites', 'consults'].includes(activeTab)">
            <label>Veterinário / Local</label>
            <input type="text" v-model="recordForm.vet" />
          </div>

          <div class="form-group" v-if="activeTab === 'weights'">
            <label>Peso (kg) *</label>
            <input type="number" step="0.1" v-model="recordForm.weight" required />
          </div>

          <div class="form-group" v-if="activeTab === 'consults'">
            <label>Anotações Adicionais</label>
            <textarea v-model="recordForm.notes" rows="3"></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showRecordModal = false">Cancelar</button>
            <button type="submit" class="btn btn-primary">Salvar</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showDocModal" class="modal-overlay visible" @click.self="showDocModal = false">
      <div class="modal-content" style="max-width: 500px;">
        <h2>👩‍⚕️ Área Médica</h2>
        <p style="color: var(--text-light); margin-bottom: 20px; font-size: 0.9rem;">Emita documentos oficiais que ficarão salvos diretamente na conta do tutor.</p>
        
        <form @submit.prevent="saveDoc">
          <div class="form-group">
            <label>Tipo de Documento *</label>
            <select v-model="docForm.type" required>
              <option value="Receituário">Receituário</option>
              <option value="Atestado">Atestado Médico / Cirúrgico</option>
              <option value="Encaminhamento">Encaminhamento</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Data da Emissão *</label>
            <input type="date" v-model="docForm.date" required />
          </div>
          
          <div class="form-group">
            <label>Veterinário Responsável *</label>
            <input type="text" v-model="docForm.vetName" required placeholder="Dr(a). João (CRMV 1234)" />
          </div>
          
          <div class="form-group">
            <label>Corpo do Documento *</label>
            <textarea v-model="docForm.content" rows="6" required style="font-family: monospace;"></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showDocModal = false">Cancelar</button>
            <button type="submit" class="btn btn-primary" style="background: var(--primary-dark);">Emitir Documento</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
.mt-4 { margin-top: 1rem; }
.next-due { font-size: 0.85rem; color: var(--warning-color); font-weight: 600; margin-top: 8px; background: #FFFBEB; padding: 4px 8px; border-radius: 6px; display: inline-block; }
</style>