<template>
  <section class="editor-card preview-card live-preview-card">
    <div class="live-preview-toolbar">
      <button class="preview-zoom-btn" type="button" :disabled="zoomScale <= minZoom" @click="zoomOut">-</button>
      <span class="preview-zoom-text">{{ Math.round(zoomScale * 100) }}%</span>
      <button class="preview-zoom-btn" type="button" :disabled="zoomScale >= maxZoom" @click="zoomIn">+</button>
      <button class="preview-zoom-reset" type="button" @click="resetZoom">{{ isMobileViewport ? '适配' : '重置' }}</button>
    </div>

    <div v-if="previewUrl" class="live-preview-viewport" :class="{ 'is-mobile-fit': isMobileViewport }">
      <div class="live-preview-stage" :class="{ 'is-mobile-fit': isMobileViewport }">
        <iframe
          class="resume-preview-frame live-preview-frame"
          :src="previewUrl"
          :style="previewFrameStyle"
          title="简历预览"
        ></iframe>
      </div>
    </div>

    <div v-else class="preview-empty-state live-preview-empty">保存或下载 PDF 后，这里会显示简历预览。</div>
  </section>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const MOBILE_BREAKPOINT = 768
const MOBILE_DEFAULT_ZOOM = 0.6
const DESKTOP_DEFAULT_ZOOM = 1
const MOBILE_MIN_ZOOM = 0.4
const DESKTOP_MIN_ZOOM = 0.6
const MAX_ZOOM = 1.8

const props = defineProps({
  previewUrl: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['navigate-section'])

const isMobileViewport = ref(false)
const zoomScale = ref(DESKTOP_DEFAULT_ZOOM)

const minZoom = computed(() => (isMobileViewport.value ? MOBILE_MIN_ZOOM : DESKTOP_MIN_ZOOM))
const maxZoom = MAX_ZOOM

const previewFrameStyle = computed(() => {
  const scale = zoomScale.value
  return {
    width: `${100 / scale}%`,
    height: `${100 / scale}%`,
    transform: `scale(${scale})`,
  }
})

function getDefaultZoom() {
  return isMobileViewport.value ? MOBILE_DEFAULT_ZOOM : DESKTOP_DEFAULT_ZOOM
}

function syncViewportMode() {
  isMobileViewport.value = window.innerWidth <= MOBILE_BREAKPOINT
}

function zoomIn() {
  zoomScale.value = Math.min(maxZoom, Number((zoomScale.value + 0.1).toFixed(1)))
}

function zoomOut() {
  zoomScale.value = Math.max(minZoom.value, Number((zoomScale.value - 0.1).toFixed(1)))
}

function resetZoom() {
  zoomScale.value = getDefaultZoom()
}

function getPreviewIdentity(previewUrl) {
  return String(previewUrl || '').split('?')[0]
}

function handlePreviewMessage(event) {
  const message = event?.data
  if (!message || message.type !== 'resume-preview-section-dblclick') {
    return
  }
  const sectionKey = String(message.sectionKey || '').trim()
  if (!sectionKey) {
    return
  }
  emit('navigate-section', sectionKey)
}

function handleResize() {
  const nextIsMobile = window.innerWidth <= MOBILE_BREAKPOINT
  if (nextIsMobile !== isMobileViewport.value) {
    isMobileViewport.value = nextIsMobile
    zoomScale.value = getDefaultZoom()
    return
  }
  syncViewportMode()
}

watch(
  () => props.previewUrl,
  (nextUrl, prevUrl) => {
    if (getPreviewIdentity(nextUrl) !== getPreviewIdentity(prevUrl)) {
      zoomScale.value = getDefaultZoom()
    }
  },
)

onMounted(() => {
  syncViewportMode()
  zoomScale.value = getDefaultZoom()
  window.addEventListener('message', handlePreviewMessage)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('message', handlePreviewMessage)
  window.removeEventListener('resize', handleResize)
})
</script>
