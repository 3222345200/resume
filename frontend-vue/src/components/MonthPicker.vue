<template>
  <div
    ref="pickerRoot"
    class="month-picker-wrap"
  >
    <button type="button" class="month-picker-trigger" @click="togglePanel">
      <span>{{ displayText }}</span>
      <span class="month-picker-arrow" :class="{ open: panelOpen }" aria-hidden="true"></span>
    </button>

    <div v-if="panelOpen" class="month-picker-panel">
      <div class="month-picker-head">
        <strong>{{ panelYear }}年</strong>
        <div class="month-picker-navs">
          <button type="button" class="month-picker-nav-btn" :disabled="panelYear <= startYear" @click="panelYear -= 1">‹</button>
          <button type="button" class="month-picker-nav-btn" :disabled="panelYear >= endYear" @click="panelYear += 1">›</button>
        </div>
      </div>

      <div class="month-picker-grid">
        <button
          v-for="month in 12"
          :key="month"
          type="button"
          class="month-picker-option"
          :class="{ active: isMonthActive(month) }"
          @click="chooseMonth(month)"
        >
          {{ month }}月
        </button>
      </div>

      <div class="month-picker-actions">
        <button
          v-if="allowPresent"
          type="button"
          class="month-present-btn"
          :class="{ active: isPresent }"
          @click="togglePresent"
        >
          至今
        </button>
        <button type="button" class="month-picker-clear" @click="clearValue">清空</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  allowPresent: {
    type: Boolean,
    default: false,
  },
  startYear: {
    type: Number,
    default: 1990,
  },
  endYear: {
    type: Number,
    default: 2035,
  },
})

const emit = defineEmits(['update:modelValue'])

const pickerRoot = ref(null)
const panelOpen = ref(false)
const panelYear = ref(new Date().getFullYear())

const isPresent = computed(() => props.modelValue === '至今')

const selectedYear = computed(() => {
  if (!props.modelValue || isPresent.value) {
    return ''
  }
  return props.modelValue.split('.')[0] || ''
})

const selectedMonth = computed(() => {
  if (!props.modelValue || isPresent.value) {
    return ''
  }
  return props.modelValue.split('.')[1] || ''
})

const displayText = computed(() => {
  if (isPresent.value) {
    return '至今'
  }
  if (selectedYear.value && selectedMonth.value) {
    return `${selectedYear.value}年${Number(selectedMonth.value)}月`
  }
  return '选择年月'
})

watch(
  () => props.modelValue,
  () => {
    if (selectedYear.value) {
      panelYear.value = Number(selectedYear.value)
    }
  },
  { immediate: true },
)

function togglePanel() {
  if (selectedYear.value) {
    panelYear.value = Number(selectedYear.value)
  }
  panelOpen.value = !panelOpen.value
}

function isMonthActive(month) {
  return !isPresent.value && selectedYear.value === String(panelYear.value) && selectedMonth.value === String(month).padStart(2, '0')
}

function chooseMonth(month) {
  emit('update:modelValue', `${panelYear.value}.${String(month).padStart(2, '0')}`)
  panelOpen.value = false
}

function clearValue() {
  emit('update:modelValue', '')
  panelOpen.value = false
}

function togglePresent() {
  emit('update:modelValue', isPresent.value ? '' : '至今')
  panelOpen.value = false
}

function handleDocumentClick(event) {
  if (!pickerRoot.value?.contains(event.target)) {
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
