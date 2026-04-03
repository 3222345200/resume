<template>
  <section class="editor-card preview-card live-preview-card">
    <div class="live-preview-toolbar">
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
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  previewUrl: {
    type: String,
    default: '',
  },
})

const zoomScale = ref(1)

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

watch(
  () => props.previewUrl,
  () => {
    zoomScale.value = 1
  },
)
</script>
