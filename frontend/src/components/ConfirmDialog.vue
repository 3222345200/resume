<template>
  <div v-if="open" class="confirm-dialog-mask" @click.self="$emit('cancel')">
    <section class="confirm-dialog-card" role="dialog" aria-modal="true" :aria-label="title">
      <p class="eyebrow confirm-dialog-eyebrow">{{ eyebrow }}</p>
      <h3 class="confirm-dialog-title">{{ title }}</h3>
      <p class="confirm-dialog-message">{{ message }}</p>

      <div class="confirm-dialog-actions">
        <button v-if="showCancel" type="button" class="ghost-button confirm-dialog-cancel" @click="$emit('cancel')">
          {{ cancelText }}
        </button>
        <button type="button" class="primary-button confirm-dialog-confirm" @click="$emit('confirm')">
          {{ confirmText }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
defineProps({
  eyebrow: {
    type: String,
    default: 'Confirm',
  },
  open: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '确认操作',
  },
  message: {
    type: String,
    default: '这个操作执行后无法撤销，确认继续吗？',
  },
  confirmText: {
    type: String,
    default: '确认删除',
  },
  cancelText: {
    type: String,
    default: '取消',
  },
  showCancel: {
    type: Boolean,
    default: true,
  },
})

defineEmits(['confirm', 'cancel'])
</script>
