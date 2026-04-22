<template>
  <div class="rich-text-editor" :class="{ 'is-left-toolbar': toolbarMode === 'left' }">
    <div class="rich-text-toolbar">
      <button v-if="toolbarMode === 'left' && hasToolbarItem('paragraph')" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="applyBlock('p')">T</button>
      <button v-if="toolbarMode === 'left' && hasToolbarItem('heading1')" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="applyBlock('h1')">H1</button>
      <button v-if="toolbarMode === 'left' && hasToolbarItem('heading2')" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="applyBlock('h2')">H2</button>
      <button v-if="toolbarMode === 'left' && hasToolbarItem('heading3')" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="applyBlock('h3')">H3</button>
      <button v-if="toolbarMode === 'left' && hasToolbarItem('orderedList')" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="execCommand('insertOrderedList')">1.</button>
      <button v-if="toolbarMode === 'left' && hasToolbarItem('unorderedList')" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="execCommand('insertUnorderedList')">•</button>
      <button v-if="toolbarMode === 'left' && hasToolbarItem('blockquote')" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="applyBlock('blockquote')">“</button>
      <button v-if="toolbarMode === 'left' && hasToolbarItem('clearFormat')" type="button" tabindex="-1" class="rich-tool-btn rich-tool-btn-block" @mousedown.prevent="execCommand('removeFormat')">Tx</button>
      <span v-if="toolbarMode !== 'left' && showTopBlockDivider" class="rich-tool-divider"></span>
      <button v-if="toolbarMode !== 'left' && hasToolbarItem('paragraph')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="applyBlock('p')">正文</button>
      <button v-if="toolbarMode !== 'left' && hasToolbarItem('heading1')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="applyBlock('h1')">H1</button>
      <button v-if="toolbarMode !== 'left' && hasToolbarItem('heading2')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="applyBlock('h2')">H2</button>
      <button v-if="toolbarMode !== 'left' && hasToolbarItem('heading3')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="applyBlock('h3')">H3</button>
      <span v-if="toolbarMode !== 'left' && showFormatDivider" class="rich-tool-divider"></span>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('undo')">撤销</button>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('redo')">重做</button>
      <span v-if="toolbarMode !== 'left' && showStructureDivider" class="rich-tool-divider"></span>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('bold')"><strong>B</strong></button>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('italic')"><em>I</em></button>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('underline')"><u>U</u></button>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('strikeThrough')"><s>S</s></button>
      <button v-if="toolbarMode !== 'left' && hasToolbarItem('blockquote')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="applyBlock('blockquote')">引用</button>
      <button v-if="toolbarMode !== 'left' && hasToolbarItem('unorderedList')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('insertUnorderedList')">• 列表</button>
      <button v-if="toolbarMode !== 'left' && hasToolbarItem('orderedList')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('insertOrderedList')">1. 列表</button>
      <button v-if="toolbarMode !== 'left' && hasToolbarItem('alignLeft')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('justifyLeft')">左对齐</button>
      <button v-if="toolbarMode !== 'left' && hasToolbarItem('alignCenter')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('justifyCenter')">居中</button>
      <button v-if="toolbarMode !== 'left' && hasToolbarItem('alignRight')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('justifyRight')">右对齐</button>
      <button v-if="toolbarMode !== 'left' && enableTables && hasToolbarItem('table')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="requestInsertTable">表格</button>
      <button type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="insertLink">链接</button>
      <button v-if="toolbarMode !== 'left' && hasToolbarItem('clearFormat')" type="button" tabindex="-1" class="rich-tool-btn" @mousedown.prevent="execCommand('removeFormat')">清格式</button>
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
      @dragstart.prevent="handleEditorDragStart"
      @drop.prevent="handleEditorDrop"
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
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

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
  toolbarPreset: {
    type: String,
    default: 'full',
  },
  enableSectionFolding: {
    type: Boolean,
    default: false,
  },
  enableTables: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'table-state-change', 'request-insert-table'])

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
const tableResizeState = ref(null)
const isPointerSelecting = ref(false)
let decorationTimer = null

