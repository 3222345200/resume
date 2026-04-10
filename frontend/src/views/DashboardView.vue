<template>
  <main class="dashboard-page">
    <header class="dashboard-hero-card">
      <div class="dashboard-brand-row">
        <div class="brand-badge">
          <img class="brand-logo" :src="brandMark" alt="OfferPilot 标志" />
          <span class="brand-name">OfferPilot</span>
        </div>

        <button class="ghost-button dashboard-logout" type="button" @click="handleLogout">
          退出登录
        </button>
      </div>

      <div class="dashboard-hero-copy">
        <div>
          <p class="eyebrow">Workflow Desk</p>
          <h1>{{ heroTitle }}</h1>
          <p class="dashboard-subtitle">{{ heroSubtitle }}</p>
        </div>

        <div class="dashboard-hero-actions">
          <button class="primary-button" type="button" @click="navigateTo({ path: '/applications', query: { create: '1' } })">
            新建投递
          </button>
          <button class="ghost-button" type="button" @click="navigateTo('/editor')">
            编辑简历
          </button>
        </div>
      </div>

      <div class="dashboard-stat-grid">
        <article class="dashboard-stat-card">
          <span>简历版本</span>
          <strong>{{ resumeStore.resumes.length }}</strong>
          <small class="dashboard-stat-note">{{ latestResume ? `最近更新：${latestResume.title}` : '先创建一份基础简历' }}</small>
        </article>
        <article class="dashboard-stat-card">
          <span>投递总数</span>
          <strong>{{ applicationStats.total_count }}</strong>
          <small class="dashboard-stat-note">本周新增 {{ applicationStats.new_this_week }}</small>
        </article>
        <article class="dashboard-stat-card">
          <span>待跟进</span>
          <strong>{{ applicationStats.todo_count }}</strong>
          <small class="dashboard-stat-note">建议优先处理需要继续推进的岗位</small>
        </article>
        <article class="dashboard-stat-card">
          <span>待复盘面试</span>
          <strong>{{ interviewStats.pending_review_count }}</strong>
          <small class="dashboard-stat-note">本周面试 {{ interviewStats.this_week_count }} 场</small>
        </article>
      </div>
    </header>

    <section class="dashboard-module-grid">
      <article class="dashboard-module-card">
        <p class="eyebrow">Next Steps</p>
        <h2>建议先做这些事</h2>
        <p class="muted-copy">首页不再只是统计看板，直接把下一步操作放到最前面，方便你继续推进。</p>

        <div class="dashboard-task-grid">
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
        </div>
      </article>

      <article class="dashboard-module-card">
        <div class="dashboard-list-head">
          <div>
            <p class="eyebrow">Resumes</p>
            <h2>最近的简历</h2>
          </div>
          <button class="ghost-button" type="button" @click="navigateTo('/editor')">
            进入编辑器
          </button>
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
        <p v-else class="dashboard-empty-copy">还没有简历，建议先创建一份基础版，再去做投递关联。</p>
      </article>

      <article class="dashboard-module-card">
        <p class="eyebrow">Pipeline</p>
        <h2>当前求职节奏</h2>
        <p class="muted-copy">把简历、投递和面试串成一条连续路径，减少在模块之间来回找入口。</p>

        <div class="dashboard-application-stats">
          <span>面试中 {{ applicationStats.interviewing_count }}</span>
          <span>Offer {{ applicationStats.offer_count }}</span>
          <span>面试总数 {{ interviewStats.total_count }}</span>
          <span>即将开始 {{ interviewStats.upcoming_count }}</span>
        </div>

        <div class="dashboard-action-row">
          <button class="primary-button" type="button" @click="navigateTo('/applications')">
            打开投递工作台
          </button>
        </div>

        <div class="dashboard-task-grid">
          <button
            type="button"
            class="dashboard-task-card"
            @click="navigateTo({ path: '/applications', query: { quick: 'todo' } })"
          >
            <strong>处理待跟进投递</strong>
            <p>集中查看需要继续推进的岗位、状态和下一步动作。</p>
            <span>进入待跟进视图</span>
          </button>

          <button
            type="button"
            class="dashboard-task-card"
            @click="navigateTo({ path: '/interviews', query: { quick: 'pending' } })"
          >
            <strong>复盘最近面试</strong>
            <p>把问题、回答、失误点和下一轮准备沉淀成结构化记录。</p>
            <span>进入复盘视图</span>
          </button>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import brandMark from '../assets/brand-mark.svg'
