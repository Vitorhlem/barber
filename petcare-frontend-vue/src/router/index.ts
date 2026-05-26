import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import AgendamentoFormView from '../views/AgendamentoFormView.vue'
import AgendamentoDetailsView from '../views/AgendamentoDetailsView.vue'
import SettingsView from '../views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 1. Rota global para o Dono do Sistema (Super Admin)
    {
      path: '/admin/lojas',
      name: 'super-admin',
      // Você precisará criar essa view posteriormente:
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
      // Pode redirecionar para uma página principal de vendas do sistema ou 404 global
      redirect: '/admin/lojas' 
    }
  ]
})

router.beforeEach((to, from) => {
  const authStore = useAuthStore()
  
  // Lógica opcional para bloquear acesso se a rota for de super-admin
  // if (to.meta.requerSuperAdmin && !authStore.isSuperAdmin()) {
  //   return '/' 
  // }
  
  if (to.meta.requerAutenticacao && !authStore.isAuthenticated()) {
    // Como a URL agora é dinâmica, pegamos o parâmetro 'slug' da tentativa de acesso
    // e enviamos o usuário de volta para a tela de login exclusiva daquela loja
    const slug = to.params.slug
    if (slug) {
      return `/${slug}/login`
    }
    
    // Fallback caso acesse algo sem slug acidentalmente
    return '/login'
  }
})

export default router