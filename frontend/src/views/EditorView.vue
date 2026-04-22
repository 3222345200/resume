<template>
  <main class="interviews-page interviews-page-modern editor-workspace-page">
    <section class="interviews-shell editor-workspace-shell">

      <div v-if="isMobileWorkspace" class="editor-mobile-switcher" role="tablist" aria-label="移动端简历工作区切换">
        <button
          type="button"
          class="editor-mobile-switch"
          :class="{ 'is-active': activeMobilePanel === 'sidebar' }"
          @click="activeMobilePanel = 'sidebar'"
        >
          简历
        </button>
        <button
          type="button"
          class="editor-mobile-switch"
          :class="{ 'is-active': activeMobilePanel === 'main' }"
          @click="activeMobilePanel = 'main'"
        >
          编辑
        </button>
        <button
          type="button"
          class="editor-mobile-switch"
          :class="{ 'is-active': activeMobilePanel === 'rail' }"
          @click="activeMobilePanel = 'rail'"
        >
          预览
        </button>
      </div>

      <ResumeSidebar
        class="interviews-sidebar editor-sidebar"
        :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'sidebar' }"
        :resumes="resumeStore.resumes"
        :active-id="resumeStore.currentResumeId"
        :current-resume="resumeStore.currentResume"
        :templates="resumeStore.templates"
        :username="authStore.user?.username || ''"
        @select-resume="handleSelectResume"
        @create-resume="handleCreateResume"
        @back-dashboard="router.push('/dashboard')"
        @logout="handleLogout"
      />

      <section class="interviews-main editor-main" :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'main' }">
        <div v-if="resumeStore.loading" class="interviews-editor-canvas editor-loading-card">正在加载简历数据...</div>

        <template v-else>
          <ResumeBasicsForm
            ref="basicsFormRef"
            :draft="resumeStore.currentResume"
            :templates="resumeStore.templates"
            :saving="saving"
            :rendering="rendering"
            :avatar-uploading="avatarUploading"
            :upload-avatar="handleUploadAvatar"
            @view-applications="handleViewApplications"
            @save="handleSave"
            @render="handleRender"
            @delete="handleDelete"
          />
        </template>
      </section>

      <aside class="interviews-rail editor-rail" :class="{ 'is-mobile-hidden': isMobileWorkspace && activeMobilePanel !== 'rail' }">
        <ResumePreviewPane :preview-url="resumeStore.previewUrl" @navigate-section="handlePreviewNavigate" />
      </aside>
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
import { RouterLink, useRouter } from 'vue-router'
import brandMark from '../assets/logo.png'
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
const activeMobilePanel = ref('main')
const isMobileWorkspace = ref(false)
let toastTimer = null
let autoPreviewTimer = null
let autoPreviewSnapshot = ''

function syncWorkspaceMode() {
  if (typeof window === 'undefined') return
  isMobileWorkspace.value = window.innerWidth <= 1024
}

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
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    toastText.value = ''
  }, 2200)
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
  if (autoPreviewTimer) clearTimeout(autoPreviewTimer)
  autoPreviewTimer = window.setTimeout(syncPreviewAutomatically, 700)
}

function handleSelectResume(resumeId) {
  resumeStore.selectResume(resumeId)
  autoPreviewSnapshot = getAutoPreviewSnapshot()
  activeMobilePanel.value = 'main'
}

function handleCreateResume() {
  resumeStore.createLocalResume()
  autoPreviewSnapshot = getAutoPreviewSnapshot()
  activeMobilePanel.value = 'main'
}

async function handleViewApplications() {
  try {
    let resumeId = resumeStore.currentResumeId
    if (!resumeId) {
      const saved = await resumeStore.saveCurrentResume()
      resumeId = saved.id
      autoPreviewSnapshot = getAutoPreviewSnapshot()
      showToast('简历已保存')
    }
    if (!resumeId) {
      openNoticeDialog('当前简历还没有可用的保存记录，请先保存后再查看关联投递。')
      return
    }
    await router.push({ path: '/applications', query: { resume_id: resumeId } })
  } catch (error) {
    reportError(error)
  }
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
  activeMobilePanel.value = 'main'
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
  try {
    syncWorkspaceMode()
    window.addEventListener('resize', syncWorkspaceMode)
    await resumeStore.bootstrapEditor()
    autoPreviewSnapshot = getAutoPreviewSnapshot()
  } catch (error) {
    reportError(error)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', syncWorkspaceMode)
  if (toastTimer) clearTimeout(toastTimer)
  if (autoPreviewTimer) clearTimeout(autoPreviewTimer)
})

watch(
  () => resumeStore.currentResume,
  () => {
    scheduleAutoPreviewSync()
  },
  { deep: true },
)
</script>
