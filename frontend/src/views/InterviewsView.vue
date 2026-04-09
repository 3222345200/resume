<template>
  <main class="interviews-page">
    <section class="interviews-shell">
      <aside class="interviews-sidebar">
        <div class="interviews-card">
          <div class="brand-badge interviews-brand">
            <img class="brand-logo" :src="brandMark" alt="OfferPilot" />
            <div>
              <strong>OfferPilot</strong>
              <p>面试记录工作台</p>
            </div>
          </div>
          <nav class="interviews-nav">
            <RouterLink v-for="item in navItems" :key="item.to" class="interviews-nav-link" :to="item.to">{{ item.label }}</RouterLink>
          </nav>
        </div>

        <div class="interviews-card">
          <div class="interviews-head">
            <div>
              <p class="eyebrow">Quick Views</p>
              <h2>快捷视图</h2>
            </div>
            <button class="primary-button" type="button" @click="openCreateDialog">新建</button>
          </div>
          <div class="interviews-quick-grid">
            <button
              v-for="view in quickViews"
              :key="view.id"
              class="interviews-quick-card"
              :class="{ 'is-active': activeQuickView === view.id }"
              type="button"
              @click="activeQuickView = view.id"
            >
              <span>{{ view.label }}</span>
              <strong>{{ quickCount(view.id) }}</strong>
            </button>
          </div>
        </div>

        <div class="interviews-card interviews-list-panel">
          <div class="interviews-head">
            <h2>面试记录</h2>
            <span>{{ filteredInterviews.length }} 条</span>
          </div>
          <label class="interviews-search">
            <input v-model="filters.q" type="text" placeholder="公司 / 岗位 / 轮次" @keyup.enter="loadInterviews()" />
          </label>
          <div class="interviews-filter-grid">
            <CustomSelect v-model="filters.result" :options="resultFilterOptions" placeholder="全部结果" />
            <CustomSelect v-model="filters.interview_type" :options="typeFilterOptions" placeholder="全部形式" />
            <CustomSelect v-model="filters.reviewed" :options="reviewFilterOptions" placeholder="全部复盘" />
            <CustomSelect v-model="filters.application_id" :options="applicationFilterOptions" placeholder="全部投递" />
          </div>
          <div class="interviews-actions">
            <button class="ghost-button" type="button" @click="resetFilters">重置</button>
            <button class="ghost-button" type="button" @click="loadInterviews()">筛选</button>
          </div>
          <p v-if="message" class="interviews-message">{{ message }}</p>
          <div class="interviews-list">
            <button
              v-for="item in filteredInterviews"
              :key="item.id"
              class="interviews-list-card"
              :class="{ 'is-active': selectedId === item.id }"
              type="button"
              @click="selectInterview(item.id)"
            >
              <div class="interviews-list-top">
                <strong>{{ item.company_name }}</strong>
                <span class="interviews-result-badge" :class="`is-${item.result}`">{{ resultLabel(item.result) }}</span>
              </div>
              <p>{{ item.job_title }}</p>
              <small>{{ item.round_name }} · {{ typeLabel(item.interview_type) }} · {{ formatDateTime(item.scheduled_at) }}</small>
            </button>
            <div v-if="!loadingList && !filteredInterviews.length" class="interviews-empty">
              <h3>暂无面试记录</h3>
              <p>可以直接新建，或者从投递页带着 `application_id` 进入。</p>
            </div>
          </div>
        </div>
      </aside>

      <section class="interviews-main">
        <div class="interviews-editor-stage">
          <header class="interviews-main-header interviews-main-header-compact">
            <div class="interviews-workspace-title">
              <h1>面试记录工作台</h1>
              <p>把一次面试当成一篇持续编辑的文档来记录。</p>
            </div>
            <div class="interviews-header-mini-stats">
              <span>全部 {{ stats.total_count }}</span>
              <span>待复盘 {{ stats.pending_review_count }}</span>
            </div>
          </header>

          <section v-if="detailDraft" class="interviews-editor-canvas interviews-editor-canvas-doc">
            <header class="interviews-doc-shell-head">
              <div class="interviews-doc-shell-title">INTERVIEW DOC</div>
              <div class="interviews-doc-toolbar">
                <button class="ghost-button interviews-toolbar-btn" type="button" @click="openEditDialog">编辑基础信息</button>
                <button class="primary-button" type="button" :disabled="savingDetail" @click="saveInterview">
                  {{ savingDetail ? '保存中...' : '保存文档' }}
                </button>
              </div>
            </header>

            <header class="interviews-doc-header interviews-doc-header-editor interviews-doc-header-freeform">
              <div class="interviews-doc-heading">
                <h2>{{ documentTitle }}</h2>
                <p class="interviews-doc-subtitle">
                  时间：{{ formatDateTime(detailDraft.scheduled_at) }} · 形式：{{ typeLabel(detailDraft.interview_type) }} · 状态：{{ resultLabel(detailDraft.result) }}
                </p>
              </div>
            </header>

            <section class="interviews-freeform-stage">
              <RichTextEditor
                v-model="detailDraft.document_content"
                class="interviews-doc-editor"
                placeholder="点击或按 '/' 开始输入面试记录..."
              />
            </section>
          </section>

          <section v-else class="interviews-editor-canvas interviews-empty-state interviews-editor-canvas-doc">
            <h2>选择一场面试开始记录</h2>
            <p>中间区域会以连续文档方式承载准备、过程、复盘和后续行动。</p>
          </section>
        </div>
      </section>

      <aside class="interviews-rail">
        <section class="interviews-card">
          <p class="eyebrow">Context</p>
          <h2>关联投递信息</h2>
          <template v-if="detailDraft">
            <dl class="interviews-summary">
              <div><dt>公司</dt><dd>{{ detailDraft.company_name }}</dd></div>
              <div><dt>岗位</dt><dd>{{ detailDraft.job_title }}</dd></div>
              <div><dt>状态</dt><dd>{{ detailDraft.application_status }}</dd></div>
              <div><dt>简历</dt><dd>{{ detailDraft.resume_title || '未关联' }}</dd></div>
            </dl>
            <RouterLink class="ghost-button" :to="`/applications?application_id=${detailDraft.application_id}`">查看投递详情</RouterLink>
          </template>
          <p v-else class="interviews-muted">选中面试后，这里展示上下文摘要。</p>
        </section>

        <section class="interviews-card">
          <p class="eyebrow">Actions</p>
          <h2>快捷操作</h2>
          <div class="interviews-rail-actions">
            <button class="ghost-button" type="button" :disabled="!detailDraft" @click="insertInterviewInfoBlock">插入面试信息</button>
            <button class="ghost-button" type="button" :disabled="!detailDraft" @click="insertQuestionTemplate">添加问题块</button>
            <button class="ghost-button" type="button" :disabled="!detailDraft" @click="insertReviewTemplate">插入复盘模板</button>
            <button class="ghost-button" type="button" :disabled="!detailDraft" @click="insertTodoTemplate">插入待办</button>
            <button class="primary-button" type="button" :disabled="!detailDraft || savingDetail" @click="saveInterview">保存文档</button>
          </div>
        </section>

        <section class="interviews-card">
          <p class="eyebrow">Workspace</p>
          <h2>辅助入口</h2>
          <div class="interviews-rail-actions">
            <RouterLink class="ghost-button" to="/dashboard">返回工作台</RouterLink>
            <button class="ghost-button" type="button" @click="handleLogout">退出登录</button>
          </div>
        </section>
      </aside>
    </section>

    <div v-if="dialogOpen" class="interviews-dialog-mask" @click.self="closeDialog">
      <div class="interviews-dialog">
        <div class="interviews-head">
          <div>
            <p class="eyebrow">{{ editingId ? 'Edit Interview' : 'Create Interview' }}</p>
            <h2>{{ editingId ? '编辑面试信息' : '新建面试记录' }}</h2>
          </div>
          <button class="interviews-dialog-close" type="button" @click="closeDialog">×</button>
        </div>
        <div class="interviews-dialog-grid">
          <CustomSelect v-model="form.application_id" :options="applicationFormOptions" placeholder="请选择关联投递" />
          <CustomSelect v-model="form.resume_id" :options="resumeFormOptions" placeholder="自动沿用投递简历" />
          <input v-model="form.round_name" type="text" placeholder="轮次名称" />
          <input v-model.number="form.round_index" type="number" min="1" max="99" />
          <DateTimePicker v-model="form.scheduled_at" type="datetime-local" placeholder="选择时间" />
          <CustomSelect v-model="form.interview_type" :options="typeOptions" placeholder="选择形式" />
          <CustomSelect v-model="form.result" :options="resultOptions" placeholder="选择结果" />
          <input v-model.number="form.duration_minutes" type="number" min="0" max="720" placeholder="时长（分钟）" />
          <input v-model="form.interviewer_name" type="text" placeholder="面试官" />
          <input v-model="form.interviewer_role" type="text" placeholder="面试官角色" />
          <textarea v-model="form.preparation_note" class="full-row" rows="4" placeholder="准备重点"></textarea>
        </div>
        <p v-if="dialogMessage" class="interviews-message">{{ dialogMessage }}</p>
        <div class="interviews-actions">
          <button class="ghost-button" type="button" @click="closeDialog">取消</button>
          <button class="primary-button" type="button" :disabled="savingDialog" @click="saveDialog">
            {{ savingDialog ? '保存中...' : editingId ? '保存修改' : '创建面试' }}
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import brandMark from '../assets/brand-mark.svg'
import { requestJson } from '../api/request'
import CustomSelect from '../components/CustomSelect.vue'
import DateTimePicker from '../components/DateTimePicker.vue'
import RichTextEditor from '../components/RichTextEditor.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const navItems = [
  { to: '/dashboard', label: '工作台' },
  { to: '/editor', label: '简历管理' },
  { to: '/applications', label: '投递管理' },
  { to: '/interviews', label: '面试记录' },
]

