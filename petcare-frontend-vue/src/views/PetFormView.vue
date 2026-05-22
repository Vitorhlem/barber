<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePetStore } from '@/stores/petStore'
import placeholderImg from '@/assets/placeholder.svg'

const route = useRoute()
const router = useRouter()
const petStore = usePetStore()

const isEditMode = computed(() => route.params.id !== undefined && route.params.id !== 'new')
const petId = computed(() => isEditMode.value ? Number(route.params.id) : null)
const isLoading = ref(false)

const form = ref({
  nome: '',
  especie: '',
  microchip: '',
  raca: '',
  data_nascimento: '',
  sexo: 'Macho'
})

const photoPreview = ref<string>(placeholderImg)
const fileInput = ref<HTMLInputElement | null>(null)

onMounted(async () => {
  if (petStore.pets.length === 0) {
    await petStore.fetchPets()
  }

  if (isEditMode.value && petId.value) {
    const existingPet = petStore.pets.find(p => p.id === petId.value)
    if (existingPet) {
      form.value = {
        nome: existingPet.name || '',
        especie: existingPet.species || '',
        microchip: existingPet.microchip || '',
        raca: existingPet.breed || '',
        data_nascimento: existingPet.birthdate || '',
        sexo: existingPet.sex || 'Macho'
      }
      if (existingPet.photo) {
        photoPreview.value = existingPet.photo
      }
    } else {
      router.push('/')
    }
  }
})

function triggerSelectPhoto() {
  fileInput.value?.click()
}

function onPhotoChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      if (e.target?.result) {
        photoPreview.value = e.target.result as string
      }
    }
    reader.readAsDataURL(file)
  }
}

function removePhoto() {
  photoPreview.value = placeholderImg
  if (fileInput.value) fileInput.value.value = ''
}

async function handleSubmit() {
  if (!form.value.nome || !form.value.especie) {
    alert('Por favor, preencha todos os campos obrigatórios (*).')
    return
  }

  isLoading.value = true
  const payload = {
    nome: form.value.nome,
    especie: form.value.especie,
    microchip: form.value.microchip || null,
    raca: form.value.raca || null,
    data_nascimento: form.value.data_nascimento || null,
    sexo: form.value.sexo,
    foto: photoPreview.value === placeholderImg ? null : photoPreview.value
  }

  try {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const API_BASE_URL = isLocalhost ? 'http://localhost:8000' : 'https://petcare-api-backend.onrender.com';
    
    let url = `${API_BASE_URL}/usuarios/${localStorage.getItem('petcareplus_user_id')}/pets/`
    let method = 'POST'

    if (isEditMode.value && petId.value) {
      url = `${API_BASE_URL}/pets/${petId.value}`
      method = 'PUT'
    }

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (response.ok) {
      await petStore.fetchPets()
      router.push('/')
    } else {
      alert('Erro ao salvar os dados do pet na API.')
    }
  } catch (error) {
    alert('Erro de conexão com o servidor.')
  } finally {
    isLoading.value = false
  }
}

function goBack() {
  router.push('/')
}
</script>

<template>
  <div class="form-page-wrapper">
    <header class="top-navbar">
      <button @click="goBack" class="icon-btn" aria-label="Voltar">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
      </button>
      <h1>{{ isEditMode ? 'Editar Companheiro' : 'Novo Companheiro' }}</h1>
      <div style="width: 42px;"></div> </header>

    <main class="form-main-container">
      <form @submit.prevent="handleSubmit" class="premium-form">
        
        <div class="photo-upload-section">
          <div class="image-preview-wrapper" @click="triggerSelectPhoto">
            <img :src="photoPreview" alt="Foto do Pet" class="avatar-preview" :class="{ 'has-photo': photoPreview !== placeholderImg }" />
            
            <div class="avatar-overlay">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
            </div>
          </div>
          
          <input type="file" ref="fileInput" accept="image/*" class="hidden-input" @change="onPhotoChange" />
          
          <div class="upload-actions">
            <button type="button" class="btn-action-outline" @click="triggerSelectPhoto">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
              Alterar Foto
            </button>
            <button v-if="photoPreview !== placeholderImg" type="button" class="btn-action-danger" @click="removePhoto">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
              Remover
            </button>
          </div>
        </div>

        <div class="form-divider"></div>

        <div class="form-grid">
          <div class="form-group full-width">
            <label>Nome do Pet *</label>
            <input type="text" v-model="form.nome" class="form-control" placeholder="Ex: Thor, Mel" required />
          </div>

          <div class="form-group">
            <label>Espécie *</label>
            <input type="text" v-model="form.especie" class="form-control" placeholder="Ex: Cão, Gato" required />
          </div>

          <div class="form-group">
            <label>Raça</label>
            <input type="text" v-model="form.raca" class="form-control" placeholder="Ex: Labrador, SRD" />
          </div>

          <div class="form-group">
            <label>Data de Nascimento</label>
            <input type="date" v-model="form.data_nascimento" class="form-control" />
          </div>

          <div class="form-group">
            <label>Sexo</label>
            <div class="select-wrapper">
              <select v-model="form.sexo" class="form-control">
                <option value="Macho">Macho</option>
                <option value="Fêmea">Fêmea</option>
              </select>
              <svg class="select-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
            </div>
          </div>
          
          <div class="form-group full-width">
            <label>Nº do Microchip (Opcional)</label>
            <input type="text" v-model="form.microchip" class="form-control" placeholder="Insira o código do chip de identificação" />
          </div>
        </div>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          <span v-if="!isLoading" style="display: flex; align-items: center; gap: 8px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
            {{ isEditMode ? 'Salvar Alterações' : 'Cadastrar Pet' }}
          </span>
          <div v-else class="spinner-loader"></div>
        </button>
      </form>
    </main>
  </div>
