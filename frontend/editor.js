const TOKEN_KEY = 'resume_auth_token';

const state = {
  authToken: localStorage.getItem(TOKEN_KEY),
  currentUser: null,
  templates: [],
  resumes: [],
  currentResumeId: null,
  currentPdfUrl: null,
  currentAvatarUrl: null,
};

const elements = {
  currentUser: document.getElementById('current-user'),
  resumeList: document.getElementById('resume-list'),
  resumeCount: document.getElementById('resume-count'),
  templateSelect: document.getElementById('template_id'),
  previewEmpty: document.getElementById('preview-empty'),
  pdfPreview: document.getElementById('pdf-preview'),
  form: document.getElementById('resume-form'),
  saveButton: document.getElementById('save-btn'),
  renderButton: document.getElementById('render-btn'),
  deleteButton: document.getElementById('delete-btn'),
  downloadLink: document.getElementById('download-link'),
  newResumeButton: document.getElementById('new-resume-btn'),
  logoutButton: document.getElementById('logout-btn'),
  educationList: document.getElementById('education-list'),
  experienceList: document.getElementById('experience-list'),
  projectsList: document.getElementById('projects-list'),
  portfolioList: document.getElementById('portfolio-list'),
  researchList: document.getElementById('research-list'),
  honorsList: document.getElementById('honors-list'),
  avatarFile: document.getElementById('avatar-file'),
  avatarPreview: document.getElementById('avatar-preview'),
  avatarStatus: document.getElementById('avatar-status'),
  avatarClear: document.getElementById('avatar-clear'),
};

const DEFAULT_AVATAR_PLACEHOLDER = '/assets/default-avatar.jpg';
const MONTH_PICKER_MIN_YEAR = 1990;
const MONTH_PICKER_MAX_YEAR = 2035;
const MONTH_LABELS = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
const RICH_ALLOWED_TAGS = new Set(['P', 'BR', 'STRONG', 'B', 'EM', 'I', 'U', 'UL', 'OL', 'LI', 'A']);

function plainTextToRichHtml(value, mode = 'paragraphs') {
  const lines = String(value || '')
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);

  if (lines.length === 0) {
    return '';
  }

  if (mode === 'list') {
    return `<ul>${lines.map((line) => `<li>${escapeHtml(line)}</li>`).join('')}</ul>`;
  }

  return lines.map((line) => `<p>${escapeHtml(line)}</p>`).join('');
}

