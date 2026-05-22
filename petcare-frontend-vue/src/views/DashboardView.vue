<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePetStore } from '@/stores/petStore'
import { useAuthStore } from '@/stores/authStore'
import placeholderImg from '@/assets/placeholder.svg'

const petStore = usePetStore()
const authStore = useAuthStore()
const router = useRouter()
const searchQuery = ref('')
const showNotifications = ref(false)
onMounted(() => {
  petStore.fetchPets()
  petStore.connectWebSocket()
})

// Filtra os pets em tempo real (inclui microchip para veterinários)
const filteredPets = computed(() => {
  const query = searchQuery.value.toLowerCase()
  return petStore.pets.filter(pet => {
    const matchName = pet.name.toLowerCase().includes(query)
    const matchSpecies = pet.species.toLowerCase().includes(query)
    const matchMicrochip = pet.microchip?.toLowerCase().includes(query) || false
    
    if (authStore.userType === 'veterinario') {
      return matchName || matchSpecies || matchMicrochip
    }
    return matchName || matchSpecies
  })
})

// Calcula os Lembretes dos próximos 30 dias (Apenas para Tutores)
const reminders = computed(() => {
  if (authStore.userType === 'veterinario') return []
  
  const upcoming: any[] = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  petStore.pets.forEach(pet => {
    ['vaccines', 'parasites'].forEach(type => {
      const records = (pet as any)[type] || []
      records.forEach((record: any) => {
        if (record.nextDate) {
          const nextDate = new Date(record.nextDate + 'T00:00:00')
          const diffTime = nextDate.getTime() - today.getTime()
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
          
          if (diffDays <= 30 && diffTime >= 0) {
            upcoming.push({ 
              petName: pet.name, 
              recordName: record.name, 
              diffDays, 
              vet: record.vet 
            })
          }
        }
      })
    })
  })
  
  return upcoming.sort((a, b) => a.diffDays - b.diffDays)
})



function logout() {
  authStore.logout()
}

function openPet(id: number) {
  router.push(`/pet/${id}`)
}

function goToAddPet() {
  router.push('/pet/new') // Certifique-se de ter essa rota criada depois para o formulário
}

function goToSettings() {
  router.push('/settings') // Certifique-se de ter essa rota criada depois
}
function toggleNotifications() {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) {
    petStore.clearNotifications()
    petStore.hasNewNotification = false
    
  }
}
</script>

<template>
  <div class="dashboard-page">
    <header class="top-navbar" :class="{ 'vet-mode': authStore.userType === 'veterinario' }">
      <div class="nav-brand">
        <svg v-if="authStore.userType === 'veterinario'" xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C7.58 2 4 5.58 4 10c0 4.42 8 12 8 12s8-7.58 8-12c0-4.42-3.58-8-8-8z"/><circle cx="12" cy="10" r="3"/></svg>
        <h1>{{ authStore.userType === 'veterinario' ? 'Portal Clínico' : 'PetCare Plus' }}</h1>
      </div>
      
      <div class="nav-actions">
        <button class="icon-btn" aria-label="Notificações" @click="toggleNotifications">
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
  <span v-if="petStore.unreadCount > 0" class="notification-badge">{{ petStore.unreadCount }}</span>
</button>

<div v-if="showNotifications" class="notifications-dropdown">
  <div class="dropdown-header">
    <span>Notificações</span>
    <button @click="showNotifications = false" class="close-btn">×</button>
  </div>
  <div v-if="petStore.notifications.length === 0" class="no-notifs">
    Nenhuma notificação nova.
  </div>
  <div v-else class="notif-list">
    <div v-for="(msg, index) in petStore.notifications" :key="index" class="notif-item">
      <div class="notif-bullet"></div>
      <p>{{ msg }}</p>
    </div>
  </div>
