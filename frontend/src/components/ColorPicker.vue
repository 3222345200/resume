<template>
  <div ref="pickerRoot" class="color-picker" :class="{ open: panelOpen }">
    <button type="button" class="color-picker-trigger" @click="togglePanel">
      <span class="color-picker-swatch" :style="{ background: safeColorValue }"></span>
    </button>

    <div v-if="panelOpen" class="color-picker-panel">
      <div class="color-picker-grid">
        <button
          v-for="colorItem in presetColors"
          :key="colorItem"
          type="button"
          class="color-picker-option"
          :class="{ active: colorItem.toLowerCase() === safeColorValue }"
          :style="{ background: colorItem }"
          :aria-label="colorItem"
          @click="chooseColor(colorItem)"
        ></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '#111111',
  },
})

const emit = defineEmits(['update:modelValue'])

const presetColors = [
  '#111111',
  '#374151',
  '#64748b',
  '#8f9d92',
  '#5f7669',
  '#7c6f64',
  '#9a6b5f',
  '#c65d1e',
  '#b45309',
  '#15803d',
  '#0f766e',
  '#1d4ed8',
  '#7c3aed',
  '#be185d',
  '#dc2626',
  '#ffffff',
]

const panelOpen = ref(false)
const pickerRoot = ref(null)
const draftColorValue = ref(normalizeColor(props.modelValue))

const safeColorValue = computed(() => normalizeColor(props.modelValue))

watch(
  () => props.modelValue,
  (nextValue) => {
    draftColorValue.value = normalizeColor(nextValue)
  },
)

function normalizeColor(colorValue) {
  const nextValue = String(colorValue || '').trim()
  if (/^#[0-9a-fA-F]{6}$/.test(nextValue)) {
    return nextValue.toLowerCase()
  }
  return '#111111'
}

function togglePanel() {
  panelOpen.value = !panelOpen.value
  if (panelOpen.value) {
    draftColorValue.value = safeColorValue.value
  }
}

function chooseColor(colorValue) {
  const nextValue = normalizeColor(colorValue)
  draftColorValue.value = nextValue
  emit('update:modelValue', nextValue)
  panelOpen.value = false
}

function commitDraftColor() {
  const normalizedValue = normalizeColor(draftColorValue.value)
  draftColorValue.value = normalizedValue
  emit('update:modelValue', normalizedValue)
}

function handleDocumentClick(event) {
  if (!pickerRoot.value?.contains(event.target)) {
    panelOpen.value = false
    commitDraftColor()
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>
