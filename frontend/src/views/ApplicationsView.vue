<template>
  <main class="interviews-page interviews-page-modern applications-page applications-page-modernized">
    <section class="applications-shell applications-shell-modernized">

      <div v-if="isMobileWorkspace" class="workspace-mobile-switcher" role="tablist" aria-label="移动端投递工作区切换">
        <button type="button" class="workspace-mobile-switch" :class="{ 'is-active': activeMobilePanel === 'main' }" @click="activeMobilePanel = 'main'">列表</button>
        <button type="button" class="workspace-mobile-switch" :class="{ 'is-active': activeMobilePanel === 'detail' }" @click="activeMobilePanel = 'detail'">详情</button>
        <button type="button" class="workspace-mobile-switch" :class="{ 'is-active': activeMobilePanel === 'sidebar' }" @click="activeMobilePanel = 'sidebar'">筛选</button>
      </div>

      <aside class="applications-sidebar" :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'sidebar' }">
        <div class="applications-sidebar-shell interviews-sidebar-shell">
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

          <button class="primary-button interviews-sidebar-primary" type="button" @click="openCreateDialog">新建投递</button>

          <section class="interviews-card interviews-card-soft applications-sidebar-panel">
            <div class="interviews-card-head">
              <div>
                <p class="eyebrow">Quick Views</p>
                <h2>快捷视图</h2>
              </div>
            </div>

            <div class="applications-sidebar-section">
              <button
                v-for="view in quickViews"
                :key="view.id"
                class="applications-shortcut"
                :class="{ 'is-active': activeQuickView === view.id }"
                type="button"
                @click="activeQuickView = view.id"
              >
                <span>{{ view.label }}</span>
                <strong>{{ quickCount(view.id) }}</strong>
              </button>
            </div>

          </section>
        </div>
      </aside>

      <section class="applications-main" :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'main' }">
        <header class="applications-header applications-surface">
          <div>
            <p class="eyebrow">Application Workspace</p>
            <h1>投递管理</h1>
          </div>
          <div class="applications-header-actions">
            <button class="ghost-button" type="button" @click="fieldSettingsOpen = !fieldSettingsOpen">字段设置</button>
            <div v-if="fieldSettingsOpen" class="applications-field-preferences applications-field-preferences-popover">
              <div class="applications-field-preferences-head">
                <div>
                  <strong>常用字段</strong>
                  <p>核心字段默认显示，可选字段按习惯勾选。</p>
                </div>
              </div>
              <div class="applications-field-chip-list">
                <button
                  v-for="field in optionalFieldOptions"
                  :key="field.key"
                  type="button"
                  class="applications-field-chip"
                  :class="{ 'is-active': visibleOptionalFields.includes(field.key) }"
                  @click="toggleOptionalField(field.key)"
                >
                  {{ field.label }}
                </button>
              </div>
            </div>
          </div>
        </header>
        <section class="applications-stats">
          <article v-for="card in statCards" :key="card.label" class="applications-stat-card">
            <span class="applications-stat-label">{{ card.label }}</span>
            <strong>{{ card.value }}</strong>
            <small>{{ card.hint }}</small>
          </article>
        </section>

        <section class="applications-toolbar applications-surface">
          <label class="applications-search">
            <span>关键词</span>
            <input v-model="filters.q" type="text" placeholder="公司名 / 岗位名" @keyup.enter="loadApplications()" />
          </label>
          <label><span>状态</span><CustomSelect v-model="filters.status" :options="statusSelectOptions" placeholder="全部状态" /></label>
          <label><span>渠道</span><CustomSelect v-model="filters.channel" :options="channelSelectOptions" placeholder="全部渠道" /></label>
          <label><span>城市</span><CustomSelect v-model="filters.city" :options="citySelectOptions" placeholder="全部城市" /></label>
          <label><span>开始日期</span><DateTimePicker v-model="filters.dateFrom" type="date" placeholder="选择日期" label-text="开始日期" /></label>
          <label><span>结束日期</span><DateTimePicker v-model="filters.dateTo" type="date" placeholder="选择日期" label-text="结束日期" /></label>
          <label><span>关联简历</span><CustomSelect v-model="filters.resumeId" :options="resumeFilterOptions" placeholder="全部简历" /></label>
          <div class="applications-toolbar-actions">
            <button class="ghost-button" type="button" @click="resetFilters">重置</button>
            <button class="primary-button" type="button" @click="loadApplications()">筛选</button>
          </div>
        </section>

        <div v-if="activeTags.length" class="applications-tags">
          <span v-for="tag in activeTags" :key="tag">{{ tag }}</span>
        </div>

        <p v-if="message" class="applications-message">{{ message }}</p>

        <section class="applications-list-wrap applications-surface">
          <div class="applications-list-header">
            <div>
              <p class="eyebrow">Application Records</p>
              <h2>投递列表</h2>
            </div>
            <div class="applications-list-header-actions">
              <span class="applications-list-count">{{ filteredApplications.length }} 条记录</span>
              <button class="primary-button" type="button" @click="openCreateDialog">新建投递</button>
            </div>
          </div>

          <section class="applications-list">
          <article v-for="item in filteredApplications" :key="item.id" class="applications-card" :class="{ 'is-selected': item.id === selectedId, 'is-todo': item.is_todo, 'is-reviewed': isReviewed(item.id) }" @click="handleSelectApplication(item.id)">
            <div class="applications-card-rail">
              <span class="applications-card-dot" :class="{ 'is-active': item.id === selectedId, 'is-warning': item.is_todo || !isReviewed(item.id) }"></span>
            </div>

              <div class="applications-card-main">
                <div class="applications-card-top">
                  <div class="applications-card-heading">
                    <div class="applications-card-title-row">
                      <h2>{{ item.company_name }}</h2>
                      <div class="applications-card-badges">
                        <span class="applications-status-badge" :class="badgeClass(item.status)">{{ item.status }}</span>
                        <span v-if="item.is_todo" class="applications-todo-badge">待跟进</span>
                        <span class="applications-review-flag" :class="{ 'is-reviewed': isReviewed(item.id) }">
                          <i></i>{{ isReviewed(item.id) ? '已复盘' : '待复盘' }}
                        </span>
                      </div>
                    </div>
                    <p>{{ item.job_title }}<span v-if="item.department"> · {{ item.department }}</span></p>
                  </div>
                  <div class="applications-card-toolbar" @click.stop>
                    <div class="applications-card-actions applications-card-actions-inline">
                      <button class="ghost-button" type="button" @click="openEditDialog(item)">编辑</button>
                      <button class="ghost-button" type="button" :class="{ 'is-accent': isReviewed(item.id) }" @click="toggleReviewed(item.id)">{{ isReviewed(item.id) ? '已复盘' : '标记复盘' }}</button>
                      <button class="ghost-button is-danger" type="button" @click="removeApplication(item)">删除</button>
                    </div>
                  </div>
                </div>

                <div class="applications-card-fields">
                <div class="applications-card-field">
                  <span>投递地点</span>
                  <strong>{{ item.city || '地点待补充' }}</strong>
                </div>
                <div class="applications-card-field">
                  <span>投递渠道</span>
                  <strong>{{ item.channel || '渠道待补充' }}</strong>
                </div>
                <div class="applications-card-field">
                  <span>关联简历</span>
                  <strong>{{ item.resume_title || '未关联简历' }}</strong>
                </div>
                <div class="applications-card-field">
                  <span>投递时间</span>
                  <strong>{{ formatDate(item.applied_at) }}</strong>
                </div>
                <div class="applications-card-field">
                  <span>面试轮次</span>
                  <strong>{{ item.interview_count ? `${item.interview_count} 轮` : '暂无' }}</strong>
                </div>
                <div class="applications-card-field">
                  <span>更新时间</span>
                  <strong>{{ formatDateTime(item.updated_at) }}</strong>
                </div>
              </div>

              <p v-if="item.note" class="applications-card-note">{{ item.note }}</p>
            </div>
          </article>
          <div v-if="!loadingList && !filteredApplications.length" class="applications-empty">
            <h3>还没有匹配的投递记录</h3>
            <p>新建第一条投递，或者调整筛选条件后再试。</p>
          </div>
          </section>
        </section>
      </section>

      <aside class="applications-detail" :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'detail' }">
        <div v-if="loadingDetail" class="applications-detail-empty">正在加载详情...</div>
        <template v-else-if="detail">
          <header class="applications-detail-header applications-surface">
            <div>
              <p class="eyebrow">Application Detail</p>
              <h2>{{ detail.company_name }}</h2>
              <p>{{ detail.job_title }}</p>
            </div>
            <div class="applications-detail-header-actions">
              <span class="applications-status-badge" :class="badgeClass(detail.status)">{{ detail.status }}</span>
              <button class="ghost-button" type="button" @click="openEditDialog(detail)">编辑</button>
            </div>
          </header>

          <section class="applications-detail-card">
            <button class="applications-section-toggle" type="button" @click="toggleDetailSection('basic')">
              <div class="applications-section-head">
                <h3>基本信息</h3>
                <p>岗位信息与 JD 摘要</p>
              </div>
              <span class="applications-section-arrow" :class="{ 'is-open': detailSections.basic }"></span>
            </button>
            <dl v-if="detailSections.basic" class="applications-detail-grid">
              <div><dt>公司名称</dt><dd>{{ detail.company_name }}</dd></div>
              <div><dt>岗位名称</dt><dd>{{ detail.job_title }}</dd></div>
              <div v-if="detail.department"><dt>部门</dt><dd>{{ detail.department }}</dd></div>
              <div v-if="detail.city"><dt>工作地点</dt><dd>{{ detail.city }}</dd></div>
              <div v-if="detail.salary_range"><dt>薪资范围</dt><dd>{{ detail.salary_range }}</dd></div>
              <div v-if="detail.job_type"><dt>岗位类型</dt><dd>{{ detail.job_type }}</dd></div>
              <div v-if="detail.job_link" class="full-row"><dt>岗位链接</dt><dd><a class="applications-link" :href="detail.job_link" target="_blank" rel="noreferrer">{{ detail.job_link }}</a></dd></div>
              <div v-if="detail.jd_summary" class="full-row"><dt>JD 摘要</dt><dd>{{ detail.jd_summary }}</dd></div>
            </dl>
          </section>

          <section class="applications-detail-card">
            <button class="applications-section-toggle" type="button" @click="toggleDetailSection('delivery')">
              <div class="applications-section-head">
                <h3>投递信息</h3>
                <p>渠道、联系人与当前判断</p>
              </div>
              <span class="applications-section-arrow" :class="{ 'is-open': detailSections.delivery }"></span>
            </button>
            <dl v-if="detailSections.delivery" class="applications-detail-grid">
              <div><dt>投递日期</dt><dd>{{ formatDate(detail.applied_at) }}</dd></div>
              <div v-if="detail.channel"><dt>投递渠道</dt><dd>{{ detail.channel }}</dd></div>
              <div v-if="detail.contact_name || detail.referrer_name"><dt>联系人</dt><dd>{{ detail.contact_name || detail.referrer_name }}</dd></div>
              <div v-if="detail.contact_value"><dt>联系方式</dt><dd>{{ detail.contact_value }}</dd></div>
              <div v-if="detail.priority"><dt>优先级</dt><dd>{{ detail.priority }}</dd></div>
              <div v-if="detail.final_result"><dt>最终结果</dt><dd>{{ detail.final_result }}</dd></div>
              <div v-if="detail.note" class="full-row"><dt>备注</dt><dd>{{ detail.note }}</dd></div>
              <div v-if="detail.risk_note" class="full-row"><dt>风险点</dt><dd>{{ detail.risk_note }}</dd></div>
            </dl>
          </section>

          <section class="applications-detail-card">
            <button class="applications-section-toggle" type="button" @click="toggleDetailSection('status')">
              <div class="applications-section-head">
                <h3>状态流转</h3>
                <p>跟进节奏与历史记录</p>
              </div>
              <span class="applications-section-arrow" :class="{ 'is-open': detailSections.status }"></span>
            </button>
            <template v-if="detailSections.status">
            <div class="applications-follow-form">
              <label><span>最近跟进</span><DateTimePicker v-model="followForm.last_follow_up_at" type="datetime-local" placeholder="选择时间" label-text="最近跟进时间" /></label>
              <label><span>下次跟进</span><DateTimePicker v-model="followForm.next_follow_up_at" type="datetime-local" placeholder="选择时间" label-text="下次跟进时间" /></label>
              <label class="full-row"><span>下一步动作</span><textarea v-model="followForm.next_action" rows="3" placeholder="例如：两天后邮件跟进 HR"></textarea></label>
              <div class="applications-follow-actions"><button class="primary-button" type="button" :disabled="savingFollow" @click="saveFollowUp">{{ savingFollow ? "保存中..." : "保存跟进" }}</button></div>
            </div>
            <dl v-if="detail.last_follow_up_at || detail.next_follow_up_at || detail.next_action" class="applications-detail-grid applications-status-summary">
              <div v-if="detail.last_follow_up_at"><dt>最近跟进</dt><dd>{{ formatDateTime(detail.last_follow_up_at) }}</dd></div>
              <div v-if="detail.next_follow_up_at"><dt>下次跟进</dt><dd>{{ formatDateTime(detail.next_follow_up_at) }}</dd></div>
              <div v-if="detail.next_action" class="full-row"><dt>下一步动作</dt><dd>{{ detail.next_action }}</dd></div>
            </dl>
            <div class="applications-history">
              <article v-for="item in detail.status_history" :key="item.id" class="applications-history-item">
                <span>{{ item.from_status || "新建" }} -> {{ item.to_status }}</span>
                <strong>{{ formatDateTime(item.changed_at) }}</strong>
                <p>{{ item.note || "状态已更新" }}</p>
              </article>
              <p v-if="!detail.status_history.length" class="applications-muted">暂无状态变更记录。</p>
            </div>
            </template>
          </section>

          <section class="applications-detail-card">
            <button class="applications-section-toggle" type="button" @click="toggleDetailSection('resume')">
              <div class="applications-section-head">
                <h3>简历关联</h3>
                <p>查看本次投递使用的简历版本</p>
              </div>
              <span class="applications-section-arrow" :class="{ 'is-open': detailSections.resume }"></span>
            </button>
            <div v-if="detailSections.resume && detail.resume_id" class="applications-detail-row">
              <div>
                <strong>{{ detail.resume_title || "未关联简历" }}</strong>
              </div>
              <button class="ghost-button" type="button" :disabled="!detail.resume_id" @click="jumpToResume(detail.resume_id)">查看 / 编辑简历</button>
            </div>
            <p v-else-if="detailSections.resume" class="applications-muted">暂无关联简历。</p>
          </section>

        </template>
        <div v-else class="applications-detail-empty">选择一条投递记录后，这里会展示完整详情。</div>
      </aside>
    </section>

    <div v-if="dialogOpen" class="applications-dialog-mask" @click.self="closeDialog">
      <div class="applications-dialog">
        <div class="applications-dialog-header">
          <div class="applications-dialog-title-group">
            <p class="eyebrow">{{ editingId ? "edit application" : "create application" }}</p>
            <h2>{{ editingId ? "编辑投递" : "新建投递" }}</h2>
          </div>
          <button class="applications-dialog-close" type="button" @click="closeDialog">×</button>
        </div>

        <div class="applications-dialog-body">
          <div class="applications-dialog-main">
            <section class="applications-dialog-panel applications-dialog-panel-primary">
              <div class="applications-form-grid applications-form-grid-primary">
                <label><span>公司名称</span><input v-model="form.company_name" type="text" /></label>
                <label><span>岗位名称</span><input v-model="form.job_title" type="text" /></label>
                <label><span>城市 / 地点</span><input v-model="form.city" type="text" /></label>
                <label><span>投递日期</span><DateTimePicker v-model="form.applied_at" type="date" placeholder="选择日期" /></label>
                <label><span>投递渠道</span><input v-model="form.channel" type="text" /></label>
                <label><span>优先级</span><CustomSelect v-model="form.priority" :options="prioritySelectOptions" placeholder="选择优先级" /></label>
              </div>
            </section>

            <section class="applications-dialog-panel applications-dialog-panel-secondary">
              <div class="applications-form-stack">
                <label>
                  <span class="applications-label-with-badge">
                    <span>当前状态</span>
                    <strong class="applications-inline-status" :class="badgeClass(form.status)">{{ form.status || '已投递' }}</strong>
                  </span>
                  <CustomSelect v-model="form.status" :options="statusFormOptions" placeholder="选择状态" />
                </label>
                <label>
                  <span>关联简历</span>
                  <CustomSelect v-model="form.resume_id" :options="resumeFormOptions" placeholder="暂不关联" />
                </label>
                <label>
                  <span>下次跟进</span>
                  <DateTimePicker v-model="form.next_follow_up_at" type="datetime-local" placeholder="选择时间" />
                </label>
              </div>
            </section>
          </div>

          <section class="applications-dialog-panel applications-dialog-extension">
            <div class="applications-form-grid applications-form-grid-footer">
              <label>
                <span>备注</span>
                <textarea v-model="form.note" rows="5"></textarea>
              </label>
              <label>
                <span>下一步动作</span>
                <textarea v-model="form.next_action" rows="5"></textarea>
              </label>
            </div>
          </section>
        </div>

        <p v-if="dialogMessage" class="applications-message is-error">{{ dialogMessage }}</p>
        <div class="applications-dialog-actions">
          <button class="ghost-button" type="button" @click="closeDialog">取消</button>
          <button class="primary-button" type="button" :disabled="savingDialog" @click="saveApplication">{{ savingDialog ? "保存中..." : editingId ? "保存修改" : "创建投递" }}</button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :open="deleteDialog.open"
      eyebrow="Delete"
      title="删除投递记录"
      :message="deleteDialog.message"
      confirm-text="确认删除"
      cancel-text="取消"
      @confirm="confirmDeleteApplication"
      @cancel="closeDeleteDialog"
    />
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import brandMark from '../assets/logo.png'
import { requestJson } from '../api/request'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import CustomSelect from '../components/CustomSelect.vue'
import DateTimePicker from '../components/DateTimePicker.vue'
import { useAuthStore } from '../stores/auth'
import { useResumeStore } from '../stores/resume'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const resumeStore = useResumeStore()


