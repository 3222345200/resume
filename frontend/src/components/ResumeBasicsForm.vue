<template>
  <section class="editor-card resume-form-card template-editor-card">
    <header class="template-editor-header">
      <!-- <div>
        <p class="eyebrow">Editor</p>
        <h2>模板字段编辑</h2>
      </div> -->
        <div class="form-actions">
          <button class="ghost-button" type="button" @click="$emit('view-applications')">查看关联投递</button>
          <button class="primary-button" type="button" :disabled="saving" @click="$emit('save')">
            {{ saving ? '保存中...' : '保存简历' }}
          </button>
          <button class="ghost-button" type="button" :disabled="rendering" @click="$emit('render')">
            {{ rendering ? '生成中...' : '下载 PDF' }}
        </button>
        <button class="ghost-button danger-lite" type="button" @click="$emit('delete')">删除</button>
      </div>
    </header>

    <div class="template-editor-scroll">
      <section class="layout-setting-panel" :class="{ 'is-expanded': isLayoutSettingExpanded }">
        <button
          type="button"
          class="layout-setting-toggle"
          :aria-expanded="String(isLayoutSettingExpanded)"
          @click="isLayoutSettingExpanded = !isLayoutSettingExpanded"
        >
          <span class="layout-setting-title">版式设置</span>
          <span class="layout-setting-tip">调整字体、字号与行距</span>
          <span class="section-toggle-chevron" :class="{ 'is-collapsed': !isLayoutSettingExpanded }" aria-hidden="true"></span>
        </button>

        <div v-if="isLayoutSettingExpanded" class="layout-setting-groups">
          <div class="layout-setting-group">
            <div class="layout-setting-fields">
              <label class="plain-field">
                <span>标题字体</span>
                <CustomSelect v-model="draft.content.layout.section_title_font_family" :options="fontFamilyOptions" />
              </label>
              <label class="plain-field">
                <span>标题字体大小</span>
                <CustomSelect v-model="draft.content.layout.section_title_size" :options="sectionTitleSizeOptions" />
              </label>
              <label class="plain-field">
                <span>标题下边距</span>
                <CustomSelect v-model="draft.content.layout.section_divider_gap" :options="dividerGapOptions" />
              </label>
              <label class="plain-field">
                <span>正文字体</span>
                <CustomSelect v-model="draft.content.layout.content_font_family" :options="fontFamilyOptions" />
              </label>
              <label class="plain-field">
                <span>正文字体大小</span>
                <CustomSelect v-model="draft.content.layout.content_font_size" :options="contentFontSizeOptions" />
              </label>
              <label class="plain-field">
                <span>正文行距</span>
                <CustomSelect v-model="draft.content.layout.content_line_height" :options="lineHeightOptions" />
              </label>
            </div>
          </div>

        </div>
      </section>

      <div class="template-editor-layout">
        <aside class="section-nav-panel vue-section-nav-panel" :class="{ 'is-collapsed': isModuleNavCollapsed }">
          <button
            type="button"
            class="module-nav-collapse-toggle"
            :aria-expanded="String(!isModuleNavCollapsed)"
            @click="isModuleNavCollapsed = !isModuleNavCollapsed"
          >
            <div class="section-nav-copy">
              <h3>编辑模块</h3>
              <p class="meta-text">左侧选模块，右侧编辑内容。</p>
            </div>
            <span v-if="isModuleNavCollapsed" class="module-nav-collapsed-label">模块</span>
            <span class="section-toggle-chevron" :class="{ 'is-collapsed': isModuleNavCollapsed }" aria-hidden="true"></span>
          </button>

          <div v-if="!isModuleNavCollapsed" class="section-nav-scrollbox">
            <div class="editor-section-nav vue-editor-section-nav">
              <div
                v-for="sectionBlock in sectionNavBlocks"
                :key="sectionBlock.key"
                class="editor-section-nav-item"
                :class="{
                  'is-active': activeSectionKey === sectionBlock.key,
                  'is-reorderable': sectionBlock.reorderable,
                  'is-dragging': draggedSectionKey === sectionBlock.key,
                  'is-drop-target': dropTargetSectionKey === sectionBlock.key,
                }"
                @dragover.prevent="handleSectionDragOver(sectionBlock)"
                @dragleave="handleSectionDragLeave(sectionBlock)"
                @drop.prevent="handleSectionDrop(sectionBlock)"
              >
                <button type="button" class="editor-section-nav-button" @click="selectSection(sectionBlock.key)">
                  <strong>{{ sectionBlock.title }}</strong>
                  <span>点击切换编辑</span>
                </button>

                <button
                  v-if="sectionBlock.reorderable"
                  type="button"
                  class="editor-section-drag-handle"
                  draggable="true"
                  aria-label="拖动排序"
                  title="拖动排序"
                  @dragstart="handleSectionDragStart(sectionBlock.key, $event)"
                  @dragend="handleSectionDragEnd"
                >
                  <span></span>
                  <span></span>
                  <span></span>
                </button>
                <span v-else class="editor-section-drag-placeholder" aria-hidden="true"></span>
              </div>
            </div>

            <button class="ghost-button section-nav-add-button" type="button" @click="addCustomSection">新增自定义模块</button>
          </div>

          <div v-else class="section-nav-mini-stack">
            <button
              v-for="sectionBlock in sectionNavBlocks"
              :key="sectionBlock.key"
              type="button"
              class="section-nav-mini-button"
              :class="{
                'is-active': activeSectionKey === sectionBlock.key,
                'is-reorderable': sectionBlock.reorderable,
              }"
              :title="sectionBlock.title"
              @click="selectSection(sectionBlock.key)"
            >
              {{ getSectionShortTitle(sectionBlock.title) }}
            </button>
          </div>
        </aside>

        <div class="section-workspace vue-section-workspace">
          <section
            v-show="activeSectionKey === 'basics'"
            :ref="(el) => setSectionRef('basics', el)"
            class="editor-card section-editor-card active-module-card"
            :class="{ 'section-jump-flash': jumpHighlightSectionKey === 'basics' }"
            data-section-key="basics"
          >
            <div class="editor-card-header">
              <h3>基础信息</h3>
            </div>

            <div class="basics-editor-layout">
              <div class="avatar-column-card">
                    <strong>头像设置</strong>

                <div
                  class="avatar-preview-box avatar-preview-large avatar-edit-trigger"
                  role="button"
                  tabindex="0"
                  @click="editCurrentAvatar"
                  @keydown.enter.prevent="editCurrentAvatar"
                  @keydown.space.prevent="editCurrentAvatar"
                >
                  <img :src="avatarPreview" :style="avatarImageStyle" alt="头像预览" />
                </div>
                <p class="avatar-frame-note">这里按一寸照比例预览，下载 PDF 时会使用同样的裁剪结果和固定尺寸。</p>

                <button class="ghost-button avatar-change-btn" type="button" :disabled="avatarUploading" @click="openAvatarFilePicker">
                  {{ avatarUploading ? '上传中...' : '修改照片' }}
                </button>
                <input ref="avatarFileInputRef" type="file" accept="image/*" hidden :disabled="avatarUploading" @change="handleAvatarChange" />
                <button class="ghost-button" type="button" @click="requestClearAvatar">移除照片</button>

                <div class="avatar-crop-controls avatar-crop-panel">
                  <label>
                    <span>缩放</span>
                    <input v-model.number="draft.content.basics.avatar_crop.scale" type="range" min="1" max="3" step="0.01" />
                  </label>
                  <label>
                    <span>左右位置</span>
                    <input v-model.number="draft.content.basics.avatar_crop.offset_x" type="range" min="0" max="100" step="1" />
                  </label>
                  <label>
                    <span>上下位置</span>
                    <input v-model.number="draft.content.basics.avatar_crop.offset_y" type="range" min="0" max="100" step="1" />
                  </label>
                </div>

                <p class="avatar-frame-note">未上传照片时，将使用默认占位图。支持图片格式，大小不能超过 5MB。</p>
              </div>

              <form class="basics-field-grid" @submit.prevent>
                <div class="avatar-column-card basics-avatar-row">
                  <strong>头像设置</strong>
                  <div
                    class="avatar-preview-box avatar-preview-large avatar-edit-trigger"
                    role="button"
                    tabindex="0"
                    @click="editCurrentAvatar"
                    @keydown.enter.prevent="editCurrentAvatar"
                    @keydown.space.prevent="editCurrentAvatar"
                  >
                    <img :src="avatarPreview" :style="avatarImageStyle" alt="头像预览" />
                  </div>
                  <p class="avatar-frame-note">点击照片可重新裁切上传，下载 PDF 时会使用同样的裁切结果和固定尺寸。</p>
                  <button class="ghost-button avatar-change-btn" type="button" :disabled="avatarUploading" @click="openAvatarFilePicker">
                    {{ avatarUploading ? '上传中...' : '修改照片' }}
                  </button>
                  <button class="ghost-button" type="button" @click="requestClearAvatar">移除照片</button>
                  <p class="avatar-frame-note">未上传照片时，将使用默认占位图。支持图片格式，大小不能超过 5MB。</p>
                </div>
                <label class="plain-field"><span>姓名</span><input v-model.trim="draft.content.basics.name" /></label>
                <label class="plain-field"><span>电话</span><input v-model.trim="draft.content.basics.phone" /></label>
                <label class="plain-field basics-email-field"><span>邮箱</span><input v-model.trim="draft.content.basics.email" /></label>
                <label class="plain-field basics-city-field"><span>意向城市</span><input v-model.trim="draft.content.basics.location" /></label>
                <label class="plain-field basics-job-target-field"><span>求职意向</span><input v-model.trim="draft.content.basics.job_target" placeholder="例如：后端开发" /></label>
                <div class="single-rich-field full-row"><span>个人简介</span><RichTextEditor v-model="draft.content.basics.summary" toolbar-preset="resume" placeholder="用一段话概括你的方向、优势和背景" /></div>
              </form>
            </div>
          </section>

          <div
            v-show="activeSectionKey === 'education'"
            :ref="(el) => setSectionRef('education', el)"
            class="active-module-wrap"
            :class="{ 'section-jump-flash': jumpHighlightSectionKey === 'education' }"
            data-section-key="education"
          >
            <ResumeRepeatSection
              :items="draft.content.education"
              title="教育经历"
              short-name="教育"
              eyebrow="Education"
              :create-item="createEducationItem"
            >
              <template #default="{ item }">
                <div class="repeat-item-grid education-item-grid">
                  <label><span>学校</span><input v-model.trim="item.school" /></label>
                  <label><span>专业</span><input v-model.trim="item.major" /></label>
                  <label>
                    <span>学历</span>
                    <CustomSelect v-model="item.degree" :options="degreeOptions" placeholder="请选择学历" />
                  </label>
                  <label class="item-start-date-field"><span>开始时间</span><MonthPicker v-model="item.start_date" /></label>
                  <label class="item-end-date-field"><span>结束时间</span><MonthPicker v-model="item.end_date" allow-present /></label>
                  <div class="single-rich-field full-row"><span>亮点</span><RichTextEditor v-model="item.highlights" mode="list" toolbar-preset="resume" placeholder="每行一条，支持加粗/链接" /></div>
                </div>
              </template>
            </ResumeRepeatSection>
          </div>

          <template v-for="sectionBlock in orderedSectionBlocks" :key="sectionBlock.key">
            <section
              v-if="sectionBlock.kind === 'skills'"
              v-show="activeSectionKey === sectionBlock.key"
              :ref="(el) => setSectionRef(sectionBlock.key, el)"
              class="editor-card section-editor-card active-module-card"
              :class="{ 'section-jump-flash': jumpHighlightSectionKey === sectionBlock.key }"
              :data-section-key="sectionBlock.key"
            >
              <div class="editor-card-header"><h3>专业技能</h3></div>
              <div class="single-rich-field"><span>专业技能</span><RichTextEditor v-model="draft.content.skills" mode="list" toolbar-preset="resume" placeholder="每行一条技能，支持加粗/斜体/列表/链接" /></div>
            </section>

            <div
              v-else-if="sectionBlock.kind === 'experience'"
              v-show="activeSectionKey === sectionBlock.key"
              :ref="(el) => setSectionRef(sectionBlock.key, el)"
              class="active-module-wrap"
              :class="{ 'section-jump-flash': jumpHighlightSectionKey === sectionBlock.key }"
              :data-section-key="sectionBlock.key"
            >
              <ResumeRepeatSection :items="draft.content.experience" title="工作/实习经历" short-name="经历" eyebrow="Experience" :create-item="createExperienceItem">
                <template #item-head-extra="{ item }">
                  <CustomSelect v-model="item.entry_type" :options="experienceTypeOptions" />
                </template>
                <template #default="{ item }">
                  <div class="repeat-item-grid experience-item-grid">
                    <label><span>公司</span><input v-model.trim="item.company" /></label>
                    <label><span>地点</span><input v-model.trim="item.location" /></label>
                    <label><span>部门</span><input v-model.trim="item.department" /></label>
                    <label><span>岗位</span><input v-model.trim="item.role" /></label>
                    <label class="item-start-date-field"><span>开始时间</span><MonthPicker v-model="item.start_date" /></label>
                    <label class="item-end-date-field"><span>结束时间</span><MonthPicker v-model="item.end_date" allow-present /></label>
                  <div class="single-rich-field full-row"><span>亮点</span><RichTextEditor v-model="item.highlights" mode="list" toolbar-preset="resume" placeholder="每行一条，支持加粗/链接" /></div>
                  </div>
                </template>
              </ResumeRepeatSection>
            </div>

            <div
              v-else-if="sectionBlock.kind === 'projects'"
              v-show="activeSectionKey === sectionBlock.key"
              :ref="(el) => setSectionRef(sectionBlock.key, el)"
              class="active-module-wrap"
              :class="{ 'section-jump-flash': jumpHighlightSectionKey === sectionBlock.key }"
              :data-section-key="sectionBlock.key"
            >
              <ResumeRepeatSection :items="draft.content.projects" title="项目经历" short-name="项目" eyebrow="Projects" :create-item="createProjectItem">
                <template #default="{ item }">
                  <div class="repeat-item-grid project-repeat-grid">
                    <label class="project-name-field"><span>项目名称</span><input v-model.trim="item.name" /></label>
                    <label class="project-date-field"><span>开始时间</span><MonthPicker v-model="item.start_date" /></label>
                    <label class="project-date-field">
                      <span>结束时间</span>
                      <MonthPicker v-model="item.end_date" allow-present />
                      <small v-if="getDateRangeError(item.start_date, item.end_date)" class="date-range-error-text">{{ getDateRangeError(item.start_date, item.end_date) }}</small>
                    </label>
                    <div class="single-rich-field full-row"><span>项目描述</span><RichTextEditor v-model="item.description" toolbar-preset="resume" placeholder="例如：企业级权限后台与数据分析平台，支持加粗/链接" /></div>
                    <div class="single-rich-field full-row"><span>主要工作</span><RichTextEditor v-model="item.highlights" mode="list" toolbar-preset="resume" placeholder="每行一条，支持加粗/链接" /></div>
                  </div>
                </template>
              </ResumeRepeatSection>
            </div>

            <div
              v-else-if="sectionBlock.kind === 'portfolio'"
              v-show="activeSectionKey === sectionBlock.key"
              :ref="(el) => setSectionRef(sectionBlock.key, el)"
              class="active-module-wrap"
              :class="{ 'section-jump-flash': jumpHighlightSectionKey === sectionBlock.key }"
              :data-section-key="sectionBlock.key"
            >
              <ResumeRepeatSection :items="draft.content.portfolio" title="作品集" short-name="作品" eyebrow="Portfolio" :create-item="createPortfolioItem">
                <template #default="{ item }">
                  <div class="repeat-item-grid">
                    <label><span>标题</span><input v-model.trim="item.title" /></label>
                    <label><span>链接</span><input v-model.trim="item.link" placeholder="https://github.com/yourname/project" /></label>
                    <div class="single-rich-field full-row"><span>简介</span><RichTextEditor v-model="item.summary" toolbar-preset="resume" placeholder="请输入简介，支持加粗/斜体/链接" /></div>
                  </div>
                </template>
              </ResumeRepeatSection>
            </div>

            <div
              v-else-if="sectionBlock.kind === 'research'"
              v-show="activeSectionKey === sectionBlock.key"
              :ref="(el) => setSectionRef(sectionBlock.key, el)"
              class="active-module-wrap"
              :class="{ 'section-jump-flash': jumpHighlightSectionKey === sectionBlock.key }"
              :data-section-key="sectionBlock.key"
            >
              <ResumeRepeatSection :items="draft.content.research" title="科研经历" short-name="科研" eyebrow="Research" :create-item="createResearchItem">
                <template #default="{ item }">
                  <div class="repeat-item-grid">
                    <label><span>标题</span><input v-model.trim="item.title" /></label>
                    <label><span>标签</span><input v-model.trim="item.label" placeholder="JSA 在投（二作）" /></label>
                    <div class="single-rich-field full-row"><span>简介</span><RichTextEditor v-model="item.summary" toolbar-preset="resume" placeholder="请输入简介，支持加粗/斜体/链接" /></div>
                  </div>
                </template>
              </ResumeRepeatSection>
            </div>

            <div
              v-else-if="sectionBlock.kind === 'honors'"
              v-show="activeSectionKey === sectionBlock.key"
              :ref="(el) => setSectionRef(sectionBlock.key, el)"
              class="active-module-wrap"
              :class="{ 'section-jump-flash': jumpHighlightSectionKey === sectionBlock.key }"
              :data-section-key="sectionBlock.key"
            >
              <ResumeRepeatSection :items="draft.content.honors" title="荣誉奖项" short-name="奖项" eyebrow="Honors" :create-item="createHonorItem">
                <template #default="{ item }">
                  <div class="repeat-item-grid">
                    <label><span>标题</span><input v-model.trim="item.title" /></label>
                    <label><span>标签</span><input v-model.trim="item.label" placeholder="国家奖学金 / 竞赛一等奖" /></label>
                    <div class="single-rich-field full-row"><span>简介</span><RichTextEditor v-model="item.summary" toolbar-preset="resume" placeholder="请输入简介，支持加粗/斜体/链接" /></div>
                  </div>
                </template>
              </ResumeRepeatSection>
            </div>

            <section
              v-else-if="sectionBlock.kind === 'custom'"
              v-show="activeSectionKey === sectionBlock.key"
              :ref="(el) => setSectionRef(sectionBlock.key, el)"
              class="editor-card section-editor-card active-module-card"
              :class="{ 'section-jump-flash': jumpHighlightSectionKey === sectionBlock.key }"
              :data-section-key="sectionBlock.key"
              :data-custom-section-id="sectionBlock.section.id"
            >
              <div class="editor-card-header custom-section-header">
                <div>
                  <p class="eyebrow">Custom</p>
                  <h3>{{ sectionBlock.title }}</h3>
                </div>
                <button class="remove-entry-btn" type="button" @click="requestRemoveCustomSection(sectionBlock.section)">删除模块</button>
              </div>

              <div class="repeat-editor-list">
                <article class="repeat-editor-item">
                  <div class="repeat-item-grid">
                    <label class="full-row">
                      <span>模块标题</span>
                      <input v-model.trim="sectionBlock.section.title" placeholder="例如：校园经历 / 社团经历 / 证书" />
                    </label>
                  </div>

                  <div class="custom-items-wrap">
                    <div class="repeat-item-head sub-head">
                      <strong>条目列表</strong>
                      <button class="ghost-button add-entry-btn" type="button" @click="addCustomItem(sectionBlock.section)">新增条目</button>
                    </div>

                    <article v-for="(item, itemIndex) in sectionBlock.section.items" :key="itemIndex" class="custom-sub-item">
                      <div class="repeat-item-head">
                        <strong>条目 {{ itemIndex + 1 }}</strong>
                        <div class="repeat-inline-actions">
                          <button class="mini-move-btn" type="button" :disabled="itemIndex === 0" @click="moveCustomItem(sectionBlock.section, itemIndex, -1)">上移</button>
                          <button class="mini-move-btn" type="button" :disabled="itemIndex === sectionBlock.section.items.length - 1" @click="moveCustomItem(sectionBlock.section, itemIndex, 1)">下移</button>
                          <button class="remove-entry-btn" type="button" @click="requestRemoveCustomItem(sectionBlock.section, itemIndex)">删除</button>
                        </div>
                      </div>

                      <div class="repeat-item-grid">
                        <label><span>标题</span><input v-model.trim="item.title" /></label>
                        <label><span>副标题</span><input v-model.trim="item.subtitle" /></label>
                        <label><span>开始时间</span><MonthPicker v-model="item.start_date" /></label>
                        <label><span>结束时间</span><MonthPicker v-model="item.end_date" allow-present /></label>
                        <div class="single-rich-field full-row"><span>描述</span><RichTextEditor v-model="item.description" toolbar-preset="resume" placeholder="请输入描述，支持加粗/链接" /></div>
                        <div class="single-rich-field full-row"><span>重点内容</span><RichTextEditor v-model="item.highlights" mode="list" toolbar-preset="resume" placeholder="每行一条，支持加粗/链接" /></div>
                      </div>
                    </article>

                    <div v-if="!sectionBlock.section.items.length" class="empty-list-tip">暂无条目。</div>
                  </div>
                </article>
              </div>
            </section>
          </template>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :open="confirmState.open"
      :title="confirmState.title"
      :message="confirmState.message"
      confirm-text="确认删除"
      cancel-text="取消"
      @confirm="handleConfirmAction"
      @cancel="closeConfirmDialog"
    />

    <ConfirmDialog
      :open="noticeState.open"
      eyebrow="Notice"
      :title="noticeState.title"
      :message="noticeState.message"
      confirm-text="我知道了"
      :show-cancel="false"
      @confirm="closeNoticeDialog"
      @cancel="closeNoticeDialog"
    />

    <AvatarCropDialog
      :open="Boolean(pendingAvatarFile)"
      :file="pendingAvatarFile"
      :can-remove="Boolean(draft.content.basics.avatar_url)"
      @confirm="confirmAvatarCrop"
      @cancel="closeAvatarCropDialog"
      @change-file="openAvatarFilePicker"
      @remove-file="handleDialogRemoveAvatar"
    />
  </section>
