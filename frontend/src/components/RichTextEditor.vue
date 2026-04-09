<template>
  <div class="rich-text-editor" :class="{ 'is-left-toolbar': toolbarMode === 'left' }">
    <div class="rich-text-toolbar">
      <button v-if="toolbarMode === 'left'" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="applyBlock('p')">T</button>
      <button v-if="toolbarMode === 'left'" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="applyBlock('h1')">H1</button>
      <button v-if="toolbarMode === 'left'" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="applyBlock('h2')">H2</button>
      <button v-if="toolbarMode === 'left'" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="applyBlock('h3')">H3</button>
      <button v-if="toolbarMode === 'left'" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="execCommand('insertOrderedList')">1.</button>
      <button v-if="toolbarMode === 'left'" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="execCommand('insertUnorderedList')">•</button>
      <button v-if="toolbarMode === 'left'" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="applyBlock('blockquote')">“</button>
      <button v-if="toolbarMode === 'left'" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="execCommand('removeFormat')">Tx</button>
      <span v-if="toolbarMode !== 'left'" class="rich-tool-divider"></span>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('undo')">撤销</button>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('redo')">重做</button>
      <span v-if="toolbarMode !== 'left'" class="rich-tool-divider"></span>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('bold')"><strong>B</strong></button>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('italic')"><em>I</em></button>
      <button v-if="toolbarMode !== 'left'" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('insertUnorderedList')">• 列表</button>
      <button v-if="toolbarMode !== 'left'" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('insertOrderedList')">1. 列表</button>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="insertLink">链接</button>
      <button v-if="toolbarMode !== 'left'" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('removeFormat')">清格式</button>
    </div>

    <div
      ref="editorRef"
      class="rich-text-surface"
      contenteditable="true"
      :data-placeholder="placeholder"
      @focus="captureSelection"
      @mouseup="captureSelection"
      @keyup="captureSelection"
      @input="handleEditorInput"
      @blur="handleEditorBlur"
      @paste.prevent="handlePaste"
    ></div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '请输入内容',
  },
  mode: {
    type: String,
    default: 'paragraphs',
  },
  toolbarMode: {
    type: String,
    default: 'top',
  },
})

const emit = defineEmits(['update:modelValue'])

const editorRef = ref(null)
const savedRange = ref(null)
const isComposing = ref(false)
const isApplyingCommand = ref(false)
const lastHtml = ref('')

const allowedTags = new Set(['P', 'DIV', 'BR', 'STRONG', 'B', 'EM', 'I', 'U', 'UL', 'OL', 'LI', 'A', 'H1', 'H2', 'H3', 'BLOCKQUOTE'])

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function plainTextToHtml(value) {
  const lines = String(value || '')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)

  if (!lines.length) {
    return ''
  }

  if (props.mode === 'list') {
    return `<ul>${lines.map((line) => `<li>${escapeHtml(line)}</li>`).join('')}</ul>`
  }

  return lines.map((line) => `<p>${escapeHtml(line)}</p>`).join('')
}

function normalizeInputHtml(value) {
  const text = String(value || '')
  if (!text.trim()) {
    return ''
  }
  if (/<[^>]+>/.test(text)) {
    return sanitizeHtml(text)
  }
  return plainTextToHtml(text)
}

function sanitizeNode(node) {
  if (node.nodeType === Node.TEXT_NODE) {
    return document.createTextNode(node.textContent || '')
  }

  if (node.nodeType !== Node.ELEMENT_NODE) {
    return document.createDocumentFragment()
  }

  if (!allowedTags.has(node.tagName)) {
    const fragment = document.createDocumentFragment()
    Array.from(node.childNodes).forEach((child) => {
      fragment.appendChild(sanitizeNode(child))
    })
    return fragment
  }

  const tagName = node.tagName === 'DIV' ? 'p' : node.tagName.toLowerCase()
  const element = document.createElement(tagName)

  if (node.tagName === 'A') {
    const href = node.getAttribute('href') || ''
    if (/^(https?:\/\/|mailto:)/i.test(href)) {
      element.setAttribute('href', href)
      element.setAttribute('target', '_blank')
      element.setAttribute('rel', 'noopener noreferrer')
    }
  }

  Array.from(node.childNodes).forEach((child) => {
    element.appendChild(sanitizeNode(child))
  })
  return element
}

