<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSettingsStore } from '@/stores/settingsStore'
import { usePetStore } from '@/stores/petStore'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const settingsStore = useSettingsStore()
const petStore = usePetStore()
const authStore = useAuthStore()

const vetContact = ref('')
const emergencyContact = ref('')
const isImporting = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

onMounted(() => {
  vetContact.value = settingsStore.contacts.vet
  emergencyContact.value = settingsStore.contacts.emergency
})

function saveContacts() {
  settingsStore.saveContacts(vetContact.value, emergencyContact.value)
  alert('Contatos salvos com sucesso!')
}

// --- LÓGICA DE EXPORTAÇÃO ---
function exportData() {
  const dataToExport = {
    pets: petStore.pets,
    contacts: settingsStore.contacts
  }
  const dataStr = JSON.stringify(dataToExport, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = `petcareplus_backup_${new Date().toISOString().split('T')[0]}.json`
  a.click()
}

// --- LÓGICA DE IMPORTAÇÃO ---
function triggerImport() {
  if (confirm('Atenção: Os pets do arquivo serão ADICIONADOS à sua conta atual. Deseja continuar?')) {
    fileInput.value?.click()
  }
}

async function handleImportFile(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const importedData = JSON.parse(e.target?.result as string)
      
      if (!importedData.pets || !Array.isArray(importedData.pets)) {
        alert('Arquivo inválido ou corrompido.')
        return
      }

      if (importedData.contacts) {
        settingsStore.saveContacts(importedData.contacts.vet, importedData.contacts.emergency)
        vetContact.value = importedData.contacts.vet
        emergencyContact.value = importedData.contacts.emergency
      }

      isImporting.value = true
      
      const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      const API_BASE_URL = isLocalhost ? 'http://localhost:8000' : 'https://petcare-api-backend.onrender.com'
      
      let petsImportados = 0

      // Loop importando cada pet para a API
      for (const pet of importedData.pets) {
        const petPayload = {
          nome: pet.name,
          especie: pet.species,
          microchip: pet.microchip || null,
          raca: pet.breed || null,
          data_nascimento: pet.birthdate || null,
          sexo: pet.sex || 'Macho',
          foto: pet.photo || null
        }

        const petRes = await fetch(`${API_BASE_URL}/usuarios/${authStore.userId}/pets/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(petPayload)
        })

        if (petRes.ok) {
          const newPet = await petRes.json()
          
          // Importando os registros (Vacinas, Pesos, Consultas, Docs)
          const allRecords = [
            ...(pet.vaccines || []).map((r:any) => ({ ...r, tipo: 'vacina' })),
            ...(pet.parasites || []).map((r:any) => ({ ...r, tipo: 'parasita' })),
            ...(pet.consults || []).map((r:any) => ({ ...r, tipo: 'consulta' })),
            ...(pet.weights || []).map((r:any) => ({ ...r, tipo: 'peso' })),
            ...(pet.documents || []).map((r:any) => ({ ...r, tipo: 'documento' }))
          ]

          for (const record of allRecords) {
            await fetch(`${API_BASE_URL}/pets/${newPet.id}/registros/`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                tipo: record.tipo,
                nome: record.name,
                data: record.date,
                proxima_data: record.nextDate || null,
                peso: record.weight || null,
                anotacoes: record.notes || record.vet || null
              })
            })
          }
          petsImportados++
        }
      }

      alert(`Importação concluída! ${petsImportados} pets importados com sucesso.`)
      await petStore.fetchPets() // Atualiza os dados locais

    } catch (error) {
      alert('Erro ao processar o arquivo. Verifique se é um backup válido.')
    } finally {
      isImporting.value = false
      if(fileInput.value) fileInput.value.value = ''
    }
  }
  reader.readAsText(file)
}
</script>

<template>
  <div class="settings-page">
    <header class="top-navbar">
      <button @click="router.push('/')" class="icon-btn" aria-label="Voltar">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
      </button>
      <h1>Configurações do App</h1>
      <div style="width: 42px;"></div>
    </header>

    <main class="settings-main-container">
      
      <section class="settings-card">
        <div class="card-header">
          <div class="icon-wrapper bg-blue">🚑</div>
          <h2>Contatos de Emergência</h2>
        </div>
        <p class="section-desc">Mantenha os telefones úteis sempre em mãos para emergências.</p>
        
        <form @submit.prevent="saveContacts" class="settings-form">
          <div class="form-group">
            <label>Veterinário(a) Principal</label>
            <input type="text" v-model="vetContact" class="form-control" placeholder="Ex: (16) 99999-9999" />
          </div>
          <div class="form-group">
            <label>Hospital 24h</label>
            <input type="text" v-model="emergencyContact" class="form-control" placeholder="Ex: (16) 98888-8888" />
          </div>
          <button type="submit" class="btn-action outline-blue">💾 Salvar Contatos</button>
        </form>
      </section>

      <section class="settings-card">
        <div class="card-header">
          <div class="icon-wrapper bg-green">☁️</div>
          <h2>Gerenciamento de Dados</h2>
        </div>
        <p class="section-desc">Faça backup dos seus dados offline ou importe um arquivo .json salvo anteriormente para sua conta na nuvem.</p>
        
        <div class="data-actions">
          <button class="btn-action solid-green" @click="exportData">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            Exportar Backup
          </button>
          
          <button class="btn-action outline-gray" @click="triggerImport" :disabled="isImporting">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
            {{ isImporting ? 'Importando...' : 'Importar Dados' }}
          </button>
          
          <input type="file" ref="fileInput" accept=".json" style="display: none;" @change="handleImportFile" />
        </div>
      </section>

    </main>
  </div>
</template>

<style scoped>
.settings-page {
  min-height: 100vh;
  background-color: #f8fafc;
}
.top-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 2rem;
  background: linear-gradient(135deg, #14B8A6 0%, #0F766E 100%);
  color: white;
  box-shadow: 0 4px 20px -2px rgba(20, 184, 166, 0.25);
}
.top-navbar h1 { margin: 0; font-size: 1.3rem; }
.icon-btn {
  background: rgba(255, 255, 255, 0.1); border: none; color: white; width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer;
}

.settings-main-container {
  max-width: 700px;
  margin: 2.5rem auto;
  padding: 0 1.5rem;
}

.settings-card {
  background: white;
  padding: 2rem;
  border-radius: 24px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  border: 1px solid #f1f5f9;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.icon-wrapper {
  width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}
.bg-blue { background: #E0F2FE; color: #0369A1; }
.bg-green { background: #D1FAE5; color: #047857; }

.settings-card h2 { font-size: 1.4rem; font-weight: 800; color: #0F172A; }
.section-desc { font-size: 0.95rem; color: #64748b; margin-bottom: 1.5rem; }

.form-group { display: flex; flex-direction: column; gap: 8px; margin-bottom: 1.2rem; }
.form-group label { font-size: 0.92rem; font-weight: 600; color: #334155; }
.form-control { width: 100%; padding: 14px 16px; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; font-size: 0.98rem; }
.form-control:focus { outline: none; border-color: #14B8A6; background-color: white; box-shadow: 0 0 0 4px rgba(20, 184, 166, 0.12); }

.data-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 14px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}
.outline-blue { background: white; color: #0369A1; border-color: #E0F2FE; }
.outline-blue:hover { background: #F0F9FF; }
.solid-green { background: #10B981; color: white; }
.solid-green:hover { background: #059669; }
.outline-gray { background: white; color: #475569; border-color: #E2E8F0; }
.outline-gray:hover { background: #F8FAFC; }

@media (max-width: 600px) {
  .data-actions { flex-direction: column; }
  .btn-action { width: 100%; }
}
</style>