</template>

<script setup>
import { computed, nextTick, onUnmounted, ref, watch } from 'vue'
import defaultAvatar from '../assets/default-avatar.jpg'
import { createCustomSection } from '../stores/resume'
import AvatarCropDialog from './AvatarCropDialog.vue'
import ConfirmDialog from './ConfirmDialog.vue'
import CustomSelect from './CustomSelect.vue'
import MonthPicker from './MonthPicker.vue'
import ResumeRepeatSection from './ResumeRepeatSection.vue'
import RichTextEditor from './RichTextEditor.vue'

const props = defineProps({
  draft: { type: Object, required: true },
  templates: { type: Array, default: () => [] },
  saving: { type: Boolean, default: false },
  rendering: { type: Boolean, default: false },
  avatarUploading: { type: Boolean, default: false },
  uploadAvatar: { type: Function, required: true },
})

defineEmits(['save', 'render', 'delete', 'view-applications'])

const avatarVersion = ref(Date.now())
const avatarFileInputRef = ref(null)
const pendingAvatarFile = ref(null)
const avatarSourceFile = ref(null)
const isLayoutSettingExpanded = ref(true)
const activeSectionKey = ref('basics')
const isModuleNavCollapsed = ref(false)
const jumpHighlightSectionKey = ref('')
const draggedSectionKey = ref('')
const dropTargetSectionKey = ref('')
const latestValidDateState = ref('')
const sectionElementMap = new Map()
let restoringInvalidDateState = false
let jumpHighlightTimer = null
const confirmState = ref({
  open: false,
  title: '',
  message: '',
  action: null,
})
const noticeState = ref({
  open: false,
  title: '',
  message: '',
})
const builtInSectionTitles = {
  skills: '专业技能',
  experience: '工作/实习经历',
  projects: '项目经历',
  portfolio: '作品集',
  research: '科研经历',
  honors: '荣誉奖项',
}

