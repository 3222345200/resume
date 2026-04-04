<template>
  <section class="editor-card preview-card live-preview-card" :class="{ 'is-collapsed': isPreviewCollapsed }">
    <button
      v-if="isCompactViewport && isPreviewCollapsed"
      class="mobile-preview-toggle"
      type="button"
      @click="isPreviewCollapsed = false"
    >
      展开预览
      <span class="mobile-preview-arrow" aria-hidden="true">∨</span>
    </button>

    <template v-else>
      <div class="live-preview-toolbar">
        <button
          v-if="isCompactViewport"
          class="mobile-preview-collapse-btn"
          type="button"
          @click="isPreviewCollapsed = true"
        >
          收起预览
        </button>
        <button class="preview-zoom-btn" type="button" :disabled="zoomScale <= 0.6" @click="zoomOut">-</button>
        <span class="preview-zoom-text">{{ Math.round(zoomScale * 100) }}%</span>
        <button class="preview-zoom-btn" type="button" :disabled="zoomScale >= 1.8" @click="zoomIn">+</button>
        <button class="preview-zoom-reset" type="button" @click="resetZoom">重置</button>
      </div>

      <div v-if="previewUrl" class="live-preview-viewport">
        <iframe
          class="resume-preview-frame live-preview-frame"
          :src="previewUrl"
          :style="previewFrameStyle"
          title="简历预览"
        ></iframe>
      </div>

      <div v-else class="preview-empty-state live-preview-empty">保存或下载 PDF 后，这里会展示简历预览。</div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  previewUrl: {
    type: String,
    default: '',
  },
})

const zoomScale = ref(1)
const isCompactViewport = ref(window.matchMedia('(max-width: 1400px)').matches)
const isPreviewCollapsed = ref(isCompactViewport.value)

const previewFrameStyle = computed(() => ({
  width: `${100 / zoomScale.value}%`,
  height: `${100 / zoomScale.value}%`,
  transform: `scale(${zoomScale.value})`,
}))

function zoomIn() {
  zoomScale.value = Math.min(1.8, Number((zoomScale.value + 0.1).toFixed(1)))
}

function zoomOut() {
  zoomScale.value = Math.max(0.6, Number((zoomScale.value - 0.1).toFixed(1)))
}

function resetZoom() {
  zoomScale.value = 1
}

function getPreviewIdentity(previewUrl) {
  return String(previewUrl || '').split('?')[0]
}

function syncPreviewCollapseByViewport() {
  isCompactViewport.value = window.matchMedia('(max-width: 1400px)').matches
  if (isCompactViewport.value) {
    isPreviewCollapsed.value = true
    return
  }
  isPreviewCollapsed.value = false
}

watch(
  () => props.previewUrl,
  (nextUrl, prevUrl) => {
    if (getPreviewIdentity(nextUrl) !== getPreviewIdentity(prevUrl)) {
      zoomScale.value = 1
    }
  },
)

onMounted(() => {
  window.addEventListener('resize', syncPreviewCollapseByViewport)
  syncPreviewCollapseByViewport()
})

onUnmounted(() => {
  window.removeEventListener('resize', syncPreviewCollapseByViewport)
})
</script>
