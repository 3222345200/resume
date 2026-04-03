<template>
  <div ref="selectRoot" class="custom-select" :class="{ open: panelOpen }">
    <button type="button" class="custom-select-trigger" @click="togglePanel">
      <span class="custom-select-value">{{ selectedLabel }}</span>
      <span class="custom-select-arrow" aria-hidden="true"></span>
    </button>

    <div v-if="panelOpen" class="custom-select-panel">
      <button
        v-for="option in options"
        :key="String(option.value)"
        type="button"
        class="custom-select-option"
        :class="{ active: option.value === modelValue }"
        @click="chooseOption(option.value)"
      >
        {{ option.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  options: {
    type: Array,
    default: () => [],
  },
  placeholder: {
    type: String,
    default: '请选择',
  },
})

const emit = defineEmits(['update:modelValue'])

const panelOpen = ref(false)
const selectRoot = ref(null)

const selectedLabel = computed(() => {
  const selectedOption = props.options.find((option) => option.value === props.modelValue)
  return selectedOption?.label || props.placeholder
})

function togglePanel() {
  panelOpen.value = !panelOpen.value
}

function chooseOption(value) {
  emit('update:modelValue', value)
  panelOpen.value = false
}

function handleDocumentClick(event) {
  if (!selectRoot.value?.contains(event.target)) {
    panelOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>