const quickViews = [
  { id: 'all', label: '全部面试' },
  { id: 'week', label: '本周面试' },
  { id: 'pending', label: '待复盘' },
  { id: 'passed', label: '已通过' },
  { id: 'rejected', label: '已淘汰' },
]

const resultOptions = [
  { value: 'scheduled', label: '待进行' },
  { value: 'completed', label: '已完成' },
  { value: 'passed', label: '通过' },
  { value: 'rejected', label: '淘汰' },
  { value: 'offer', label: 'Offer' },
]

const typeOptions = [
  { value: 'online', label: '线上' },
  { value: 'phone', label: '电话' },
  { value: 'onsite', label: '现场' },
  { value: 'video', label: '视频' },
]

const stats = ref({ total_count: 0, this_week_count: 0, upcoming_count: 0, completed_count: 0, pending_review_count: 0 })
const applications = ref([])
const resumes = ref([])
const interviews = ref([])
const detailDraft = ref(null)
const selectedId = ref('')
const activeQuickView = ref('all')
const loadingList = ref(false)
const savingDetail = ref(false)
const savingDialog = ref(false)
const dialogOpen = ref(false)
const editingId = ref('')
const message = ref('')
const dialogMessage = ref('')

const filters = reactive({ q: '', result: '', interview_type: '', reviewed: '', application_id: '' })
const form = reactive({
  application_id: '',
  resume_id: '',
  round_name: '',
  round_index: 1,
  scheduled_at: '',
  interview_type: 'online',
  duration_minutes: 60,
  interviewer_name: '',
  interviewer_role: '',
  result: 'scheduled',
  preparation_note: '',
})

