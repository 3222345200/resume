import { defineStore } from 'pinia'
import { getToken, requestJson } from '../api/request'

const ONE_INCH_PHOTO_RATIO = 5 / 7
const DEFAULT_AVATAR_CROP = {
  scale: 1,
  offset_x: 50,
  offset_y: 50,
}
const BASE_SECTION_ORDER = ['skills', 'experience', 'projects', 'portfolio', 'research', 'honors']

const defaultContent = () => ({
  basics: {
    name: '',
    phone: '',
    email: '',
    location: '',
    summary: '',
    job_target: '',
    avatar_url: null,
    avatar_crop: { ...DEFAULT_AVATAR_CROP },
  },
  layout: {
    section_title_size: '18',
    content_font_size: '13.5',
    content_line_height: '1.36',
    section_divider_gap: '4',
    section_title_font_family: 'fangsong',
    content_font_family: 'kaiti',
    font_family: 'kaiti',
    section_title_color: '#111111',
    content_font_color: '#111111',
    font_color: '#111111',
  },
  education: [],
  experience: [],
  projects: [],
  portfolio: [],
  research: [],
  honors: [],
  custom_sections: [],
  skills: '',
  section_order: [...BASE_SECTION_ORDER],
})

const createDraftResume = (templateId = 'pro_resume', title = '新建简历') => ({
  id: '',
  title,
  template_id: templateId,
  content: defaultContent(),
  rendered_pdf_url: '',
  created_at: '',
  updated_at: '',
})

const cloneResume = (resume) => JSON.parse(JSON.stringify(resume || createDraftResume()))

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
    scale: clamp(crop.scale, 1, 3, DEFAULT_AVATAR_CROP.scale),
    offset_x: clamp(crop.offset_x, 0, 100, DEFAULT_AVATAR_CROP.offset_x),
    offset_y: clamp(crop.offset_y, 0, 100, DEFAULT_AVATAR_CROP.offset_y),
  }
}

function normalizeSectionOrder(content) {
  const customOrder = Array.isArray(content?.custom_sections)
    ? content.custom_sections.map((section) => 'custom:' + section.id).filter(Boolean)
    : []
  const allowedOrder = [...BASE_SECTION_ORDER, ...customOrder]
  const incomingOrder = Array.isArray(content?.section_order) ? content.section_order : []
  const ordered = []

  incomingOrder.forEach((key) => {
    if (allowedOrder.includes(key) && !ordered.includes(key)) {
      ordered.push(key)
    }
  })

  allowedOrder.forEach((key) => {
    if (!ordered.includes(key)) {
      ordered.push(key)
    }
  })

  return ordered
}

function resolveUniqueResumeTitle(resumes, baseTitle = '新建简历', excludeResumeId = '') {
  const normalizedBaseTitle = String(baseTitle || '').trim() || '新建简历'
  const existingTitles = new Set(
    (Array.isArray(resumes) ? resumes : [])
      .filter((resume) => !excludeResumeId || resume.id !== excludeResumeId)
      .map((resume) => String(resume?.title || '').trim())
      .filter(Boolean),
  )

  if (!existingTitles.has(normalizedBaseTitle)) {
    return normalizedBaseTitle
  }

  let suffix = 2
  while (existingTitles.has(`${normalizedBaseTitle} ${suffix}`)) {
    suffix += 1
  }
  return `${normalizedBaseTitle} ${suffix}`
}

function normalizeCurrentResume(resume, fallbackTemplateId = 'pro_resume') {
  const cloned = cloneResume(resume || createDraftResume(fallbackTemplateId))
  cloned.content = {
    ...defaultContent(),
    ...(cloned.content || {}),
    basics: {
      ...defaultContent().basics,
      ...(cloned.content?.basics || {}),
      avatar_crop: normalizeAvatarCrop(cloned.content?.basics?.avatar_crop),
    },
    layout: {
      ...defaultContent().layout,
      ...(cloned.content?.layout || {}),
      section_title_font_family: cloned.content?.layout?.section_title_font_family || cloned.content?.layout?.font_family || defaultContent().layout.section_title_font_family,
      content_font_family: cloned.content?.layout?.content_font_family || cloned.content?.layout?.font_family || defaultContent().layout.content_font_family,
      font_family: cloned.content?.layout?.content_font_family || cloned.content?.layout?.font_family || defaultContent().layout.font_family,
      section_title_color: cloned.content?.layout?.section_title_color || cloned.content?.layout?.font_color || defaultContent().layout.section_title_color,
      content_font_color: cloned.content?.layout?.content_font_color || cloned.content?.layout?.font_color || defaultContent().layout.content_font_color,
      font_color: cloned.content?.layout?.font_color || cloned.content?.layout?.content_font_color || defaultContent().layout.font_color,
    },
    education: Array.isArray(cloned.content?.education) ? cloned.content.education : [],
    experience: Array.isArray(cloned.content?.experience) ? cloned.content.experience : [],
    projects: Array.isArray(cloned.content?.projects) ? cloned.content.projects : [],
    portfolio: Array.isArray(cloned.content?.portfolio) ? cloned.content.portfolio : [],
    research: Array.isArray(cloned.content?.research) ? cloned.content.research : [],
    honors: Array.isArray(cloned.content?.honors) ? cloned.content.honors : [],
    custom_sections: Array.isArray(cloned.content?.custom_sections) ? cloned.content.custom_sections : [],
  }
  cloned.content.section_order = normalizeSectionOrder(cloned.content)
  return cloned
}

