<template>
  <div ref="pickerRoot" class="color-picker" :class="{ open: panelOpen }">
    <button type="button" class="color-picker-trigger" @mousedown.prevent @click="togglePanel">
      <span class="color-picker-swatch" :style="{ background: safeColorValue }"></span>
    </button>

    <Teleport to="body">
      <div
        v-if="panelOpen"
        ref="panelRef"
        class="color-picker-panel"
        :style="panelStyle"
      >
        <div class="color-picker-grid">
          <button
            v-for="colorItem in presetColors"
            :key="colorItem"
            type="button"
            class="color-picker-option"
            :class="{ active: colorItem.toLowerCase() === safeColorValue }"
            :style="{ background: colorItem }"
            :aria-label="colorItem"
            @mousedown.prevent
            @click="chooseColor(colorItem)"
          ></button>
        </div>
      </div>
    </Teleport>
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
]

const panelOpen = ref(false)
const pickerRoot = ref(null)
const panelRef = ref(null)
const draftColorValue = ref(normalizeColor(props.modelValue))
const panelStyle = ref({})

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
    updatePanelPosition()
  }
}

function chooseColor(colorValue) {
  const nextValue = normalizeColor(colorValue)
  draftColorValue.value = nextValue
  emit('update:modelValue', nextValue)
  panelOpen.value = false
}

function updatePanelPosition() {
  const trigger = pickerRoot.value?.querySelector('.color-picker-trigger')
  if (!trigger) {
    return
  }

  const rect = trigger.getBoundingClientRect()
  const panelWidth = 180
  const gap = 8
  const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0
  const left = Math.max(12, Math.min(rect.left, viewportWidth - panelWidth - 12))

  panelStyle.value = {
    position: 'fixed',
    top: `${rect.bottom + gap}px`,
    left: `${left}px`,
    width: `${panelWidth}px`,
    zIndex: '10000',
  }
}

function commitDraftColor() {
  const normalizedValue = normalizeColor(draftColorValue.value)
  draftColorValue.value = normalizedValue
  emit('update:modelValue', normalizedValue)
}

function handleDocumentClick(event) {
  if (!pickerRoot.value?.contains(event.target) && !panelRef.value?.contains(event.target)) {
    panelOpen.value = false
    commitDraftColor()
  }
}

function handleWindowResize() {
  if (!panelOpen.value) {
    return
  }
  updatePanelPosition()
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  window.addEventListener('resize', handleWindowResize)
  window.addEventListener('scroll', handleWindowResize, true)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
  window.removeEventListener('resize', handleWindowResize)
  window.removeEventListener('scroll', handleWindowResize, true)
})
</script>
