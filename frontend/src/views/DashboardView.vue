<template>
  <main class="interviews-page interviews-page-modern dashboard-page dashboard-page-modern">
    <section class="interviews-shell dashboard-shell">

      <div v-if="isMobileWorkspace" class="workspace-mobile-switcher" role="tablist" aria-label="移动端工作台切换">
        <button type="button" class="workspace-mobile-switch" :class="{ 'is-active': activeMobilePanel === 'main' }" @click="activeMobilePanel = 'main'">总览</button>
        <button type="button" class="workspace-mobile-switch" :class="{ 'is-active': activeMobilePanel === 'sidebar' }" @click="activeMobilePanel = 'sidebar'">快捷</button>
        <button type="button" class="workspace-mobile-switch" :class="{ 'is-active': activeMobilePanel === 'rail' }" @click="activeMobilePanel = 'rail'">数据</button>
      </div>

      <aside class="interviews-sidebar dashboard-sidebar" :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'sidebar' }">
        <div class="interviews-sidebar-shell dashboard-sidebar-shell">
          <div class="sidebar-brand interviews-sidebar-brand">
            <div class="brand-row interviews-brand-row">
              <div class="brand-copy-block interviews-brand-copy">
                <p class="eyebrow">职跃 OfferPilot</p>
                <h1>求职工作台</h1>
              </div>
            </div>
            <p class="sidebar-desc interviews-sidebar-desc">从求职工作台出发，逐步串联简历、投递与面试管理。</p>
            <p class="sidebar-user interviews-sidebar-user">已登录：{{ authStore.user?.username || '用户' }}</p>
          </div>

          <!-- <button class="primary-button interviews-sidebar-primary" type="button" @click="navigateTo({ path: '/applications', query: { create: '1' } })">
            新建投递
          </button> -->

          <section class="interviews-card interviews-card-soft dashboard-intro-card dashboard-overview-card">
            <div class="interviews-card-head dashboard-overview-head">
              <div>
                <p class="eyebrow">Quick Panel</p>
                <h2>快捷面板</h2>
              </div>
            </div>

            <div class="dashboard-overview-chart">
              <div class="dashboard-overview-chart-copy">
                <span>当前重点</span>
                <strong>{{ quickChartHighlight.value }}</strong>
                <p>{{ quickChartHighlight.label }}</p>
              </div>

              <div class="dashboard-overview-bars" aria-label="求职进度图表">
                <div v-for="item in quickChartData" :key="item.label" class="dashboard-overview-bar-item">
                  <span class="dashboard-overview-bar-track">
                    <span class="dashboard-overview-bar-fill" :style="{ height: `${item.height}%` }"></span>
                  </span>
                  <strong>{{ item.value }}</strong>
                  <small>{{ item.shortLabel }}</small>
                </div>
              </div>
            </div>

          </section>

          <section class="interviews-card interviews-card-soft">
            <div class="interviews-card-head">
              <div>
                <p class="eyebrow">Resumes</p>
                <h2>最近简历</h2>
              </div>
              <span class="interviews-mini-pill">{{ resumeStore.resumes.length }} 份</span>
            </div>

            <div v-if="resumeStore.loading" class="dashboard-loading">正在加载简历...</div>
            <div v-else-if="recentResumes.length" class="dashboard-sidebar-list">
              <button
                v-for="resume in recentResumes"
                :key="resume.id"
                class="dashboard-sidebar-item"
                type="button"
                @click="openResume(resume.id)"
              >
                <strong>{{ resume.title }}</strong>
                <small>{{ formatDate(resume.updated_at) }}</small>
              </button>
            </div>
            <p v-else class="muted-copy">还没有简历，建议先准备一份基础版本。</p>
          </section>
        </div>
      </aside>

      <section class="interviews-main dashboard-main" :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'main' }">
        <section class="interviews-editor-canvas dashboard-hero-surface">
          <header class="dashboard-hero-head">
            <div>
              <p class="interviews-doc-kicker">Workflow Desk</p>
              <h1>{{ heroTitle }}</h1>
              <p class="dashboard-hero-copy">{{ heroSubtitle }}</p>
            </div>

            <div class="dashboard-hero-actions">
              <button class="primary-button" type="button" @click="navigateTo({ path: '/applications', query: { create: '1' } })">
                新建投递
              </button>
              <button class="ghost-button" type="button" @click="navigateTo('/editor')">
                编辑简历
              </button>
            </div>
          </header>

          <section class="dashboard-stat-grid dashboard-stat-grid-modern">
            <article v-for="card in statCards" :key="card.label" class="dashboard-stat-card">
              <span>{{ card.label }}</span>
              <strong>{{ card.value }}</strong>
              <small class="dashboard-stat-note">{{ card.hint }}</small>
            </article>
          </section>

          <section class="dashboard-task-grid dashboard-task-grid-modern">
            <button
              v-for="task in taskCards"
              :key="task.title"
              type="button"
              class="dashboard-task-card"
              :class="{ 'is-accent': task.accent }"
              @click="navigateTo(task.to)"
            >
              <strong>{{ task.title }}</strong>
              <p>{{ task.description }}</p>
              <span>{{ task.cta }}</span>
            </button>
          </section>
        </section>
      </section>

      <aside class="interviews-rail dashboard-rail" :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'rail' }">
        <section class="interviews-card interviews-card-plain">
          <div class="interviews-card-head">
            <div>
              <p class="eyebrow">Snapshot</p>
              <h2>当前节奏</h2>
            </div>
          </div>

          <dl class="interviews-summary">
            <div>
              <dt>待跟进</dt>
              <dd>{{ applicationStats.todo_count }}</dd>
            </div>
            <div>
              <dt>总投递</dt>
              <dd>{{ applicationStats.total_count }}</dd>
            </div>
            <div>
              <dt>Offer</dt>
              <dd>{{ applicationStats.offer_count }}</dd>
            </div>
            <div>
              <dt>待复盘</dt>
              <dd>{{ interviewStats.pending_review_count }}</dd>
            </div>
          </dl>
        </section>

        <section class="interviews-card interviews-card-plain">
          <div class="interviews-card-head">
            <div>
              <p class="eyebrow">Shortcuts</p>
              <h2>快捷入口</h2>
            </div>
          </div>

          <div class="interviews-rail-actions">
            <RouterLink class="ghost-button" to="/editor">打开简历管理</RouterLink>
            <RouterLink class="ghost-button" to="/applications">打开投递管理</RouterLink>
            <RouterLink class="ghost-button" to="/interviews">打开面试记录</RouterLink>
          </div>
        </section>
      </aside>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { requestJson } from '../api/request'