function createCustomSectionId() {
  return `section-${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`
}

function parseMonthValue(value) {
  const monthText = String(value || '').trim()
  if (!/^\d{4}\.\d{2}$/.test(monthText)) {
    return null
  }
  const [yearText, monthPartText] = monthText.split('.')
  const year = Number(yearText)
  const month = Number(monthPartText)
  if (!Number.isInteger(year) || !Number.isInteger(month)) {
    return null
  }
  return year * 100 + month
}

function validateResumeDateRanges(content) {
  const sections = [
    { items: content?.education, name: '教育经历' },
    { items: content?.experience, name: '工作/实习经历' },
    { items: content?.projects, name: '项目经历' },
  ]

  sections.forEach((section) => {
    ;(Array.isArray(section.items) ? section.items : []).forEach((item, index) => {
      const startValue = parseMonthValue(item?.start_date)
      const endValue = parseMonthValue(item?.end_date)
      if (startValue !== null && endValue !== null && startValue > endValue) {
        throw new Error(`${section.name}第${index + 1}条：开始时间不能晚于结束时间`)
      }
    })
  })

  ;(Array.isArray(content?.custom_sections) ? content.custom_sections : []).forEach((section) => {
    const sectionName = String(section?.title || '').trim() || '自定义模块'
    ;(Array.isArray(section?.items) ? section.items : []).forEach((item, index) => {
      const startValue = parseMonthValue(item?.start_date)
      const endValue = parseMonthValue(item?.end_date)
      if (startValue !== null && endValue !== null && startValue > endValue) {
        throw new Error(`${sectionName}第${index + 1}条：开始时间不能晚于结束时间`)
      }
    })
  })
}

function getImageSize(file) {
  return new Promise((resolve, reject) => {
    const objectUrl = URL.createObjectURL(file)
    const image = new Image()

    image.onload = () => {
      URL.revokeObjectURL(objectUrl)
      resolve({ width: image.naturalWidth || 0, height: image.naturalHeight || 0 })
    }

    image.onerror = () => {
      URL.revokeObjectURL(objectUrl)
      reject(new Error('image-load-failed'))
    }

    image.src = objectUrl
  })
}

async function getAutoAvatarCrop(file) {
  try {
    const { width, height } = await getImageSize(file)
    if (!width || !height) {
      return { ...DEFAULT_AVATAR_CROP }
    }

    const imageRatio = width / height
    const portraitBias = imageRatio < ONE_INCH_PHOTO_RATIO
    const ratioGap = portraitBias
      ? ONE_INCH_PHOTO_RATIO / imageRatio
      : imageRatio / ONE_INCH_PHOTO_RATIO

    const scale = portraitBias
      ? Math.min(1.32, Math.max(1, 1 + (ratioGap - 1) * 0.45))
      : Math.min(1.16, Math.max(1, 1 + (ratioGap - 1) * 0.12))

    return normalizeAvatarCrop({
      scale,
      offset_x: 50,
      offset_y: portraitBias ? 38 : 42,
    })
  } catch {
    return { ...DEFAULT_AVATAR_CROP }
  }
}

export function createCustomSection() {
  return {
    id: createCustomSectionId(),
    title: '',
    items: [
      {
        title: '',
        subtitle: '',
        start_date: '',
        end_date: '',
        description: '',
        highlights: '',
      },
    ],
  }
}