const sectionTitleSizeOptions = [
  '14', '15', '16', '17', '18', '19', '20', '21', '22', '24', '26', '28'
].map((value) => ({ label: value, value }))
const contentFontSizeOptions = [
  '10', '10.5', '11', '11.5', '12', '12.5', '13', '13.5', '14', '14.5', '15', '16', '17', '18'
].map((value) => ({ label: value, value }))
const lineHeightOptions = [
  '1.0', '1.1', '1.15', '1.2', '1.25', '1.3', '1.36', '1.4', '1.45', '1.5', '1.6', '1.75', '2.0'
].map((value) => ({ label: value, value }))
const dividerGapOptions = [
  '0', '1', '2', '3', '4', '5', '6', '8', '10', '12', '14', '16'
].map((value) => ({ label: value, value }))
const fontFamilyOptions = [
  { label: '楷体', value: 'kaiti' },
  { label: '宋体', value: 'songti' },
  { label: '仿宋', value: 'fangsong' },
  { label: '黑体', value: 'heiti' },
]
const fontFamilyOptionStyles = {
  kaiti: "'KaiTi', 'STKaiti', serif",
  songti: "'SimSun', 'Songti SC', serif",
  fangsong: "'FangSong', 'STFangsong', serif",
  heiti: "'SimHei', 'Heiti SC', sans-serif",
}
fontFamilyOptions.forEach((option) => {
  option.fontFamily = fontFamilyOptionStyles[option.value]
})

