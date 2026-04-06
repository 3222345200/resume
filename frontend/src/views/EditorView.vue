<template>
  <main
    class="vue-editor-page"
    :class="{
      'sidebar-open': sidebarOpen,
      'desktop-sidebar-collapsed': desktopSidebarCollapsed,
    }"
  >
    <button
      class="mobile-sidebar-toggle"
      type="button"
      :aria-label="sidebarOpen ? '收起简历侧栏' : '打开简历侧栏'"
      @click="sidebarOpen = !sidebarOpen"
    >
      <img class="mobile-sidebar-logo" :src="brandMark" alt="" aria-hidden="true" />
      <span class="mobile-sidebar-arrow">{{ sidebarOpen ? '‹' : '›' }}</span>
      <span class="mobile-sidebar-label">{{ sidebarOpen ? '收起' : '简历' }}</span>
    </button>

    <button
      v-if="desktopSidebarCollapsed"
      class="desktop-sidebar-reopen"
      type="button"
      aria-label="展开简历侧栏"
      @click="desktopSidebarCollapsed = false"
    >
      <img class="desktop-sidebar-reopen-logo" :src="brandMark" alt="" aria-hidden="true" />
      <span class="desktop-sidebar-reopen-arrow">&gt;</span>
    </button>

    <div v-if="sidebarOpen" class="sidebar-mask" @click="sidebarOpen = false"></div>

    <ResumeSidebar
      :resumes="resumeStore.resumes"
      :active-id="resumeStore.currentResumeId"
      :current-resume="resumeStore.currentResume"
      :templates="resumeStore.templates"
      :username="authStore.user?.username || ''"
      :collapsed-on-mobile="!sidebarOpen"
      @select-resume="handleSelectResume"
      @create-resume="handleCreateResume"
      @back-dashboard="router.push('/dashboard')"
      @logout="handleLogout"
      @toggle-sidebar="desktopSidebarCollapsed = true"
    />

    <section class="vue-editor-main template-editor-main">
      <div v-if="resumeStore.loading" class="loading-card">正在加载简历数据...</div>

      <template v-else>
        <ResumeBasicsForm
          ref="basicsFormRef"
          :draft="resumeStore.currentResume"
          :templates="resumeStore.templates"
          :saving="saving"
          :rendering="rendering"
          :avatar-uploading="avatarUploading"
          :upload-avatar="handleUploadAvatar"
          @save="handleSave"
          @render="handleRender"
          @delete="handleDelete"
        />

        <ResumePreviewPane
          :preview-url="resumeStore.previewUrl"
          @navigate-section="handlePreviewNavigate"
        />
      </template>
    </section>

    <div v-if="toastText" class="vue-toast">{{ toastText }}</div>

    <ConfirmDialog
      :open="deleteConfirmOpen"
      eyebrow="Confirm"
      title="删除简历"
      message="确认删除当前简历吗？删除后无法恢复。"
      confirm-text="确认删除"
      cancel-text="取消"
      @confirm="confirmDeleteResume"
      @cancel="deleteConfirmOpen = false"
    />

    <ConfirmDialog
      :open="noticeDialogOpen"
      eyebrow="Notice"
      :title="noticeDialogTitle"
      :message="noticeDialogMessage"
      confirm-text="我知道了"
      :show-cancel="false"
      @confirm="noticeDialogOpen = false"
      @cancel="noticeDialogOpen = false"
    />
  </main>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import brandMark from '../assets/brand-mark.svg'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import ResumeBasicsForm from '../components/ResumeBasicsForm.vue'
import ResumePreviewPane from '../components/ResumePreviewPane.vue'
import ResumeSidebar from '../components/ResumeSidebar.vue'
import { useAuthStore } from '../stores/auth'
import { useResumeStore } from '../stores/resume'

const authStore = useAuthStore()
const resumeStore = useResumeStore()
const router = useRouter()

const saving = ref(false)
const rendering = ref(false)
const avatarUploading = ref(false)
const basicsFormRef = ref(null)
const toastText = ref('')
const deleteConfirmOpen = ref(false)
const noticeDialogOpen = ref(false)
const noticeDialogTitle = ref('提示')
const noticeDialogMessage = ref('')
const sidebarOpen = ref(window.matchMedia('(min-width: 1401px)').matches)
const desktopSidebarCollapsed = ref(false)

let toastTimer = null
let autoPreviewTimer = null
let autoPreviewSnapshot = ''

function openNoticeDialog(message, title = '提示') {
  noticeDialogTitle.value = title
  noticeDialogMessage.value = message
  noticeDialogOpen.value = true
}

