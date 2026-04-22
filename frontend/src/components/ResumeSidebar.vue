<template>
  <aside class="resume-sidebar">
    <div class="resume-sidebar-shell interviews-sidebar-shell">
      <div class="sidebar-brand interviews-sidebar-brand">
      <div class="brand-row interviews-brand-row">
        <div class="brand-copy-block interviews-brand-copy">
          <p class="eyebrow">职跃 OfferPilot</p>
          <h1>求职工作台</h1>
        </div>
      </div>
      <p class="sidebar-desc interviews-sidebar-desc">从求职工作台出发，逐步串联简历、投递与面试管理。</p>
      <p class="sidebar-user interviews-sidebar-user">已登录：{{ username || '用户' }}</p>
    </div>

    <button class="primary-button interviews-sidebar-primary" type="button" @click="$emit('create-resume')">新建简历</button>

    <!-- <section class="interviews-card interviews-card-soft resume-sidebar-panel">
      <div class="interviews-card-head">
        <div>
          <p class="eyebrow">Workspace</p>
          <h2>简历操作</h2>
        </div>
      </div>

      <button class="ghost-button sidebar-workspace-button" type="button" @click="$emit('back-dashboard')">
        返回工作台
      </button>
      <button class="ghost-button" type="button" @click="$emit('logout')">退出登录</button>
    </section> -->

    <section class="interviews-card interviews-card-soft resume-sidebar-panel resume-sidebar-list-panel">
      <div class="sidebar-list-head">
        <h2>我的简历</h2>
        <span>{{ resumes.length }} 份</span>
      </div>

      <div class="resume-list-scroll">
      <div v-if="showDraftCard" class="resume-item-card active">
        <div class="sidebar-edit-row">
          <span class="sidebar-edit-label">标题</span>
          <input v-model.trim="currentResume.title" class="sidebar-edit-control" placeholder="例如：Java后端" />
        </div>
        <div class="sidebar-edit-row">
          <span class="sidebar-edit-label">模板</span>
          <div class="sidebar-edit-control">
            <CustomSelect v-model="currentResume.template_id" :options="templateOptions" />
          </div>
        </div>
        <p v-if="isCurrentTitleDuplicated" class="sidebar-inline-error">该简历名称已存在，请换一个标题。</p>
        <small>{{ formatTime(currentResume.updated_at) }}</small>
      </div>

      <component
        v-for="resume in resumes"
        :key="resume.id"
        :is="resume.id === activeId ? 'div' : 'button'"
        :type="resume.id === activeId ? undefined : 'button'"
        class="resume-item-card"
        :class="{ active: resume.id === activeId }"
        @click="resume.id === activeId ? undefined : $emit('select-resume', resume.id)"
      >
        <template v-if="resume.id === activeId">
          <div class="sidebar-edit-row">
            <span class="sidebar-edit-label">标题</span>
            <input v-model.trim="currentResume.title" class="sidebar-edit-control" placeholder="例如：Java后端" @click.stop />
          </div>
          <div class="sidebar-edit-row">
            <span class="sidebar-edit-label">模板</span>
            <div class="sidebar-edit-control" @click.stop>
              <CustomSelect v-model="currentResume.template_id" :options="templateOptions" />
            </div>
          </div>
          <p v-if="isCurrentTitleDuplicated" class="sidebar-inline-error">该简历名称已存在，请换一个标题。</p>
          <small>{{ formatTime(resume.updated_at || currentResume.updated_at) }}</small>
        </template>
        <template v-else>
          <strong>{{ resume.title }}</strong>
          <div>模板：{{ getTemplateName(resume.template_id) }}</div>
          <small>{{ formatTime(resume.updated_at) }}</small>
        </template>
      </component>

      <div v-if="!resumes.length && !showDraftCard" class="empty-list-tip">暂无已保存简历，先新建一份。</div>
      </div>
    </section>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import CustomSelect from './CustomSelect.vue'

const props = defineProps({
  resumes: {
    type: Array,
    default: () => [],
  },
  activeId: {
    type: String,
    default: '',
  },
  username: {
    type: String,
    default: '',
  },
  currentResume: {
    type: Object,
    default: () => ({
      id: '',
      title: '',
      template_id: '',
      updated_at: '',
    }),
  },
  templates: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['select-resume', 'create-resume', 'back-dashboard', 'logout'])

const templateOptions = computed(() =>
  props.templates.map((template) => ({
    label: template.name,
    value: template.id,
  })),
)

const showDraftCard = computed(() => !props.activeId && !!props.currentResume)

const isCurrentTitleDuplicated = computed(() => {
  const currentTitle = String(props.currentResume?.title || '').trim()
  if (!currentTitle) {
    return false
  }
  return props.resumes.some((resume) => resume.id !== props.activeId && String(resume?.title || '').trim() === currentTitle)
})

function formatTime(value) {
  if (!value) {
    return '未保存'
  }
  return new Date(value).toLocaleString('zh-CN')
}

function getTemplateName(templateId) {
  const template = props.templates.find((item) => item.id === templateId)
  return template?.name || templateId || '默认模板'
}
</script>
