<template>
  <main class="dashboard-page">
    <header class="dashboard-hero-card">
      <div class="dashboard-brand-row">
        <div class="brand-badge">
          <img class="brand-logo" :src="brandMark" alt="职跃 OfferPilot 标志" />
          <span class="brand-name">职跃 OfferPilot</span>
        </div>

        <button class="ghost-button dashboard-logout" type="button" @click="handleLogout">
          退出登录
        </button>
      </div>

      <p class="eyebrow">Career Dashboard</p>
      <h1>欢迎回来，{{ authStore.user?.username || '求职者' }}</h1>
      <p class="dashboard-subtitle">
        这里会作为你的求职工作台首页。1.0 阶段先从简历管理进入，后续再把投递管理、面试记录、数据统计逐步挂到这里。
      </p>

      <div class="dashboard-stat-grid">
        <article class="dashboard-stat-card">
          <span>我的简历</span>
          <strong>{{ resumeStore.resumes.length }}</strong>
        </article>
        <article class="dashboard-stat-card is-muted">
          <span>投递记录</span>
          <strong>待上线</strong>
        </article>
        <article class="dashboard-stat-card is-muted">
          <span>面试记录</span>
          <strong>待上线</strong>
        </article>
      </div>
    </header>

    <section class="dashboard-module-grid">
      <article class="dashboard-module-card">
        <p class="eyebrow">Resume</p>
        <h2>简历管理</h2>
        <p class="muted-copy">
          创建、编辑、预览和导出多份简历版本，当前已有功能会先统一收进这个入口。
        </p>

        <div class="dashboard-action-row">
          <RouterLink class="primary-button" to="/editor">进入简历编辑</RouterLink>
        </div>

        <div v-if="resumeStore.loading" class="dashboard-loading">正在加载简历...</div>
        <div v-else-if="recentResumes.length" class="dashboard-resume-list">
          <button
            v-for="resume in recentResumes"
            :key="resume.id"
            type="button"
            class="dashboard-resume-item"
            @click="openResume(resume.id)"
          >
            <span>{{ resume.title }}</span>
            <small>{{ formatDate(resume.updated_at) }}</small>
          </button>
        </div>
        <p v-else class="dashboard-empty-copy">当前还没有简历，先去创建第一份简历。</p>
      </article>

      <article class="dashboard-module-card is-coming-soon">
        <p class="eyebrow">Applications</p>
        <h2>投递管理</h2>
        <p class="muted-copy">1.0 下一步接入投递记录、状态流转、渠道筛选和基础统计。</p>
        <RouterLink class="ghost-button" to="/applications">进入投递管理</RouterLink>
      </article>

      <article class="dashboard-module-card is-coming-soon">
        <p class="eyebrow">Interviews</p>
        <h2>面试记录</h2>
        <p class="muted-copy">后续在这里沉淀面试问答、单题复盘、整场总结和状态看板。</p>
        <RouterLink class="ghost-button" to="/interviews">进入面试记录</RouterLink>
      </article>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import brandMark from '../assets/brand-mark.svg'
import { useAuthStore } from '../stores/auth'
import { useResumeStore } from '../stores/resume'

const authStore = useAuthStore()
const resumeStore = useResumeStore()
const router = useRouter()

const recentResumes = computed(() => resumeStore.resumes.slice(0, 4))

function formatDate(value) {
  if (!value) {
    return ''
  }
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return ''
  }
  return parsed.toLocaleDateString('zh-CN')
}

async function openResume(resumeId) {
  resumeStore.selectResume(resumeId)
  await router.push('/editor')
}

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}

onMounted(async () => {
  if (!resumeStore.resumes.length) {
    await resumeStore.bootstrapEditor()
  }
})
</script>
