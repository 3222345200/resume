<template>
  <aside class="resume-sidebar" :class="{ collapsed: collapsedOnMobile }">
    <div class="sidebar-brand">
      <div class="brand-row sidebar-brand-row">
        <img :src="brandMark" alt="职跃 OfferPilot 标志" />
        <div class="brand-copy-block">
          <p class="eyebrow">职跃 OfferPilot</p>
          <h1>求职工作台</h1>
        </div>
        <button class="desktop-sidebar-toggle" type="button" @click="$emit('toggle-sidebar')">&lt;</button>
      </div>
      <p class="sidebar-desc">从简历编辑开始，逐步扩展到完整的求职材料与投递管理。</p>
      <p class="sidebar-user">已登录：{{ username || '用户' }}</p>
    </div>

    <button class="primary-button" type="button" @click="$emit('create-resume')">新建简历</button>
    <button class="ghost-button" type="button" @click="$emit('logout')">退出登录</button>

    <div class="sidebar-list-head">
      <h2>我的简历</h2>
      <span>{{ resumes.length }} 份</span>
    </div>

    <div class="resume-list-scroll">
      <button
        v-for="resume in resumes"
        :key="resume.id"
        type="button"
        class="resume-item-card"
        :class="{ active: resume.id === activeId }"
        @click="$emit('select-resume', resume.id)"
      >
        <strong>{{ resume.title }}</strong>
        <div>模板：{{ resume.template_id }}</div>
        <small>{{ formatTime(resume.updated_at) }}</small>
      </button>

      <div v-if="!resumes.length" class="empty-list-tip">暂无已保存简历，先新建一份。</div>
    </div>
  </aside>
</template>

<script setup>
import brandMark from '../assets/brand-mark.svg'

defineProps({
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
  collapsedOnMobile: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['select-resume', 'create-resume', 'logout', 'toggle-sidebar'])

function formatTime(value) {
  if (!value) {
    return '未保存'
  }
  return new Date(value).toLocaleString('zh-CN')
}
</script>