import { requestJson } from '../api/request'
import { useAuthStore } from '../stores/auth'
import { useResumeStore } from '../stores/resume'

const authStore = useAuthStore()
const resumeStore = useResumeStore()
const router = useRouter()

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

const recentResumes = computed(() => resumeStore.resumes.slice(0, 4))
const latestResume = computed(() => resumeStore.resumes[0] || null)

const heroTitle = computed(() => {
  if (!resumeStore.resumes.length) {
    return '先搭好你的第一份求职资料'
  }
  if (applicationStats.todo_count > 0) {
    return '今天优先推进待跟进的岗位'
  }
  if (interviewStats.pending_review_count > 0) {
    return '把最近的面试尽快复盘下来'
  }
  return `欢迎回来，${authStore.user?.username || '求职者'}`
})

const heroSubtitle = computed(() => {
  if (!resumeStore.resumes.length) {
    return '建议先完成一份基础简历，再从投递工作台开始记录岗位、状态流转和面试过程。'
  }
  if (applicationStats.todo_count > 0) {
    return `你现在有 ${applicationStats.todo_count} 条待跟进投递，首页已经帮你把继续推进的入口放到了最前面。`
  }
  if (interviewStats.pending_review_count > 0) {
    return `还有 ${interviewStats.pending_review_count} 场面试等待复盘，及时记录会更容易沉淀经验和下一轮准备。`
  }
  return '这里是你的求职工作台，可以从简历、投递、面试三个模块继续往前推进。'
})

const taskCards = computed(() => {
  const cards = []

  if (!resumeStore.resumes.length) {
    cards.push({
      title: '创建第一份简历',
      description: '先准备一个可以持续迭代的基础版本，后面投递和面试都围绕它展开。',
      cta: '打开简历编辑器',
      to: '/editor',
      accent: true,
    })
  } else {
    cards.push({
      title: '继续编辑最近简历',
      description: latestResume.value ? `最近更新的是《${latestResume.value.title}》，可以继续补充项目和经历。` : '回到简历编辑器继续完善内容。',
      cta: '继续编辑',
      to: '/editor',
      accent: false,
    })
  }

  cards.push({
    title: '新增一条投递',
    description: '把岗位、渠道、状态、关联简历和下一步动作一起记录下来。',
    cta: '打开投递新建弹窗',
    to: { path: '/applications', query: { create: '1' } },
    accent: true,
  })

  cards.push({
    title: applicationStats.todo_count > 0 ? '先处理待跟进岗位' : '检查投递进度',
    description: applicationStats.todo_count > 0
      ? `有 ${applicationStats.todo_count} 条投递已经到了该继续推进的时候。`
      : '快速查看最近的岗位进展，避免投出去就忘了跟进。',
    cta: '进入投递工作台',
    to: { path: '/applications', query: { quick: applicationStats.todo_count > 0 ? 'todo' : 'all' } },
    accent: false,
  })

  cards.push({
    title: interviewStats.pending_review_count > 0 ? '复盘最近面试' : '准备一场新的面试记录',
    description: interviewStats.pending_review_count > 0
      ? `当前有 ${interviewStats.pending_review_count} 场面试还没复盘，建议尽快补上。`
      : '如果已经开始面试，可以把每一场都整理成持续编辑的记录文档。',
    cta: '进入面试记录',
    to: { path: '/interviews', query: interviewStats.pending_review_count > 0 ? { quick: 'pending' } : { create: '1' } },
    accent: false,
  })

  return cards
})

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
    const stats = await requestJson('/api/applications/stats/overview')
    Object.assign(applicationStats, stats || {})
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
    const stats = await requestJson('/api/interviews/stats/overview')
    Object.assign(interviewStats, stats || {})
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
