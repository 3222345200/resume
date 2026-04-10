<template>
  <main class="interviews-page interviews-page-modern dashboard-page dashboard-page-modern">
    <section class="interviews-shell dashboard-shell" :class="{ 'sidebar-collapsed': leftSidebarCollapsed }">
      <aside class="interviews-primary-nav">
        <div class="interviews-primary-brand" title="OfferPilot">
          <img class="brand-logo" :src="brandMark" alt="OfferPilot" />
        </div>

        <nav class="interviews-primary-links" aria-label="Primary navigation">
          <RouterLink
            v-for="item in primaryNavItems"
            :key="item.to"
            class="interviews-primary-link"
            :class="{ 'is-active': item.to === '/dashboard' }"
            :to="item.to"
            :title="item.label"
          >
            <span class="interviews-primary-icon" v-html="item.icon"></span>
            <span class="sr-only">{{ item.label }}</span>
          </RouterLink>
        </nav>
      </aside>

      <button
        v-if="leftSidebarCollapsed"
        class="desktop-sidebar-reopen dashboard-desktop-sidebar-reopen"
        type="button"
        aria-label="展开求职工作台侧栏"
        @click="leftSidebarCollapsed = false"
      >
        <img class="desktop-sidebar-reopen-logo" :src="brandMark" alt="" aria-hidden="true" />
        <span class="desktop-sidebar-reopen-arrow">&gt;</span>
      </button>

      <aside class="interviews-sidebar dashboard-sidebar">
        <div class="interviews-sidebar-shell dashboard-sidebar-shell">
          <div class="sidebar-brand interviews-sidebar-brand">
            <div class="brand-row interviews-brand-row">
              <div class="brand-copy-block interviews-brand-copy">
                <p class="eyebrow">职跃 OfferPilot</p>
                <h1>求职工作台</h1>
              </div>
              <button
                class="desktop-sidebar-toggle interviews-sidebar-desktop-toggle"
                type="button"
                aria-label="收起求职工作台侧栏"
                @click="leftSidebarCollapsed = true"
              >
                &lt;
              </button>
            </div>
            <p class="sidebar-desc interviews-sidebar-desc">从首页总览出发，逐步把简历、投递和面试串成一套连续流程。</p>
            <p class="sidebar-user interviews-sidebar-user">已登录：{{ authStore.user?.username || '用户' }}</p>
          </div>

          <button class="primary-button interviews-sidebar-primary" type="button" @click="navigateTo({ path: '/applications', query: { create: '1' } })">
            新建投递
          </button>

          <section class="interviews-card interviews-card-soft dashboard-intro-card dashboard-overview-card">
            <div class="interviews-card-head dashboard-overview-head">
              <div>
                <p class="eyebrow">Quick Panel</p>
                <h2>快捷面板</h2>
              </div>
              <button class="ghost-button" type="button" @click="handleLogout">退出登录</button>
            </div>

            <div class="dashboard-overview-chart">
              <div class="dashboard-overview-chart-copy">
                <span>当前进度</span>
                <strong>{{ quickChartHighlight.value }}</strong>
                <p>{{ quickChartHighlight.label }}</p>
              </div>

              <div class="dashboard-overview-bars" aria-label="求职进度图表">
                <div
                  v-for="item in quickChartData"
                  :key="item.label"
                  class="dashboard-overview-bar-item"
                >
                  <span class="dashboard-overview-bar-track">
                    <span class="dashboard-overview-bar-fill" :style="{ height: `${item.height}%` }"></span>
                  </span>
                  <strong>{{ item.value }}</strong>
                  <small>{{ item.shortLabel }}</small>
                </div>
              </div>
            </div>

            <div class="interviews-quick-grid dashboard-quick-grid">
              <button
                v-for="task in taskCards.slice(0, 4)"
                :key="task.title"
                class="interviews-quick-card dashboard-sidebar-quick-card"
                :class="{ 'is-active': task.accent }"
                type="button"
                @click="navigateTo(task.to)"
              >
                <span class="dashboard-sidebar-quick-icon" v-html="getSidebarQuickIcon(task)" aria-hidden="true"></span>
                <strong class="dashboard-sidebar-quick-title">
                  <span v-for="line in splitSidebarQuickTitle(task.sidebarTitle || task.cta)" :key="line">{{ line }}</span>
                </strong>
              </button>
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

      <section class="interviews-main dashboard-main">
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

      <aside class="interviews-rail dashboard-rail">
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
              <dt>进行中面试</dt>
              <dd>{{ applicationStats.interviewing_count }}</dd>
            </div>
            <div>
              <dt>待复盘</dt>
              <dd>{{ interviewStats.pending_review_count }}</dd>
            </div>
            <div>
              <dt>Offer</dt>
              <dd>{{ applicationStats.offer_count }}</dd>
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
            <RouterLink class="ghost-button" :to="{ path: '/interviews', query: { quick: 'pending' } }">打开面试记录</RouterLink>
          </div>
        </section>
      </aside>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import brandMark from '../assets/logo.png'
import { requestJson } from '../api/request'
import { useAuthStore } from '../stores/auth'
import { useResumeStore } from '../stores/resume'

