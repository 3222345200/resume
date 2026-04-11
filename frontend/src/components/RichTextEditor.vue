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
      <button v-if="toolbarMode !== 'left'" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="applyBlock('p')">正文</button>
      <button v-if="toolbarMode !== 'left'" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="applyBlock('h1')">H1</button>
      <button v-if="toolbarMode !== 'left'" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="applyBlock('h2')">H2</button>
      <button v-if="toolbarMode !== 'left'" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="applyBlock('h3')">H3</button>
      <span v-if="toolbarMode !== 'left'" class="rich-tool-divider"></span>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('undo')">撤销</button>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('redo')">重做</button>
      <span v-if="toolbarMode !== 'left'" class="rich-tool-divider"></span>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('bold')"><strong>B</strong></button>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('italic')"><em>I</em></button>
      <button v-if="toolbarMode !== 'left'" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="applyBlock('blockquote')">引用</button>
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
      @keydown="handleEditorKeydown"
      @focus="captureSelection"
      @mouseup="captureSelection"
      @keyup="captureSelection"
      @input="handleEditorInput"
      @blur="handleEditorBlur"
      @paste.prevent="handlePaste"
    ></div>

    <div v-if="linkDialogOpen" class="rich-link-dialog-mask" @click.self="closeLinkDialog">
      <section class="rich-link-dialog-card" role="dialog" aria-modal="true" aria-label="设置链接">
        <p class="eyebrow rich-link-dialog-eyebrow">Link</p>
        <h3 class="rich-link-dialog-title">设置超链接</h3>
        <p class="rich-link-dialog-copy">可以分别设置跳转地址和显示名称。</p>

        <div class="rich-link-dialog-form">
          <label>
            <span>链接地址</span>
            <input
              ref="linkUrlInputRef"
              v-model.trim="linkDialog.url"
              type="text"
              placeholder="https://example.com"
              @keydown.enter.prevent="submitLinkDialog"
            />
          </label>
          <label>
            <span>显示名称</span>
            <input
              v-model="linkDialog.text"
              type="text"
              placeholder="例如：项目主页"
              @keydown.enter.prevent="submitLinkDialog"
            />
          </label>
        </div>

        <p v-if="linkDialogError" class="rich-link-dialog-error">{{ linkDialogError }}</p>

        <div class="rich-link-dialog-actions">
          <button type="button" class="ghost-button" @click="closeLinkDialog">取消</button>
          <button type="button" class="primary-button" @click="submitLinkDialog">插入链接</button>
        </div>
      </section>
    </div>

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
  enableSectionFolding: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const editorRef = ref(null)