const degreeOptions = [
  { label: '请选择学历', value: '' },
  { label: '专科', value: '专科' },
  { label: '本科', value: '本科' },
  { label: '硕士', value: '硕士' },
  { label: '博士', value: '博士' },
]
const experienceTypeOptions = [
  { label: '实习经历', value: '实习经历' },
  { label: '工作经历', value: '工作经历' },
]

const orderedSectionBlocks = computed(() => {
  syncSectionOrder()
  return props.draft.content.section_order
    .map((key) => {
      if (isCustomSectionKey(key)) {
        const section = getCustomSectionByKey(key)
        if (!section) {
          return null
        }
        return {
          key,
          kind: 'custom',
          title: section.title || '自定义模块',
          section,
        }
      }

      return {
        key,
        kind: key,
        title: builtInSectionTitles[key] || '简历模块',
      }
    })
    .filter(Boolean)
})

const sectionNavBlocks = computed(() => [
  { key: 'basics', title: '基础信息', reorderable: false },
  { key: 'education', title: '教育经历', reorderable: false },
  ...orderedSectionBlocks.value.map((section) => ({
    key: section.key,
    title: section.title,
    reorderable: true,
  })),
])

const avatarCrop = computed(() => normalizeAvatarCrop(props.draft.content?.basics?.avatar_crop))