</div>

        <button class="icon-btn" aria-label="Configurações" @click="goToSettings">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
        </button>

        <button class="icon-btn logout-btn" aria-label="Sair" @click="logout">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
        </button>
      </div>
    </header>

    <div class="search-wrapper">
      <div class="search-box">
        <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input 
          v-model="searchQuery" 
          type="text" 
          class="search-input" 
          :placeholder="authStore.userType === 'veterinario' ? 'Buscar por nome, espécie ou microchip...' : 'Buscar pet por nome ou espécie...'" 
        />
      </div>
    </div>

    <main class="main-content">
      <section v-if="reminders.length > 0" class="reminders-section">
        <h2 class="section-title">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
          Próximos Lembretes
        </h2>
        <div class="reminders-list">
          <div v-for="(reminder, idx) in reminders" :key="idx" class="reminder-card">
            <div class="reminder-icon">🗓️</div>
            <div class="reminder-info">
              <p>
                <strong>{{ reminder.petName }}</strong>: Próximo(a) {{ reminder.recordName }} 
                <span class="highlight">{{ reminder.diffDays === 0 ? 'hoje' : `em ${reminder.diffDays} dia(s)` }}</span>
                <span v-if="reminder.vet"> na {{ reminder.vet }}</span>.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section class="pets-section">
        <div class="section-header">
          <h2 class="section-title">{{ authStore.userType === 'veterinario' ? 'Pacientes Registrados' : 'Seus Companheiros' }}</h2>
          <span class="count-badge" :class="{ 'vet-badge': authStore.userType === 'veterinario' }">
            {{ filteredPets.length }} {{ authStore.userType === 'veterinario' ? 'Pacientes' : 'Pets' }}
          </span>
        </div>

        <div v-if="filteredPets.length === 0" class="empty-state">
          <div class="empty-icon">🐾</div>
          <p>Nenhum registro encontrado no momento.</p>
        </div>

        <div class="pet-grid">
          <transition-group name="list">
            <div 
              v-for="pet in filteredPets" 
              :key="pet.id" 
              class="pet-card" 
              @click="openPet(pet.id)"
            >
              <div class="pet-photo-container">
                <img :src="pet.photo || placeholderImg" class="pet-photo" :alt="pet.name" />
              </div>
              <div class="pet-info">
                <h3>{{ pet.name }}</h3>
                <div class="pet-tags">
                  <span class="tag species-tag">{{ pet.species }}</span>
                  <span v-if="pet.breed" class="tag breed-tag">{{ pet.breed }}</span>
                </div>
                <p v-if="authStore.userType === 'veterinario'" class="microchip-text">
                  Microchip: {{ pet.microchip || 'Não informado' }}
                </p>
              </div>
              <div class="pet-action">
                <button class="action-btn">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                </button>
              </div>
            </div>
          </transition-group>
        </div>
      </section>
    </main>

    <button v-if="authStore.userType === 'tutor'" class="fab-add-pet" @click="goToAddPet" aria-label="Adicionar novo pet">
      <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
    </button>
  </div>
</template>

<style scoped>
/* Container Principal */
.dashboard-page {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: 'Inter', system-ui, sans-serif;
  padding-bottom: 80px;
}

/* Header Navbar */
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
.top-navbar.vet-mode {
  background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.4);
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nav-brand h1 {
  font-size: 1.4rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0;
}
.nav-actions {
  display: flex;
  gap: 8px;
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
  position: relative;
  transition: all 0.2s ease;
}
.icon-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
}
.notification-badge {
  position: absolute;
  top: 8px;
  right: 10px;
  width: 10px;
  height: 10px;
  background-color: #EF4444;
  border-radius: 50%;
  border: 2px solid #14B8A6;
}

