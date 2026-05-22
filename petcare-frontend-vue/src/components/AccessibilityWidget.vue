<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settingsStore'

const settingsStore = useSettingsStore()
const isOpen = ref(false)

onMounted(() => {
  settingsStore.applyAccessibility() // Aplica as configs assim que o app abre
})

function togglePanel() {
  isOpen.value = !isOpen.value
}
</script>

<template>
  <div class="accessibility-widget">
    <button class="fab-a11y" @click="togglePanel" aria-label="Acessibilidade">
      <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"></path><circle cx="12" cy="12" r="9"></circle><path d="M10 16.5l2 -3l2 3m-2 -3v-2l3 -1m-6 0l3 1"></path><circle cx="12" cy="7.5" r=".5" fill="currentColor"></circle></svg>
    </button>
    
    <div class="a11y-panel" :class="{ 'visible': isOpen }">
      <h3>Acessibilidade</h3>
      
      <div class="a11y-option">
        <label>Alto Contraste</label>
        <button class="switch-btn" :class="{ 'active': settingsStore.a11y.highContrast }" @click="settingsStore.a11y.highContrast = !settingsStore.a11y.highContrast"><span></span></button>
      </div>
      <div class="a11y-option">
        <label>Aumentar Texto</label>
        <button class="switch-btn" :class="{ 'active': settingsStore.a11y.largeText }" @click="settingsStore.a11y.largeText = !settingsStore.a11y.largeText"><span></span></button>
      </div>
      <div class="a11y-option">
        <label>Fonte Amigável (Dislexia)</label>
        <button class="switch-btn" :class="{ 'active': settingsStore.a11y.dyslexiaFont }" @click="settingsStore.a11y.dyslexiaFont = !settingsStore.a11y.dyslexiaFont"><span></span></button>
      </div>
      <div class="a11y-option">
        <label>Destacar Links e Botões</label>
        <button class="switch-btn" :class="{ 'active': settingsStore.a11y.highlightLinks }" @click="settingsStore.a11y.highlightLinks = !settingsStore.a11y.highlightLinks"><span></span></button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.accessibility-widget {
  position: fixed;
  bottom: 2rem;
  left: 2rem; /* Alterado para a esquerda para não conflitar com o botão de Adicionar Pet */
  z-index: 999;
}
.fab-a11y {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #1E293B;
  color: white;
  border: none;
  box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.fab-a11y:hover {
  transform: scale(1.1) rotate(5deg);
}
.a11y-panel {
  position: absolute;
  bottom: 75px;
  left: 0;
  width: 280px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0,0,0,0.15);
  padding: 1.5rem;
  visibility: hidden;
  opacity: 0;
  transform: translateY(20px) scale(0.95);
  transform-origin: bottom left;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid #e2e8f0;
}
.a11y-panel.visible {
  visibility: visible;
  opacity: 1;
  transform: translateY(0) scale(1);
}
.a11y-panel h3 {
  margin-top: 0;
  margin-bottom: 1.2rem;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
}
.a11y-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.a11y-option label {
  font-size: 0.95rem;
  font-weight: 500;
  color: #334155;
}
.switch-btn {
  position: relative;
  width: 44px;
  height: 24px;
  background-color: #cbd5e1;
  border-radius: 34px;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.switch-btn span {
  position: absolute;
  height: 20px;
  width: 20px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.switch-btn.active {
  background-color: #14B8A6;
}
.switch-btn.active span {
  transform: translateX(20px);
}
</style>

<style>
/* 1. Alto Contraste */
body.high-contrast {
  --primary-color: #00A896;
  --primary-dark: #02C39A;
  --text-color: #000000;
  --text-light: #2a2a2a;
  --bg-color: #E0E0E0;
  background-color: var(--bg-color) !important;
}
body.high-contrast * {
  box-shadow: none !important;
}
body.high-contrast .premium-form, body.high-contrast .pet-card {
  border: 2px solid #000 !important;
  background: #FFF !important;
}

/* 2. Texto Maior */
html.large-text {
  font-size: 18px !important;
}

/* 3. Fonte Amigável (Dislexia) */
body.dyslexia-font {
  font-family: 'Open Sans', 'Comic Sans MS', sans-serif !important;
  letter-spacing: 0.05em !important;
  word-spacing: 0.1em !important;
}

/* 4. Destacar Links e Botões */
body.highlight-links a, body.highlight-links button {
  border: 3px solid #0F766E !important;
}
</style>