const quickViews = [
  { id: 'all', label: '全部投递' },
  { id: 'todo', label: '待跟进' },
  { id: 'interviewing', label: '面试中' },
  { id: 'offer', label: 'Offer' },
  { id: 'rejected', label: '已拒绝' },
  { id: 'week', label: '本周新增' },
]
const statusOptions = ['想投', '已投递', '笔试', '面试中', 'HR 面', 'Offer', '已拒绝', '已结束']
const priorityOptions = ['低', '中', '高']
const OPTIONAL_FIELD_STORAGE_KEY = 'applications_optional_fields'
const REVIEWED_STORAGE_KEY = 'applications_reviewed_records'
const DEFAULT_OPTIONAL_FIELDS = ['city', 'channel', 'resume_id', 'priority', 'note', 'next_follow_up_at', 'next_action']
const optionalFieldOptions = [
  { key: 'department', label: '部门' },
  { key: 'city', label: '城市 / 地点' },
  { key: 'job_type', label: '岗位类型' },
  { key: 'salary_range', label: '薪资范围' },
  { key: 'channel', label: '投递渠道' },
  { key: 'priority', label: '优先级' },
  { key: 'contact_name', label: '联系人' },
  { key: 'contact_value', label: '联系方式' },
  { key: 'referrer_name', label: '内推人' },
  { key: 'resume_id', label: '关联简历' },
  { key: 'job_link', label: '岗位链接' },
  { key: 'jd_summary', label: 'JD 摘要' },
  { key: 'note', label: '备注' },
  { key: 'risk_note', label: '风险点' },
  { key: 'last_follow_up_at', label: '最近跟进' },
  { key: 'next_follow_up_at', label: '下次跟进' },
  { key: 'next_action', label: '下一步动作' },
]
const statusSelectOptions = [{ label: '全部状态', value: '' }, ...statusOptions.map((item) => ({ label: item, value: item }))]
const prioritySelectOptions = priorityOptions.map((item) => ({ label: item, value: item }))