import { useAuthStore } from '../stores/auth'
import { useResumeStore } from '../stores/resume'

const authStore = useAuthStore()
const resumeStore = useResumeStore()
const router = useRouter()
const activeMobilePanel = ref('main')
const isMobileWorkspace = ref(false)

const applicationStats = reactive({
  total_count: 0,
  new_this_week: 0,
  offer_count: 0,
  todo_count: 0,
})

const interviewStats = reactive({
  total_count: 0,
  this_week_count: 0,
  upcoming_count: 0,
  completed_count: 0,
  pending_review_count: 0,
  passed_count: 0,
  rejected_count: 0,
})

const recentResumes = computed(() => resumeStore.resumes.slice(0, 4))
const latestResume = computed(() => resumeStore.resumes[0] || null)

const heroTitle = computed(() => {
  if (!resumeStore.resumes.length) return '先准备你的第一份简历'
  if (applicationStats.todo_count > 0) return '今天优先推进待跟进岗位'
  return `欢迎回来，${authStore.user?.username || '求职者'}`
})

const heroSubtitle = computed(() => {
  if (!resumeStore.resumes.length) {
    return '建议先完成一份基础简历，再开始整理投递记录和跟进节奏。'
  }
  if (applicationStats.todo_count > 0) {
    return `当前还有 ${applicationStats.todo_count} 条投递待跟进，继续推进就能更快拿到反馈。`
  }
  return '这里把简历和投递串成了一套顺手的工作流，可以继续往前推进。'
})

const statCards = computed(() => [
  {
    label: '简历版本',
    value: resumeStore.resumes.length,
    hint: latestResume.value ? `最近更新：${latestResume.value.title}` : '先创建一份基础简历',
  },
  {
    label: '投递总数',
    value: applicationStats.total_count,
    hint: `本周新增 ${applicationStats.new_this_week}`,
  },
  {
    label: '待跟进',
    value: applicationStats.todo_count,
    hint: '优先处理需要继续推进的岗位',
  },
  {
    label: '面试记录',
    value: interviewStats.total_count,
    hint: interviewStats.pending_review_count > 0 ? `${interviewStats.pending_review_count} 场待复盘` : `本周 ${interviewStats.this_week_count} 场`,
  },
])

