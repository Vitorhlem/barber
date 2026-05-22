<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(true)
const isLoading = ref(false)

// Sistema Reativo de Toasts (Substitui os alerts nativos por avisos lindos)
const toast = ref<{ show: boolean; message: string; type: 'success' | 'error' }>({
  show: false,
  message: '',
  type: 'error'
})

function showToast(message: string, type: 'success' | 'error' = 'error') {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 4000)
}

const form = ref({
  email: '',
  senha: '',
  nome: '',
  tipo: 'tutor' // 'tutor' ou 'veterinario'
})

async function handleSubmit() {
  if (!form.value.email || !form.value.senha || (!isLogin.value && !form.value.nome)) {
    showToast('Por favor, preencha todos os campos obrigatórios.', 'error')
    return
  }

  isLoading.value = true
  try {
    const endpoint = isLogin.value ? '/login/' : '/usuarios/'
    
    // LÓGICA AUTOMÁTICA DE AMBIENTE
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const API_BASE_URL = isLocalhost ? 'http://localhost:8000' : 'https://petcare-api-backend.onrender.com';

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(isLogin.value ? { email: form.value.email, senha: form.value.senha } : form.value)
    })

    if (response.ok) {
      const data = await response.json()
      authStore.login(data.id, data.tipo)
      showToast('Autenticação realizada com sucesso! Redirecionando...', 'success')
      setTimeout(() => {
        router.push('/')
      }, 1000)
    } else {
      showToast(isLogin.value ? 'E-mail ou senha incorretos. Tente novamente.' : 'Este e-mail já está em uso ou os dados são inválidos.', 'error')
    }
  } catch (error) {
    showToast('Falha na comunicação com o servidor. Tente novamente mais tarde.', 'error')
  } finally {
    isLoading.value = false
  }
}

function toggleMode() {
  isLogin.value = !isLogin.value
}
</script>

