<template>
  <q-layout view="hHh lpR fFf" class="catalog-layout">
    <q-header elevated class="catalog-header">
      <q-toolbar class="q-px-lg q-py-sm">
        <q-btn flat round icon="arrow_back" color="white" @click="router.push(`/${slug}/dashboard`)" />
        <q-toolbar-title class="text-weight-bold header-title q-ml-sm">
          Vitrine da Barbearia
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page padding class="catalog-page">
        <div style="max-width: 1200px; margin: 0 auto;">
          
          <div class="text-center q-mb-xl q-mt-lg">
            <div class="text-h3 text-weight-bolder text-primary letter-spacing">Nossos Produtos</div>
            <div class="text-subtitle1 text-grey-7 q-mt-sm">
              Descubra os itens exclusivos vendidos na nossa loja física.
            </div>
          </div>

          <div v-if="carregando" class="flex flex-center q-pa-xl">
            <q-spinner-tail color="primary" size="3em" />
          </div>

          <template v-else>
            <q-tabs
              v-model="categoriaAtiva"
              dense
              class="custom-tabs q-mb-xl"
              active-color="primary"
              indicator-color="primary"
              align="center"
              narrow-indicator
            >
              <q-tab name="Todos" label="Todos os Produtos" no-caps class="text-weight-bold" />
              <q-tab v-for="cat in categoriasUnicas" :key="cat" :name="cat" :label="cat" no-caps class="text-weight-bold" />
            </q-tabs>

            <div v-if="produtosFiltrados.length === 0" class="flex flex-center q-pa-xl shadow-2 empty-state">
              <q-icon name="inventory_2" size="72px" color="grey-4" />
              <div class="text-h6 text-grey-5 q-mt-md full-width text-center">Nenhum produto encontrado nesta categoria.</div>
            </div>

            <div class="row q-col-gutter-xl">
              <div class="col-12 col-sm-6 col-md-4 col-lg-3" v-for="produto in produtosFiltrados" :key="produto.id">
                <q-card class="product-card shadow-4">
                  <div class="product-image bg-grey-2 flex flex-center">
                    <q-img v-if="produto.imagem_url" :src="produto.imagem_url" fit="cover" style="height: 200px; width: 100%;" />
                    <q-icon v-else name="shopping_bag" size="64px" color="grey-4" />
                  </div>
                  
                  <q-card-section class="q-pa-md">
                    <q-chip color="primary" text-color="white" size="sm" class="text-weight-bold text-uppercase q-mb-sm shadow-1">
                      {{ produto.categoria }}
                    </q-chip>
                    <div class="text-h6 text-weight-bolder product-title ellipsis">{{ produto.nome }}</div>
                    <div class="text-body2 text-grey-6 q-mt-xs description-text">
                      {{ produto.descricao || 'Produto de alta qualidade disponível na loja.' }}
                    </div>
                    
                    <div class="row items-center justify-between q-mt-md">
                      <div class="text-h5 text-weight-bolder text-positive">R$ {{ produto.preco.toFixed(2) }}</div>
                      <q-icon name="storefront" color="grey-5" size="24px" title="Vendido no local" />
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </template>

        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const slug = route.params.slug as string // Captura o link dinâmico da loja

const produtos = ref<any[]>([])
const categoriaAtiva = ref('Todos')
const carregando = ref(true)

const fetchProdutos = async () => {
  try {
    const res = await fetch(`http://localhost:8000/${slug}/produtos/`)
    if (res.ok) {
      produtos.value = await res.json()
    }
  } catch (error) {
    console.error(error)
  } finally {
    carregando.value = false
  }
}

onMounted(() => {
  fetchProdutos()
})

const categoriasUnicas = computed(() => {
  const cats = produtos.value.map(p => p.categoria)
  return [...new Set(cats)].sort()
})

const produtosFiltrados = computed(() => {
  if (categoriaAtiva.value === 'Todos') return produtos.value
  return produtos.value.filter(p => p.categoria === categoriaAtiva.value)
})
</script>

<style scoped>
/* O seu estilo original permanece igual */
.catalog-layout {
  --cor-fundo-pagina: #f8fafc;
  --cor-header-inicio: #1e293b;
  --cor-header-fim: #0f172a;
}
.catalog-page { background-color: var(--cor-fundo-pagina); min-height: 100vh; }
.catalog-header { background: linear-gradient(135deg, var(--cor-header-inicio) 0%, var(--cor-header-fim) 100%); }
.letter-spacing { letter-spacing: -1px; }

.custom-tabs { color: #64748b; font-size: 1.1rem; }
.empty-state { border: 1px dashed #cbd5e1; background-color: white; border-radius: 16px; }

.product-card {
  border-radius: 16px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid #e2e8f0;
}
.product-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
  border-color: var(--q-primary);
}
.product-image {
  height: 200px;
  width: 100%;
  border-bottom: 1px solid #f1f5f9;
}
.product-title { color: #0f172a; line-height: 1.2; }
.description-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 40px;
}
</style>