const avatarImageStyle = computed(() => ({
  transform: getAvatarTransform(avatarCrop.value),
  transformOrigin: 'center center',
  objectFit: 'cover',
  objectPosition: '50% 50%',
}))

const avatarPreview = computed(() => {
  const url = props.draft.content.basics.avatar_url
  if (!url) {
    return defaultAvatar
  }
  const joiner = url.includes('?') ? '&' : '?'
  return `${url}${joiner}t=${avatarVersion.value}`
})

watch(
  () => props.draft.id,
  () => {
    activeSectionKey.value = 'basics'
    avatarVersion.value = Date.now()
  },
)

watch(
  sectionNavBlocks,
  (blocks) => {
    if (!blocks.some((section) => section.key === activeSectionKey.value)) {
      activeSectionKey.value = 'basics'
    }
  },
  { immediate: true },
)

watch(
  () => getDateStateSnapshot(),
  (nextSnapshot) => {
    if (restoringInvalidDateState) {
      return
    }

    const dateRangeError = getFirstDateRangeError()
    if (!dateRangeError) {
      latestValidDateState.value = nextSnapshot
      return
    }

    restoringInvalidDateState = true
    restoreDateStateSnapshot(latestValidDateState.value)
    openNoticeDialog('时间范围有误', dateRangeError)
    nextTick(() => {
      restoringInvalidDateState = false
    })
  },
  { immediate: true },
)