function reportError(error) {
  const message = String(error?.message || error || '操作失败')
  if (message.includes('开始时间不能晚于结束时间')) {
    openNoticeDialog(message, '时间范围有误')
    return
  }
  if (message.includes('简历标题不能重复')) {
    openNoticeDialog(message, '标题重复')
    return
  }
  showToast(message)
}

function showToast(message) {
  toastText.value = message
  if (toastTimer) {
    clearTimeout(toastTimer)
  }
  toastTimer = window.setTimeout(() => {
    toastText.value = ''
  }, 2200)
}

function syncSidebarByViewport() {
  const isDesktop = window.matchMedia('(min-width: 1401px)').matches
  const shouldCollapseDesktopSidebar = window.matchMedia('(max-width: 1800px)').matches
  sidebarOpen.value = isDesktop
  if (!isDesktop) {
    desktopSidebarCollapsed.value = false
    return
  }
  desktopSidebarCollapsed.value = shouldCollapseDesktopSidebar
}

function getAutoPreviewSnapshot() {
  return JSON.stringify({
    id: resumeStore.currentResumeId || '',
    title: resumeStore.currentResume?.title || '',
    template_id: resumeStore.currentResume?.template_id || '',
    content: resumeStore.currentResume?.content || {},
  })
}

async function syncPreviewAutomatically() {
  const nextSnapshot = getAutoPreviewSnapshot()
  if (
    resumeStore.loading ||
    saving.value ||
    rendering.value ||
    avatarUploading.value ||
    !String(resumeStore.currentResume?.title || '').trim() ||
    nextSnapshot === autoPreviewSnapshot
  ) {
    return
  }

  try {
    await resumeStore.saveCurrentResume()
    autoPreviewSnapshot = getAutoPreviewSnapshot()
  } catch (error) {
    reportError(error)
    autoPreviewSnapshot = getAutoPreviewSnapshot()
  }
}

function scheduleAutoPreviewSync() {
  if (autoPreviewTimer) {
    clearTimeout(autoPreviewTimer)
  }
  autoPreviewTimer = window.setTimeout(syncPreviewAutomatically, 700)
}

function closeSidebarOnMobile() {
  if (!window.matchMedia('(min-width: 1401px)').matches) {
    sidebarOpen.value = false
  }
}

function handleSelectResume(resumeId) {
  resumeStore.selectResume(resumeId)
  autoPreviewSnapshot = getAutoPreviewSnapshot()
  closeSidebarOnMobile()
}

function handleCreateResume() {
  resumeStore.createLocalResume()
  autoPreviewSnapshot = getAutoPreviewSnapshot()
  closeSidebarOnMobile()
}

async function handleSave() {
  try {
    saving.value = true
    await resumeStore.saveCurrentResume()
    autoPreviewSnapshot = getAutoPreviewSnapshot()
    showToast('简历已保存')
  } catch (error) {
    reportError(error)
  } finally {
    saving.value = false
  }
}

async function handleRender() {
  try {
    rendering.value = true
    const pdfUrl = await resumeStore.renderCurrentResume()
    showToast('PDF 已生成')
    if (pdfUrl) {
      window.open(pdfUrl, '_blank', 'noopener')
    }
  } catch (error) {
    reportError(error)
  } finally {
    rendering.value = false
  }
}

async function handleUploadAvatar(file) {
  try {
    avatarUploading.value = true
    await resumeStore.uploadAvatar(file)
    showToast('头像已上传')
  } catch (error) {
    reportError(error)
    throw error
  } finally {
    avatarUploading.value = false
  }
}

function handleDelete() {
  deleteConfirmOpen.value = true
}

function handlePreviewNavigate(sectionKey) {
  basicsFormRef.value?.navigateToSection?.(sectionKey)
}

async function confirmDeleteResume() {
  deleteConfirmOpen.value = false
  try {
    await resumeStore.deleteCurrentResume()
    showToast('简历已删除')
  } catch (error) {
    reportError(error)
  }
}

async function handleLogout() {
  authStore.logout()
  resumeStore.$reset()
  await router.push('/login')
}

onMounted(async () => {
  window.addEventListener('resize', syncSidebarByViewport)
  try {
    await resumeStore.bootstrapEditor()
    autoPreviewSnapshot = getAutoPreviewSnapshot()
  } catch (error) {
    reportError(error)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', syncSidebarByViewport)
  if (toastTimer) {
    clearTimeout(toastTimer)
  }
  if (autoPreviewTimer) {
    clearTimeout(autoPreviewTimer)
  }
})

watch(
  () => resumeStore.currentResume,
  () => {
    scheduleAutoPreviewSync()
  },
  { deep: true },
)
</script>

