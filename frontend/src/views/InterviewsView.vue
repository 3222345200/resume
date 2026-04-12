<template>
  <main class="interviews-page interviews-page-modern">
    <section class="interviews-shell">
      <aside class="interviews-primary-nav">
        <div class="interviews-primary-brand" title="OfferPilot">
          <img class="brand-logo" :src="brandMark" alt="OfferPilot" />
        </div>

        <nav class="interviews-primary-links" aria-label="Primary navigation">
          <RouterLink
            v-for="item in primaryNavItems"
            :key="item.to"
            class="interviews-primary-link"
            :class="{ 'is-active': item.to === '/interviews' }"
            :to="item.to"
            :title="item.label"
          >
            <span class="interviews-primary-icon" v-html="item.icon"></span>
            <span class="sr-only">{{ item.label }}</span>
          </RouterLink>
        </nav>
      </aside>

      <div v-if="isMobileWorkspace" class="workspace-mobile-switcher" role="tablist" aria-label="移动端面试工作区切换">
        <button type="button" class="workspace-mobile-switch" :class="{ 'is-active': activeMobilePanel === 'sidebar' }" @click="activeMobilePanel = 'sidebar'">列表</button>
        <button type="button" class="workspace-mobile-switch" :class="{ 'is-active': activeMobilePanel === 'main' }" @click="activeMobilePanel = 'main'">记录</button>
        <button type="button" class="workspace-mobile-switch" :class="{ 'is-active': activeMobilePanel === 'rail' }" @click="activeMobilePanel = 'rail'">信息</button>
      </div>

      <aside class="interviews-sidebar" :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'sidebar' }">
          <div class="interviews-sidebar-shell">
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

          <button class="primary-button interviews-sidebar-primary" type="button" @click="openCreateDialog">新建面试</button>

          <section class="interviews-card interviews-card-soft">
            <div class="interviews-card-head">
              <div>
                <p class="eyebrow">Quick Views</p>
                <h2>快捷视图</h2>
              </div>
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
        </section>

        <section class="interviews-card interviews-card-soft interviews-trend-card">
          <div class="interviews-card-head">
            <div>
              <p class="eyebrow">Snapshot</p>
              <h2>近期面试卡片</h2>
            </div>
            <span class="interviews-mini-pill">{{ stats.total_count }} 场</span>
          </div>

          <div class="interviews-trend-metrics">
            <div>
              <span>本周面试</span>
              <strong>{{ stats.this_week_count }}</strong>
            </div>
            <div>
              <span>待复盘</span>
              <strong>{{ stats.pending_review_count }}</strong>
            </div>
            <div>
              <span>即将开始</span>
              <strong>{{ stats.upcoming_count }}</strong>
            </div>
          </div>

          <div class="interviews-trend-chart">
            <svg viewBox="0 0 220 84" aria-hidden="true">
              <defs>
                <linearGradient id="interviewTrendFill" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stop-color="rgba(31,122,114,0.22)" />
                  <stop offset="100%" stop-color="rgba(31,122,114,0.02)" />
                </linearGradient>
              </defs>
              <path class="interviews-trend-grid-line" d="M0 70 H220" />
              <path class="interviews-trend-area" :d="trendAreaPath" />
              <polyline class="interviews-trend-line" :points="trendPoints" />
            </svg>
          </div>
        </section>

        <section class="interviews-card interviews-card-soft interviews-list-panel">
          <div class="interviews-card-head">
            <div>
              <p class="eyebrow">Quick Views</p>
              <h2>近期面试卡片</h2>
            </div>
            <span class="interviews-mini-pill">{{ filteredInterviews.length }} 条</span>
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

          <p v-if="message" class="interviews-message">{{ message }}</p>

          <div class="interviews-list">
            <button
              v-for="item in filteredInterviews"
              :key="item.id"
              class="interviews-list-card"
              :class="{ 'is-active': selectedId === item.id }"
              type="button"
              @click="handleSelectInterview(item.id)"
            >
              <div class="interviews-list-top">
                <strong>{{ item.company_name }}</strong>
                <span class="interviews-result-badge" :class="`is-${item.result}`">{{ resultLabel(item.result) }}</span>
              </div>
              <p>{{ item.job_title }}</p>
              <small>{{ item.round_name || `第 ${item.round_index || 1} 轮` }} · {{ typeLabel(item.interview_type) }} · {{ formatDateTime(item.scheduled_at) }}</small>
            </button>

            <div v-if="!loadingList && !filteredInterviews.length" class="interviews-empty">
              <h3>暂无面试记录</h3>
              <p>可以直接新建，或者从投递页进入。</p>
            </div>
          </div>
        </section>
        </div>
      </aside>

      <section class="interviews-main" :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'main' }">
        <div v-if="detailDraft" class="interviews-workspace" :class="{ 'is-outline-collapsed': isOutlinePanelCollapsed }">
          <aside class="interviews-outline-panel" :class="{ 'is-collapsed': isOutlinePanelCollapsed }">
            <section class="interviews-outline-card">
              <div class="interviews-outline-head">
                <div v-if="!isOutlinePanelCollapsed">
                  <p class="eyebrow">Outline</p>
                  <h2>文档目录</h2>
                  <p class="interviews-outline-copy">根据正文里的标题自动生成，点击即可快速定位。</p>

                </div>
                <button
                  class="interviews-outline-panel-toggle"
                  type="button"
                  :aria-expanded="String(!isOutlinePanelCollapsed)"
                  @click="toggleOutlinePanel"
                >
                  <span aria-hidden="true">{{ isOutlinePanelCollapsed ? '›' : '‹' }}</span>
                  <span class="sr-only">{{ isOutlinePanelCollapsed ? '展开目录' : '收起目录' }}</span>
                </button>
              </div>

              <div v-if="!isOutlinePanelCollapsed" class="interviews-outline-list">
                <div
                  v-for="item in visibleOutlineItems"
                  :key="item.id"
                  class="interviews-outline-item"
                  :class="`is-level-${item.level}`"
                  @click="handleOutlineItemClick(item)"
                  @keydown.enter.prevent="handleOutlineItemClick(item)"
                  @keydown.space.prevent="handleOutlineItemClick(item)"
                  role="button"
                  tabindex="0"
                >
                  <span
                    class="interviews-outline-indent"
                    :style="{ width: `${Math.max(item.depth - 1, 0) * 10}px` }"
                    aria-hidden="true"
                  ></span>
                  <button
                    v-if="item.hasChildren"
                    type="button"
                    class="interviews-outline-caret"
                    :class="{ 'is-collapsed': item.isCollapsed }"
                    :aria-expanded="String(!item.isCollapsed)"
                    @click.stop="toggleOutlineBranch(item.id)"
                  >
                    <span aria-hidden="true">▸</span>
                    <span class="sr-only">{{ item.isCollapsed ? '展开子标题' : '收起子标题' }}</span>
                  </button>
                  <span v-else class="interviews-outline-caret interviews-outline-caret-placeholder" aria-hidden="true"></span>
                  <span class="interviews-outline-branch" aria-hidden="true">
                    <span class="interviews-outline-node"></span>
                  </span>
                  <span class="interviews-outline-label">{{ item.text }}</span>
                </div>
                <p v-if="!outlineItems.length" class="interviews-muted">先在正文里插入 H1/H2/H3 标题，目录会自动显示在这里。</p>
              </div>
            </section>
          </aside>

          <section class="interviews-editor-panel">
            <section class="interviews-editor-canvas interviews-editor-canvas-doc">
              <header class="interviews-doc-shell-head">
                <div class="interviews-doc-shell-title">INTERVIEW DOC</div>
                <div class="interviews-doc-toolbar">
                  <span class="interviews-doc-save-state" :class="`is-${autosaveState}`">{{ autosaveText }}</span>
                  <button class="primary-button" type="button" :disabled="savingDetail" @click="saveInterview">
                    {{ savingDetail ? '保存中...' : '保存文档' }}
                  </button>
                </div>
              </header>

              <header class="interviews-doc-header interviews-doc-header-editor interviews-doc-header-freeform">
                <div class="interviews-doc-heading">
                  <p class="interviews-doc-kicker">面试记录工作台</p>
                  <h2>{{ documentTitle }}</h2>
                  <p class="interviews-doc-subtitle">
                    时间：{{ formatDateTime(detailDraft.scheduled_at) }} · 形式：{{ typeLabel(detailDraft.interview_type) }} · 状态：{{ resultLabel(detailDraft.result) }}
                  </p>
                </div>
              </header>

              <section class="interviews-freeform-stage">
                <RichTextEditor
                  ref="editorRef"
                  v-model="detailDraft.document_content"
                  class="interviews-doc-editor"
                  :enable-section-folding="true"
                  :enable-tables="true"
                  placeholder="点击开始记录面试过程、问题、复盘和后续行动..."
                  @table-state-change="handleTableStateChange"
                  @request-insert-table="openTableDialog"
                />
              </section>
            </section>
          </section>
        </div>

        <section v-else class="interviews-editor-canvas interviews-empty-state interviews-editor-canvas-doc">
          <h2>选择一场面试开始记录</h2>
          <p>左侧是工作台和面试卡片，中间是目录与正文编辑区，右侧则是基础信息编辑面板。</p>
        </section>
      </section>

      <aside class="interviews-rail" :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'rail' }">
        <template v-if="detailDraft">
          <section class="interviews-card interviews-card-plain">
            <div class="interviews-card-head">
              <div>
                <p class="eyebrow">Context &amp; Info</p>
                <h2>关联投递信息</h2>
              </div>
            </div>

            <dl class="interviews-summary">
              <div><dt>公司</dt><dd>{{ detailDraft.company_name }}</dd></div>
              <div><dt>岗位</dt><dd>{{ detailDraft.job_title }}</dd></div>
              <div><dt>状态</dt><dd>{{ detailDraft.application_status }}</dd></div>
              <div><dt>简历</dt><dd>{{ detailDraft.resume_title || '未关联' }}</dd></div>
            </dl>
          </section>

          <section class="interviews-card interviews-card-plain">
            <div class="interviews-card-head">
              <div>
                <p class="eyebrow">Editor</p>
                <h2>基础信息编辑</h2>
              </div>
            </div>

            <div class="interviews-rail-form">
              <label>
                <span>轮次名称</span>
                <input v-model="detailDraft.round_name" type="text" placeholder="例如：技术一面 / HR 面" />
              </label>

              <label>
                <span>轮次序号</span>
                <input v-model.number="detailDraft.round_index" type="number" min="1" max="99" />
              </label>

              <label>
                <span>预约时间</span>
                <DateTimePicker v-model="detailDraft.scheduled_at" type="datetime-local" placeholder="日 / 时 / 分" />
              </label>

              <label>
                <span>面试形式</span>
                <CustomSelect v-model="detailDraft.interview_type" :options="typeOptions" placeholder="选择形式" />
              </label>

              <label>
                <span>面试状态</span>
                <CustomSelect v-model="detailDraft.result" :options="resultOptions" placeholder="选择状态" />
              </label>

              <label>
                <span>面试时长（分钟）</span>
                <input v-model.number="detailDraft.duration_minutes" type="number" min="0" max="720" />
              </label>

              <label>
                <span>面试官</span>
                <input v-model="detailDraft.interviewer_name" type="text" placeholder="请输入面试官姓名" />
              </label>

              <label>
                <span>面试官角色</span>
                <input v-model="detailDraft.interviewer_role" type="text" placeholder="例如：技术负责人" />
              </label>

              <label class="full-row">
                <span>准备重点</span>
                <textarea v-model="detailDraft.preparation_note" rows="4" placeholder="记录面试前重点准备内容"></textarea>
              </label>

              <label class="full-row">
                <span>后续行动</span>
                <textarea v-model="detailDraft.follow_up_action" rows="4" placeholder="记录感谢信、HR 跟进和下一轮准备等"></textarea>
              </label>
            </div>
          </section>

          <section class="interviews-card interviews-card-plain">
            <div class="interviews-card-head">
              <div>
                <p class="eyebrow">Actions</p>
                <h2>结构模板</h2>
              </div>
            </div>

            <p class="interviews-muted">模板会优先插入到当前光标位置；如果还没点进正文，就会追加到文末。</p>

            <div class="interviews-rail-actions">
              <button class="ghost-button" type="button" @click="insertInterviewInfoBlock">插入面试信息</button>
              <button class="ghost-button" type="button" @click="insertQuestionTemplate">添加问题块</button>
              <button class="ghost-button" type="button" @click="insertStarAnswerTemplate">插入 STAR 回答</button>
              <button class="ghost-button" type="button" @click="insertFeedbackTemplate">插入现场反馈</button>
              <button class="ghost-button" type="button" @click="insertReviewTemplate">插入复盘模板</button>
              <button class="ghost-button" type="button" @click="insertTodoTemplate">插入待办</button>
              <button class="primary-button" type="button" :disabled="savingDetail" @click="saveInterview">保存文档</button>
            </div>
          </section>

          <section class="interviews-card interviews-card-plain">
            <div class="interviews-card-head">
              <div>
                <p class="eyebrow">Tables</p>
                <h2>表格工具</h2>
              </div>
            </div>

            <p class="interviews-muted">点击按钮先设置行数、列数，再把表格插入到当前光标位置。插入后可继续增删行列，并拖拽列边调整宽度。</p>

            <div class="interviews-rail-actions">
              <button class="primary-button" type="button" @click="openTableDialog">插入表格</button>
              <button class="ghost-button" type="button" :disabled="!tableState.inTable" @click="addTableRowBefore">上方加一行</button>
              <button class="ghost-button" type="button" :disabled="!tableState.inTable" @click="addTableRowAfter">下方加一行</button>
              <button class="ghost-button" type="button" :disabled="!tableState.inTable" @click="addTableColumnBefore">左侧加一列</button>
              <button class="ghost-button" type="button" :disabled="!tableState.inTable" @click="addTableColumnAfter">右侧加一列</button>
              <button class="ghost-button" type="button" :disabled="!tableState.inTable" @click="removeTableRow">删除当前行</button>
              <button class="ghost-button" type="button" :disabled="!tableState.inTable" @click="removeTableColumn">删除当前列</button>
            </div>

            <p class="interviews-table-state" :class="{ 'is-active': tableState.inTable }">
              {{ tableState.inTable ? `当前表格：${tableState.rows} 行 / ${tableState.cols} 列` : '把光标放进表格单元格后，这里会显示当前表格尺寸。' }}
            </p>
          </section>
        </template>

        <section class="interviews-card interviews-card-plain">
          <div class="interviews-card-head">
            <div>
              <p class="eyebrow">Workspace</p>
              <h2>辅助入口</h2>
            </div>
          </div>

          <div class="interviews-rail-actions">
            <button class="ghost-button" type="button" @click="openCreateDialog">新建面试</button>
            <RouterLink class="ghost-button" :to="detailDraft ? `/applications?application_id=${detailDraft.application_id}` : '/applications'">打开投递详情</RouterLink>
            <RouterLink class="ghost-button" to="/dashboard">返回工作台</RouterLink>
            <button class="ghost-button" type="button" @click="handleLogout">退出登录</button>
          </div>
        </section>
      </aside>
    </section>

    <div v-if="dialogOpen" class="interviews-dialog-mask" @click.self="closeDialog">
      <div class="interviews-dialog">
        <div class="interviews-card-head">
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
          <input v-model="form.interviewer_name" type="text" placeholder="面试官姓名" />
          <input v-model="form.interviewer_role" type="text" placeholder="面试官角色" />
          <textarea v-model="form.preparation_note" class="full-row" rows="4" placeholder="准备重点"></textarea>
        </div>

        <p v-if="dialogMessage" class="interviews-message">{{ dialogMessage }}</p>

        <div class="interviews-actions">
          <button class="ghost-button" type="button" @click="closeDialog">取消</button>
          <button class="primary-button" type="button" :disabled="savingDialog" @click="saveDialog">
            {{ savingDialog ? '保存中...' : '创建面试' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="tableDialogOpen" class="interviews-dialog-mask" @click.self="closeTableDialog">
      <div class="interviews-dialog interviews-table-dialog">
        <div class="interviews-card-head">
          <div>
            <p class="eyebrow">Insert Table</p>
            <h2>插入表格</h2>
          </div>
          <button class="interviews-dialog-close" type="button" @click="closeTableDialog">×</button>
        </div>

        <div class="interviews-dialog-grid">
          <label>
            <span>行数</span>
            <input v-model.number="tableDraft.rows" type="number" min="1" max="20" />
          </label>

          <label>
            <span>列数</span>
            <input v-model.number="tableDraft.cols" type="number" min="1" max="8" />
          </label>

          <label class="full-row interviews-checkbox-row">
            <input v-model="tableDraft.withHeader" type="checkbox" />
            <span>首行为表头</span>
          </label>
        </div>

        <p v-if="tableDialogMessage" class="interviews-message">{{ tableDialogMessage }}</p>

        <div class="interviews-actions">
          <button class="ghost-button" type="button" @click="closeTableDialog">取消</button>
          <button class="primary-button" type="button" @click="confirmInsertTable">插入表格</button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import brandMark from '../assets/logo.png'
import { requestJson } from '../api/request'
import CustomSelect from '../components/CustomSelect.vue'
import DateTimePicker from '../components/DateTimePicker.vue'
import RichTextEditor from '../components/RichTextEditor.vue'
import { useAuthStore } from '../stores/auth'
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const editorRef = ref(null)

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
const tableDraft = reactive({ rows: 3, cols: 3, withHeader: true })
const tableState = ref({ inTable: false, rows: 0, cols: 0 })
const detailDraft = ref(null)
const selectedId = ref('')
const activeMobilePanel = ref('main')
const isMobileWorkspace = ref(false)
const activeQuickView = ref('all')
const loadingList = ref(false)
const savingDetail = ref(false)
const savingDialog = ref(false)
const dialogOpen = ref(false)
const tableDialogOpen = ref(false)
const message = ref('')
const dialogMessage = ref('')
const tableDialogMessage = ref('')
const isOutlinePanelCollapsed = ref(false)
const collapsedOutlineIds = ref({})
const autosaveState = ref('saved')
const autosaveError = ref('')
const lastSavedSnapshot = ref('')
const isHydratingDraft = ref(false)

let autosaveTimer = null
let activeSavePromise = null
let queuedAutosave = false
let filterTimer = null
const AUTOSAVE_DELAY = 1500
const FILTER_DELAY = 250

const QUICK_VIEW_IDS = new Set(['all', 'week', 'pending', 'passed', 'rejected'])

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
  return `${detailDraft.value.company_name} · ${detailDraft.value.job_title} · ${detailDraft.value.round_name || `第 ${detailDraft.value.round_index || 1} 轮`}`
})