const stats = ref({ total_count: 0, new_this_week: 0, interviewing_count: 0, offer_count: 0, rejected_count: 0, no_feedback_count: 0, todo_count: 0 })
const applications = ref([])
const resumes = ref([])
const selectedId = ref('')
const detail = ref(null)
const activeMobilePanel = ref('main')
const isMobileWorkspace = ref(false)
const activeQuickView = ref('all')
const loadingList = ref(false)
const loadingDetail = ref(false)
const savingDialog = ref(false)
const savingFollow = ref(false)
const message = ref('')
const dialogMessage = ref('')
const dialogOpen = ref(false)
const editingId = ref('')
const fieldSettingsOpen = ref(false)
const visibleOptionalFields = ref(loadOptionalFields())
const reviewedIds = ref(loadReviewedIds())
const deleteDialog = reactive({
  open: false,
  applicationId: '',
  message: '',
})
const detailSections = reactive({
  basic: true,
  delivery: true,
  status: true,
  resume: true,
  interview: true,
})

const QUICK_VIEW_IDS = new Set(['all', 'todo', 'interviewing', 'offer', 'rejected', 'week'])

const filters = reactive({ q: '', status: '', channel: '', city: '', dateFrom: '', dateTo: '', resumeId: '' })
const form = reactive(emptyForm())
const followForm = reactive({ last_follow_up_at: '', next_follow_up_at: '', next_action: '' })