const filteredInterviews = computed(() => interviews.value.filter((item) => matchQuickView(item, activeQuickView.value)))
const resultFilterOptions = computed(() => [{ label: '全部结果', value: '' }, ...resultOptions])
const typeFilterOptions = computed(() => [{ label: '全部形式', value: '' }, ...typeOptions])
const reviewFilterOptions = computed(() => [{ label: '全部复盘', value: '' }, { label: '已复盘', value: 'true' }, { label: '待复盘', value: 'false' }])
const applicationFilterOptions = computed(() => [{ label: '全部投递', value: '' }, ...applications.value.map((item) => ({ label: `${item.company_name} / ${item.job_title}`, value: item.id }))])
const applicationFormOptions = computed(() => applications.value.map((item) => ({ label: `${item.company_name} / ${item.job_title}`, value: item.id })))
const resumeFormOptions = computed(() => [{ label: '自动沿用投递简历', value: '' }, ...resumes.value.map((item) => ({ label: item.title, value: item.id }))])
const documentTitle = computed(() => {
  if (!detailDraft.value) return ''
  return `${detailDraft.value.company_name} · ${detailDraft.value.job_title} · ${detailDraft.value.round_name}`
})
const resultLabel = (value) => resultOptions.find((item) => item.value === value)?.label || value
const typeLabel = (value) => typeOptions.find((item) => item.value === value)?.label || value
const formatDateTime = (value) => !value ? '待补充' : (Number.isNaN(new Date(value).getTime()) ? value : new Date(value).toLocaleString('zh-CN', { hour12: false }))
const toIso = (value) => value ? new Date(value).toISOString() : null

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function weekStart() {
  const now = new Date()
  const start = new Date(now)
  start.setDate(now.getDate() - ((now.getDay() + 6) % 7))
  start.setHours(0, 0, 0, 0)
  return start
}