</template>

<style scoped>
.form-page-wrapper {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: 'Inter', system-ui, sans-serif;
}

/* Navbar Premium (Idêntica à Dashboard) */
.top-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 2rem;
  background: linear-gradient(135deg, #14B8A6 0%, #0F766E 100%);
  color: white;
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 4px 20px -2px rgba(20, 184, 166, 0.25);
}
.top-navbar h1 {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
}
.icon-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}
.icon-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
}

/* Container do Formulário */
.form-main-container {
  max-width: 650px;
  margin: 2.5rem auto;
  padding: 0 1.5rem;
  width: 100%;
}
.premium-form {
  background: #ffffff;
  padding: 3rem;
  border-radius: 28px;
  box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.08);
  border: 1px solid #e2e8f0;
}

/* Seção de Upload de Imagem */
.photo-upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}
.image-preview-wrapper {
  position: relative;
  width: 140px;
  height: 140px;
  cursor: pointer;
  border-radius: 50%;
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.image-preview-wrapper:hover {
  transform: scale(1.05);
}
.avatar-preview {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #f1f5f9;
  box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.1);
  transition: border-color 0.3s;
}
.avatar-preview.has-photo {
  border-color: #CCFBF1; /* Borda verdinha se tiver foto */
}

/* Overlay Escuro com Câmera ao passar o mouse */
.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.image-preview-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.hidden-input {
  display: none;
}
.upload-actions {
  display: flex;
  gap: 12px;
}
.btn-action-outline, .btn-action-danger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}
.btn-action-outline {
  background: #f1f5f9;
  color: #475569;
}
.btn-action-outline:hover {
  background: #e2e8f0;
  color: #0f172a;
}
.btn-action-danger {
  background: #fef2f2;
  color: #ef4444;
}
.btn-action-danger:hover {
  background: #fee2e2;
}

.form-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 2.5rem 0;
}

/* Grid de Inputs */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
.full-width {
  grid-column: 1 / -1;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.form-group label {
  font-size: 0.92rem;
  font-weight: 600;
  color: #334155;
}
.form-control {
  width: 100%;
  padding: 14px 16px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  font-size: 0.98rem;
  color: #0f172a;
  transition: all 0.25s ease;
  font-family: inherit;
}
.form-control:focus {
  outline: none;
  border-color: #14B8A6;
  background-color: white;
  box-shadow: 0 0 0 4px rgba(20, 184, 166, 0.12);
}

/* Customização do Select */
.select-wrapper {
  position: relative;
}
.select-wrapper select {
  appearance: none;
  cursor: pointer;
}
.select-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

/* Botão Principal */
.btn-primary {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #14B8A6 0%, #0F766E 100%);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(20, 184, 166, 0.25);
  margin-top: 2.5rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  justify-content: center;
  align-items: center;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(20, 184, 166, 0.35);
}
.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Spinner de Loading */
.spinner-loader {
  width: 22px;
  height: 22px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #ffffff;
  animation: spinWheel 0.8s linear infinite;
}
@keyframes spinWheel {
  to { transform: rotate(360deg); }
}

/* Responsividade */
@media (max-width: 640px) {
  .top-navbar {
    padding: 1rem 1.5rem;
  }
  .form-main-container {
    margin: 1.5rem auto;
    padding: 0 1rem;
  }
  .premium-form {
    padding: 2rem 1.5rem;
    border-radius: 20px;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>