function emptyForm() {
  return { company_name: '', job_title: '', department: '', city: '', job_link: '', jd_summary: '', salary_range: '', job_type: '', applied_at: toDateInput(new Date().toISOString()), status: '已投递', channel: '', referrer_name: '', contact_name: '', contact_value: '', resume_id: '', note: '', risk_note: '', priority: '中', next_action: '', next_follow_up_at: '', last_follow_up_at: '' }
}

const statCards = computed(() => [
  { label: '总投递数', value: stats.value.total_count, hint: '累计岗位申请' },
  { label: '本周新增', value: stats.value.new_this_week, hint: '最近新增记录' },
  { label: '面试中', value: stats.value.interviewing_count, hint: '含 HR 面阶段' },
  { label: 'Offer 数量', value: stats.value.offer_count, hint: '进入录用阶段' },
  { label: '已拒数量', value: stats.value.rejected_count, hint: '被拒或主动结束' },
  { label: '无反馈', value: stats.value.no_feedback_count, hint: '两周未反馈' },
])
const channelOptions = computed(() => [...new Set(applications.value.map((item) => item.channel).filter(Boolean))])
const cityOptions = computed(() => [...new Set(applications.value.map((item) => item.city).filter(Boolean))])
const channelSelectOptions = computed(() => [{ label: '全部渠道', value: '' }, ...channelOptions.value.map((item) => ({ label: item, value: item }))])
const citySelectOptions = computed(() => [{ label: '全部城市', value: '' }, ...cityOptions.value.map((item) => ({ label: item, value: item }))])
const resumeFilterOptions = computed(() => [{ label: '全部简历', value: '' }, ...resumes.value.map((item) => ({ label: item.title, value: item.id }))])
const resumeFormOptions = computed(() => [{ label: '暂不关联', value: '' }, ...resumes.value.map((item) => ({ label: item.title, value: item.id }))])
const statusFormOptions = computed(() => statusOptions.map((item) => ({ label: item, value: item })))

