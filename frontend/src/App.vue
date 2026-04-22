<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'

const route = useRoute()
const showAppHeader = computed(() => Boolean(route.meta.requiresAuth))
</script>

<template>
  <div class="app-shell">
    <AppHeader v-if="showAppHeader" />
    <div class="app-content">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.app-content {
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden;
}
</style>