const autosaveText = computed(() => {
  if (!detailDraft.value) return ''
  if (autosaveState.value === 'saving') return '自动保存中...'
  if (autosaveState.value === 'dirty') return '编辑中'
  if (autosaveState.value === 'error') return autosaveError.value || '自动保存失败'
  return '已保存'
})

function getHeadingText(node) {
  return String(node?.textContent || '')
    .replace(/[\u200B-\u200D\uFEFF]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

const outlineItems = computed(() => {
  const html = String(detailDraft.value?.document_content || '').trim()
  if (!html) {
    return []
  }

  const parser = new DOMParser()
  const doc = parser.parseFromString(`<div>${html}</div>`, 'text/html')
  const nodes = Array.from(doc.body.querySelectorAll('h1, h2, h3'))

  return nodes
    .map((node, index) => ({
      index,
      domIndex: index,
      level: Number(node.tagName.slice(1)),
      text: getHeadingText(node),
    }))
    .filter((item) => item.text)
})

const visibleOutlineItems = computed(() => {
  const html = String(detailDraft.value?.document_content || '').trim()
  if (!html) {
    return []
  }

  const parser = new DOMParser()
  const doc = parser.parseFromString(`<div>${html}</div>`, 'text/html')
  const nodes = Array.from(doc.body.querySelectorAll('h1, h2, h3'))
  const tree = []
  const stack = []

  nodes.forEach((node, index) => {
    const text = getHeadingText(node)
    if (!text) {
      return
    }

    const item = {
      id: `outline-${index}`,
      domIndex: index,
      level: Number(node.tagName.slice(1)),
      depth: 1,
      text,
      children: [],
    }

    while (stack.length && stack[stack.length - 1].level >= item.level) {
      stack.pop()
    }

    item.depth = stack.length + 1

    if (stack.length) {
      stack[stack.length - 1].children.push(item)
    } else {
      tree.push(item)
    }

    stack.push(item)
  })

  const items = []

  function walk(branches) {
    branches.forEach((branch) => {
      const isCollapsed = Boolean(collapsedOutlineIds.value[branch.id])
      items.push({
        id: branch.id,
        domIndex: branch.domIndex,
        level: branch.level,
        depth: branch.depth,
        text: branch.text,
        hasChildren: branch.children.length > 0,
        isCollapsed,
      })

      if (!isCollapsed && branch.children.length) {
        walk(branch.children)
      }
    })
  }

  walk(tree)
  return items
})

const trendData = computed(() => {
  const values = [
    Math.max(stats.value.total_count - stats.value.completed_count, 0),
    stats.value.this_week_count,
    stats.value.upcoming_count,
    stats.value.pending_review_count,
    stats.value.completed_count,
    stats.value.total_count,
  ]
  return values.map((value) => Math.max(value, 0))
})

const trendPoints = computed(() => {
  const values = trendData.value
  const maxValue = Math.max(...values, 1)
  const width = 220
  const height = 84
  const xStep = width / Math.max(values.length - 1, 1)
  return values
    .map((value, index) => {
      const x = index * xStep
      const y = height - (value / maxValue) * 54 - 10
      return `${x},${y}`
    })
    .join(' ')
})

const trendAreaPath = computed(() => {
  const points = trendPoints.value.split(' ').filter(Boolean)
  if (!points.length) {
    return ''
  }
  return `M${points[0]} L${points.slice(1).join(' L')} L220,84 L0,84 Z`
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
    '<h2>面试信息</h2>',
    `<p><strong>时间：</strong>${escapeHtml(formatDateTime(detail.scheduled_at))}</p>`,
    `<p><strong>形式：</strong>${escapeHtml(typeLabel(detail.interview_type))}</p>`,
    `<p><strong>结果：</strong>${escapeHtml(resultLabel(detail.result))}</p>`,
    `<p><strong>准备状态：</strong>${escapeHtml(detail.preparation_note || '待补充')}</p>`,
    '<h2>问题记录</h2>',
    '<h3>问题 1</h3>',
    '<p>记录问题、回答和追问。</p>',
    '<h2>自由笔记</h2>',
    `<p>${escapeHtml(detail.free_note || '记录现场反馈、氛围和零散观察。')}</p>`,
    '<h2>复盘总结</h2>',
    `<p>${escapeHtml(detail.strength_note || '')}</p>`,
    `<p>${escapeHtml(detail.weakness_note || '')}</p>`,
    `<p>${escapeHtml(detail.missing_knowledge_note || '')}</p>`,
    `<p>${escapeHtml(detail.next_round_prep_note || '')}</p>`,
    '<h2>后续行动</h2>',
    `<p>${escapeHtml(detail.follow_up_action || '发送感谢信\n跟进 HR\n整理下一轮准备')}</p>`,
  ]
  return lines.join('')
}

function getOutlineDomNodes() {
  const surface = editorRef.value?.getSurfaceElement?.()
  if (!surface) {
    return []
  }
  return Array.from(surface.querySelectorAll('h1, h2, h3'))
}

function toggleOutlinePanel() {
  isOutlinePanelCollapsed.value = !isOutlinePanelCollapsed.value
}

function syncWorkspaceMode() {
  if (typeof window === 'undefined') return
  isMobileWorkspace.value = window.innerWidth <= 1024
}

function toggleOutlineBranch(id) {
  collapsedOutlineIds.value = {
    ...collapsedOutlineIds.value,
    [id]: !collapsedOutlineIds.value[id],
  }
}

function handleOutlineItemClick(item) {
  if (item?.hasChildren) {
    toggleOutlineBranch(item.id)
    return
  }
  scrollToOutline(item.domIndex)
}

function scrollToOutline(index) {
  const target = getOutlineDomNodes()[index]
  if (!target) {
    return
  }
  target.scrollIntoView({ behavior: 'smooth', block: 'start' })
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
  await flushAutosave()
  clearAutosaveTimer()
  selectedId.value = id
  const detail = await requestJson(`/api/interviews/${id}`)
      isHydratingDraft.value = true
      detailDraft.value = {
    ...detail,
    scheduled_at: detail.scheduled_at || '',
    follow_up_at: detail.follow_up_at || '',
    document_content: detail.document_content || buildDefaultDocument(detail),
  }
  lastSavedSnapshot.value = serializeDraft(detailDraft.value)
  autosaveState.value = 'saved'
  autosaveError.value = ''
  Promise.resolve().then(() => {
    isHydratingDraft.value = false
  })
}

async function handleSelectInterview(id) {
  await selectInterview(id)
  activeMobilePanel.value = 'main'
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

function serializeDraft(source) {
  return JSON.stringify(buildPayload(source))
}

function syncInterviewListItem(source) {
  if (!source?.id) return
  interviews.value = interviews.value.map((item) => (
    item.id === source.id
      ? {
          ...item,
          round_name: source.round_name,
          round_index: source.round_index,
          scheduled_at: source.scheduled_at,
          interview_type: source.interview_type,
          result: source.result,
          duration_minutes: source.duration_minutes,
          interviewer_name: source.interviewer_name,
        }
      : item
  ))
}

function clearAutosaveTimer() {
  if (!autosaveTimer) return
  window.clearTimeout(autosaveTimer)
  autosaveTimer = null
}

function queueAutosave() {
  if (!detailDraft.value) return
  clearAutosaveTimer()
  autosaveTimer = window.setTimeout(() => {
    autosaveTimer = null
    void saveInterview({ silent: true, refresh: false })
  }, AUTOSAVE_DELAY)
}

async function flushAutosave() {
  clearAutosaveTimer()
  if (!detailDraft.value) return
  const snapshot = serializeDraft(detailDraft.value)
  if (snapshot === lastSavedSnapshot.value) return
  await saveInterview({ silent: true, refresh: false })
}

function openCreateDialog() {
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
  activeMobilePanel.value = 'sidebar'
}

function applyRouteFilters() {
  filters.application_id = typeof route.query.application_id === 'string' ? route.query.application_id : ''
  const quick = typeof route.query.quick === 'string' ? route.query.quick : ''
  activeQuickView.value = QUICK_VIEW_IDS.has(quick) ? quick : 'all'
}

async function maybeOpenCreateDialogFromRoute() {
  if (route.query.create !== '1') {
    return
  }
  openCreateDialog()
  await router.replace({
    query: {
      ...route.query,
      create: undefined,
    },
  })
}

function closeDialog() {
  dialogOpen.value = false
  dialogMessage.value = ''
}

async function saveDialog() {
  if (!form.application_id) {
    dialogMessage.value = '请先选择关联投递。'
    return
  }
  savingDialog.value = true
  try {
    const saved = await requestJson('/api/interviews', {
      method: 'POST',
      body: JSON.stringify(buildPayload(form)),
    })
    closeDialog()
    await Promise.all([loadStats(), loadApplications(), loadInterviews(saved.id)])
  } catch (error) {
    dialogMessage.value = error.message || '保存失败'
  } finally {
    savingDialog.value = false
  }
}

async function saveInterview(options = {}) {
  if (!detailDraft.value) return
  const { silent = false, refresh = true } = options
  const snapshot = serializeDraft(detailDraft.value)

  if (silent && snapshot === lastSavedSnapshot.value) {
    autosaveState.value = 'saved'
    return
  }

  if (activeSavePromise) {
    if (silent) {
      queuedAutosave = true
      return activeSavePromise
    }
    await activeSavePromise
  }

  savingDetail.value = true
  if (!silent) {
    message.value = ''
  }
  autosaveState.value = 'saving'
  autosaveError.value = ''

  activeSavePromise = (async () => {
    await requestJson(`/api/interviews/${detailDraft.value.id}`, {
      method: 'PUT',
      body: JSON.stringify(buildPayload(detailDraft.value)),
    })
    lastSavedSnapshot.value = snapshot
    const currentSnapshot = detailDraft.value ? serializeDraft(detailDraft.value) : snapshot
    if (currentSnapshot !== snapshot) {
      autosaveState.value = 'dirty'
      queueAutosave()
    } else {
      autosaveState.value = 'saved'
    }
    syncInterviewListItem(detailDraft.value)
    if (refresh) {
      await Promise.all([loadStats(), loadApplications()])
    }
  })()

  try {
    await activeSavePromise
  } catch (error) {
    autosaveState.value = 'error'
    autosaveError.value = error.message || '自动保存失败'
    if (!silent) {
      message.value = error.message || '保存失败'
    }
  } finally {
    activeSavePromise = null
    savingDetail.value = false
    if (queuedAutosave) {
      queuedAutosave = false
      queueAutosave()
    }
  }
}

function appendToDocument(html) {
  if (!detailDraft.value) return
  const current = detailDraft.value.document_content || ''
  detailDraft.value.document_content = `${current}${current ? '<p><br></p>' : ''}${html}`
}

async function insertIntoDocument(html) {
  if (!detailDraft.value) return
  const inserted = await editorRef.value?.insertHtml?.(html)
  if (inserted) {
    return
  }
  appendToDocument(html)
}

function handleTableStateChange(state) {
  tableState.value = {
    inTable: Boolean(state?.inTable),
    rows: Number(state?.rows) || 0,
    cols: Number(state?.cols) || 0,
  }
}

function openTableDialog() {
  if (!detailDraft.value) return
  tableDialogMessage.value = ''
  tableDraft.rows = Math.min(20, Math.max(1, Number(tableDraft.rows) || 3))
  tableDraft.cols = Math.min(8, Math.max(1, Number(tableDraft.cols) || 3))
  tableDialogOpen.value = true
}

function closeTableDialog() {
  tableDialogOpen.value = false
  tableDialogMessage.value = ''
}

async function insertTableAtSelection() {
  const inserted = await editorRef.value?.insertTable?.({
    rows: tableDraft.rows,
    cols: tableDraft.cols,
    withHeader: tableDraft.withHeader,
  })
  if (inserted) {
    return true
  }
  const rows = Math.min(20, Math.max(1, Number(tableDraft.rows) || 3))
  const cols = Math.min(8, Math.max(1, Number(tableDraft.cols) || 3))
  const withHeader = tableDraft.withHeader !== false
  const colgroup = Array.from({ length: cols }, () => '<col style="width:160px">').join('')
  const header = withHeader ? `<thead><tr>${Array.from({ length: cols }, (_, index) => `<th><p>表头 ${index + 1}</p></th>`).join('')}</tr></thead>` : ''
  const bodyRows = Math.max(rows - (withHeader ? 1 : 0), 1)
  const body = Array.from({ length: bodyRows }, () => `<tr>${Array.from({ length: cols }, () => '<td><p><br></p></td>').join('')}</tr>`).join('')
  appendToDocument(`<table class="rich-doc-table"><colgroup>${colgroup}</colgroup>${header}<tbody>${body}</tbody></table>`)
  return false
}

async function confirmInsertTable() {
  if (!detailDraft.value) return
  const rows = Number(tableDraft.rows)
  const cols = Number(tableDraft.cols)
  if (!Number.isFinite(rows) || rows < 1 || rows > 20) {
    tableDialogMessage.value = '行数请填写 1 到 20 之间的数字。'
    return
  }
  if (!Number.isFinite(cols) || cols < 1 || cols > 8) {
    tableDialogMessage.value = '列数请填写 1 到 8 之间的数字。'
    return
  }
  if (tableDraft.withHeader && rows < 2) {
    tableDialogMessage.value = '启用表头时，行数至少需要 2 行。'
    return
  }
  closeTableDialog()
  await insertTableAtSelection()
}

function syncTableDraft() {
  if (!tableState.value.inTable) {
    return
  }
  tableDraft.rows = tableState.value.rows
  tableDraft.cols = tableState.value.cols
}

async function addTableRowBefore() {
  await editorRef.value?.addTableRowBefore?.()
  syncTableDraft()
}

async function addTableRowAfter() {
  await editorRef.value?.addTableRowAfter?.()
  syncTableDraft()
}

async function addTableColumnBefore() {
  await editorRef.value?.addTableColumnBefore?.()
  syncTableDraft()
}

async function addTableColumnAfter() {
  await editorRef.value?.addTableColumnAfter?.()
  syncTableDraft()
}

async function removeTableRow() {
  await editorRef.value?.deleteTableRow?.()
  syncTableDraft()
}

async function removeTableColumn() {
  await editorRef.value?.deleteTableColumn?.()
  syncTableDraft()
}

function insertInterviewInfoBlock() {
  if (!detailDraft.value) return
  void insertIntoDocument([
    '<h2>面试信息</h2>',
    `<p><strong>时间：</strong>${escapeHtml(formatDateTime(detailDraft.value.scheduled_at))}</p>`,
    `<p><strong>形式：</strong>${escapeHtml(typeLabel(detailDraft.value.interview_type))}</p>`,
    `<p><strong>面试官：</strong>${escapeHtml(detailDraft.value.interviewer_name || '待补充')}</p>`,
    `<p><strong>准备状态：</strong>${escapeHtml(detailDraft.value.preparation_note || '待补充')}</p>`,
  ].join(''))
}

function insertQuestionTemplate() {
  if (!detailDraft.value) return
  void insertIntoDocument([
    '<h2>问题记录</h2>',
    '<h3>问题 1</h3>',
    '<p>问题内容：</p>',
    '<p>我的回答：</p>',
    '<p>面试官追问：</p>',
    '<p>自评：</p>',
  ].join(''))
}

function insertStarAnswerTemplate() {
  if (!detailDraft.value) return
  void insertIntoDocument([
    '<h3>STAR 回答</h3>',
    '<ul>',
    '<li>Situation: 背景是什么？</li>',
    '<li>Task: 我的目标是什么？</li>',
    '<li>Action: 我具体做了什么？</li>',
    '<li>Result: 结果和量化收益是什么？</li>',
    '</ul>',
  ].join(''))
}

function insertFeedbackTemplate() {
  if (!detailDraft.value) return
  void insertIntoDocument([
    '<h2>现场反馈</h2>',
    '<ul>',
    '<li>面试官关注点：</li>',
    '<li>我回答最顺的部分：</li>',
    '<li>我明显卡顿的部分：</li>',
    '<li>对方的正向信号：</li>',
    '<li>对方的风险信号：</li>',
    '</ul>',
  ].join(''))
}

function insertReviewTemplate() {
  if (!detailDraft.value) return
  void insertIntoDocument([
    '<h2>复盘总结</h2>',
    '<ul>',
    '<li>答得好的地方：</li>',
    '<li>卡住的地方：</li>',
    '<li>暴露的短板：</li>',
    '<li>下轮需要补什么：</li>',
    '</ul>',
  ].join(''))
}

function insertTodoTemplate() {
  if (!detailDraft.value) return
  void insertIntoDocument([
    '<h2>后续行动</h2>',
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

function clearFilterTimer() {
  if (!filterTimer) return
  window.clearTimeout(filterTimer)
  filterTimer = null
}

function queueFilterLoad() {
  clearFilterTimer()
  filterTimer = window.setTimeout(() => {
    filterTimer = null
    void loadInterviews()
  }, FILTER_DELAY)
}

watch(
  visibleOutlineItems,
  (items) => {
    const validIds = new Set(items.map((item) => item.id))
    const nextState = Object.fromEntries(
      Object.entries(collapsedOutlineIds.value).filter(([id, value]) => validIds.has(id) && value),
    )
    if (Object.keys(nextState).length !== Object.keys(collapsedOutlineIds.value).length) {
      collapsedOutlineIds.value = nextState
    }
  },
  { immediate: true },
)

watch(
  detailDraft,
  (draft) => {
    if (!draft) {
      clearAutosaveTimer()
      autosaveState.value = 'saved'
      autosaveError.value = ''
      lastSavedSnapshot.value = ''
      tableState.value = { inTable: false, rows: 0, cols: 0 }
      tableDialogOpen.value = false
      tableDialogMessage.value = ''
      return
    }
    if (isHydratingDraft.value) {
      return
    }
    const snapshot = serializeDraft(draft)
    if (snapshot === lastSavedSnapshot.value) {
      autosaveState.value = 'saved'
      return
    }
    autosaveState.value = 'dirty'
    autosaveError.value = ''
    queueAutosave()
  },
  { deep: true },
)

watch(
  () => [filters.q, filters.result, filters.interview_type, filters.reviewed, filters.application_id],
  (nextValues, prevValues) => {
    if (!applications.value.length) {
      return
    }
    if (!prevValues) {
      return
    }
    if (nextValues.every((value, index) => value === prevValues[index])) {
      return
    }
    queueFilterLoad()
  },
)

watch(
  () => [route.query.application_id, route.query.interview_id, route.query.quick, route.query.create],
  async () => {
    applyRouteFilters()
    if (applications.value.length) {
      await loadInterviews()
    }
    await maybeOpenCreateDialogFromRoute()
  },
)

function handleBeforeUnload(event) {
  if (!detailDraft.value) return
  if (serializeDraft(detailDraft.value) === lastSavedSnapshot.value) return
  event.preventDefault()
  event.returnValue = ''
}

onMounted(async () => {
  syncWorkspaceMode()
  window.addEventListener('resize', syncWorkspaceMode)
  window.addEventListener('beforeunload', handleBeforeUnload)
  applyRouteFilters()
  await Promise.all([loadStats(), loadApplications(), loadResumes()])
  await loadInterviews()
  await maybeOpenCreateDialogFromRoute()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', syncWorkspaceMode)
  window.removeEventListener('beforeunload', handleBeforeUnload)
  clearAutosaveTimer()
  clearFilterTimer()
})
</script>