function sanitizeHtml(html) {
  const template = document.createElement('template')
  template.innerHTML = String(html || '')
  const fragment = document.createDocumentFragment()
  Array.from(template.content.childNodes).forEach((child) => {
    fragment.appendChild(sanitizeNode(child))
  })
  const wrapper = document.createElement('div')
  wrapper.appendChild(fragment)
  return wrapper.innerHTML
}

function isSelectionInsideEditor(range) {
  const editor = editorRef.value
  if (!editor || !range) {
    return false
  }
  return editor.contains(range.startContainer) && editor.contains(range.endContainer)
}

function captureSelection() {
  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0) {
    return
  }
  const range = selection.getRangeAt(0)
  if (isSelectionInsideEditor(range)) {
    savedRange.value = range.cloneRange()
  }
}

function restoreSelection() {
  const editor = editorRef.value
  const range = savedRange.value
  if (!editor) {
    return
  }

  try {
    editor.focus({ preventScroll: true })
  } catch {
    editor.focus()
  }

  const selection = window.getSelection()
  if (!selection) {
    return
  }

  if (range && isSelectionInsideEditor(range)) {
    selection.removeAllRanges()
    selection.addRange(range)
    return
  }

  const fallbackRange = document.createRange()
  fallbackRange.selectNodeContents(editor)
  fallbackRange.collapse(false)
  selection.removeAllRanges()
  selection.addRange(fallbackRange)
  savedRange.value = fallbackRange.cloneRange()
}

function renderValueToDom(value) {
  const editor = editorRef.value
  if (!editor) {
    return
  }
  const nextHtml = normalizeInputHtml(value)
  if (editor.innerHTML !== nextHtml) {
    editor.innerHTML = nextHtml
  }
  lastHtml.value = nextHtml
  nextTick(() => {
    captureSelection()
  })
}

function emitCurrentValue() {
  const html = sanitizeHtml(editorRef.value?.innerHTML || '')
  lastHtml.value = html
  emit('update:modelValue', html)
}

function handleEditorInput() {
  if (isComposing.value || isApplyingCommand.value) {
    return
  }
  captureSelection()
  emitCurrentValue()
}

function handleEditorBlur() {
  captureSelection()
  emitCurrentValue()
}

async function execCommand(command, value = null) {
  isApplyingCommand.value = true
  restoreSelection()
  document.execCommand(command, false, value)
  captureSelection()
  emitCurrentValue()
  await nextTick()
  restoreSelection()
  isApplyingCommand.value = false
}

function applyBlock(tagName) {
  execCommand('formatBlock', tagName)
}

function insertLink() {
  restoreSelection()
  const selectedText = window.getSelection()?.toString().trim()
  const fallback = selectedText && /^(https?:\/\/|mailto:)/i.test(selectedText) ? selectedText : 'https://'
  const href = window.prompt('请输入链接地址', fallback)
  if (!href) {
    restoreSelection()
    return
  }
  execCommand('createLink', href)
}

function handlePaste(event) {
  restoreSelection()
  const text = event.clipboardData?.getData('text/plain') || ''
  if (!text) {
    return
  }
  document.execCommand('insertText', false, text)
  captureSelection()
  emitCurrentValue()
}

function handleSelectionChange() {
  if (document.activeElement === editorRef.value) {
    captureSelection()
  }
}

watch(
  () => props.modelValue,
  (value) => {
    const nextHtml = normalizeInputHtml(value)
    if (nextHtml === lastHtml.value) {
      return
    }
    if (document.activeElement === editorRef.value) {
      return
    }
    renderValueToDom(value)
  },
)

onMounted(() => {
  renderValueToDom(props.modelValue)
  document.addEventListener('selectionchange', handleSelectionChange)
})

onUnmounted(() => {
  document.removeEventListener('selectionchange', handleSelectionChange)
})
</script>


