<template>
  <div ref="pickerRoot" class="date-time-picker" :class="{ open: panelOpen }">
    <button type="button" class="date-time-picker-trigger" @click="togglePanel">
      <span>{{ displayText }}</span>
      <span class="date-time-picker-arrow" :class="{ open: panelOpen }" aria-hidden="true"></span>
    </button>

    <Teleport to="body">
      <div v-if="panelOpen" ref="panelRef" class="date-time-picker-panel date-time-picker-panel-teleport" :style="panelStyle">
        <div class="date-time-picker-head">
          <strong>{{ panelYear }}年{{ panelMonth + 1 }}月</strong>
          <div class="date-time-picker-navs">
            <button type="button" class="date-time-picker-nav-btn" @click="moveMonth(-1)">‹</button>
            <button type="button" class="date-time-picker-nav-btn" @click="moveMonth(1)">›</button>
          </div>
        </div>

        <div class="date-time-picker-weekdays">
          <span v-for="weekday in weekdays" :key="weekday">{{ weekday }}</span>
        </div>

        <div class="date-time-picker-grid">
          <button
            v-for="cell in calendarCells"
            :key="cell.key"
            type="button"
            class="date-time-picker-day"
            :class="{
              'is-muted': !cell.currentMonth,
              'is-active': cell.active,
              'is-today': cell.today,
            }"
            @click="chooseDate(cell.date)"
          >
            {{ cell.label }}
          </button>
        </div>

        <div v-if="type === 'datetime-local'" class="date-time-picker-time-row">
          <label>
            <span>小时</span>
            <select v-model="selectedHour">
              <option v-for="hour in hourOptions" :key="hour" :value="hour">{{ hour }}</option>
            </select>
          </label>
          <label>
            <span>分钟</span>
            <select v-model="selectedMinute">
              <option v-for="minute in minuteOptions" :key="minute" :value="minute">{{ minute }}</option>
            </select>
          </label>
        </div>

        <div class="date-time-picker-actions">
          <button type="button" class="date-time-picker-clear" @click="clearValue">清空</button>
          <button type="button" class="date-time-picker-apply" @click="applyValue">完成</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  type: {
    type: String,
    default: 'date',
  },
  placeholder: {
    type: String,
    default: '选择时间',
  },
})

const emit = defineEmits(['update:modelValue'])

const weekdays = ['一', '二', '三', '四', '五', '六', '日']
const hourOptions = Array.from({ length: 24 }, (_, index) => String(index).padStart(2, '0'))
const minuteOptions = Array.from({ length: 60 }, (_, index) => String(index).padStart(2, '0'))

const pickerRoot = ref(null)
const panelRef = ref(null)
const panelOpen = ref(false)
const panelStyle = ref({})
const panelYear = ref(new Date().getFullYear())
const panelMonth = ref(new Date().getMonth())
const selectedDate = ref(null)
const selectedHour = ref('09')
const selectedMinute = ref('00')

const displayText = computed(() => {
  if (!props.modelValue) {
    return props.placeholder
  }
  const parsed = parseValue(props.modelValue)
  if (!parsed) {
    return props.modelValue
  }
  const year = parsed.getFullYear()
  const month = parsed.getMonth() + 1
  const day = parsed.getDate()
  if (props.type === 'datetime-local') {
    const hours = String(parsed.getHours()).padStart(2, '0')
    const minutes = String(parsed.getMinutes()).padStart(2, '0')
    return `${year}年${month}月${day}日 ${hours}:${minutes}`
  }
  return `${year}年${month}月${day}日`
})

const calendarCells = computed(() => {
  const firstDay = new Date(panelYear.value, panelMonth.value, 1)
  const startWeekday = (firstDay.getDay() + 6) % 7
  const startDate = new Date(panelYear.value, panelMonth.value, 1 - startWeekday)
  const cells = []

  for (let index = 0; index < 42; index += 1) {
    const cellDate = new Date(startDate)
    cellDate.setDate(startDate.getDate() + index)
    cells.push({
      key: `${cellDate.getFullYear()}-${cellDate.getMonth()}-${cellDate.getDate()}`,
      label: cellDate.getDate(),
      date: cellDate,
      currentMonth: cellDate.getMonth() === panelMonth.value,
      active: isSameDay(cellDate, selectedDate.value),
      today: isSameDay(cellDate, new Date()),
    })
  }

  return cells
})

watch(
  () => props.modelValue,
  (value) => {
    const parsed = parseValue(value)
    selectedDate.value = parsed
    if (parsed) {
      panelYear.value = parsed.getFullYear()
      panelMonth.value = parsed.getMonth()
      selectedHour.value = String(parsed.getHours()).padStart(2, '0')
      selectedMinute.value = String(parsed.getMinutes()).padStart(2, '0')
    }
  },
  { immediate: true },
)

function parseValue(value) {
  if (!value) {
    return null
  }
  if (props.type === 'date') {
    const matched = String(value).match(/^(\d{4})-(\d{2})-(\d{2})$/)
    if (!matched) {
      return null
    }
    return new Date(Number(matched[1]), Number(matched[2]) - 1, Number(matched[3]), 0, 0, 0, 0)
  }
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

function isSameDay(left, right) {
  if (!left || !right) {
    return false
  }
  return left.getFullYear() === right.getFullYear() && left.getMonth() === right.getMonth() && left.getDate() === right.getDate()
}

function updatePanelPosition() {
  if (!pickerRoot.value) {
    return
  }
  const rect = pickerRoot.value.getBoundingClientRect()
  const panelWidth = 336
  const panelHeight = props.type === 'datetime-local' ? 420 : 360
  const openAbove = window.innerHeight - rect.bottom < panelHeight + 16 && rect.top > panelHeight
  panelStyle.value = {
    position: 'fixed',
    top: openAbove ? `${Math.max(12, rect.top - panelHeight - 8)}px` : `${rect.bottom + 8}px`,
    left: `${Math.max(12, Math.min(rect.left, window.innerWidth - 360))}px`,
    width: `${panelWidth}px`,
  }
}

async function togglePanel() {
  panelOpen.value = !panelOpen.value
  if (panelOpen.value) {
    await nextTick()
    updatePanelPosition()
  }
}

function moveMonth(offset) {
  const next = new Date(panelYear.value, panelMonth.value + offset, 1)
  panelYear.value = next.getFullYear()
  panelMonth.value = next.getMonth()
}

function chooseDate(date) {
  selectedDate.value = new Date(date)
  panelYear.value = selectedDate.value.getFullYear()
  panelMonth.value = selectedDate.value.getMonth()
  if (props.type === 'date') {
    applyValue()
  }
}

function applyValue() {
  if (!selectedDate.value) {
    emit('update:modelValue', '')
    panelOpen.value = false
    return
  }

  const nextValue = new Date(selectedDate.value)
  nextValue.setHours(Number(selectedHour.value), Number(selectedMinute.value), 0, 0)

  if (props.type === 'date') {
    emit('update:modelValue', `${nextValue.getFullYear()}-${String(nextValue.getMonth() + 1).padStart(2, '0')}-${String(nextValue.getDate()).padStart(2, '0')}`)
  } else {
    emit('update:modelValue', nextValue.toISOString())
  }
  panelOpen.value = false
}

function clearValue() {
  selectedDate.value = null
  emit('update:modelValue', '')
  panelOpen.value = false
}

function handleDocumentClick(event) {
  if (!pickerRoot.value?.contains(event.target) && !panelRef.value?.contains(event.target)) {
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
