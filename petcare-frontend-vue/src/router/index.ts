import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import AgendamentoFormView from '../views/AgendamentoFormView.vue'
import AgendamentoDetailsView from '../views/AgendamentoDetailsView.vue'
import SettingsView from '../views/SettingsView.vue'
// NOVO: Importamos a HomeView
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 0. Rota Raiz (Página de Vendas / Portfolio)
    {
      path: '/',
      name: 'home',
      component: HomeView
    },

    // 1. Rota global para o Dono do Sistema (Super Admin)
    {
      path: '/admin/lojas',
      name: 'super-admin',
      component: () => import('../views/SuperAdminView.vue'), 
      meta: { requerSuperAdmin: true }
    },

    // 2. Rotas Dinâmicas por Barbearia (Inquilino)
    {
      path: '/:slug/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/:slug/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requerAutenticacao: true }
    },
    {
      path: '/:slug/agendamento/novo',
      name: 'novo-agendamento',
      component: AgendamentoFormView,
      meta: { requerAutenticacao: true }
    },
    {
      path: '/:slug/agendamento/:id',
      name: 'detalhes-agendamento',
      component: AgendamentoDetailsView,
      meta: { requerAutenticacao: true }
    },
    {
      path: '/:slug/estatisticas',
      name: 'estatisticas',
      component: () => import('../views/EstatisticasView.vue'),
      meta: { requerAutenticacao: true }
    },
    {
      path: '/:slug/produtos',
      name: 'produtos',
      component: () => import('../views/ProdutosView.vue'),
      meta: { requerAutenticacao: true }
    },
    {
      path: '/:slug/settings',
      name: 'settings',
      component: SettingsView,
      meta: { requerAutenticacao: true }
    },

    // 3. Rota de fallback (404)
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      // Agora, qualquer rota inválida ou sem slug (ex: /qualquer-coisa) vai para a página inicial
      redirect: '/' 
    }
  ]
})

router.beforeEach((to, from) => {
  const authStore = useAuthStore()
  
  if (to.meta.requerSuperAdmin && !authStore.isSuperAdmin()) {
    if (authStore.barbeariaSlug) {
      return `/${authStore.barbeariaSlug}/dashboard`
    }
    return false 
  }
  
  if (to.meta.requerAutenticacao && !authStore.isAuthenticated()) {
    const slugParam = to.params.slug
    const slug = Array.isArray(slugParam) ? slugParam[0] : slugParam
    
    if (slug) {
      return `/${slug}/login`
    }
    
    return false 
  }
})

export default router