function matchQuickView(item, view) {
  if (view === 'week') return item.scheduled_at && new Date(item.scheduled_at) >= weekStart()
  if (view === 'pending') return !item.is_reviewed
  if (view === 'passed') return item.result === 'passed' || item.result === 'offer'
  if (view === 'rejected') return item.result === 'rejected'
  return true
}

function quickCount(view) {
  return interviews.value.filter((item) => matchQuickView(item, view)).length
}

function queryString() {
  const params = new URLSearchParams()
  if (filters.q.trim()) params.set('q', filters.q.trim())
  if (filters.result) params.set('result', filters.result)
  if (filters.interview_type) params.set('interview_type', filters.interview_type)
  if (filters.reviewed) params.set('reviewed', filters.reviewed)
  if (filters.application_id) params.set('application_id', filters.application_id)
  return params.toString()
}

function buildDefaultDocument(detail) {
  const lines = [
    `<p><strong>可问时间：</strong>${escapeHtml(formatDateTime(detail.scheduled_at))} · <strong>形式：</strong>${escapeHtml(typeLabel(detail.interview_type))} · <strong>结果：</strong>${escapeHtml(resultLabel(detail.result))}</p>`,
    '<p><br></p>',
    '<p><strong>1. 面试信息</strong></p>',
    `<p>${escapeHtml(detail.preparation_note || '时间：\n面试官：\n准备状态：')}</p>`,
    '<p><br></p>',
    '<p><strong>2. 问题记录</strong></p>',
    '<p>点击开始记录问题、回答、追问和自评。</p>',
    '<p><br></p>',
    '<p><strong>3. 自由笔记</strong></p>',
    `<p>${escapeHtml(detail.free_note || '记录现场反馈、氛围和零散观察。')}</p>`,
    '<p><br></p>',
    '<p><strong>4. 复盘总结</strong></p>',
    `<p>${escapeHtml(detail.strength_note || '')}</p>`,
    `<p>${escapeHtml(detail.weakness_note || '')}</p>`,
    `<p>${escapeHtml(detail.missing_knowledge_note || '')}</p>`,
    `<p>${escapeHtml(detail.next_round_prep_note || '')}</p>`,
    '<p><br></p>',
    '<p><strong>5. 后续行动</strong></p>',
    `<p>${escapeHtml(detail.follow_up_action || '发送感谢信\n跟进 HR\n整理下一轮准备')}</p>`,
  ]
  return lines.join('')
}