const TOOLBAR_PRESETS = {
  full: new Set([
    'paragraph',
    'heading1',
    'heading2',
    'heading3',
    'orderedList',
    'unorderedList',
    'blockquote',
    'alignLeft',
    'alignCenter',
    'alignRight',
    'table',
    'clearFormat',
  ]),
  resume: new Set([
    'orderedList',
    'unorderedList',
    'table',
    'clearFormat',
  ]),
}

const activeToolbarItems = computed(() => TOOLBAR_PRESETS[props.toolbarPreset] || TOOLBAR_PRESETS.full)
const showTopBlockDivider = computed(() => activeToolbarItems.value.has('paragraph') || activeToolbarItems.value.has('heading1') || activeToolbarItems.value.has('heading2') || activeToolbarItems.value.has('heading3'))
const showFormatDivider = computed(() => showTopBlockDivider.value)
const showStructureDivider = computed(() => (
  activeToolbarItems.value.has('blockquote') ||
  activeToolbarItems.value.has('unorderedList') ||
  activeToolbarItems.value.has('orderedList') ||
  activeToolbarItems.value.has('alignLeft') ||
  activeToolbarItems.value.has('alignCenter') ||
  activeToolbarItems.value.has('alignRight') ||
  activeToolbarItems.value.has('table') ||
  activeToolbarItems.value.has('clearFormat')
))

function hasToolbarItem(name) {
  return activeToolbarItems.value.has(name)
}

const allowedTags = new Set([
  'P',
  'DIV',
  'BR',
  'STRONG',
  'B',
  'EM',
  'I',
  'U',
  'S',
  'STRIKE',
  'SPAN',
  'FONT',
  'UL',
  'OL',
  'LI',
  'A',
  'H1',
  'H2',
  'H3',
  'BLOCKQUOTE',
  'TABLE',
  'THEAD',
  'TBODY',
  'TR',
  'TH',
  'TD',
  'COLGROUP',
  'COL',
])

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

function clampTableSize(value, minimum, maximum) {
  const number = Number(value)
  if (!Number.isFinite(number)) {
    return minimum
  }
  return Math.min(maximum, Math.max(minimum, Math.round(number)))
}

function normalizePixelSize(value, minimum = 48, maximum = 1200) {
  const match = String(value || '').match(/(\d+(?:\.\d+)?)px/i)
  if (!match) {
    return ''
  }
  const number = Number(match[1])
  if (!Number.isFinite(number)) {
    return ''
  }
  return `${Math.min(maximum, Math.max(minimum, Math.round(number)))}px`
}

function normalizeCssColor(value) {
  const raw = String(value || '').trim()
  if (!raw) {
    return ''
  }
  const tester = new Option().style
  tester.color = ''
  tester.color = raw
  return tester.color || ''
}

