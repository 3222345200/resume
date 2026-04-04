<template>
  <section class="editor-card section-editor-card">
    <div class="editor-card-header">
      <div>
        <p class="eyebrow">{{ eyebrow }}</p>
        <h2>{{ title }}</h2>
      </div>
      <button class="ghost-button add-entry-btn" type="button" @click="addItem">新增{{ shortName }}</button>
    </div>

    <div class="repeat-editor-list">
      <article
        v-for="(item, index) in items"
        :key="index"
        :ref="(element) => setItemRef(element, index)"
        class="repeat-editor-item"
      >
        <div class="repeat-item-head">
          <div class="repeat-item-title-wrap">
            <strong>{{ shortName }} {{ index + 1 }}</strong>
            <slot name="item-head-extra" :item="item" :index="index"></slot>
          </div>
          <div class="repeat-inline-actions">
            <button class="mini-move-btn" type="button" :disabled="index === 0" @click="moveItem(index, -1)">上移</button>
            <button class="mini-move-btn" type="button" :disabled="index === items.length - 1" @click="moveItem(index, 1)">下移</button>
            <button class="remove-entry-btn" type="button" @click="requestRemoveItem(index)">删除</button>
          </div>
        </div>

        <slot :item="item" :index="index"></slot>
      </article>

      <div v-if="!items.length" class="empty-list-tip">暂无{{ shortName }}，点击右上角新增。</div>
    </div>

    <ConfirmDialog
      :open="confirmOpen"
      :title="`删除${shortName}`"
      :message="`确认删除这条${shortName}吗？删除后无法恢复。`"
      confirm-text="确认删除"
      cancel-text="取消"
      @confirm="confirmRemoveItem"
      @cancel="closeConfirm"
    />
  </section>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import ConfirmDialog from './ConfirmDialog.vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  shortName: {
    type: String,
    required: true,
  },
  eyebrow: {
    type: String,
    default: 'Section',
  },
  createItem: {
    type: Function,
    required: true,
  },
})

const confirmOpen = ref(false)
const pendingDeleteIndex = ref(-1)
const itemRefs = ref([])

function setItemRef(element, index) {
  if (element) {
    itemRefs.value[index] = element
  }
}

async function addItem() {
  props.items.push(props.createItem())
  await nextTick()
  itemRefs.value[props.items.length - 1]?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

function moveItem(index, step) {
  const targetIndex = index + step
  if (targetIndex < 0 || targetIndex >= props.items.length) {
    return
  }
  const temp = props.items[index]
  props.items[index] = props.items[targetIndex]
  props.items[targetIndex] = temp
}

function requestRemoveItem(index) {
  pendingDeleteIndex.value = index
  confirmOpen.value = true
}

function closeConfirm() {
  confirmOpen.value = false
  pendingDeleteIndex.value = -1
}

function confirmRemoveItem() {
  if (pendingDeleteIndex.value >= 0) {
    props.items.splice(pendingDeleteIndex.value, 1)
  }
  closeConfirm()
}
</script>