function normalizeIncomingRichValue(value, mode = 'paragraphs') {
  if (Array.isArray(value)) {
    return plainTextToRichHtml(value.join('\n'), mode);
  }
  if (typeof value === 'string' && /<[^>]+>/.test(value)) {
    return sanitizeRichHtml(value);
  }
  return plainTextToRichHtml(value || '', mode);
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function sanitizeRichHtml(inputHtml) {
  const template = document.createElement('template');
  template.innerHTML = inputHtml || '';

  const walk = (node) => {
    Array.from(node.childNodes).forEach((child) => {
      if (child.nodeType === Node.ELEMENT_NODE) {
        if (!RICH_ALLOWED_TAGS.has(child.tagName)) {
          const fragment = document.createDocumentFragment();
          while (child.firstChild) {
            fragment.appendChild(child.firstChild);
          }
          child.replaceWith(fragment);
          walk(node);
          return;
        }

        if (child.tagName === 'A') {
          const href = (child.getAttribute('href') || '').trim();
          Array.from(child.attributes).forEach((attribute) => child.removeAttribute(attribute.name));
          if (/^(https?:\/\/|mailto:)/i.test(href)) {
            child.setAttribute('href', href);
            child.setAttribute('target', '_blank');
            child.setAttribute('rel', 'noopener');
          }
        } else {
          Array.from(child.attributes).forEach((attribute) => child.removeAttribute(attribute.name));
        }

        walk(child);
        return;
      }

      if (child.nodeType === Node.COMMENT_NODE) {
        child.remove();
      }
    });
  };

  walk(template.content);
  return template.innerHTML.trim();
}

function ensureRichTextEditor(textarea) {
  if (!textarea || textarea.dataset.richReady === 'true') {
    return;
  }

  const wrapper = document.createElement('div');
  wrapper.className = 'rich-editor';
  wrapper.innerHTML = `
    <div class="rich-toolbar">
      <button type="button" class="tool-icon" data-command="undo" data-tooltip="撤销" aria-label="撤销">&#8630;</button>
      <button type="button" class="tool-icon" data-command="redo" data-tooltip="重做" aria-label="重做">&#8631;</button>
      <span class="tool-divider"></span>
      <button type="button" class="tool-icon" data-command="bold" data-tooltip="加粗" aria-label="加粗"><strong>B</strong></button>
      <button type="button" class="tool-icon" data-command="italic" data-tooltip="斜体" aria-label="斜体"><em>I</em></button>
      <span class="tool-divider"></span>
      <button type="button" class="tool-icon" data-command="insertUnorderedList" data-tooltip="无序列表" aria-label="无序列表">&#8226;</button>
      <button type="button" class="tool-icon" data-command="insertOrderedList" data-tooltip="有序列表" aria-label="有序列表">1.</button>
      <button type="button" class="tool-icon" data-action="outdent" data-tooltip="减少缩进" aria-label="减少缩进">&#8647;</button>
      <button type="button" class="tool-icon" data-action="indent" data-tooltip="增加缩进" aria-label="增加缩进">&#8649;</button>
      <button type="button" class="tool-icon" data-action="link" data-tooltip="插入链接" aria-label="插入链接">&#128279;</button>
      <button type="button" class="tool-icon" data-command="removeFormat" data-tooltip="清除格式" aria-label="清除格式">Tx</button>
    </div>
    <div class="rich-surface" contenteditable="true"></div>
  `;

  textarea.classList.add('rich-editor-input');
  textarea.hidden = true;
  textarea.insertAdjacentElement('afterend', wrapper);

  const surface = wrapper.querySelector('.rich-surface');
  const sync = () => {
    const sanitized = sanitizeRichHtml(surface.innerHTML);
    textarea.value = sanitized;
    if (surface.innerHTML !== sanitized) {
      surface.innerHTML = sanitized;
    }
    updatePreviewMessage();
  };

  wrapper.querySelectorAll('[data-command]').forEach((button) => {
    button.addEventListener('click', () => {
      surface.focus();
      document.execCommand(button.dataset.command, false);
      sync();
    });
  });

  wrapper.querySelector('[data-action="indent"]')?.addEventListener('click', () => {
    surface.focus();
    document.execCommand('indent', false);
    sync();
  });

  wrapper.querySelector('[data-action="outdent"]')?.addEventListener('click', () => {
    surface.focus();
    document.execCommand('outdent', false);
    sync();
  });

  wrapper.querySelector('[data-action="link"]')?.addEventListener('click', () => {
    surface.focus();
    const existing = window.getSelection()?.toString().trim();
    const href = window.prompt('请输入链接地址', existing && /^(https?:\/\/|mailto:)/i.test(existing) ? existing : 'https://');
    if (!href) {
      return;
    }
    document.execCommand('createLink', false, href);
    sync();
  });

  surface.addEventListener('input', sync);
  surface.addEventListener('blur', sync);
  textarea.dataset.richReady = 'true';
}

function setRichTextValue(textarea, value) {
  if (!textarea) {
    return;
  }
  ensureRichTextEditor(textarea);
  const html = normalizeIncomingRichValue(value, textarea.dataset.richMode || 'paragraphs');
  textarea.value = html;
  const surface = textarea.nextElementSibling?.querySelector('.rich-surface');
  if (surface) {
    surface.innerHTML = html;
  }
}

function getRichTextValue(textarea) {
  if (!textarea) {
    return '';
  }
  if (textarea.dataset.richText === 'true') {
    ensureRichTextEditor(textarea);
    const surface = textarea.nextElementSibling?.querySelector('.rich-surface');
    const html = sanitizeRichHtml(surface?.innerHTML || textarea.value || '');
    textarea.value = html;
    return html;
  }
  return textarea.value.trim();
}

function formatMonthPickerValue(value) {
  if (!value) {
    return '请选择时间';
  }
  if (value === '至今') {
    return '至今';
  }

  const parsed = parseDateValue(value);
  if (!parsed) {
    return value;
  }
  return `${parsed.year}年${parsed.month}月`;
}

function closeAllMonthPickers(exceptInput = null) {
  document.querySelectorAll('.month-picker.is-open').forEach((picker) => {
    const input = picker.previousElementSibling;
    if (input === exceptInput) {
      return;
    }
    picker.classList.remove('is-open');
    picker.querySelector('.month-picker-trigger')?.setAttribute('aria-expanded', 'false');
  });
}

function setMonthPickerYear(input, year) {
  const picker = input.nextElementSibling;
  if (!picker) {
    return;
  }
  const nextYear = Math.min(MONTH_PICKER_MAX_YEAR, Math.max(MONTH_PICKER_MIN_YEAR, year));
  picker.dataset.viewYear = String(nextYear);
  picker.querySelector('.month-picker-title').textContent = `${nextYear}年`;
  picker.querySelector('.month-picker-prev').disabled = nextYear <= MONTH_PICKER_MIN_YEAR;
  picker.querySelector('.month-picker-next').disabled = nextYear >= MONTH_PICKER_MAX_YEAR;
}

function syncMonthPickerSelection(input) {
  const picker = input.nextElementSibling;
  if (!picker) {
    return;
  }

  const trigger = picker.querySelector('.month-picker-trigger');
  trigger.querySelector('.month-picker-value').textContent = formatMonthPickerValue(input.value);
  trigger.classList.toggle('is-placeholder', !input.value);

  const parsed = parseDateValue(input.value);
  if (parsed && input.value !== '至今') {
    setMonthPickerYear(input, parsed.year);
  }

  picker.querySelectorAll('.month-picker-month').forEach((button) => {
    const buttonYear = Number(button.dataset.year);
    const buttonMonth = Number(button.dataset.month);
    const isSelected = parsed && input.value !== '至今' && parsed.year === buttonYear && parsed.month === buttonMonth;
    button.classList.toggle('is-selected', Boolean(isSelected));
  });

  const presentButton = picker.querySelector('.month-picker-present');
  if (presentButton) {
    presentButton.classList.toggle('is-selected', input.value === '至今');
  }
}

function rebuildMonthPickerGrid(input) {
  const picker = input.nextElementSibling;
  if (!picker) {
    return;
  }

  const year = Number(picker.dataset.viewYear || MONTH_PICKER_MAX_YEAR);
  const grid = picker.querySelector('.month-picker-grid');
  grid.innerHTML = '';

  MONTH_LABELS.forEach((label, index) => {
    const month = index + 1;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'month-picker-month';
    button.dataset.year = String(year);
    button.dataset.month = String(month);
    button.textContent = label;
    button.addEventListener('click', () => {
      input.value = `${year}.${String(month).padStart(2, '0')}`;
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      syncMonthPickerSelection(input);
      closeAllMonthPickers();
    });
    grid.appendChild(button);
  });

  syncMonthPickerSelection(input);
}

function toggleMonthPicker(input) {
  const picker = input.nextElementSibling;
  if (!picker) {
    return;
  }

  const willOpen = !picker.classList.contains('is-open');
  closeAllMonthPickers(willOpen ? input : null);
  picker.classList.toggle('is-open', willOpen);
  picker.querySelector('.month-picker-trigger')?.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
  if (willOpen) {
    syncMonthPickerSelection(input);
  }
}

function createMonthPicker(input) {
  if (input.nextElementSibling?.classList.contains('month-picker')) {
    return;
  }

  const allowPresent = input.dataset.allowPresent === 'true';
  const picker = document.createElement('div');
  picker.className = 'month-picker';
  picker.dataset.viewYear = String(parseDateValue(input.value)?.year || new Date().getFullYear());
  picker.innerHTML = `
    <button type="button" class="month-picker-trigger is-placeholder" aria-expanded="false">
      <span class="month-picker-value">请选择时间</span>
      <span class="month-picker-chevron" aria-hidden="true"></span>
    </button>
    <div class="month-picker-popover">
      <div class="month-picker-header">
        <button type="button" class="month-picker-nav month-picker-prev" aria-label="上一年"></button>
        <div class="month-picker-title"></div>
        <button type="button" class="month-picker-nav month-picker-next" aria-label="下一年"></button>
      </div>
      ${allowPresent ? '<button type="button" class="month-picker-present">至今</button>' : ''}
      <div class="month-picker-weekdays">
        <span>一</span>
        <span>二</span>
        <span>三</span>
        <span>四</span>
        <span>五</span>
        <span>六</span>
        <span>日</span>
      </div>
      <div class="month-picker-grid"></div>
    </div>
  `;

  input.classList.add('month-picker-native');
  input.tabIndex = -1;
  input.setAttribute('aria-hidden', 'true');
  input.insertAdjacentElement('afterend', picker);

  picker.querySelector('.month-picker-trigger').addEventListener('click', (event) => {
    event.preventDefault();
    toggleMonthPicker(input);
  });

  picker.querySelector('.month-picker-prev').addEventListener('click', () => {
    setMonthPickerYear(input, Number(picker.dataset.viewYear) - 1);
    rebuildMonthPickerGrid(input);
  });

  picker.querySelector('.month-picker-next').addEventListener('click', () => {
    setMonthPickerYear(input, Number(picker.dataset.viewYear) + 1);
    rebuildMonthPickerGrid(input);
  });

  picker.querySelector('.month-picker-present')?.addEventListener('click', () => {
    input.value = '至今';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    syncMonthPickerSelection(input);
    closeAllMonthPickers();
  });

  input.addEventListener('change', () => {
    syncMonthPickerSelection(input);
  });

  setMonthPickerYear(input, parseDateValue(input.value)?.year || new Date().getFullYear());
  rebuildMonthPickerGrid(input);
}

function defaultResume() {
  return {
    title: '新建简历',
    template_id: 'pro_resume',
    rendered_pdf_url: null,
    content: {
      basics: {
        name: '',
        phone: '',
        email: '',
        location: '',
        summary: '',
        job_target: '',
        avatar_url: null,
      },
      education: [],
      experience: [],
      projects: [],
      portfolio: [],
      research: [],
      honors: [],
      skills: [],
    },
  };
}

function redirectToLogin() {
  window.location.href = '/login';
}

function showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2400);
}