function extractStyleValue(styleText, propertyName) {
  const pattern = new RegExp(`${propertyName}\\s*:\\s*([^;]+)`, 'i')
  const matched = String(styleText || '').match(pattern)
  return matched ? matched[1].trim() : ''
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

  if (node.tagName === 'TABLE') {
    element.classList.add('rich-doc-table')
  }

  if (node.tagName === 'FONT') {
    const color = normalizeCssColor(node.getAttribute('color'))
    if (color) {
      element.style.color = color
    }
  }

  if (node.tagName === 'SPAN') {
    const color = normalizeCssColor(extractStyleValue(node.getAttribute('style'), 'color'))
    if (color) {
      element.style.color = color
    }
  }

  if (['P', 'DIV', 'H1', 'H2', 'H3', 'BLOCKQUOTE', 'LI', 'TD', 'TH'].includes(node.tagName)) {
    const textAlign = (
      extractStyleValue(node.getAttribute('style'), 'text-align')
      || String(node.getAttribute('align') || '')
    ).toLowerCase()
    if (['left', 'center', 'right'].includes(textAlign)) {
      element.style.textAlign = textAlign
    }
    const color = normalizeCssColor(extractStyleValue(node.getAttribute('style'), 'color'))
    if (color) {
      element.style.color = color
    }
  }

  if (node.tagName === 'COL') {
    const width = normalizePixelSize(node.getAttribute('style') || node.style?.width || node.getAttribute('width'))
    if (width) {
      element.style.width = width
    }
  }

  if (['TD', 'TH'].includes(node.tagName)) {
    const colspan = Number(node.getAttribute('colspan'))
    const rowspan = Number(node.getAttribute('rowspan'))
    if (Number.isInteger(colspan) && colspan > 1 && colspan <= 12) {
      element.setAttribute('colspan', String(colspan))
    }
    if (Number.isInteger(rowspan) && rowspan > 1 && rowspan <= 50) {
      element.setAttribute('rowspan', String(rowspan))
    }
  }

  Array.from(node.childNodes).forEach((child) => {
    element.appendChild(sanitizeNode(child))
  })

  if (['TD', 'TH'].includes(node.tagName) && !element.childNodes.length) {
    const paragraph = document.createElement('p')
    paragraph.innerHTML = '<br>'
    element.appendChild(paragraph)
  }
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

function hasExpandedSelectionInEditor() {
  const range = getSelectionRange()
  return Boolean(range && !range.collapsed)
}

function shouldDeferDecoration() {
  return isPointerSelecting.value || hasExpandedSelectionInEditor()
}

function isEditorFocused() {
  return document.activeElement === editorRef.value
}

function scheduleDecoration(delay = 80) {
  if (decorationTimer) {
    clearTimeout(decorationTimer)
  }

  decorationTimer = window.setTimeout(() => {
    decorationTimer = null
    if (shouldDeferDecoration()) {
      scheduleDecoration(120)
      return
    }
    decorateFoldableSections()
  }, delay)
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

function getSelectedTableCell(range = getSelectionRange()) {
  const editor = editorRef.value
  if (!editor || !range) {
    return null
  }

  const startElement = range.startContainer.nodeType === Node.ELEMENT_NODE
    ? range.startContainer
    : range.startContainer.parentElement
  const endElement = range.endContainer.nodeType === Node.ELEMENT_NODE
    ? range.endContainer
    : range.endContainer.parentElement

  const startCell = startElement?.closest?.('td, th')
  const endCell = endElement?.closest?.('td, th')
  if (startCell && startCell === endCell && editor.contains(startCell)) {
    return startCell
  }
  return null
}

function getSelectedTable(range = getSelectionRange()) {
  return getSelectedTableCell(range)?.closest?.('table') || null
}

function getTableRows(table) {
  return Array.from(table?.querySelectorAll?.('tr') || [])
}

function getTableCells(row) {
  return Array.from(row?.children || []).filter((node) => /^(TD|TH)$/.test(node.tagName))
}

function ensureCellContent(cell) {
  if (!cell) {
    return
  }
  if (!cell.childNodes.length) {
    const paragraph = document.createElement('p')
    paragraph.innerHTML = '<br>'
    cell.appendChild(paragraph)
  }
}

function getTableColumnCount(table) {
  const firstRow = getTableRows(table)[0]
  return getTableCells(firstRow).length
}

function getTableCellPosition(cell) {
  const row = cell?.parentElement
  const table = row?.closest?.('table')
  if (!row || !table) {
    return null
  }

  const rows = getTableRows(table)
  const rowIndex = rows.indexOf(row)
  const columnIndex = getTableCells(row).indexOf(cell)
  if (rowIndex === -1 || columnIndex === -1) {
    return null
  }

  return {
    table,
    row,
    rows,
    rowIndex,
    columnIndex,
  }
}

function createTableCell(tagName = 'td') {
  const cell = document.createElement(tagName)
  const paragraph = document.createElement('p')
  paragraph.innerHTML = '<br>'
  cell.appendChild(paragraph)
  return cell
}

function getOrCreateColgroup(table, columnCount) {
  let colgroup = table.querySelector('colgroup')
  if (!colgroup) {
    colgroup = document.createElement('colgroup')
    table.insertBefore(colgroup, table.firstChild)
  }

  while (colgroup.children.length < columnCount) {
    const col = document.createElement('col')
    col.style.width = `${Math.max(120, Math.round(1000 / Math.max(columnCount, 1)))}px`
    colgroup.appendChild(col)
  }

  while (colgroup.children.length > columnCount) {
    colgroup.lastElementChild?.remove()
  }

  return colgroup
}

function setCaretInsideCell(cell) {
  ensureCellContent(cell)
  const anchor = cell.querySelector('p, div, br') || cell
  placeCaretAtEnd(anchor)
}

function emitTableState() {
  const activeCell = getSelectedTableCell()
  const table = activeCell?.closest?.('table') || null
  emit('table-state-change', {
    inTable: Boolean(table),
    rows: table ? getTableRows(table).length : 0,
    cols: table ? getTableColumnCount(table) : 0,
  })
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

function cleanupTableUi(editor) {
  Array.from(editor.querySelectorAll('.rich-table-cell-selected')).forEach((node) => {
    node.classList.remove('rich-table-cell-selected')
  })
  Array.from(editor.querySelectorAll('.rich-table-resize-handle')).forEach((node) => node.remove())
}

function decorateTables(editor) {
  cleanupTableUi(editor)

  const activeCell = getSelectedTableCell()
  if (activeCell && editor.contains(activeCell)) {
    activeCell.classList.add('rich-table-cell-selected')
  }

  Array.from(editor.querySelectorAll('table')).forEach((table) => {
    table.classList.add('rich-doc-table')
    const firstRow = getTableRows(table)[0]
    const columnCount = getTableCells(firstRow).length
    if (!columnCount) {
      return
    }

    getOrCreateColgroup(table, columnCount)

    getTableRows(table).forEach((row) => {
      getTableCells(row).forEach((cell) => {
        const handle = document.createElement('button')
        handle.type = 'button'
        handle.className = 'rich-table-resize-handle'
        handle.setAttribute('data-editor-ui', 'true')
        handle.setAttribute('contenteditable', 'false')
        handle.setAttribute('tabindex', '-1')
        handle.setAttribute('aria-label', '调整列表格宽度')
        cell.appendChild(handle)
      })
    })
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

function decorateFoldableSections(options = {}) {
  const editor = editorRef.value
  if (!editor) return
  const { force = false } = options

  if (!force && shouldDeferDecoration()) {
    scheduleDecoration(120)
    return
  }

  cleanupHeadingUi(editor)
  decorateTables(editor)

  if (!props.enableSectionFolding || isEditorFocused()) {
    emitTableState()
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
  emitTableState()
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
    decorateFoldableSections({ force: true })
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
    scheduleDecoration()
  })
}

function handleEditorBlur() {
  captureSelection()
  emitCurrentValue()
  nextTick(() => {
    scheduleDecoration(120)
  })
}

function handleEditorKeydown(event) {
  const activeCell = getSelectedTableCell()
  if (event.key === 'Tab') {
    event.preventDefault()
    if (activeCell) {
      moveTableSelection(activeCell, event.shiftKey ? -1 : 1)
      return
    }
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

function moveTableSelection(cell, offset) {
  const position = getTableCellPosition(cell)
  if (!position) {
    return
  }

  const nextRowIndex = position.rowIndex
  const nextColumnIndex = position.columnIndex + offset
  let nextCell = getTableCells(position.rows[nextRowIndex])[nextColumnIndex]

  if (!nextCell && offset > 0) {
    nextCell = getTableCells(position.rows[nextRowIndex + 1])[0]
  }

  if (!nextCell && offset < 0) {
    const previousRow = position.rows[nextRowIndex - 1]
    const previousCells = getTableCells(previousRow)
    nextCell = previousCells[previousCells.length - 1]
  }

  if (nextCell) {
    setCaretInsideCell(nextCell)
    nextTick(() => {
      decorateFoldableSections()
    })
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

function requestInsertTable() {
  emit('request-insert-table')
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
  if (editorRef.value?.contains(document.activeElement) || document.activeElement === editorRef.value) {
    captureSelection()
  }
}

function handleEditorDragStart(event) {
  event.preventDefault()
}

function handleEditorDrop(event) {
  event.preventDefault()
}

function handleEditorClick(event) {
  const resizeHandle = event.target.closest?.('.rich-table-resize-handle')
  if (resizeHandle) {
    return
  }

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

function handleEditorMouseDown(event) {
  if (editorRef.value?.contains(event.target)) {
    isPointerSelecting.value = true
  }

  const handle = event.target.closest?.('.rich-table-resize-handle')
  if (!handle || !editorRef.value?.contains(handle)) {
    return
  }

  event.preventDefault()
  event.stopPropagation()

  const cell = handle.closest('td, th')
  const position = getTableCellPosition(cell)
  if (!position) {
    return
  }

  const colgroup = getOrCreateColgroup(position.table, getTableColumnCount(position.table))
  const col = colgroup.children[position.columnIndex]
  const width = col ? Number.parseInt(col.style.width, 10) || cell.getBoundingClientRect().width : cell.getBoundingClientRect().width

  tableResizeState.value = {
    table: position.table,
    columnIndex: position.columnIndex,
    startX: event.clientX,
    startWidth: Math.max(72, Math.round(width)),
  }
}

function handleWindowMouseMove(event) {
  const state = tableResizeState.value
  if (!state) {
    return
  }

  const colgroup = getOrCreateColgroup(state.table, getTableColumnCount(state.table))
  const col = colgroup.children[state.columnIndex]
  if (!col) {
    return
  }

  const width = Math.max(72, state.startWidth + event.clientX - state.startX)
  col.style.width = `${Math.round(width)}px`
}

function handleWindowMouseUp() {
  isPointerSelecting.value = false

  if (!tableResizeState.value) {
    captureSelection()
    return
  }
  tableResizeState.value = null
  captureSelection()
  emitCurrentValue()
  nextTick(() => {
    decorateFoldableSections()
  })
}

function buildTableHtml(options = {}) {
  const rows = clampTableSize(options.rows, 1, 20)
  const cols = clampTableSize(options.cols, 1, 8)
  const withHeader = options.withHeader !== false
  const columnWidth = Math.max(120, Math.round(960 / cols))
  const colgroupHtml = Array.from({ length: cols }, () => `<col style="width:${columnWidth}px">`).join('')
  const headerHtml = withHeader
    ? `<thead><tr>${Array.from({ length: cols }, (_, index) => `<th><p>表头 ${index + 1}</p></th>`).join('')}</tr></thead>`
    : ''
  const bodyRowCount = Math.max(rows - (withHeader ? 1 : 0), 1)
  const rowsHtml = Array.from({ length: bodyRowCount }, () => (
    `<tr>${Array.from({ length: cols }, () => '<td><p><br></p></td>').join('')}</tr>`
  )).join('')
  return `<table class="rich-doc-table"><colgroup>${colgroupHtml}</colgroup>${headerHtml}<tbody>${rowsHtml}</tbody></table><p><br></p>`
}

async function insertTable(options = {}) {
  return insertHtml(buildTableHtml(options))
}

async function mutateSelectedTable(mutator) {
  restoreSelection()
  const cell = getSelectedTableCell()
  if (!cell) {
    return false
  }

  isApplyingCommand.value = true
  let nextCell = cell
  try {
    nextCell = mutator(cell) || cell
    emitCurrentValue()
    await nextTick()
    decorateFoldableSections()
    if (nextCell) {
      setCaretInsideCell(nextCell)
    } else {
      restoreSelection()
    }
    return true
  } finally {
    isApplyingCommand.value = false
  }
}

async function addTableRow(after = true) {
  return mutateSelectedTable((cell) => {
    const position = getTableCellPosition(cell)
    if (!position) {
      return cell
    }

    const newRow = document.createElement('tr')
    const cells = getTableCells(position.row)
    cells.forEach(() => {
      newRow.appendChild(createTableCell('td'))
    })

    position.row.parentElement?.insertBefore(newRow, after ? position.row.nextSibling : position.row)
    return getTableCells(newRow)[position.columnIndex] || getTableCells(newRow)[0]
  })
}

async function addTableColumn(after = true) {
  return mutateSelectedTable((cell) => {
    const position = getTableCellPosition(cell)
    if (!position) {
      return cell
    }

    position.rows.forEach((row) => {
      const cells = getTableCells(row)
      const reference = cells[position.columnIndex] || null
      row.insertBefore(createTableCell(row.parentElement?.tagName === 'THEAD' ? 'th' : 'td'), after ? reference?.nextSibling || null : reference)
    })

    const colgroup = getOrCreateColgroup(position.table, getTableColumnCount(position.table))
    const referenceCol = colgroup.children[position.columnIndex] || null
    const newCol = document.createElement('col')
    newCol.style.width = `${Math.max(120, Math.round((referenceCol?.getBoundingClientRect?.().width || 160)))}px`
    colgroup.insertBefore(newCol, after ? referenceCol?.nextSibling || null : referenceCol)
    return getTableCells(position.rows[position.rowIndex])[position.columnIndex + (after ? 1 : 0)] || cell
  })
}

async function deleteTableRow() {
  return mutateSelectedTable((cell) => {
    const position = getTableCellPosition(cell)
    if (!position) {
      return cell
    }

    if (position.rows.length <= 1) {
      const onlyCell = getTableCells(position.row)[0]
      onlyCell.innerHTML = '<p><br></p>'
      return onlyCell
    }

    const fallbackRow = position.rows[position.rowIndex + 1] || position.rows[position.rowIndex - 1]
    position.row.remove()
    return getTableCells(fallbackRow)[Math.min(position.columnIndex, getTableCells(fallbackRow).length - 1)] || null
  })
}

async function deleteTableColumn() {
  return mutateSelectedTable((cell) => {
    const position = getTableCellPosition(cell)
    if (!position) {
      return cell
    }

    const columnCount = getTableColumnCount(position.table)
    if (columnCount <= 1) {
      const onlyCell = getTableCells(position.rows[0])[0]
      onlyCell.innerHTML = '<p><br></p>'
      return onlyCell
    }

    position.rows.forEach((row) => {
      const targetCell = getTableCells(row)[position.columnIndex]
      targetCell?.remove()
    })

    const colgroup = getOrCreateColgroup(position.table, columnCount)
    colgroup.children[position.columnIndex]?.remove()

    const fallbackColumnIndex = Math.max(0, position.columnIndex - 1)
    return getTableCells(position.rows[position.rowIndex])[fallbackColumnIndex] || null
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
  editorRef.value?.addEventListener('mousedown', handleEditorMouseDown)
  window.addEventListener('mousemove', handleWindowMouseMove)
  window.addEventListener('mouseup', handleWindowMouseUp)
})

onUnmounted(() => {
  document.removeEventListener('selectionchange', handleSelectionChange)
  editorRef.value?.removeEventListener('click', handleEditorClick)
  editorRef.value?.removeEventListener('mousedown', handleEditorMouseDown)
  window.removeEventListener('mousemove', handleWindowMouseMove)
  window.removeEventListener('mouseup', handleWindowMouseUp)
  if (decorationTimer) {
    clearTimeout(decorationTimer)
  }
})

defineExpose({
  getSurfaceElement() {
    return editorRef.value
  },
  focusEditor() {
    restoreSelection()
  },
  insertHtml,
  insertTable,
  addTableRowAfter() {
    return addTableRow(true)
  },
  addTableRowBefore() {
    return addTableRow(false)
  },
  addTableColumnAfter() {
    return addTableColumn(true)
  },
  addTableColumnBefore() {
    return addTableColumn(false)
  },
  deleteTableRow,
  deleteTableColumn,
})
</script>