async function loadStats() {
  stats.value = await requestJson('/api/interviews/stats/overview')
}

async function loadApplications() {
  applications.value = (await requestJson('/api/applications')).items || []
}

async function loadResumes() {
  resumes.value = (await requestJson('/api/resumes')).items || []
}

async function loadInterviews(preferredId = selectedId.value) {
  loadingList.value = true
  message.value = ''
  try {
    const result = await requestJson(`/api/interviews${queryString() ? `?${queryString()}` : ''}`)
    interviews.value = result.items || []
    const routeInterviewId = typeof route.query.interview_id === 'string' ? route.query.interview_id : ''
    const nextId = [routeInterviewId, preferredId, interviews.value[0]?.id].find((id) => id && interviews.value.some((item) => item.id === id)) || ''
    if (nextId) {
      await selectInterview(nextId)
    } else {
      selectedId.value = ''
      detailDraft.value = null
    }
  } catch (error) {
    message.value = error.message || '面试列表加载失败'
  } finally {
    loadingList.value = false
  }
}

async function selectInterview(id) {
  if (!id) return
  selectedId.value = id
  const detail = await requestJson(`/api/interviews/${id}`)
  detailDraft.value = {
    ...detail,
    scheduled_at: detail.scheduled_at || '',
    follow_up_at: detail.follow_up_at || '',
    document_content: detail.document_content || buildDefaultDocument(detail),
  }
}

function buildPayload(source) {
  return {
    application_id: source.application_id,
    resume_id: source.resume_id || null,
    round_name: source.round_name?.trim() || '',
    round_index: Number(source.round_index) || 1,
    scheduled_at: toIso(source.scheduled_at),
    interview_type: source.interview_type,
    duration_minutes: Number(source.duration_minutes) || 0,
    interviewer_name: source.interviewer_name?.trim() || '',
    interviewer_role: source.interviewer_role?.trim() || '',
    result: source.result,
    is_reviewed: !!source.is_reviewed,
    document_content: source.document_content || '',
    preparation_note: source.preparation_note?.trim() || '',
    free_note: source.free_note?.trim() || '',
    strength_note: source.strength_note?.trim() || '',
    weakness_note: source.weakness_note?.trim() || '',
    missing_knowledge_note: source.missing_knowledge_note?.trim() || '',
    next_round_prep_note: source.next_round_prep_note?.trim() || '',
    follow_up_action: source.follow_up_action?.trim() || '',
    follow_up_at: toIso(source.follow_up_at),
    need_thank_you: !!source.need_thank_you,
    need_follow_up: !!source.need_follow_up,
  }
}

function openCreateDialog() {
  editingId.value = ''
  dialogMessage.value = ''
  Object.assign(form, {
    application_id: filters.application_id || (typeof route.query.application_id === 'string' ? route.query.application_id : '') || '',
    resume_id: '',
    round_name: '',
    round_index: 1,
    scheduled_at: '',
    interview_type: 'online',
    duration_minutes: 60,
    interviewer_name: '',
    interviewer_role: '',
    result: 'scheduled',
    preparation_note: '',
  })
  dialogOpen.value = true
}

function openEditDialog() {
  if (!detailDraft.value) return
  editingId.value = detailDraft.value.id
  dialogMessage.value = ''
  Object.assign(form, {
    application_id: detailDraft.value.application_id || '',
    resume_id: detailDraft.value.resume_id || '',
    round_name: detailDraft.value.round_name || '',
    round_index: detailDraft.value.round_index || 1,
    scheduled_at: detailDraft.value.scheduled_at || '',
    interview_type: detailDraft.value.interview_type || 'online',
    duration_minutes: detailDraft.value.duration_minutes || 60,
    interviewer_name: detailDraft.value.interviewer_name || '',
    interviewer_role: detailDraft.value.interviewer_role || '',
    result: detailDraft.value.result || 'scheduled',
    preparation_note: detailDraft.value.preparation_note || '',
  })
  dialogOpen.value = true
}