export const useResumeStore = defineStore('resume', {
  state: () => ({
    templates: [],
    resumes: [],
    currentResumeId: '',
    currentResume: createDraftResume(),
    previewUrl: '',
    loading: false,
  }),

  getters: {
    activeTemplateName: (state) => {
      const template = state.templates.find((item) => item.id === state.currentResume.template_id)
      return template?.name || state.currentResume.template_id || '默认模板'
    },
  },

  actions: {
    buildPreviewUrl(resumeId) {
      if (!resumeId) {
        return ''
      }
      const token = encodeURIComponent(getToken())
      return `/api/resumes/${resumeId}/preview?v=${Date.now()}&token=${token}`
    },

    buildPdfDownloadUrl(resumeId) {
      if (!resumeId) {
        return ''
      }
      const token = encodeURIComponent(getToken())
      return `/api/resumes/${resumeId}/pdf/download?v=${Date.now()}&token=${token}`
    },

    async bootstrapEditor() {
      this.loading = true
      try {
        const [templates, resumeResult] = await Promise.all([
          requestJson('/api/templates'),
          requestJson('/api/resumes'),
        ])
        this.templates = templates
        this.resumes = resumeResult.items || []

        if (this.resumes.length > 0) {
          this.selectResume(this.resumes[0].id)
          return
        }

        this.currentResumeId = ''
        this.currentResume = createDraftResume(this.templates[0]?.id || 'pro_resume')
        this.previewUrl = ''
      } finally {
        this.loading = false
      }
    },

    selectResume(resumeId) {
      const resume = this.resumes.find((item) => item.id === resumeId)
      if (!resume) {
        return
      }
      this.currentResumeId = resume.id
      this.currentResume = normalizeCurrentResume(resume, this.templates[0]?.id || 'pro_resume')
      this.previewUrl = this.buildPreviewUrl(resume.id)
    },

    createLocalResume() {
      this.currentResumeId = ''
      const nextTitle = resolveUniqueResumeTitle(this.resumes, '新建简历')
      this.currentResume = createDraftResume(this.templates[0]?.id || 'pro_resume', nextTitle)
      this.previewUrl = ''
    },

    async saveCurrentResume() {
      this.currentResume = normalizeCurrentResume(this.currentResume, this.templates[0]?.id || 'pro_resume')
      this.currentResume.content.section_order = normalizeSectionOrder(this.currentResume.content)
      this.currentResume.content.layout.font_family = this.currentResume.content.layout.content_font_family
      validateResumeDateRanges(this.currentResume.content)
      const payload = {
        title: this.currentResume.title.trim(),
        template_id: this.currentResume.template_id,
        content: this.currentResume.content,
      }

      if (!payload.title) {
        throw new Error('标题不能为空')
      }

      const duplicatedTitle = this.resumes.some((resume) => {
        return resume.id !== this.currentResumeId && String(resume.title || '').trim() === payload.title
      })
      if (duplicatedTitle) {
        throw new Error('同一用户下简历标题不能重复')
      }

      const path = this.currentResumeId ? `/api/resumes/${this.currentResumeId}` : '/api/resumes'
      const method = this.currentResumeId ? 'PUT' : 'POST'
      const saved = await requestJson(path, {
        method,
        body: JSON.stringify(payload),
      })

      this.currentResumeId = saved.id
      this.currentResume = normalizeCurrentResume(saved, this.templates[0]?.id || 'pro_resume')
      await this.refreshResumeList(saved.id)
      this.previewUrl = this.buildPreviewUrl(saved.id)
      return saved
    },

    async renderCurrentResume() {
      const saved = await this.saveCurrentResume()
      const result = await requestJson(`/api/resumes/${saved.id}/render`, {
        method: 'POST',
        body: JSON.stringify({
          title: this.currentResume.title.trim(),
          template_id: this.currentResume.template_id,
          content: this.currentResume.content,
        }),
      })
      if (result.resume) {
        this.currentResume = normalizeCurrentResume(result.resume, this.templates[0]?.id || 'pro_resume')
      }
      await this.refreshResumeList(saved.id)
      this.previewUrl = this.buildPreviewUrl(saved.id)
      return this.buildPdfDownloadUrl(saved.id) || result.pdf_url
    },

    async uploadAvatar(file) {
      if (!file) {
        return ''
      }
      if (!this.currentResumeId) {
        await this.saveCurrentResume()
      }

      const formData = new FormData()
      formData.append('resume_id', this.currentResumeId)
      formData.append('file', file)

      const result = await requestJson('/api/uploads/avatar', {
        method: 'POST',
        body: formData,
      })

      this.currentResume.content.basics.avatar_url = result.url
      this.currentResume.content.basics.avatar_crop = { ...DEFAULT_AVATAR_CROP }
      await this.saveCurrentResume()
      return result.url
    },

    async deleteCurrentResume() {
      if (!this.currentResumeId) {
        this.createLocalResume()
        return
      }

      await requestJson(`/api/resumes/${this.currentResumeId}`, {
        method: 'DELETE',
      })
      await this.refreshResumeList('')

      if (this.resumes.length > 0) {
        this.selectResume(this.resumes[0].id)
      } else {
        this.createLocalResume()
      }
    },

    async refreshResumeList(preferredResumeId = this.currentResumeId) {
      const result = await requestJson('/api/resumes')
      this.resumes = result.items || []

      if (!preferredResumeId) {
        return
      }

      const latest = this.resumes.find((item) => item.id === preferredResumeId)
      if (latest) {
        this.currentResumeId = latest.id
        this.currentResume = normalizeCurrentResume(latest, this.templates[0]?.id || 'pro_resume')
      }
    },
  },
})