onUnmounted(() => {
  if (jumpHighlightTimer) {
    clearTimeout(jumpHighlightTimer)
  }
})

function normalizeAvatarCrop(value) {
  const crop = value && typeof value === 'object' ? value : {}
  const clamp = (input, minimum, maximum, fallback) => {
    const number = Number(input)
    if (!Number.isFinite(number)) {
      return fallback
    }
    return Math.min(maximum, Math.max(minimum, number))
  }

  return {
    scale: clamp(crop.scale, 1, 3, 1),
    offset_x: clamp(crop.offset_x, 0, 100, 50),
    offset_y: clamp(crop.offset_y, 0, 100, 50),
  }
}

function getAvatarTransform(crop) {
  const moveStrength = 0.45 + (crop.scale - 1) * 0.9
  const translateX = (50 - crop.offset_x) * moveStrength
  const translateY = (50 - crop.offset_y) * moveStrength
  return `translate(${translateX}%, ${translateY}%) scale(${crop.scale})`
}

function getSectionShortTitle(title) {
  const value = String(title || '').trim()
  if (!value) {
    return '模块'
  }
  return value.slice(0, 2)
}

async function handleAvatarChange(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) {
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    openNoticeDialog('照片上传失败', '照片大小不能超过 5MB')
    return
    window.alert('照片大小不能超过 5MB')
    return
  }
  avatarSourceFile.value = file
  pendingAvatarFile.value = file
}

function openAvatarFilePicker() {
  if (props.avatarUploading) {
    return
  }
  avatarFileInputRef.value?.click()
}

async function editCurrentAvatar() {
  if (props.avatarUploading) {
    return
  }

  if (!props.draft.content.basics.avatar_url) {
    openAvatarFilePicker()
    return
  }

  if (avatarSourceFile.value) {
    pendingAvatarFile.value = avatarSourceFile.value
    return
  }

  try {
    const response = await fetch(avatarPreview.value)
    if (!response.ok) {
      throw new Error('avatar-load-failed')
    }
    const blob = await response.blob()
    pendingAvatarFile.value = new File([blob], 'avatar.jpg', {
      type: blob.type || 'image/jpeg',
    })
  } catch {
    openAvatarFilePicker()
  }
}

function closeAvatarCropDialog() {
  pendingAvatarFile.value = null
}

async function confirmAvatarCrop(file) {
  await props.uploadAvatar(file)
  avatarVersion.value = Date.now()
  pendingAvatarFile.value = null
}

function openConfirmDialog(title, message, action) {
  confirmState.value = {
    open: true,
    title,
    message,
    action,
  }
}

function closeConfirmDialog() {
  confirmState.value = {
    open: false,
    title: '',
    message: '',
    action: null,
  }
}

function openNoticeDialog(title, message) {
  noticeState.value = {
    open: true,
    title,
    message,
  }
}

function closeNoticeDialog() {
  noticeState.value = {
    open: false,
    title: '',
    message: '',
  }
}