function closeDialog() {
  dialogOpen.value = false
  dialogMessage.value = ''
  editingId.value = ''
}

async function saveDialog() {
  if (!form.application_id) {
    dialogMessage.value = '请先选择关联投递。'
    return
  }
  savingDialog.value = true
  try {
    const path = editingId.value ? `/api/interviews/${editingId.value}` : '/api/interviews'
    const method = editingId.value ? 'PUT' : 'POST'
    const basePayload = buildPayload(editingId.value ? detailDraft.value : form)
    const saved = await requestJson(path, {
      method,
      body: JSON.stringify({
        ...basePayload,
        ...buildPayload(form),
        document_content: editingId.value ? detailDraft.value.document_content || '' : '',
      }),
    })
    closeDialog()
    await Promise.all([loadStats(), loadApplications(), loadInterviews(saved.id)])
  } catch (error) {
    dialogMessage.value = error.message || '保存失败'
  } finally {
    savingDialog.value = false
  }
}

async function saveInterview() {
  if (!detailDraft.value) return
  savingDetail.value = true
  message.value = ''
  try {
    await requestJson(`/api/interviews/${detailDraft.value.id}`, { method: 'PUT', body: JSON.stringify(buildPayload(detailDraft.value)) })
    await Promise.all([loadStats(), loadApplications(), loadInterviews(detailDraft.value.id)])
  } catch (error) {
    message.value = error.message || '保存失败'
  } finally {
    savingDetail.value = false
  }
}

function appendToDocument(html) {
  if (!detailDraft.value) return
  const current = detailDraft.value.document_content || ''
  detailDraft.value.document_content = `${current}${current ? '<p><br></p>' : ''}${html}`
}

function insertInterviewInfoBlock() {
  if (!detailDraft.value) return
  appendToDocument([
    '<p><strong>面试信息</strong></p>',
    `<p>时间：${escapeHtml(formatDateTime(detailDraft.value.scheduled_at))}</p>`,
    `<p>形式：${escapeHtml(typeLabel(detailDraft.value.interview_type))}</p>`,
    `<p>面试官：${escapeHtml(detailDraft.value.interviewer_name || '待补充')}</p>`,
    `<p>准备状态：${escapeHtml(detailDraft.value.preparation_note || '待补充')}</p>`,
  ].join(''))
}

function insertQuestionTemplate() {
  appendToDocument([
    '<p><strong>问题记录</strong></p>',
    '<p>问题内容：</p>',
    '<p>我的回答：</p>',
    '<p>面试官追问：</p>',
    '<p>自评：</p>',
  ].join(''))
}

function insertReviewTemplate() {
  appendToDocument([
    '<p><strong>复盘总结</strong></p>',
    '<ul>',
    '<li>答得好的地方：</li>',
    '<li>卡住的地方：</li>',
    '<li>暴露的短板：</li>',
    '<li>下轮需要补什么：</li>',
    '</ul>',
  ].join(''))
}

function insertTodoTemplate() {
  appendToDocument([
    '<p><strong>后续行动</strong></p>',
    '<ul>',
    '<li>发送感谢信</li>',
    '<li>跟进 HR</li>',
    '<li>准备下一轮面试</li>',
    '</ul>',
  ].join(''))
}

async function resetFilters() {
  filters.q = ''
  filters.result = ''
  filters.interview_type = ''
  filters.reviewed = ''
  filters.application_id = typeof route.query.application_id === 'string' ? route.query.application_id : ''
  activeQuickView.value = 'all'
  await loadInterviews()
}

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}

onMounted(async () => {
  filters.application_id = typeof route.query.application_id === 'string' ? route.query.application_id : ''
  await Promise.all([loadStats(), loadApplications(), loadResumes()])
  await loadInterviews()
})
</script>
