<script setup lang="ts">
import { Bell, X, CheckCircle } from 'lucide-vue-next'

defineProps<{ message: string, visible: boolean }>()
const emit = defineEmits(['close'])
</script>

<template>
  <transition name="toast-slide">
    <div v-if="visible" class="toast-card">
      <div class="toast-icon bg-blue"><Bell :size="20" /></div>
      <div class="toast-body">
        <strong>Nova Atualização</strong>
        <p>{{ message }}</p>
      </div>
      <button class="toast-close" @click="emit('close')"><X :size="16" /></button>
    </div>
  </transition>
</template>

<style scoped>
.toast-card {
  position: fixed; top: 20px; right: 20px; z-index: 2000;
  background: white; padding: 1rem; border-radius: 16px;
  display: flex; align-items: flex-start; gap: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  border: 1px solid #e2e8f0; width: 320px;
}
.toast-icon { padding: 8px; border-radius: 8px; }
.bg-blue { background: #E0F2FE; color: #0284C7; }
.toast-body { flex: 1; }
.toast-body strong { font-size: 0.9rem; color: #0F172A; display: block; }
.toast-body p { font-size: 0.85rem; color: #475569; margin: 4px 0 0 0; }
.toast-close { border: none; background: none; cursor: pointer; color: #94A3B8; }

.toast-slide-enter-active, .toast-slide-leave-active { transition: all 0.3s ease; }
.toast-slide-enter-from, .toast-slide-leave-to { transform: translateX(100%); opacity: 0; }
</style>