const authStore = useAuthStore()
const resumeStore = useResumeStore()
const router = useRouter()

const primaryNavItems = [
  {
    to: '/dashboard',
    label: '工作台',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 4h7v7H4z"/><path d="M13 4h7v5h-7z"/><path d="M13 11h7v9h-7z"/><path d="M4 13h7v7H4z"/></svg>`,
  },
  {
    to: '/editor',
    label: '简历管理',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M10 13h6"/><path d="M10 17h6"/></svg>`,
  },
  {
    to: '/applications',
    label: '投递管理',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 8h16v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M4 12h16"/></svg>`,
  },
  {
    to: '/interviews',
    label: '面试记录',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 6h16v10H8l-4 4z"/><path d="M8 10h8"/><path d="M8 13h5"/></svg>`,
  },
]

const applicationStats = reactive({
  total_count: 0,
  new_this_week: 0,
  interviewing_count: 0,
  offer_count: 0,
  todo_count: 0,
})

const interviewStats = reactive({
  total_count: 0,
  this_week_count: 0,
  upcoming_count: 0,
  pending_review_count: 0,
})

const leftSidebarCollapsed = ref(false)

const recentResumes = computed(() => resumeStore.resumes.slice(0, 4))
const latestResume = computed(() => resumeStore.resumes[0] || null)

const heroTitle = computed(() => {
  if (!resumeStore.resumes.length) return '先搭好你的第一份求职材料'
  if (applicationStats.todo_count > 0) return '今天优先推进待跟进的岗位'
  if (interviewStats.pending_review_count > 0) return '把最近的面试尽快复盘下来'
  return `欢迎回来，${authStore.user?.username || '求职者'}`
})

const heroSubtitle = computed(() => {
  if (!resumeStore.resumes.length) {
    return '建议先完成一份基础简历，再从投递管理开始记录岗位、状态流转和面试过程。'
  }
  if (applicationStats.todo_count > 0) {
    return `你现在有 ${applicationStats.todo_count} 条待跟进投递，继续推进的入口已经放到最前面。`
  }
  if (interviewStats.pending_review_count > 0) {
    return `还有 ${interviewStats.pending_review_count} 场面试待复盘，及时记录更容易沉淀经验。`
  }
  return '这里把简历、投递、面试三部分串成了一套统一工作台，你可以连续推进。'
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
    label: '待复盘面试',
    value: interviewStats.pending_review_count,
    hint: `本周面试 ${interviewStats.this_week_count} 场`,
  },
])

const quickChartData = computed(() => {
  const items = [
    { label: '简历版本', shortLabel: '简历', value: resumeStore.resumes.length },
    { label: '投递总数', shortLabel: '投递', value: applicationStats.total_count },
    { label: '待跟进', shortLabel: '跟进', value: applicationStats.todo_count },
    { label: '待复盘面试', shortLabel: '面试', value: interviewStats.pending_review_count },
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
  if (interviewStats.pending_review_count > 0) {
    return {
      value: interviewStats.pending_review_count,
      label: '待复盘面试',
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
      description: '先准备一个可以持续迭代的基础版本，后面的投递和面试都围绕它展开。',
      cta: '打开简历编辑器',
      sidebarHint: '最近没有简历',
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
    title: interviewStats.pending_review_count > 0 ? '复盘最近面试' : '准备新的面试记录',
    description: interviewStats.pending_review_count > 0
      ? `当前有 ${interviewStats.pending_review_count} 场面试还没复盘，建议尽快补上。`
      : '如果已经开始面试，可以把每一场都整理成持续更新的记录文档。',
    cta: '进入面试记录',
    sidebarTitle: '进入面试',
    to: { path: '/interviews', query: interviewStats.pending_review_count > 0 ? { quick: 'pending' } : { create: '1' } },
    accent: false,
  })

  return cards
})

function splitSidebarQuickTitle(value) {
  const text = String(value || '').trim()
  if (!text) return ['']
  return text.match(/.{1,2}/g) || [text]
}

function getSidebarQuickIcon(task) {
  const title = String(task?.sidebarTitle || task?.cta || '')
  if (title.includes('简历')) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M10 13h6"/><path d="M10 17h6"/></svg>'
  }
  if (title.includes('投递')) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 8h16v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M4 12h16"/></svg>'
  }
  if (title.includes('面试')) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 6h16v10H8l-4 4z"/><path d="M8 10h8"/><path d="M8 13h5"/></svg>'
  }
  return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12h14"/><path d="M12 5v14"/></svg>'
}

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

async function loadApplicationStats() {
  try {
    Object.assign(applicationStats, await requestJson('/api/applications/stats/overview'))
  } catch {
    Object.assign(applicationStats, {
      total_count: 0,
      new_this_week: 0,
      interviewing_count: 0,
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
      pending_review_count: 0,
    })
  }
}

onMounted(async () => {
  if (!resumeStore.resumes.length) {
    await resumeStore.bootstrapEditor()
  }
  await Promise.all([loadApplicationStats(), loadInterviewStats()])
})
</script>