const quickChartData = computed(() => {
  const items = [
    { label: '简历版本', shortLabel: '简历', value: resumeStore.resumes.length },
    { label: '投递总数', shortLabel: '投递', value: applicationStats.total_count },
    { label: '面试记录', shortLabel: '面试', value: interviewStats.total_count },
  ]
  const maxValue = Math.max(...items.map((item) => item.value), 1)
  return items.map((item) => ({
    ...item,
    height: Math.max(18, Math.round((item.value / maxValue) * 100)),
  }))
})

const quickChartHighlight = computed(() => {
  if (applicationStats.todo_count > 0) {
    return {
      value: applicationStats.todo_count,
      label: '待跟进岗位',
    }
  }
  return {
    value: applicationStats.total_count,
    label: '累计投递数',
  }
})

const taskCards = computed(() => {
  const cards = []

  if (!resumeStore.resumes.length) {
    cards.push({
      title: '创建第一份简历',
      description: '先准备一份可以持续迭代的基础版本，后续投递都围绕它展开。',
      cta: '打开简历编辑器',
      sidebarTitle: '创建简历',
      to: '/editor',
      accent: true,
    })
  } else {
    cards.push({
      title: '继续编辑最近简历',
      description: latestResume.value ? `最近更新的是《${latestResume.value.title}》，可以继续补充项目和经历。` : '回到编辑器继续完善内容。',
      cta: '继续编辑',
      sidebarTitle: '继续简历',
      to: '/editor',
      accent: false,
    })
  }

  cards.push({
    title: '新增一条投递',
    description: '把岗位、渠道、状态、关联简历和下一步动作一起记录下来。',
    cta: '打开投递新建弹窗',
    sidebarTitle: '新建投递',
    to: { path: '/applications', query: { create: '1' } },
    accent: true,
  })

  cards.push({
    title: applicationStats.todo_count > 0 ? '先处理待跟进岗位' : '检查投递进度',
    description: applicationStats.todo_count > 0
      ? `当前有 ${applicationStats.todo_count} 条投递已经到了该继续推进的时候。`
      : '快速查看最近岗位进展，避免投出去之后忘记跟进。',
    cta: '进入投递工作台',
    sidebarTitle: '进入投递',
    to: { path: '/applications', query: { quick: applicationStats.todo_count > 0 ? 'todo' : 'all' } },
    accent: false,
  })

  cards.push({
    title: interviewStats.pending_review_count > 0 ? '整理面试复盘' : '记录一场面试',
    description: interviewStats.pending_review_count > 0
      ? `还有 ${interviewStats.pending_review_count} 场面试需要补充复盘和后续行动。`
      : '把面试时间、轮次、问题、复盘和下一步动作都放进记录里。',
    cta: interviewStats.pending_review_count > 0 ? '进入面试记录' : '新建面试记录',
    sidebarTitle: interviewStats.pending_review_count > 0 ? '面试复盘' : '面试记录',
    to: '/interviews',
    accent: interviewStats.pending_review_count > 0,
  })

  return cards
})


function formatDate(value) {
  if (!value) return ''
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return ''
  return parsed.toLocaleDateString('zh-CN')
}

async function navigateTo(target) {
  await router.push(target)
}

async function openResume(resumeId) {
  resumeStore.selectResume(resumeId)
  await router.push('/editor')
}

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}

function syncWorkspaceMode() {
  if (typeof window === 'undefined') return
  isMobileWorkspace.value = window.innerWidth <= 1024
}

async function loadApplicationStats() {
  try {
    Object.assign(applicationStats, await requestJson('/api/applications/stats/overview'))
  } catch {
    Object.assign(applicationStats, {
      total_count: 0,
      new_this_week: 0,
      offer_count: 0,
      todo_count: 0,
    })
  }
}

async function loadInterviewStats() {
  try {
    Object.assign(interviewStats, await requestJson('/api/interviews/stats/overview'))
  } catch {
    Object.assign(interviewStats, {
      total_count: 0,
      this_week_count: 0,
      upcoming_count: 0,
      completed_count: 0,
      pending_review_count: 0,
      passed_count: 0,
      rejected_count: 0,
    })
  }
}

onMounted(async () => {
  syncWorkspaceMode()
  window.addEventListener('resize', syncWorkspaceMode)
  if (!resumeStore.resumes.length) {
    await resumeStore.bootstrapEditor()
  }
  await Promise.all([loadApplicationStats(), loadInterviewStats()])
})

onUnmounted(() => {
  window.removeEventListener('resize', syncWorkspaceMode)
})
</script>