function setPreviewMessage(message) {
  elements.previewEmpty.textContent = message;
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  state.authToken = null;
}

function applyCurrentUser(user) {
  state.currentUser = user || null;
  elements.currentUser.textContent = state.currentUser
    ? `已登录：${state.currentUser.username}`
    : '未登录';
}

function handleUnauthorized() {
  clearToken();
  redirectToLogin();
}

function setAvatar(url) {
  state.currentAvatarUrl = url || null;
  if (state.currentAvatarUrl) {
    elements.avatarPreview.src = state.currentAvatarUrl;
    elements.avatarStatus.textContent = '头像已上传，生成 PDF 时会使用这张照片。';
  } else {
    elements.avatarPreview.src = DEFAULT_AVATAR_PLACEHOLDER;
    elements.avatarStatus.textContent = '未上传头像，将使用默认占位图。';
  }
}

function resetPreview() {
  state.currentPdfUrl = null;
  elements.downloadLink.removeAttribute('href');
  elements.downloadLink.removeAttribute('download');
  elements.downloadLink.classList.add('hidden-link');
  elements.pdfPreview.removeAttribute('src');
  elements.pdfPreview.classList.add('hidden-preview');
  elements.previewEmpty.classList.remove('hidden-preview');
}

function setPreviewUrl(url) {
  state.currentPdfUrl = url || null;
  if (!state.currentPdfUrl) {
    resetPreview();
    return;
  }

  const filename = `${document.getElementById('title').value.trim() || 'resume'}.pdf`;
  elements.downloadLink.href = state.currentPdfUrl;
  elements.downloadLink.download = filename;
  elements.downloadLink.target = '_blank';
  elements.downloadLink.rel = 'noopener';
  elements.downloadLink.classList.remove('hidden-link');
  elements.pdfPreview.src = state.currentPdfUrl;
  elements.pdfPreview.classList.remove('hidden-preview');
  elements.previewEmpty.classList.add('hidden-preview');
}

