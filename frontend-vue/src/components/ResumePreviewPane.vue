<template>
  <section class="editor-card preview-card live-preview-card">
    <iframe v-if="previewUrl" class="resume-preview-frame live-preview-frame" :src="previewUrl" title="简历预览"></iframe>
    <div v-else class="preview-empty-state live-preview-empty">保存或下载 PDF 后，这里会展示简历预览。</div>
  </section>
</template>

<script setup>
defineProps({
  previewUrl: {
    type: String,
    default: '',
  },
})
</script>