<template>
  <div class="auth-page-container">
    <div class="animated-bg">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
    </div>

    <div class="toast-notification" :class="{ 'show': toast.show, 'success': toast.type === 'success', 'error': toast.type === 'error' }">
      <div class="toast-content">
        <svg v-if="toast.type === 'success'" class="toast-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
        <svg v-else class="toast-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        <span>{{ toast.message }}</span>
      </div>
    </div>

    <div class="auth-wrapper">
      <div class="auth-brand">
        <div class="brand-logo">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C7.58 2 4 5.58 4 10c0 4.42 8 12 8 12s8-7.58 8-12c0-4.42-3.58-8-8-8z"/><circle cx="12" cy="10" r="3"/></svg>
          <span>PetCare Plus</span>
        </div>
        <div class="brand-main-text">
          <h2>A saúde do seu melhor amigo em boas mãos.</h2>
          <p>Acesse o portal completo para gerenciar carteirinhas de vacinação, prontuários clínicos e históricos médicos em tempo real.</p>
        </div>
        <div class="brand-footer-decor"></div>
      </div>

      <div class="auth-form-container">
        <div class="form-header">
          <h1>{{ isLogin ? 'Acessar Conta' : 'Criar Nova Conta' }}</h1>
          <p>{{ isLogin ? 'Insira suas credenciais para entrar na plataforma.' : 'Preencha os dados abaixo para começar a usar.' }}</p>
        </div>

        <form @submit.prevent="handleSubmit" class="interactive-form">
          <transition-group name="form-slide">
            <div v-if="!isLogin" class="form-group" key="reg-nome">
              <label>Nome Completo</label>
              <div class="input-wrapper">
                <input type="text" v-model="form.nome" class="form-control" placeholder="Ex: João da Silva" />
                <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
              </div>
            </div>
            
            <div v-if="!isLogin" class="form-group" key="reg-tipo">
              <label>Perfil de Acesso</label>
              <div class="profile-cards-selector">
                <div class="profile-selector-card" :class="{ 'selected': form.tipo === 'tutor' }" @click="form.tipo = 'tutor'">
                  <div class="selector-circle"></div>
                  <span>Tutor (Dono)</span>
                </div>
                <div class="profile-selector-card" :class="{ 'selected': form.tipo === 'veterinario' }" @click="form.tipo = 'veterinario'">
                  <div class="selector-circle"></div>
                  <span>Veterinário</span>
                </div>
              </div>
            </div>

            <div class="form-group" key="field-email">
              <label>E-mail</label>
              <div class="input-wrapper">
                <input type="email" v-model="form.email" class="form-control" placeholder="seu@email.com" required />
                <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
              </div>
            </div>
            
            <div class="form-group" key="field-senha">
              <label>Senha</label>
              <div class="input-wrapper">
                <input type="password" v-model="form.senha" class="form-control" placeholder="••••••••" required />
                <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
              </div>
            </div>
          </transition-group>

          <button type="submit" class="btn-primary" :disabled="isLoading">
            <span v-if="!isLoading">{{ isLogin ? 'Entrar na Plataforma' : 'Finalizar Cadastro' }}</span>
            <div v-else class="spinner-loader"></div>
          </button>
        </form>

        <div class="auth-footer">
          <span>{{ isLogin ? 'Ainda não tem conta?' : 'Já possui conta?' }}</span>
          <button type="button" class="toggle-link" @click="toggleMode">
            {{ isLogin ? 'Cadastre-se grátis' : 'Faça login aqui' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Container de Fundo Completo */
.auth-page-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f1f5f9;
  position: relative;
  overflow: hidden;
  padding: 1.5rem;
  font-family: 'Inter', system-ui, sans-serif;
}

/* Background com Animações Fluidas Orgânicas */
.animated-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 1;
}
.blob {
  position: absolute;
  background: linear-gradient(135deg, rgba(20, 184, 166, 0.25) 0%, rgba(15, 118, 110, 0.2) 100%);
  border-radius: 50%;
  filter: blur(60px);
  animation: floatBlobs 12s infinite alternate ease-in-out;
}
.blob-1 {
  width: 500px;
  height: 500px;
  top: -10%;
  right: -5%;
}
.blob-2 {
  width: 450px;
  height: 450px;
  bottom: -10%;
  left: -5%;
  animation-delay: -4s;
}

@keyframes floatBlobs {
  0% { transform: translateY(0) scale(1) rotate(0deg); }
  100% { transform: translateY(50px) scale(1.1) rotate(45deg); }
}