/* Busca Flutuante */
.search-wrapper {
  padding: 1.5rem 2rem 0;
  max-width: 900px;
  margin: 0 auto;
}
.search-box {
  position: relative;
  display: flex;
  align-items: center;
}
.search-icon {
  position: absolute;
  left: 18px;
  color: #94A3B8;
}
.search-input {
  width: 100%;
  padding: 16px 16px 16px 48px;
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  font-size: 1.05rem;
  color: #1E293B;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}
.search-input:focus {
  outline: none;
  border-color: #14B8A6;
  box-shadow: 0 0 0 4px rgba(20, 184, 166, 0.15), 0 10px 15px -3px rgba(0, 0, 0, 0.05);
}

/* Área de Conteúdo Principal */
.main-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

/* Lembretes */
.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  font-weight: 800;
  color: #0F172A;
  margin-bottom: 1.2rem;
}
.reminders-section {
  margin-bottom: 2.5rem;
}
.reminders-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.reminder-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: linear-gradient(to right, #FFFBEB, #FFFFFF);
  border-left: 5px solid #F59E0B;
  padding: 1.2rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.reminder-icon {
  font-size: 1.5rem;
}
.reminder-info p {
  margin: 0;
  color: #334155;
  font-size: 1rem;
  line-height: 1.5;
}
.reminder-info .highlight {
  color: #D97706;
  font-weight: 700;
}

/* Header da Seção de Pets */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.count-badge {
  background: #E2E8F0;
  color: #475569;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 700;
}
.vet-badge {
  background: #E0F2FE;
  color: #0369A1;
}

/* Grid de Pets */
.pet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.2rem;
}
.pet-card {
  display: flex;
  align-items: center;
  background: white;
  padding: 1.2rem;
  border-radius: 20px;
  border: 1px solid #F1F5F9;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.pet-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 25px -5px rgba(0, 0, 0, 0.1);
  border-color: #CCFBF1;
}
.pet-photo-container {
  flex-shrink: 0;
  margin-right: 1.2rem;
}
.pet-photo {
  width: 75px;
  height: 75px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #F0F9FF;
}
.pet-info {
  flex-grow: 1;
  overflow: hidden;
}
.pet-info h3 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.pet-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.tag {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 8px;
}
.species-tag {
  background: #F1F5F9;
  color: #475569;
}
.breed-tag {
  background: #F0FDF4;
  color: #166534;
}
.microchip-text {
  font-size: 0.85rem;
  color: #64748B;
  margin: 8px 0 0 0;
}
.pet-action {
  margin-left: 10px;
}
.action-btn {
  background: #F8FAFC;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94A3B8;
  transition: all 0.2s;
}
.pet-card:hover .action-btn {
  background: #CCFBF1;
  color: #0F766E;
}

/* Estado Vazio */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 24px;
  border: 2px dashed #E2E8F0;
}
.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}
.empty-state p {
  color: #64748B;
  font-size: 1.1rem;
}

/* Botão Flutuante (FAB) */
.fab-add-pet {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #14B8A6 0%, #0F766E 100%);
  color: white;
  border: none;
  box-shadow: 0 10px 25px -5px rgba(20, 184, 166, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.fab-add-pet:hover {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 15px 30px -5px rgba(20, 184, 166, 0.6);
}

/* Animações da Lista */
.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Responsividade */
@media (max-width: 768px) {
  .top-navbar {
    padding: 1rem 1.5rem;
  }
  .search-wrapper {
    padding: 1.5rem 1.5rem 0;
  }
  .main-content {
    padding: 1.5rem;
  }
  .pet-grid {
    grid-template-columns: 1fr;
  }
  .fab-add-pet {
    bottom: 1.5rem;
    right: 1.5rem;
    width: 56px;
    height: 56px;
  }
}
.notifications-dropdown {
  position: absolute;
  top: 70px;
  right: 20px;
  width: 320px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 15px 35px -5px rgba(0,0,0,0.15);
  border: 1px solid #E2E8F0;
  z-index: 100;
  overflow: hidden;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.dropdown-header {
  padding: 1rem;
  border-bottom: 1px solid #F1F5F9;
  font-weight: 700;
  color: #0F172A;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #64748B;
}

.notif-list {
  max-height: 300px;
  overflow-y: auto;
}

.notif-item {
  color: rgb(0, 0, 0); /* Texto da notificação cinza escuro */
  padding: 1rem;
  border-bottom: 1px solid #F8FAFC;
  display: flex;
  gap: 10px;
  align-items: flex-start;
  transition: background 0.2s;
}

.notif-item:hover {
  background: #F1F5F9;
}

.notif-bullet {
  width: 8px; height: 8px; border-radius: 50%; background: #14B8A6; margin-top: 6px;
}

.no-notifs {
  padding: 2rem;
  text-align: center;
  color: #64748B; /* Cor neutra para mensagem vazia */
  font-size: 0.9rem;
}
</style>