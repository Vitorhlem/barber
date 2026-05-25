import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import AgendamentoFormView from '../views/AgendamentoFormView.vue'
import AgendamentoDetailsView from '../views/AgendamentoDetailsView.vue'
import SettingsView from '../views/SettingsView.vue' // <--- IMPORTADO

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requerAutenticacao: true }
    },
    {
      path: '/agendamento/novo',
      name: 'novo-agendamento',
      component: AgendamentoFormView,
      meta: { requerAutenticacao: true }
    },
    {
      path: '/agendamento/:id',
      name: 'detalhes-agendamento',
      component: AgendamentoDetailsView,
      meta: { requerAutenticacao: true }
    },
    {
      path: '/produtos',
      name: 'produtos',
      component: () => import('../views/ProdutosView.vue')
    },
    {
      path: '/settings', // <--- ROTA ADICIONADA
      name: 'settings',
      component: SettingsView,
      meta: { requerAutenticacao: true }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard'
    }
  ]
})

router.beforeEach((to, from) => {
  const authStore = useAuthStore()
  
  if (to.meta.requerAutenticacao && !authStore.isAuthenticated()) {
    return '/login'
  }
})

export default router