function handleConfirmAction() {
  const action = confirmState.value.action
  closeConfirmDialog()
  if (typeof action === 'function') {
    action()
  }
}

function requestClearAvatar() {
  openConfirmDialog('移除照片', '确认移除当前头像照片吗？移除后保存简历才会生效。', clearAvatar)
}

function handleDialogRemoveAvatar() {
  closeAvatarCropDialog()
  requestClearAvatar()
}

function clearAvatar() {
  props.draft.content.basics.avatar_url = null
  props.draft.content.basics.avatar_crop = { scale: 1, offset_x: 50, offset_y: 50 }
  avatarSourceFile.value = null
  avatarVersion.value = Date.now()
}

function moveArrayItem(items, index, step) {
  const target = index + step
  if (target < 0 || target >= items.length) {
    return
  }
  const temp = items[index]
  items[index] = items[target]
  items[target] = temp
}

function isCustomSectionKey(sectionKey) {
  return sectionKey.startsWith('custom:')
}

function getCustomSectionByKey(sectionKey) {
  if (!isCustomSectionKey(sectionKey)) {
    return null
  }
  const sectionId = sectionKey.slice('custom:'.length)
  return props.draft.content.custom_sections.find((item) => item.id === sectionId) || null
}

function syncSectionOrder() {
  const builtinKeys = Object.keys(builtInSectionTitles)
  const customKeys = props.draft.content.custom_sections
    .map((section) => section.id)
    .filter(Boolean)
    .map((id) => `custom:${id}`)
  const allowedKeys = [...builtinKeys, ...customKeys]
  const incomingKeys = Array.isArray(props.draft.content.section_order) ? props.draft.content.section_order : []
  const nextOrder = []

  incomingKeys.forEach((key) => {
    if (allowedKeys.includes(key) && !nextOrder.includes(key)) {
      nextOrder.push(key)
    }
  })

  allowedKeys.forEach((key) => {
    if (!nextOrder.includes(key)) {
      nextOrder.push(key)
    }
  })

  const currentOrder = props.draft.content.section_order || []
  if (nextOrder.join('|') !== currentOrder.join('|')) {
    props.draft.content.section_order = nextOrder
  }
}

function moveSectionOrder(index, step) {
  syncSectionOrder()
  moveArrayItem(props.draft.content.section_order, index, step)
}

function handleSectionDragStart(sectionKey, event) {
  draggedSectionKey.value = sectionKey
  dropTargetSectionKey.value = ''
  if (event?.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', sectionKey)
  }
}

function handleSectionDragOver(sectionBlock) {
  if (!sectionBlock.reorderable || !draggedSectionKey.value || draggedSectionKey.value === sectionBlock.key) {
    return
  }
  dropTargetSectionKey.value = sectionBlock.key
}

function handleSectionDragLeave(sectionBlock) {
  if (dropTargetSectionKey.value === sectionBlock.key) {
    dropTargetSectionKey.value = ''
  }
}

function handleSectionDrop(sectionBlock) {
  if (!sectionBlock.reorderable || !draggedSectionKey.value || draggedSectionKey.value === sectionBlock.key) {
    handleSectionDragEnd()
    return
  }
  moveSectionToTarget(draggedSectionKey.value, sectionBlock.key)
  selectSection(draggedSectionKey.value)
  handleSectionDragEnd()
}

function handleSectionDragEnd() {
  draggedSectionKey.value = ''
  dropTargetSectionKey.value = ''
}

function moveSectionToTarget(sourceKey, targetKey) {
  syncSectionOrder()
  const order = props.draft.content.section_order
  const sourceIndex = order.indexOf(sourceKey)
  const targetIndex = order.indexOf(targetKey)
  if (sourceIndex === -1 || targetIndex === -1 || sourceIndex === targetIndex) {
    return
  }

  order.splice(sourceIndex, 1)
  const nextTargetIndex = order.indexOf(targetKey)
  const insertIndex = sourceIndex < targetIndex ? nextTargetIndex + 1 : nextTargetIndex
  order.splice(insertIndex, 0, sourceKey)
}

function addCustomSection() {
  const section = createCustomSection()
  props.draft.content.custom_sections.push(section)
  syncSectionOrder()
  selectSection(`custom:${section.id}`)
}

function requestRemoveCustomSection(section) {
  const sectionName = section?.title?.trim() || '自定义模块'
  openConfirmDialog('删除自定义模块', `确认删除「${sectionName}」吗？模块内所有条目都会一起删除。`, () => removeCustomSectionById(section.id))
}

function removeCustomSectionById(sectionId) {
  const index = props.draft.content.custom_sections.findIndex((section) => section.id === sectionId)
  if (index === -1) {
    return
  }
  props.draft.content.custom_sections.splice(index, 1)
  syncSectionOrder()
  selectSection('basics')
}

function selectSection(sectionKey) {
  activeSectionKey.value = sectionKey
}

function setSectionRef(sectionKey, element) {
  if (!sectionKey) {
    return
  }
  if (element) {
    sectionElementMap.set(sectionKey, element)
    return
  }
  sectionElementMap.delete(sectionKey)
}