function buildDateOptions(allowPresent = false) {
  const options = ['<option value="">请选择时间</option>'];
  if (allowPresent) {
    options.push('<option value="至今">至今</option>');
  }

  for (let year = 2035; year >= 1990; year -= 1) {
    for (let month = 12; month >= 1; month -= 1) {
      const value = `${year}.${String(month).padStart(2, '0')}`;
      options.push(`<option value="${value}">${value}</option>`);
    }
  }
  return options.join('');
}

function parseDateValue(value) {
  if (!value) {
    return null;
  }
  if (value === '至今') {
    return { year: 9999, month: 12 };
  }

  const match = /^(\d{4})\.(\d{2})$/.exec(value);
  if (!match) {
    return null;
  }

  return {
    year: Number(match[1]),
    month: Number(match[2]),
  };
}

function validateDateRange(startValue, endValue) {
  const start = parseDateValue(startValue);
  const end = parseDateValue(endValue);
  if (!start || !end) {
    return true;
  }
  return start.year < end.year || (start.year === end.year && start.month <= end.month);
}

function syncDateRangeState(container) {
  const startInput = container?.querySelector('[data-field="start_date"]');
  const endInput = container?.querySelector('[data-field="end_date"]');
  if (!startInput || !endInput) {
    return true;
  }

  const isValid = validateDateRange(startInput.value, endInput.value);
  startInput.classList.toggle('date-input-error', !isValid);
  endInput.classList.toggle('date-input-error', !isValid);
  startInput.closest('label')?.classList.toggle('date-field-error', !isValid);
  endInput.closest('label')?.classList.toggle('date-field-error', !isValid);
  startInput.nextElementSibling?.querySelector('.month-picker-trigger')?.classList.toggle('date-input-error', !isValid);
  endInput.nextElementSibling?.querySelector('.month-picker-trigger')?.classList.toggle('date-input-error', !isValid);
  return isValid;
}

