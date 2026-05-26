<template>
  <q-layout view="hHh lpR fFf" class="landing-layout">
    <q-page-container>
      <q-page class="flex flex-center text-center q-pa-md">
        <div style="max-width: 800px; width: 100%;">
          
          <div class="q-mb-xl">
            <q-icon name="content_cut" size="80px" color="primary" class="shadow-icon" />
          </div>

          <h1 class="text-h2 text-weight-bolder text-dark q-mb-md letter-spacing">
            A Solução Completa para a sua <span class="text-primary">Barbearia</span>
          </h1>
          
          <p class="text-h5 text-grey-7 q-mb-xl text-weight-medium" style="line-height: 1.5;">
            Otimize o seu tempo, organize a sua agenda e ofereça uma experiência de marcação premium aos seus clientes, 24h por dia.
          </p>

          <div class="row justify-center q-gutter-md q-mb-xl">
            <q-btn 
              color="primary" 
              size="xl" 
              label="Quero uma Demonstração" 
              icon-right="arrow_forward"
              unelevated 
              no-caps 
              class="action-btn shadow-4 q-px-xl"
              href="mailto:seu-email@exemplo.com"
            />
          </div>

          <div class="row q-col-gutter-lg q-mt-xl justify-center">
            <div class="col-12 col-md-4">
              <q-card flat class="bg-transparent">
                <q-icon name="schedule" size="48px" color="primary" class="q-mb-sm" />
                <div class="text-h6 text-weight-bold">Agenda Automática</div>
                <div class="text-grey-7">Sem mais interrupções para atender o telefone. O seu cliente marca sozinho.</div>
              </q-card>
            </div>
            <div class="col-12 col-md-4">
              <q-card flat class="bg-transparent">
                <q-icon name="security" size="48px" color="primary" class="q-mb-sm" />
                <div class="text-h6 text-weight-bold">Link Exclusivo</div>
                <div class="text-grey-7">O sistema roda com o nome da sua barbearia no link, isolado e seguro.</div>
              </q-card>
            </div>
            <div class="col-12 col-md-4">
              <q-card flat class="bg-transparent">
                <q-icon name="sync" size="48px" color="primary" class="q-mb-sm" />
                <div class="text-h6 text-weight-bold">Integração Google</div>
                <div class="text-grey-7">Tudo sincronizado automaticamente com o seu Google Calendar pessoal.</div>
              </q-card>
            </div>
          </div>
          
        </div>

      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
// Nenhuma lógica pesada necessária para a Landing Page
</script>

<style scoped>
.landing-layout {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  min-height: 100vh;
}
.letter-spacing {
  letter-spacing: -1.5px;
}
.shadow-icon {
  filter: drop-shadow(0 4px 6px rgba(37, 99, 235, 0.2));
}
.action-btn {
  border-radius: 12px;
  font-weight: 700;
  transition: transform 0.2s;
}
.action-btn:hover {
  transform: translateY(-3px);
}
</style>