async function navigateToSection(sectionKey) {
  const targetKey = String(sectionKey || '').trim()
  if (!targetKey) {
    return
  }

  const availableKeys = new Set(['basics', 'education', ...sectionNavBlocks.value.map((section) => section.key)])
  if (!availableKeys.has(targetKey)) {
    return
  }

  selectSection(targetKey)
  await nextTick()

  const element = sectionElementMap.get(targetKey)
  element?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })

  jumpHighlightSectionKey.value = targetKey
  if (jumpHighlightTimer) {
    clearTimeout(jumpHighlightTimer)
  }
  jumpHighlightTimer = window.setTimeout(() => {
    if (jumpHighlightSectionKey.value === targetKey) {
      jumpHighlightSectionKey.value = ''
    }
  }, 1400)
}

defineExpose({
  navigateToSection,
})

async function addCustomItem(section) {
  section.items.push({ title: '', subtitle: '', start_date: '', end_date: '', description: '', highlights: '' })
  await nextTick()
  document
    .querySelector(`[data-custom-section-id="${section.id}"] .custom-sub-item:last-of-type`)
    ?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    })
}

function requestRemoveCustomItem(section, index) {
  const itemTitle = section?.items?.[index]?.title?.trim() || `条目 ${index + 1}`
  openConfirmDialog('删除自定义条目', `确认删除「${itemTitle}」吗？删除后无法恢复。`, () => removeCustomItem(section, index))
}

function removeCustomItem(section, index) {
  section.items.splice(index, 1)
}

function moveCustomItem(section, index, step) {
  moveArrayItem(section.items, index, step)
}

function createEducationItem() {
  return { school: '', major: '', degree: '', start_date: '', end_date: '', highlights: '' }
}

function createExperienceItem() {
  return {
    entry_type: '实习经历',
    company: '',
    role: '',
    department: '',
    location: '',
    start_date: '',
    end_date: '',
    highlights: '',
  }
}

function parseMonthValue(value) {
  if (!value || value === '至今') {
    return null
  }
  const parts = String(value).split('.')
  const year = Number(parts[0])
  const month = Number(parts[1])
  if (!Number.isInteger(year) || !Number.isInteger(month)) {
    return null
  }
  return year * 100 + month
}

function getDateRangeError(startDate, endDate) {
  const startValue = parseMonthValue(startDate)
  const endValue = parseMonthValue(endDate)
  if (startValue !== null && endValue !== null && endValue < startValue) {
    return '结束时间不能早于开始时间'
  }
  return ''
}

function getDateStateSnapshot() {
  return JSON.stringify({
    education: props.draft.content.education.map((item) => ({
      start_date: item.start_date || '',
      end_date: item.end_date || '',
    })),
    experience: props.draft.content.experience.map((item) => ({
      start_date: item.start_date || '',
      end_date: item.end_date || '',
    })),
    projects: props.draft.content.projects.map((item) => ({
      start_date: item.start_date || '',
      end_date: item.end_date || '',
    })),
    custom_sections: props.draft.content.custom_sections.map((section) => ({
      items: section.items.map((item) => ({
        start_date: item.start_date || '',
        end_date: item.end_date || '',
      })),
    })),
  })
}

function getFirstDateRangeError() {
  const builtinDateSections = [
    { items: props.draft.content.education, title: '教育经历' },
    { items: props.draft.content.experience, title: '工作/实习经历' },
    { items: props.draft.content.projects, title: '项目经历' },
  ]

  for (const sectionInfo of builtinDateSections) {
    for (const [itemIndex, item] of sectionInfo.items.entries()) {
      if (getDateRangeError(item.start_date, item.end_date)) {
        return `${sectionInfo.title}第${itemIndex + 1}条：开始时间不能晚于结束时间`
      }
    }
  }

  for (const section of props.draft.content.custom_sections) {
    const sectionTitle = String(section.title || '').trim() || '自定义模块'
    for (const [itemIndex, item] of section.items.entries()) {
      if (getDateRangeError(item.start_date, item.end_date)) {
        return `${sectionTitle}第${itemIndex + 1}条：开始时间不能晚于结束时间`
      }
    }
  }

  return ''
}

function restoreDateStateSnapshot(snapshotText) {
  if (!snapshotText) {
    return
  }

  const snapshot = JSON.parse(snapshotText)
  ;['education', 'experience', 'projects'].forEach((sectionKey) => {
    const currentItems = props.draft.content[sectionKey] || []
    const cachedItems = snapshot[sectionKey] || []
    currentItems.forEach((item, itemIndex) => {
      if (!cachedItems[itemIndex]) {
        return
      }
      item.start_date = cachedItems[itemIndex].start_date || ''
      item.end_date = cachedItems[itemIndex].end_date || ''
    })
  })

  props.draft.content.custom_sections.forEach((section, sectionIndex) => {
    const cachedSection = snapshot.custom_sections?.[sectionIndex]
    if (!cachedSection) {
      return
    }
    section.items.forEach((item, itemIndex) => {
      const cachedItem = cachedSection.items?.[itemIndex]
      if (!cachedItem) {
        return
      }
      item.start_date = cachedItem.start_date || ''
      item.end_date = cachedItem.end_date || ''
    })
  })
}

function createProjectItem() {
  return { name: '', description: '', tech_stack: '', start_date: '', end_date: '', highlights: '' }
}

function createPortfolioItem() {
  return { title: '', link: '', summary: '' }
}

function createResearchItem() {
  return { title: '', label: '', summary: '' }
}

function createHonorItem() {
  return { title: '', label: '', summary: '' }
}
</script>








