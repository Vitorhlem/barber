import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import PetDetailsView from '../views/PetDetailsView.vue'
import PetFormView from '../views/PetFormView.vue'
import SettingsView from '../views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login', name: 'login', component: LoginView },
    { path: '/', name: 'dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/pet/:id', name: 'pet-details', component: PetDetailsView, meta: { requiresAuth: true } },
    { path: '/pet/new', name: 'pet-new', component: PetFormView, meta: { requiresAuth: true } },
    { path: '/pet/edit/:id', name: 'pet-edit', component: PetFormView, meta: { requiresAuth: true } },
    { path: '/settings', name: 'settings', component: SettingsView, meta: { requiresAuth: true } }
  ]
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated()) {
    next('/login')
  } else if (to.path === '/login' && auth.isAuthenticated()) {
    next('/')
  } else {
    next()
  }
})

export default router