/* Wrapper Principal */
.auth-wrapper {
  display: flex;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  width: 100%;
  max-width: 1020px;
  min-height: 640px;
  border-radius: 28px;
  box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.08), 0 0 0 1px rgba(226, 232, 240, 0.8);
  overflow: hidden;
  z-index: 2;
  animation: wrapperEntrance 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes wrapperEntrance {
  from { opacity: 0; transform: translateY(30px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* Painel de Branding */
.auth-brand {
  flex: 1.1;
  background: linear-gradient(135deg, #14B8A6 0%, #0F766E 100%);
  padding: 3.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
  position: relative;
  overflow: hidden;
}
.auth-brand::before {
  content: '';
  position: absolute;
  bottom: -60px;
  right: -60px;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, transparent 75%);
  border-radius: 50%;
}
.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: -0.03em;
}
.brand-main-text h2 {
  font-size: 2.4rem;
  font-weight: 800;
  line-height: 1.25;
  margin-bottom: 1.2rem;
  letter-spacing: -0.02em;
}
.brand-main-text p {
  font-size: 1.1rem;
  opacity: 0.9;
  line-height: 1.6;
  font-weight: 400;
}

/* Container do Formulário */
.auth-form-container {
  flex: 1;
  padding: 4rem 3.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #ffffff;
}
.form-header {
  margin-bottom: 2.2rem;
}
.form-header h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}
.form-header p {
  color: #64748b;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Grupos de Inputs Premium */
.form-group {
  margin-bottom: 1.4rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  font-size: 0.88rem;
  color: #1e293b;
}
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 14px;
  width: 20px;
  height: 20px;
  color: #94a3b8;
  transition: color 0.25s ease;
  pointer-events: none;
}
.form-control {
  width: 100%;
  padding: 14px 14px 14px 44px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  font-size: 0.98rem;
  color: #0f172a;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.form-control:focus {
  outline: none;
  border-color: #14B8A6;
  background-color: #ffffff;
  box-shadow: 0 0 0 4px rgba(20, 184, 166, 0.12);
}
.form-control:focus + .input-icon {
  color: #14B8A6;
}

/* Seletor de Perfil Moderno (Cards Horizontais) */
.profile-cards-selector {
  display: flex;
  gap: 12px;
  width: 100%;
  margin-top: 0.25rem;
}
.profile-selector-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}
.profile-selector-card:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
}
.profile-selector-card.selected {
  border-color: #14B8A6;
  background: rgba(20, 184, 166, 0.05);
}
.selector-circle {
  width: 18px;
  height: 18px;
  border: 2px solid #cbd5e1;
  border-radius: 50%;
  position: relative;
  transition: all 0.2s ease;
}
.profile-selector-card.selected .selector-circle {
  border-color: #14B8A6;
}
.profile-selector-card.selected .selector-circle::after {
  content: '';
  position: absolute;
  width: 10px;
  height: 10px;
  background: #14B8A6;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
.profile-selector-card span {
  font-size: 0.92rem;
  font-weight: 600;
  color: #334155;
}
.profile-selector-card.selected span {
  color: #0f766e;
}

/* Botão de Ação Principal */
.btn-primary {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #14B8A6 0%, #0F766E 100%);
  color: #ffffff;
  border: none;
  border-radius: 14px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(20, 184, 166, 0.25);
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 1.8rem;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(20, 184, 166, 0.35);
}
.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}
.btn-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* Spinner animado interno do botão */
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

/* Rodapé de Alternância */
.auth-footer {
  margin-top: 2.2rem;
  text-align: center;
  font-size: 0.95rem;
  color: #64748b;
}
.toggle-link {
  color: #0F766E;
  cursor: pointer;
  background: transparent;
  border: none;
  font-weight: 700;
  font-size: 0.95rem;
  margin-left: 6px;
  transition: color 0.2s ease;
}
.toggle-link:hover {
  color: #14B8A6;
  text-decoration: underline;
}

/* Animações de Entrada dos Campos Condicionais */
.form-slide-enter-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.form-slide-leave-active {
  transition: all 0.25s ease;
}
.form-slide-enter-from {
  opacity: 0;
  transform: translateY(-15px);
}
.form-slide-leave-to {
  opacity: 0;
  transform: translateY(-15px);
}

/* Estilização do Toast Customizado */
.toast-notification {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 1000;
  background: #ffffff;
  padding: 16px 24px;
  border-radius: 16px;
  box-shadow: 0 12px 30px -5px rgba(15, 23, 42, 0.15);
  border-left: 5px solid #14B8A6;
  transform: translateX(120%);
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-notification.show {
  transform: translateX(0);
}
.toast-notification.error {
  border-left-color: #ef4444;
}
.toast-notification.success {
  border-left-color: #10b981;
}
.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  color: #1e293b;
}
.toast-icon {
  width: 20px;
  height: 20px;
}
.toast-notification.success .toast-icon { color: #10b981; }
.toast-notification.error .toast-icon { color: #ef4444; }

/* Responsividade Adaptativa */
@media (max-width: 900px) {
  .auth-wrapper {
    flex-direction: column;
    max-width: 460px;
    min-height: auto;
  }
  .auth-brand {
    padding: 2.5rem 2rem;
  }
  .brand-main-text h2 {
    font-size: 1.8rem;
  }
  .brand-main-text p {
    font-size: 0.98rem;
  }
  .auth-form-container {
    padding: 3rem 2rem;
  }
}
</style>