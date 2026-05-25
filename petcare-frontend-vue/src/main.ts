import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Importações do Quasar
import { Quasar, Notify, Dialog } from 'quasar'
import '@quasar/extras/material-icons/material-icons.css'
import 'quasar/src/css/index.sass'

import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Configuração Global do Quasar (White-Label Mágica)
app.use(Quasar, {
  plugins: {
    Notify, // Ativa o plugin de notificações nativas do Quasar
    Dialog  // Ativa o plugin de diálogos nativos do Quasar
  },
  config: {
    brand: {
      primary: '#111827',   // Sua cor principal Dark
      secondary: '#4b5563', // Tom de cinza
      accent: '#3b82f6',    // Azul para destaques
      dark: '#1d1d1d',
      positive: '#10b981',  // Verde sucesso
      negative: '#ef4444',  // Vermelho erro
      info: '#3b82f6',
      warning: '#f59e0b'
    }
  }
})

app.mount('#app')