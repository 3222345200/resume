<template>
  <div ref="selectRoot" class="custom-select" :class="{ open: panelOpen }">
    <button type="button" class="custom-select-trigger" @click="togglePanel">
      <span class="custom-select-value" :style="selectedOptionStyle">{{ selectedLabel }}</span>
      <span class="custom-select-arrow" aria-hidden="true"></span>
    </button>

    <Teleport to="body">
      <div v-if="panelOpen" ref="panelRef" class="custom-select-panel custom-select-panel-teleport" :style="panelStyle">
        <button
          v-for="option in options"
          :key="String(option.value)"
          type="button"
          class="custom-select-option"
          :class="{ active: option.value === modelValue }"
          :style="getOptionStyle(option)"
          @click="chooseOption(option.value)"
        >
          {{ option.label }}
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'

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
const panelRef = ref(null)
const panelStyle = ref({})

const selectedLabel = computed(() => {
  const selectedOption = props.options.find((option) => option.value === props.modelValue)
  return selectedOption?.label || props.placeholder
})

const selectedOptionStyle = computed(() => {
  const selectedOption = props.options.find((option) => option.value === props.modelValue)
  return getOptionStyle(selectedOption)
})

function getOptionStyle(option) {
  if (!option?.fontFamily) {
    return {}
  }
  return {
    fontFamily: option.fontFamily,
  }
}

function updatePanelPosition() {
  if (!selectRoot.value) {
    return
  }
  const rect = selectRoot.value.getBoundingClientRect()
  panelStyle.value = {
    position: 'fixed',
    top: `${rect.bottom + 8}px`,
    left: `${rect.left}px`,
    width: `${rect.width}px`,
  }
}

async function togglePanel() {
  panelOpen.value = !panelOpen.value
  if (panelOpen.value) {
    await nextTick()
    updatePanelPosition()
  }
}

function chooseOption(value) {
  emit('update:modelValue', value)
  panelOpen.value = false
}

function handleDocumentClick(event) {
  if (!selectRoot.value?.contains(event.target) && !panelRef.value?.contains(event.target)) {
    panelOpen.value = false
  }
}

function handleViewportChange() {
  if (panelOpen.value) {
    updatePanelPosition()
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  window.addEventListener('resize', handleViewportChange)
  window.addEventListener('scroll', handleViewportChange, true)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
  window.removeEventListener('resize', handleViewportChange)
  window.removeEventListener('scroll', handleViewportChange, true)
})
</script>