function validateSectionDateRanges() {
  const items = Array.from(document.querySelectorAll('.repeat-item'));
  for (const item of items) {
    const isValid = syncDateRangeState(item);
    if (!isValid) {
      item.querySelector('[data-field="end_date"]')?.nextElementSibling?.querySelector('.month-picker-trigger')?.focus();
      showToast('开始日期不能晚于结束日期');
      return false;
    }
  }
  return true;
}

function multilineToArray(value) {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

function arrayToMultiline(items = []) {
  return items.join('\n');
}

function hydrateDynamicField(input, field, data) {
  const sourceValue = field === 'description' ? (data.description || data.tech_stack || '') : (data[field] || '');
  const value = Array.isArray(sourceValue) ? arrayToMultiline(sourceValue) : sourceValue;

  if (input.dataset.dateSelect === 'true') {
    input.innerHTML = buildDateOptions(input.dataset.allowPresent === 'true');
    input.value = value;
    input.closest('label')?.classList.add('date-field-card');
    createMonthPicker(input);
    input.addEventListener('change', () => {
      syncDateRangeState(input.closest('.repeat-item'));
    });
  } else if (input.dataset.richText === 'true') {
    setRichTextValue(input, value);
  } else {
    input.value = value;
  }
  input.addEventListener('input', updatePreviewMessage);
  input.addEventListener('change', updatePreviewMessage);
}

function createRepeatItem(section, data = {}) {
  const template = document.getElementById(`${section}-template`);
  const node = template.content.firstElementChild.cloneNode(true);
  node.querySelectorAll('[data-field]').forEach((input) => {
    hydrateDynamicField(input, input.dataset.field, data);
  });
  node.querySelector('.remove-btn').addEventListener('click', () => {
    node.remove();
    updatePreviewMessage();
  });
  return node;
}

function mountRepeatList(section, list) {
  const target = elements[`${section}List`];
  target.innerHTML = '';
  list.forEach((item) => target.appendChild(createRepeatItem(section, item)));
}

function collectRepeatList(section) {
  return Array.from(elements[`${section}List`].querySelectorAll('.repeat-item')).map((item) => {
    const result = {};
    item.querySelectorAll('[data-field]').forEach((input) => {
      if (input.tagName === 'TEXTAREA') {
        const textareaValue = getRichTextValue(input);
        result[input.dataset.field] = input.dataset.richMode === 'list'
          ? textareaValue
          : textareaValue;
      } else {
        result[input.dataset.field] = input.value.trim();
      }
    });
    return result;
  });
}

function getFormPayload() {
  return {
    title: document.getElementById('title').value.trim(),
    template_id: document.getElementById('template_id').value,
    content: {
      basics: {
        name: document.getElementById('basics_name').value.trim(),
        phone: document.getElementById('basics_phone').value.trim(),
        email: document.getElementById('basics_email').value.trim(),
        location: document.getElementById('basics_location').value.trim(),
        summary: getRichTextValue(document.getElementById('basics_summary')),
        job_target: document.getElementById('basics_job_target').value.trim(),
        avatar_url: state.currentAvatarUrl,
      },
      education: collectRepeatList('education'),
      experience: collectRepeatList('experience'),
      projects: collectRepeatList('projects'),
      portfolio: collectRepeatList('portfolio'),
      research: collectRepeatList('research'),
      honors: collectRepeatList('honors'),
      skills: getRichTextValue(document.getElementById('skills')),
    },
  };
}

function fillForm(resume) {
  const current = resume || defaultResume();
  document.getElementById('title').value = current.title || '';
  document.getElementById('template_id').value = current.template_id || state.templates[0]?.id || '';
  document.getElementById('basics_name').value = current.content?.basics?.name || '';
  document.getElementById('basics_phone').value = current.content?.basics?.phone || '';
  document.getElementById('basics_email').value = current.content?.basics?.email || '';
  document.getElementById('basics_location').value = current.content?.basics?.location || '';
  setRichTextValue(document.getElementById('basics_summary'), current.content?.basics?.summary || '');
  document.getElementById('basics_job_target').value = current.content?.basics?.job_target || '';
  setRichTextValue(document.getElementById('skills'), current.content?.skills || []);

  setAvatar(current.content?.basics?.avatar_url || null);
  mountRepeatList('education', current.content?.education || []);
  mountRepeatList('experience', current.content?.experience || []);
  mountRepeatList('projects', current.content?.projects || []);
  mountRepeatList('portfolio', current.content?.portfolio || []);
  mountRepeatList('research', current.content?.research || []);
  mountRepeatList('honors', current.content?.honors || []);

  if (current.rendered_pdf_url) {
    setPreviewUrl(current.rendered_pdf_url);
  } else {
    resetPreview();
  }
  updatePreviewMessage();
}

function renderResumeList() {
  elements.resumeCount.textContent = `${state.resumes.length} 份`;
  elements.resumeList.innerHTML = '';

  state.resumes.forEach((resume) => {
    const item = document.createElement('button');
    item.type = 'button';
    item.className = `resume-item${resume.id === state.currentResumeId ? ' active' : ''}`;
    item.innerHTML = `
      <strong>${resume.title}</strong>
      <div class="meta-text">模板：${resume.template_id}</div>
      <small>${new Date(resume.updated_at).toLocaleString('zh-CN')}</small>
    `;
    item.addEventListener('click', () => {
      state.currentResumeId = resume.id;
      fillForm(resume);
      renderResumeList();
    });
    elements.resumeList.appendChild(item);
  });
}

function renderTemplateOptions() {
  elements.templateSelect.innerHTML = state.templates
    .map((template) => `<option value="${template.id}">${template.name}</option>`)
    .join('');
}

function updatePreviewMessage() {
  if (!state.currentPdfUrl) {
    setPreviewMessage('生成 PDF 后，这里会直接显示简历预览。');
  }
}

function bindCollapsibleSections() {
  document.querySelectorAll('.section-card[data-collapsible="true"]').forEach((card) => {
    const toggle = card.querySelector('.section-toggle');
    const body = card.querySelector('.section-card-body');
    if (!toggle || !body || toggle.dataset.collapseBound === 'true') {
      return;
    }

    toggle.addEventListener('click', () => {
      const nextExpanded = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(nextExpanded));
      card.classList.toggle('is-collapsed', !nextExpanded);
    });
    toggle.dataset.collapseBound = 'true';
  });
}

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  headers.Authorization = `Bearer ${state.authToken}`;

  const response = await fetch(path, { ...options, headers });
  if (response.status === 401) {
    handleUnauthorized();
    throw new Error('登录已失效，请重新登录');
  }
  if (!response.ok) {
    const contentType = response.headers.get('content-type') || '';
    const error = contentType.includes('application/json')
      ? JSON.stringify(await response.json())
      : await response.text();
    throw new Error(error || '请求失败');
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

async function uploadAvatar(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch('/api/uploads/avatar', {
    method: 'POST',
    body: formData,
    headers: { Authorization: `Bearer ${state.authToken}` },
  });

  if (response.status === 401) {
    handleUnauthorized();
    throw new Error('登录已失效，请重新登录');
  }
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || '头像上传失败');
  }
  return response.json();
}