function loadOptionalFields() {
  try {
    const raw = localStorage.getItem(OPTIONAL_FIELD_STORAGE_KEY)
    const parsed = raw ? JSON.parse(raw) : null
    if (Array.isArray(parsed) && parsed.length) {
      return parsed.filter((item) => optionalFieldOptions.some((field) => field.key === item))
    }
  } catch {
    // ignore local preference parse errors
  }
  return [...DEFAULT_OPTIONAL_FIELDS]
}

function persistOptionalFields() {
  localStorage.setItem(OPTIONAL_FIELD_STORAGE_KEY, JSON.stringify(visibleOptionalFields.value))
}

function loadReviewedIds() {
  try {
    const raw = localStorage.getItem(REVIEWED_STORAGE_KEY)
    const parsed = raw ? JSON.parse(raw) : null
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function persistReviewedIds() {
  localStorage.setItem(REVIEWED_STORAGE_KEY, JSON.stringify(reviewedIds.value))
}

function isReviewed(id) {
  return reviewedIds.value.includes(id)
}

function syncWorkspaceMode() {
  if (typeof window === 'undefined') return
  isMobileWorkspace.value = window.innerWidth <= 1024
}

function toggleReviewed(id) {
  if (!id) return
  if (reviewedIds.value.includes(id)) {
    reviewedIds.value = reviewedIds.value.filter((item) => item !== id)
  } else {
    reviewedIds.value = [...reviewedIds.value, id]
  }
  persistReviewedIds()
}

function shouldShowField(fieldKey) {
  return visibleOptionalFields.value.includes(fieldKey)
}

function toggleOptionalField(fieldKey) {
  if (visibleOptionalFields.value.includes(fieldKey)) {
    visibleOptionalFields.value = visibleOptionalFields.value.filter((item) => item !== fieldKey)
  } else {
    visibleOptionalFields.value = [...visibleOptionalFields.value, fieldKey]
  }
  persistOptionalFields()
}

function toggleDetailSection(sectionKey) {
  detailSections[sectionKey] = !detailSections[sectionKey]
}
const activeTags = computed(() => {
  const tags = []
  if (filters.q) tags.push(`关键词：${filters.q}`)
  if (filters.status) tags.push(`状态：${filters.status}`)
  if (filters.channel) tags.push(`渠道：${filters.channel}`)
  if (filters.city) tags.push(`城市：${filters.city}`)
  if (filters.resumeId) tags.push(`简历：${resumes.value.find((item) => item.id === filters.resumeId)?.title || filters.resumeId}`)
  if (filters.dateFrom || filters.dateTo) tags.push(`日期：${filters.dateFrom || '不限'} 至 ${filters.dateTo || '不限'}`)
  return tags
})
const filteredApplications = computed(() => applications.value.filter((item) => matchQuickView(item, activeQuickView.value)))

watch(filteredApplications, async (items) => {
  if (!items.length) {
    selectedId.value = ''
    detail.value = null
    return
  }
  if (!items.some((item) => item.id === selectedId.value)) {
    await selectApplication(items[0].id)
  }
})

watch(detail, (item) => {
  followForm.last_follow_up_at = toDateTimeInput(item?.last_follow_up_at)
  followForm.next_follow_up_at = toDateTimeInput(item?.next_follow_up_at)
  followForm.next_action = item?.next_action || ''
})

function matchQuickView(item, view) {
  if (view === 'todo') return item.is_todo
  if (view === 'interviewing') return item.status === '面试中' || item.status === 'HR 面'
  if (view === 'offer') return item.status === 'Offer'
  if (view === 'rejected') return item.status === '已拒绝'
  if (view === 'week') return new Date(item.applied_at) >= weekStart()
  return true
}

function weekStart() {
  const now = new Date()
  const start = new Date(now)
  start.setDate(now.getDate() - ((now.getDay() + 6) % 7))
  start.setHours(0, 0, 0, 0)
  return start
}

function quickCount(view) {
  return applications.value.filter((item) => matchQuickView(item, view)).length
}

function badgeClass(status) {
  return `is-${String(status || '').replace(/\s+/g, '-').toLowerCase()}`
}

function toDateInput(value) {
  if (!value) return ''
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? String(value).slice(0, 10) : parsed.toISOString().slice(0, 10)
}

function toDateParam(value) {
  if (!value) return ''
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? String(value).slice(0, 10) : parsed.toISOString().slice(0, 10)
}

function toDateTimeInput(value) {
  if (!value) return ''
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return ''
  return new Date(parsed.getTime() - parsed.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
}

function toIso(value) {
  if (!value) return null
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString()
}

function formatDate(value) {
  if (!value) return '未填写'
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleDateString('zh-CN')
}

function formatDateTime(value) {
  if (!value) return '未填写'
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString('zh-CN', { hour12: false })
}

function resetForm() {
  Object.assign(form, emptyForm())
}

function fillForm(item) {
  Object.assign(form, { company_name: item.company_name || '', job_title: item.job_title || '', department: item.department || '', city: item.city || '', job_link: item.job_link || '', jd_summary: item.jd_summary || '', salary_range: item.salary_range || '', job_type: item.job_type || '', applied_at: toDateInput(item.applied_at), status: item.status || '已投递', channel: item.channel || '', referrer_name: item.referrer_name || '', contact_name: item.contact_name || '', contact_value: item.contact_value || '', resume_id: item.resume_id || '', note: item.note || '', risk_note: item.risk_note || '', priority: item.priority || '中', next_action: item.next_action || '', next_follow_up_at: toDateTimeInput(item.next_follow_up_at), last_follow_up_at: toDateTimeInput(item.last_follow_up_at) })
}

async function loadResumes() {
  resumes.value = (await requestJson('/api/resumes')).items || []
}

async function loadStats() {
  stats.value = await requestJson('/api/applications/stats/overview')
}

function queryString() {
  const params = new URLSearchParams()
  if (filters.q.trim()) params.set('q', filters.q.trim())
  if (filters.status) params.set('status', filters.status)
  if (filters.channel) params.set('channel', filters.channel)
  if (filters.city) params.set('city', filters.city)
  if (filters.dateFrom) params.set('date_from', toDateParam(filters.dateFrom))
  if (filters.dateTo) params.set('date_to', toDateParam(filters.dateTo))
  if (filters.resumeId) params.set('resume_id', filters.resumeId)
  return params.toString()
}

async function loadApplications(preferredId = selectedId.value) {
  loadingList.value = true
  message.value = ''
  try {
    const result = await requestJson(`/api/applications${queryString() ? `?${queryString()}` : ''}`)
    applications.value = result.items || []
    const routeApplicationId = typeof route.query.application_id === 'string' ? route.query.application_id : ''
    const nextId = [routeApplicationId, preferredId, applications.value[0]?.id].find((id) => id && applications.value.some((item) => item.id === id)) || ''
    if (nextId) await selectApplication(nextId)
    else { selectedId.value = ''; detail.value = null }
  } catch (error) {
    message.value = error.message || '投递数据加载失败'
  } finally {
    loadingList.value = false
  }
}

async function selectApplication(id) {
  if (!id) return
  selectedId.value = id
  loadingDetail.value = true
  try {
    detail.value = await requestJson(`/api/applications/${id}`)
  } catch (error) {
    message.value = error.message || '详情加载失败'
  } finally {
    loadingDetail.value = false
  }
}

async function handleSelectApplication(id) {
  await selectApplication(id)
  activeMobilePanel.value = 'detail'
}

function openCreateDialog() {
  editingId.value = ''
  dialogMessage.value = ''
  resetForm()
  dialogOpen.value = true
  activeMobilePanel.value = 'main'
}

function openEditDialog(item) {
  editingId.value = item.id
  dialogMessage.value = ''
  fillForm(item)
  dialogOpen.value = true
}

function closeDialog() {
  dialogOpen.value = false
  editingId.value = ''
  dialogMessage.value = ''
}

function payload() {
  return { company_name: form.company_name.trim(), job_title: form.job_title.trim(), department: form.department.trim(), city: form.city.trim(), job_link: form.job_link.trim(), jd_summary: form.jd_summary.trim(), salary_range: form.salary_range.trim(), job_type: form.job_type.trim(), applied_at: toDateParam(form.applied_at), status: form.status, channel: form.channel.trim(), referrer_name: form.referrer_name.trim(), contact_name: form.contact_name.trim(), contact_value: form.contact_value.trim(), resume_id: form.resume_id || null, note: form.note.trim(), risk_note: form.risk_note.trim(), priority: form.priority, next_action: form.next_action.trim(), next_follow_up_at: toIso(form.next_follow_up_at), last_follow_up_at: toIso(form.last_follow_up_at) }
}

async function saveApplication() {
  if (!form.company_name.trim() || !form.job_title.trim() || !form.applied_at) {
    dialogMessage.value = '请先填写公司名称、岗位名称和投递日期。'
    return
  }
  savingDialog.value = true
  try {
    const path = editingId.value ? `/api/applications/${editingId.value}` : '/api/applications'
    const method = editingId.value ? 'PUT' : 'POST'
    const saved = await requestJson(path, { method, body: JSON.stringify(payload()) })
    closeDialog()
    await Promise.all([loadStats(), loadApplications(saved.id)])
  } catch (error) {
    dialogMessage.value = error.message || '保存失败'
  } finally {
    savingDialog.value = false
  }
}

async function changeStatus(id, status) {
  try {
    await requestJson(`/api/applications/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status, note: `状态更新为「${status}」` }) })
    await Promise.all([loadStats(), loadApplications(id)])
  } catch (error) {
    message.value = error.message || '状态更新失败'
  }
}

async function saveFollowUp() {
  if (!selectedId.value) return
  savingFollow.value = true
  try {
    await requestJson(`/api/applications/${selectedId.value}/follow-up`, { method: 'PATCH', body: JSON.stringify({ last_follow_up_at: toIso(followForm.last_follow_up_at), next_follow_up_at: toIso(followForm.next_follow_up_at), next_action: followForm.next_action.trim() }) })
    await Promise.all([loadStats(), loadApplications(selectedId.value), selectApplication(selectedId.value)])
  } catch (error) {
    message.value = error.message || '跟进信息保存失败'
  } finally {
    savingFollow.value = false
  }
}

function removeApplication(item) {
  deleteDialog.open = true
  deleteDialog.applicationId = item.id
  deleteDialog.message = `确认删除「${item.company_name} / ${item.job_title}」吗？删除后无法恢复。`
}

function closeDeleteDialog() {
  deleteDialog.open = false
  deleteDialog.applicationId = ''
  deleteDialog.message = ''
}

async function confirmDeleteApplication() {
  if (!deleteDialog.applicationId) return
  try {
    await requestJson(`/api/applications/${deleteDialog.applicationId}`, { method: 'DELETE' })
    closeDeleteDialog()
    await Promise.all([loadStats(), loadApplications()])
  } catch (error) {
    message.value = error.message || '删除失败'
  }
}

async function jumpToResume(resumeId) {
  if (!resumeId) return
  if (!resumeStore.resumes.length) await resumeStore.bootstrapEditor()
  resumeStore.selectResume(resumeId)
  await router.push('/editor')
}

async function resetFilters() {
  Object.assign(filters, { q: '', status: '', channel: '', city: '', dateFrom: '', dateTo: '', resumeId: '' })
  activeQuickView.value = 'all'
  await loadApplications()
}

function applyResumeFilterFromRoute() {
  const resumeId = typeof route.query.resume_id === 'string' ? route.query.resume_id : ''
  filters.resumeId = resumeId
}

function applyQuickViewFromRoute() {
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

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}

watch(
  () => [route.query.resume_id, route.query.application_id, route.query.quick, route.query.create],
  async () => {
    applyResumeFilterFromRoute()
    applyQuickViewFromRoute()
    if (resumes.value.length) {
      await loadApplications()
    }
    await maybeOpenCreateDialogFromRoute()
  },
)

onMounted(async () => {
  syncWorkspaceMode()
  window.addEventListener('resize', syncWorkspaceMode)
  await Promise.all([loadResumes(), loadStats()])
  applyResumeFilterFromRoute()
  applyQuickViewFromRoute()
  await loadApplications()
  await maybeOpenCreateDialogFromRoute()
})

onUnmounted(() => {
  window.removeEventListener('resize', syncWorkspaceMode)
})
</script>