const linkUrlInputRef = ref(null)
const savedRange = ref(null)
const isComposing = ref(false)
const isApplyingCommand = ref(false)
const lastHtml = ref('')
const foldedHeadingState = ref({})
const linkDialogOpen = ref(false)
const linkDialogError = ref('')
const linkDialog = ref({
  url: '',
  text: '',
})

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

  if (node.getAttribute?.('data-editor-ui') === 'true') {
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

  if (node.tagName === 'OL') {
    const start = Number(node.getAttribute('start'))
    if (Number.isInteger(start) && start > 1) {
      element.setAttribute('start', String(start))
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

function normalizeLinkHref(value) {
  const raw = String(value || '').trim()
  if (!raw) {
    return ''
  }
  if (/^(https?:\/\/|mailto:)/i.test(raw)) {
    return raw
  }
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(raw)) {
    return `mailto:${raw}`
  }
  return `https://${raw}`
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

function getSelectionRange() {
  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0) {
    return null
  }

  const range = selection.getRangeAt(0)
  return isSelectionInsideEditor(range) ? range : null
}

function getClosestBlockElement(node) {
  const editor = editorRef.value
  if (!editor || !node) {
    return null
  }

  const startNode = node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement
  if (!startNode) {
    return null
  }

  const block = startNode.closest?.('p, h1, h2, h3, blockquote, li')
  return block && editor.contains(block) ? block : null
}

function getBlockElementFromRange(range) {
  const editor = editorRef.value
  if (!editor || !range) {
    return null
  }

  const directBlock = getClosestBlockElement(range.startContainer) || getClosestBlockElement(range.commonAncestorContainer)
  if (directBlock) {
    return directBlock
  }

  if (range.startContainer.nodeType === Node.ELEMENT_NODE) {
    const container = range.startContainer
    const offset = Math.min(range.startOffset, container.childNodes.length)
    const candidates = [
      container.childNodes[offset],
      container.childNodes[offset - 1],
      container.childNodes[0],
      container.childNodes[container.childNodes.length - 1],
    ].filter(Boolean)

    for (const candidate of candidates) {
      const block = getClosestBlockElement(candidate)
      if (block) {
        return block
      }
    }
  }

  return null
}

function getCurrentBlockElement() {
  return getBlockElementFromRange(getSelectionRange())
}

function getTextBeforeCaretInBlock(block) {
  const range = getSelectionRange()
  if (!block || !range || !range.collapsed) {
    return ''
  }

  const probe = range.cloneRange()
  probe.selectNodeContents(block)
  probe.setEnd(range.startContainer, range.startOffset)
  return String(probe.toString() || '')
}

function isBlockElement(node) {
  return Boolean(node?.nodeType === Node.ELEMENT_NODE && /^(P|H1|H2|H3|BLOCKQUOTE|UL|OL|LI)$/.test(node.tagName))
}

function getTopLevelChild(node) {
  const editor = editorRef.value
  if (!editor || !node) {
    return null
  }

  let current = node.nodeType === Node.ELEMENT_NODE ? node : node.parentNode
  while (current && current.parentNode && current.parentNode !== editor) {
    current = current.parentNode
  }

  if (current && current.parentNode === editor) {
    return current
  }
  return null
}

function wrapCurrentInlineRun(tagName) {
  const editor = editorRef.value
  const range = getSelectionRange()
  if (!editor || !range) {
    return false
  }

  const anchorNode = getTopLevelChild(range.startContainer)
  if (!anchorNode || isBlockElement(anchorNode)) {
    return false
  }

  const inlineNodes = Array.from(editor.childNodes)
  const anchorIndex = inlineNodes.indexOf(anchorNode)
  if (anchorIndex === -1) {
    return false
  }

  let startIndex = anchorIndex
  let endIndex = anchorIndex

  while (startIndex > 0 && !isBlockElement(inlineNodes[startIndex - 1])) {
    startIndex -= 1
  }

  while (endIndex < inlineNodes.length - 1 && !isBlockElement(inlineNodes[endIndex + 1])) {
    endIndex += 1
  }

  const replacement = document.createElement(tagName)
  const fragment = document.createDocumentFragment()
  for (let index = startIndex; index <= endIndex; index += 1) {
    fragment.appendChild(inlineNodes[index])
  }
  replacement.appendChild(fragment)

  const insertBeforeNode = editor.childNodes[startIndex] || null
  editor.insertBefore(replacement, insertBeforeNode)
  placeCaretAtEnd(replacement)
  return true
}

function placeCaretAtEnd(element) {
  if (!element) {
    return
  }

  const selection = window.getSelection()
  if (!selection) {
    return
  }

  const range = document.createRange()
  range.selectNodeContents(element)
  range.collapse(false)
  selection.removeAllRanges()
  selection.addRange(range)
  savedRange.value = range.cloneRange()
}

async function replaceCurrentBlock(tagName) {
  restoreSelection()

  const range = getSelectionRange()
  const currentBlock = getBlockElementFromRange(range)
  if (!currentBlock) {
    return false
  }

  if (currentBlock.tagName === 'LI') {
    return replaceCurrentListItem(tagName, currentBlock)
  }

  if (currentBlock.tagName.toLowerCase() === tagName) {
    return true
  }

  const replacement = document.createElement(tagName)
  while (currentBlock.firstChild) {
    replacement.appendChild(currentBlock.firstChild)
  }
  currentBlock.replaceWith(replacement)
  placeCaretAtEnd(replacement)
  emitCurrentValue()
  await nextTick()
  decorateFoldableSections()
  placeCaretAtEnd(replacement)
  return true
}

async function replaceCurrentListItem(tagName, listItem) {
  const list = listItem?.parentElement
  if (!list || !/^(UL|OL)$/.test(list.tagName)) {
    return false
  }

  const editor = editorRef.value
  if (!editor) {
    return false
  }

  const items = Array.from(list.children).filter((node) => node.tagName === 'LI')
  const currentIndex = items.indexOf(listItem)
  if (currentIndex === -1) {
    return false
  }

  const replacement = document.createElement(tagName)
  while (listItem.firstChild) {
    replacement.appendChild(listItem.firstChild)
  }

  const fragment = document.createDocumentFragment()
  const beforeItems = items.slice(0, currentIndex)
  const afterItems = items.slice(currentIndex + 1)

  if (beforeItems.length) {
    const beforeList = document.createElement(list.tagName.toLowerCase())
    beforeItems.forEach((item) => beforeList.appendChild(item))
    fragment.appendChild(beforeList)
  }

  fragment.appendChild(replacement)

  if (afterItems.length) {
    const afterList = document.createElement(list.tagName.toLowerCase())
    afterItems.forEach((item) => afterList.appendChild(item))
    fragment.appendChild(afterList)
  }

  list.replaceWith(fragment)
  placeCaretAtEnd(replacement)
  emitCurrentValue()
  await nextTick()
  decorateFoldableSections()
  placeCaretAtEnd(replacement)
  return true
}

function cleanupHeadingUi(editor) {
  Array.from(editor.querySelectorAll('[data-editor-ui="true"]')).forEach((node) => node.remove())
  Array.from(editor.querySelectorAll('.rich-fold-hidden')).forEach((node) => node.classList.remove('rich-fold-hidden'))
  Array.from(editor.querySelectorAll('.rich-fold-heading')).forEach((node) => node.classList.remove('rich-fold-heading', 'is-folded'))
  Array.from(editor.querySelectorAll('[data-heading-key]')).forEach((node) => {
    node.removeAttribute('data-heading-key')
    node.removeAttribute('data-foldable-heading')
  })
}

function getFoldableSectionNodes(heading) {
  const nodes = []
  const currentLevel = Number(heading.tagName.slice(1))
  let pointer = heading.nextElementSibling

  while (pointer) {
    if (/^H[1-3]$/.test(pointer.tagName) && Number(pointer.tagName.slice(1)) <= currentLevel) {
      break
    }
    nodes.push(pointer)
    pointer = pointer.nextElementSibling
  }

  return nodes
}

function getHeadingPlainText(heading) {
  return String(heading?.textContent || '')
    .replace(/[\u200B-\u200D\uFEFF]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

function decorateFoldableSections() {
  const editor = editorRef.value
  if (!editor) return

  cleanupHeadingUi(editor)

  if (!props.enableSectionFolding) {
    return
  }

  const headings = Array.from(editor.querySelectorAll('h1, h2, h3'))
  const nextFoldState = {}

  headings.forEach((heading, index) => {
    const text = getHeadingPlainText(heading)
    if (!text) {
      return
    }

    const key = `${heading.tagName.toLowerCase()}-${index}-${text}`
    const sectionNodes = getFoldableSectionNodes(heading)
    const isCollapsed = Boolean(foldedHeadingState.value[key])
    heading.classList.add('rich-fold-heading')

    if (sectionNodes.length) {
      heading.setAttribute('data-heading-key', key)
      heading.setAttribute('data-foldable-heading', 'true')
      if (isCollapsed) {
        heading.classList.add('is-folded')
        sectionNodes.forEach((node) => node.classList.add('rich-fold-hidden'))
      }

      const toggle = document.createElement('button')
      toggle.type = 'button'
      toggle.className = 'rich-heading-toggle'
      toggle.setAttribute('data-editor-ui', 'true')
      toggle.setAttribute('data-heading-key', key)
      toggle.setAttribute('contenteditable', 'false')
      toggle.setAttribute('tabindex', '-1')
      toggle.setAttribute('aria-label', isCollapsed ? '展开此标题内容' : '收起此标题内容')
      heading.prepend(toggle)
    }

    if (isCollapsed) {
      nextFoldState[key] = true
    }
  })

  foldedHeadingState.value = nextFoldState
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
    decorateFoldableSections()
    captureSelection()
  })
}

function serializeEditorHtml() {
  const editor = editorRef.value
  if (!editor) {
    return ''
  }
  const clone = editor.cloneNode(true)
  const html = sanitizeHtml(clone.innerHTML || '')
  return html
}

function emitCurrentValue() {
  const html = serializeEditorHtml()
  lastHtml.value = html
  emit('update:modelValue', html)
}

function handleEditorInput() {
  if (isComposing.value || isApplyingCommand.value) {
    return
  }
  captureSelection()
  emitCurrentValue()
  nextTick(() => {
    decorateFoldableSections()
  })
}

function handleEditorBlur() {
  captureSelection()
  emitCurrentValue()
  nextTick(() => {
    decorateFoldableSections()
  })
}

function handleEditorKeydown(event) {
  if (event.key === 'Tab') {
    event.preventDefault()
    const currentBlock = getCurrentBlockElement()
    if (currentBlock?.tagName === 'LI') {
      void execCommand(event.shiftKey ? 'outdent' : 'indent')
      return
    }
    void insertHtml('&nbsp;&nbsp;&nbsp;&nbsp;')
    return
  }

  if (event.key === ' ' && !event.shiftKey && !event.ctrlKey && !event.metaKey && !event.altKey) {
    if (maybeConvertBlockShortcut()) {
      event.preventDefault()
    }
  }
}

function maybeConvertBlockShortcut() {
  const currentBlock = getCurrentBlockElement()
  const range = getSelectionRange()
  if (!currentBlock || !range || !range.collapsed) {
    return false
  }

  if (!['P', 'DIV'].includes(currentBlock.tagName)) {
    return false
  }

  const textBeforeCaret = getTextBeforeCaretInBlock(currentBlock)
  const orderedMatch = textBeforeCaret.match(/^(\d+)\.$/)
  if (orderedMatch) {
    return convertBlockToList(currentBlock, {
      type: 'ol',
      start: Number(orderedMatch[1]),
      prefixLength: textBeforeCaret.length,
    })
  }

  if (/^[-*]$/.test(textBeforeCaret)) {
    return convertBlockToList(currentBlock, {
      type: 'ul',
      prefixLength: textBeforeCaret.length,
    })
  }

  return false
}

function convertBlockToList(currentBlock, options) {
  const { type, start = 1, prefixLength = 0 } = options
  const finalList = document.createElement(type === 'ol' ? 'ol' : 'ul')
  if (type === 'ol' && Number.isFinite(start) && start > 1) {
    finalList.setAttribute('start', String(start))
  }

  const item = document.createElement('li')
  const trailingText = String(currentBlock.textContent || '').slice(prefixLength)
  if (trailingText) {
    item.textContent = trailingText
  } else {
    item.innerHTML = '<br>'
  }
  finalList.appendChild(item)

  currentBlock.replaceWith(finalList)
  placeCaretAtEnd(item)
  emitCurrentValue()
  nextTick(() => {
    decorateFoldableSections()
    placeCaretAtEnd(item)
  })
  return true
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

async function insertHtml(html) {
  const editor = editorRef.value
  if (!editor) {
    return false
  }

  const sanitized = sanitizeHtml(html)
  if (!sanitized.trim()) {
    return false
  }

  isApplyingCommand.value = true
  restoreSelection()

  const selection = window.getSelection()
  const range = getSelectionRange()
  if (!selection || !range) {
    isApplyingCommand.value = false
    return false
  }

  range.deleteContents()
  const fragment = range.createContextualFragment(sanitized)
  const insertedNodes = Array.from(fragment.childNodes)
  const lastNode = insertedNodes[insertedNodes.length - 1] || null
  range.insertNode(fragment)

  if (lastNode) {
    const nextRange = document.createRange()
    if (lastNode.nodeType === Node.TEXT_NODE) {
      nextRange.setStart(lastNode, lastNode.textContent?.length || 0)
    } else {
      nextRange.selectNodeContents(lastNode)
    }
    nextRange.collapse(false)
    selection.removeAllRanges()
    selection.addRange(nextRange)
    savedRange.value = nextRange.cloneRange()
  } else {
    captureSelection()
  }

  emitCurrentValue()
  await nextTick()
  decorateFoldableSections()
  restoreSelection()
  isApplyingCommand.value = false
  return true
}

async function applyBlock(tagName) {
  if (['p', 'h1', 'h2', 'h3', 'blockquote'].includes(tagName)) {
    isApplyingCommand.value = true
    try {
      const replaced = await replaceCurrentBlock(tagName)
      if (!replaced && wrapCurrentInlineRun(tagName)) {
        emitCurrentValue()
        await nextTick()
        decorateFoldableSections()
        return
      }
      if (!replaced) {
        await execCommand('formatBlock', tagName)
      }
    } finally {
      isApplyingCommand.value = false
    }
    return
  }

  execCommand('formatBlock', tagName)
}

function insertLink() {
  restoreSelection()
  const selectedText = window.getSelection()?.toString().trim() || ''
  const selectedLink = getSelectedAnchorElement()
  linkDialog.value = {
    url: selectedLink?.getAttribute('href') || (selectedText && /^(https?:\/\/|mailto:)/i.test(selectedText) ? selectedText : ''),
    text: selectedText || selectedLink?.textContent || '',
  }
  linkDialogError.value = ''
  linkDialogOpen.value = true
  nextTick(() => {
    linkUrlInputRef.value?.focus()
    linkUrlInputRef.value?.select?.()
  })
}

function getSelectedAnchorElement() {
  const range = getSelectionRange()
  if (!range) {
    return null
  }

  const startElement = range.startContainer.nodeType === Node.ELEMENT_NODE
    ? range.startContainer
    : range.startContainer.parentElement
  const endElement = range.endContainer.nodeType === Node.ELEMENT_NODE
    ? range.endContainer
    : range.endContainer.parentElement

  const startAnchor = startElement?.closest?.('a')
  const endAnchor = endElement?.closest?.('a')
  if (startAnchor && startAnchor === endAnchor && editorRef.value?.contains(startAnchor)) {
    return startAnchor
  }
  return null
}

function closeLinkDialog() {
  linkDialogOpen.value = false
  linkDialogError.value = ''
  nextTick(() => {
    restoreSelection()
  })
}

async function submitLinkDialog() {
  const href = normalizeLinkHref(linkDialog.value.url)
  const displayText = String(linkDialog.value.text || '').trim()

  if (!href) {
    linkDialogError.value = '请先填写链接地址。'
    return
  }

  const linkHtml = `<a href="${escapeHtml(href)}">${escapeHtml(displayText || href)}</a>`
  const inserted = await insertHtml(linkHtml)
  if (!inserted) {
    linkDialogError.value = '当前无法插入链接，请先把光标放回编辑区。'
    return
  }

  linkDialogOpen.value = false
  linkDialogError.value = ''
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

function handleEditorClick(event) {
  const toggle = event.target.closest?.('.rich-heading-toggle')

  if (!toggle || !editorRef.value?.contains(toggle) || toggle.classList.contains('is-placeholder')) {
    return
  }

  event.preventDefault()
  event.stopPropagation()

  const key = toggle.getAttribute('data-heading-key')
  if (!key) return

  foldedHeadingState.value = {
    ...foldedHeadingState.value,
    [key]: !foldedHeadingState.value[key],
  }

  const selection = window.getSelection()
  if (selection) {
    selection.removeAllRanges()
  }

  nextTick(() => {
    decorateFoldableSections()
    captureSelection()
  })
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
  editorRef.value?.addEventListener('click', handleEditorClick)
})

onUnmounted(() => {
  document.removeEventListener('selectionchange', handleSelectionChange)
  editorRef.value?.removeEventListener('click', handleEditorClick)
})

defineExpose({
  getSurfaceElement() {
    return editorRef.value
  },
  focusEditor() {
    restoreSelection()
  },
  insertHtml,
})
</script>