async function loadTemplates() {
  state.templates = await request('/api/templates');
  renderTemplateOptions();
}

async function loadResumes() {
  const data = await request('/api/resumes');
  state.resumes = data.items;

  if (!state.currentResumeId && state.resumes.length > 0) {
    state.currentResumeId = state.resumes[0].id;
    fillForm(state.resumes[0]);
  }
  if (state.resumes.length === 0) {
    fillForm(defaultResume());
  }
  renderResumeList();
}

async function saveResume({ silent = false } = {}) {
  const payload = getFormPayload();
  if (!payload.title) {
    showToast('标题不能为空');
    return null;
  }
  if (!validateSectionDateRanges()) {
    return null;
  }

  const path = state.currentResumeId ? `/api/resumes/${state.currentResumeId}` : '/api/resumes';
  const method = state.currentResumeId ? 'PUT' : 'POST';
  const saved = await request(path, { method, body: JSON.stringify(payload) });
  state.currentResumeId = saved.id;
  await loadResumes();
  fillForm(saved);

  if (!silent) {
    showToast('简历已保存');
  }
  return saved;
}

async function renderPdf() {
  try {
    elements.renderButton.disabled = true;
    setPreviewMessage('正在生成 PDF，请稍等...');
    elements.previewEmpty.classList.remove('hidden-preview');
    elements.pdfPreview.classList.add('hidden-preview');

    if (!validateSectionDateRanges()) {
      return;
    }

    if (!state.currentResumeId) {
      await saveResume({ silent: true });
    }
    if (!state.currentResumeId) {
      return;
    }

    const payload = getFormPayload();
    if (!payload.title) {
      showToast('标题不能为空');
      return;
    }

    const result = await request(`/api/resumes/${state.currentResumeId}/render`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (result.resume) {
      state.currentResumeId = result.resume.id;
      await loadResumes();
      fillForm(result.resume);
    }
    setPreviewUrl(result.pdf_url);
    showToast('PDF 已生成');
  } catch (error) {
    console.error(error);
    resetPreview();
    setPreviewMessage(`生成失败：${String(error.message || error)}`);
    showToast('生成 PDF 失败');
  } finally {
    elements.renderButton.disabled = false;
  }
}

async function deleteResume() {
  if (!state.currentResumeId) {
    showToast('当前没有可删除的简历');
    return;
  }

  await request(`/api/resumes/${state.currentResumeId}`, { method: 'DELETE' });
  state.currentResumeId = null;
  setAvatar(null);
  resetPreview();
  await loadResumes();
  renderResumeList();
  showToast('简历已删除');
}

async function restoreSession() {
  if (!state.authToken) {
    redirectToLogin();
    return false;
  }

  try {
    const user = await request('/api/auth/me');
    applyCurrentUser(user);
    return true;
  } catch (error) {
    console.error(error);
    return false;
  }
}

function bindEvents() {
  document.querySelectorAll('[data-rich-text="true"]').forEach((textarea) => ensureRichTextEditor(textarea));
  bindCollapsibleSections();

  document.addEventListener('click', (event) => {
    if (!event.target.closest('.month-picker')) {
      closeAllMonthPickers();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeAllMonthPickers();
    }
  });

  elements.form.addEventListener('input', updatePreviewMessage);
  elements.form.addEventListener('change', updatePreviewMessage);
  elements.saveButton.addEventListener('click', () => saveResume());
  elements.renderButton.addEventListener('click', renderPdf);
  elements.deleteButton.addEventListener('click', deleteResume);
  elements.newResumeButton.addEventListener('click', () => {
    state.currentResumeId = null;
    setAvatar(null);
    resetPreview();
    fillForm(defaultResume());
    renderResumeList();
  });
  elements.logoutButton.addEventListener('click', () => {
    clearToken();
    redirectToLogin();
  });

  elements.avatarFile.addEventListener('change', async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    try {
      elements.avatarStatus.textContent = '头像上传中...';
      const result = await uploadAvatar(file);
      setAvatar(result.url);
      showToast('头像上传成功');
    } catch (error) {
      console.error(error);
      setAvatar(state.currentAvatarUrl);
      elements.avatarStatus.textContent = `上传失败：${String(error.message || error)}`;
      showToast('头像上传失败');
    } finally {
      elements.avatarFile.value = '';
    }
  });

  elements.avatarClear.addEventListener('click', () => setAvatar(null));

  document.querySelectorAll('[data-add-section]').forEach((button) => {
    button.addEventListener('click', () => {
      const section = button.dataset.addSection;
      elements[`${section}List`].appendChild(createRepeatItem(section, {}));
      updatePreviewMessage();
    });
  });
}

async function bootstrap() {
  bindEvents();
  fillForm(defaultResume());
  updatePreviewMessage();
  const ok = await restoreSession();
  if (!ok) {
    return;
  }
  await loadTemplates();
  await loadResumes();
}

bootstrap().catch((error) => {
  console.error(error);
  showToast('页面初始化失败，请检查后端服务');
});
