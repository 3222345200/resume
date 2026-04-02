const TOKEN_KEY = 'resume_auth_token';
const SIDEBAR_COLLAPSED_KEY = 'resume_sidebar_collapsed';

const state = {
  authToken: localStorage.getItem(TOKEN_KEY),
  currentUser: null,
  templates: [],
  resumes: [],
  currentResumeId: null,
  currentPdfUrl: null,
  currentAvatarUrl: null,
  currentAvatarCrop: null,
  renderedPayloadSignature: null,
  activeEditorSectionKey: 'basics',
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
  avatarScale: document.getElementById('avatar-scale'),
  avatarOffsetX: document.getElementById('avatar-offset-x'),
  avatarOffsetY: document.getElementById('avatar-offset-y'),
  layoutFontColorValue: document.getElementById('layout_font_color_value'),
  sortableSections: document.getElementById('sortable-sections'),
  addCustomSectionButton: document.getElementById('add-custom-section-btn'),
  editorShell: document.getElementById('editor-shell'),
  sidebarToggle: document.getElementById('sidebar-toggle'),
  sidebarReopen: document.getElementById('sidebar-reopen'),
  sidebarLogoToggle: document.getElementById('sidebar-logo-toggle'),
  editorSectionNav: document.getElementById('editor-section-nav'),
  sectionWorkspace: document.getElementById('section-workspace'),
  sectionNavAddCustomButton: document.getElementById('section-nav-add-custom-btn'),
  confirmDialog: document.getElementById('confirm-dialog'),
  confirmDialogTitle: document.getElementById('confirm-dialog-title'),
  confirmDialogMessage: document.getElementById('confirm-dialog-message'),
  confirmDialogCancel: document.getElementById('confirm-dialog-cancel'),
  confirmDialogConfirm: document.getElementById('confirm-dialog-confirm'),
};

const DEFAULT_AVATAR_PLACEHOLDER = '/assets/default-avatar.jpg';
const DEFAULT_AVATAR_CROP = {
  scale: 1,
  offset_x: 50,
  offset_y: 50,
};
const ONE_INCH_PHOTO_RATIO = 5 / 7;
const MAX_AVATAR_FILE_SIZE = 5 * 1024 * 1024;
const MONTH_PICKER_MIN_YEAR = 1990;
const MONTH_PICKER_MAX_YEAR = 2035;
const MONTH_LABELS = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
const RICH_ALLOWED_TAGS = new Set(['P', 'BR', 'STRONG', 'B', 'EM', 'I', 'U', 'UL', 'OL', 'LI', 'A']);
const DEFAULT_LAYOUT_SETTINGS = {
  section_title_size: '18',
  content_font_size: '13.5',
  content_line_height: '1.36',
  section_divider_gap: '4',
  font_color: '#111111',
};
const MOVABLE_SECTION_ORDER = ['skills', 'experience', 'projects', 'portfolio', 'research', 'honors'];
const CUSTOM_SECTION_PREFIX = 'custom:';
const SECTION_DELETE_LABELS = {
  education: '\u6559\u80b2\u7ecf\u5386',
  experience: '\u5de5\u4f5c/\u5b9e\u4e60\u7ecf\u5386',
  projects: '\u9879\u76ee\u7ecf\u5386',
  portfolio: '\u4f5c\u54c1\u96c6',
  research: '\u79d1\u7814\u7ecf\u5386',
  honors: '\u8363\u8a89\u5956\u9879',
  custom: '\u6761\u76ee',
};
const REPEAT_ITEM_TITLE_FIELDS = {
  education: ['school', 'major'],
  experience: ['company', 'role', 'department'],
  projects: ['name', 'description'],
  portfolio: ['title', 'link'],
  research: ['title', 'label'],
  honors: ['title', 'label'],
  custom: ['title', 'subtitle'],
};

let confirmDialogResolver = null;

function normalizeAvatarCrop(value) {
  const crop = value && typeof value === 'object' ? value : {};
  const clamp = (input, minimum, maximum, fallback) => {
    const number = Number(input);
    if (!Number.isFinite(number)) {
      return fallback;
    }
    return Math.min(maximum, Math.max(minimum, number));
  };

  return {
    scale: clamp(crop.scale, 1, 3, DEFAULT_AVATAR_CROP.scale),
    offset_x: clamp(crop.offset_x, 0, 100, DEFAULT_AVATAR_CROP.offset_x),
    offset_y: clamp(crop.offset_y, 0, 100, DEFAULT_AVATAR_CROP.offset_y),
  };
}

function syncAvatarControls() {
  const crop = normalizeAvatarCrop(state.currentAvatarCrop);
  state.currentAvatarCrop = crop;
  if (elements.avatarScale) {
    elements.avatarScale.value = String(crop.scale);
  }
  if (elements.avatarOffsetX) {
    elements.avatarOffsetX.value = String(crop.offset_x);
  }
  if (elements.avatarOffsetY) {
    elements.avatarOffsetY.value = String(crop.offset_y);
  }
}

function getAvatarTransform(crop) {
  const normalized = normalizeAvatarCrop(crop);
  const moveStrength = 0.45 + (normalized.scale - 1) * 0.9;
  const translateX = (50 - normalized.offset_x) * moveStrength;
  const translateY = (50 - normalized.offset_y) * moveStrength;
  return `translate(${translateX}%, ${translateY}%) scale(${normalized.scale})`;
}

function applyAvatarPreview() {
  const crop = normalizeAvatarCrop(state.currentAvatarCrop);
  state.currentAvatarCrop = crop;
  elements.avatarPreview.style.objectFit = 'cover';
  elements.avatarPreview.style.objectPosition = '50% 50%';
  elements.avatarPreview.style.transform = getAvatarTransform(crop);
  elements.avatarPreview.style.transformOrigin = 'center center';
}

function buildAvatarDisplayUrl(url) {
  if (!url) {
    return null;
  }
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}t=${Date.now()}`;
}

function setAvatarCrop(value) {
  state.currentAvatarCrop = normalizeAvatarCrop(value);
  syncAvatarControls();
  applyAvatarPreview();
}

async function getImageSize(file) {
  return new Promise((resolve, reject) => {
    const objectUrl = URL.createObjectURL(file);
    const image = new Image();

    image.onload = () => {
      URL.revokeObjectURL(objectUrl);
      resolve({ width: image.naturalWidth || 0, height: image.naturalHeight || 0 });
    };

    image.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      reject(new Error('image-load-failed'));
    };

    image.src = objectUrl;
  });
}

async function getAutoAvatarCrop(file) {
  try {
    const { width, height } = await getImageSize(file);
    if (!width || !height) {
      return { ...DEFAULT_AVATAR_CROP };
    }

    const imageRatio = width / height;
    const targetRatio = ONE_INCH_PHOTO_RATIO;
    const portraitBias = imageRatio < targetRatio;
    const ratioGap = portraitBias
      ? targetRatio / imageRatio
      : imageRatio / targetRatio;

    const scale = portraitBias
      ? Math.min(1.32, Math.max(1, 1 + (ratioGap - 1) * 0.45))
      : Math.min(1.16, Math.max(1, 1 + (ratioGap - 1) * 0.12));

    return normalizeAvatarCrop({
      scale,
      offset_x: 50,
      offset_y: portraitBias ? 38 : 42,
    });
  } catch {
    return { ...DEFAULT_AVATAR_CROP };
  }
}


function syncLayoutColorValue(color) {
  const value = String(color || DEFAULT_LAYOUT_SETTINGS.font_color).toUpperCase();
  if (elements.layoutFontColorValue) {
    elements.layoutFontColorValue.textContent = value;
  }
}

function applySectionUiLabels() {
  const hint = document.querySelector('.section-order-hint');
  if (hint) {
    hint.textContent = '下面这些模块支持调整顺序，PDF 也会按这里的顺序输出。基础信息和教育经历保持固定。';
  }

  if (elements.addCustomSectionButton) {
    elements.addCustomSectionButton.textContent = '新增自定义模块';
  }

  const labels = {
    basics: { title: '基础信息' },
    education: { title: '教育经历' },
    skills: { title: '专业技能', add: '', field: '技能关键词' },
    experience: { title: '\u5de5\u4f5c/\u5b9e\u4e60\u7ecf\u5386', add: '\u65b0\u589e\u7ecf\u5386' },
    projects: { title: '项目经历', add: '新增项目' },
    portfolio: { title: '作品集', add: '新增作品' },
    research: { title: '科研经历', add: '新增科研' },
    honors: { title: '荣誉奖项', add: '新增奖项' },
  };

  Object.entries(labels).forEach(([key, config]) => {
    const card = document.querySelector(`[data-editor-section-key="${key}"]`) || document.querySelector(`[data-section-key="${key}"]`);
    if (!card) {
      return;
    }
    const title = card.querySelector('.section-toggle-title');
    if (title) {
      title.textContent = config.title;
    }
    const addButton = card.querySelector('[data-add-section]');
    if (addButton && config.add) {
      addButton.textContent = config.add;
    }
    const upButton = card.querySelector('[data-move-section="up"]');
    const downButton = card.querySelector('[data-move-section="down"]');
    if (upButton) {
      upButton.textContent = '↑';
      upButton.title = '上移';
      upButton.setAttribute('aria-label', '上移');
    }
    if (downButton) {
      downButton.textContent = '↓';
      downButton.title = '下移';
      downButton.setAttribute('aria-label', '下移');
    }
  });

  const skillsLabel = document.getElementById('skills')?.closest('label');
  if (skillsLabel && skillsLabel.firstChild?.nodeType === Node.TEXT_NODE) {
    skillsLabel.firstChild.textContent = '技能关键词';
  }
  renderEditorSectionNav();
}

function slugifySectionId(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_-]+/g, '-')
    .replace(/^[-_]+|[-_]+$/g, '')
    .slice(0, 60);
}

function createCustomSectionId() {
  return `section-${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
}

function getCustomSectionKey(id) {
  return `${CUSTOM_SECTION_PREFIX}${id}`;
}

function normalizeCustomSections(value) {
  const incoming = Array.isArray(value) ? value : [];
  const usedIds = new Set();
  return incoming.map((section, index) => {
    const source = section && typeof section === 'object' ? section : {};
    let id = slugifySectionId(source.id) || `section-${index + 1}`;
    const baseId = id;
    let suffix = 2;
    while (usedIds.has(id)) {
      id = `${baseId}-${suffix}`;
      suffix += 1;
    }
    usedIds.add(id);
    return {
      id,
      title: String(source.title || '').trim(),
      items: Array.isArray(source.items) ? source.items : [],
    };
  });
}

function normalizeSectionOrder(value, customSections = []) {
  const incoming = Array.isArray(value) ? value.map((item) => String(item || '').trim()).filter(Boolean) : [];
  const customKeys = normalizeCustomSections(customSections).map((section) => getCustomSectionKey(section.id));
  const allowed = [...MOVABLE_SECTION_ORDER, ...customKeys];
  const unique = [];
  incoming.forEach((key) => {
    if (allowed.includes(key) && !unique.includes(key)) {
      unique.push(key);
    }
  });
  allowed.forEach((key) => {
    if (!unique.includes(key)) {
      unique.push(key);
    }
  });
  return unique;
}

function getEditorSectionCards() {
  if (!elements.sectionWorkspace) {
    return [];
  }
  return Array.from(elements.sectionWorkspace.querySelectorAll('[data-editor-section-key]'));
}

function getEditorSectionKey(card) {
  return card?.dataset.editorSectionKey || card?.dataset.sectionKey || '';
}

function getEditorSectionTitle(card) {
  const sectionKey = getEditorSectionKey(card);
  const builtInTitles = {
    basics: '\u57fa\u7840\u4fe1\u606f',
    education: '\u6559\u80b2\u7ecf\u5386',
    skills: '\u4e13\u4e1a\u6280\u80fd',
    experience: '\u5de5\u4f5c/\u5b9e\u4e60\u7ecf\u5386',
    projects: '\u9879\u76ee\u7ecf\u5386',
    portfolio: '\u4f5c\u54c1\u96c6',
    research: '\u79d1\u7814\u7ecf\u5386',
    honors: '\u8363\u8a89\u5956\u9879',
  };
  if (builtInTitles[sectionKey]) {
    return builtInTitles[sectionKey];
  }
  const title = card?.querySelector('.section-toggle-title')?.textContent?.trim();
  return title || '\u81ea\u5b9a\u4e49\u6a21\u5757';
}

function ensureActiveEditorSection() {
  const cards = getEditorSectionCards();
  if (cards.length === 0) {
    state.activeEditorSectionKey = null;
    return;
  }
  const available = cards.map((card) => getEditorSectionKey(card));
  if (!available.includes(state.activeEditorSectionKey) || state.activeEditorSectionKey === 'layout') {
    state.activeEditorSectionKey = available.includes('basics') ? 'basics' : available[0];
  }
}

function syncEditorSectionPanels() {
  ensureActiveEditorSection();
  getEditorSectionCards().forEach((card) => {
    const key = getEditorSectionKey(card);
    card.hidden = key !== state.activeEditorSectionKey;
  });
}

function setActiveEditorSection(sectionKey) {
  if (!sectionKey) {
    return;
  }
  state.activeEditorSectionKey = sectionKey;
  syncEditorSectionPanels();
  renderEditorSectionNav();
}

function getEditorSectionSubtitle(card) {
  return '\u70b9\u51fb\u5207\u6362\u7f16\u8f91';
}

function isSectionReorderable(sectionKey) {
  return getCurrentSectionOrder().includes(sectionKey);
}

function moveSectionBefore(sectionKey, targetSectionKey) {
  const order = getCurrentSectionOrder();
  const currentIndex = order.indexOf(sectionKey);
  const targetIndex = order.indexOf(targetSectionKey);
  if (currentIndex === -1 || targetIndex === -1 || currentIndex === targetIndex) {
    return;
  }

  const nextOrder = [...order];
  nextOrder.splice(currentIndex, 1);
  const insertIndex = nextOrder.indexOf(targetSectionKey);
  nextOrder.splice(insertIndex, 0, sectionKey);
  applySectionOrder(nextOrder);
  updatePreviewMessage();
}


function renderEditorSectionNav() {
  if (!elements.editorSectionNav) {
    return;
  }

  ensureActiveEditorSection();
  elements.editorSectionNav.innerHTML = '';

  getEditorSectionCards().forEach((card) => {
    const sectionKey = getEditorSectionKey(card);
    if (sectionKey === 'layout') {
      return;
    }

    const item = document.createElement('div');
    const isReorderable = isSectionReorderable(sectionKey);
    item.className = `editor-section-nav-item${state.activeEditorSectionKey === sectionKey ? ' is-active' : ''}${isReorderable ? ' is-reorderable' : ''}`;
    item.dataset.sectionKey = sectionKey;
    item.innerHTML = `
      <button type="button" class="editor-section-nav-button">
        <strong>${escapeHtml(getEditorSectionTitle(card))}</strong>
        <span>${escapeHtml(getEditorSectionSubtitle(card))}</span>
      </button>
      ${isReorderable ? '<button type="button" class="editor-section-drag-handle" draggable="true" aria-label="\u62d6\u52a8\u6392\u5e8f" title="\u62d6\u52a8\u6392\u5e8f"><span></span><span></span><span></span></button>' : ''}
    `;

    item.querySelector('.editor-section-nav-button')?.addEventListener('click', () => {
      setActiveEditorSection(sectionKey);
      expandSectionCard(card);
    });

    const handle = item.querySelector('.editor-section-drag-handle');
    if (handle) {
      handle.addEventListener('dragstart', (event) => {
        item.classList.add('is-dragging');
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData('text/plain', sectionKey);
      });
      handle.addEventListener('dragend', () => {
        item.classList.remove('is-dragging');
        elements.editorSectionNav?.querySelectorAll('.is-drop-target').forEach((node) => node.classList.remove('is-drop-target'));
      });
      item.addEventListener('dragover', (event) => {
        event.preventDefault();
        if (!item.classList.contains('is-dragging')) {
          item.classList.add('is-drop-target');
        }
      });
      item.addEventListener('dragleave', () => {
        item.classList.remove('is-drop-target');
      });
      item.addEventListener('drop', (event) => {
        event.preventDefault();
        item.classList.remove('is-drop-target');
        const sourceSectionKey = event.dataTransfer.getData('text/plain');
        if (!sourceSectionKey || sourceSectionKey === sectionKey) {
          return;
        }
        moveSectionBefore(sourceSectionKey, sectionKey);
      });
    }

    elements.editorSectionNav.appendChild(item);
  });

  syncEditorSectionPanels();
}

function getCurrentSectionOrder() {
  if (!elements.sortableSections) {
    return [...MOVABLE_SECTION_ORDER];
  }
  return Array.from(elements.sortableSections.querySelectorAll('[data-section-key]')).map((card) => card.dataset.sectionKey);
}

function getCustomSectionCards() {
  if (!elements.sortableSections) {
    return [];
  }
  return Array.from(elements.sortableSections.querySelectorAll('[data-custom-section="true"]'));
}

function syncCustomSectionTitle(card) {
  const input = card?.querySelector('[data-custom-section-title="true"]');
  const title = card?.querySelector('.section-toggle-title');
  if (!input || !title) {
    return;
  }
  title.textContent = input.value.trim() || '\u81ea\u5b9a\u4e49\u6a21\u5757';
}

function applySectionOrder(order, customSections = collectCustomSections()) {
  if (!elements.sortableSections) {
    return;
  }
  const normalized = normalizeSectionOrder(order, customSections);
  normalized.forEach((key) => {
    const card = elements.sortableSections.querySelector(`[data-section-key="${key}"]`);
    if (card) {
      elements.sortableSections.appendChild(card);
    }
  });
  syncSectionMoveButtons();
  renderEditorSectionNav();
}

function syncSectionMoveButtons() {
  const order = getCurrentSectionOrder();
  order.forEach((key, index) => {
    const card = elements.sortableSections?.querySelector(`[data-section-key="${key}"]`);
    if (!card) {
      return;
    }
    const upButton = card.querySelector('[data-move-section="up"]');
    const downButton = card.querySelector('[data-move-section="down"]');
    if (upButton) {
      upButton.disabled = index === 0;
    }
    if (downButton) {
      downButton.disabled = index === order.length - 1;
    }
  });
}

function moveSection(sectionKey, direction) {
  const order = getCurrentSectionOrder();
  const currentIndex = order.indexOf(sectionKey);
  if (currentIndex === -1) {
    return;
  }
  const targetIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
  if (targetIndex < 0 || targetIndex >= order.length) {
    return;
  }
  const nextOrder = [...order];
  [nextOrder[currentIndex], nextOrder[targetIndex]] = [nextOrder[targetIndex], nextOrder[currentIndex]];
  applySectionOrder(nextOrder);
  updatePreviewMessage();
}

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
  const sync = ({ normalizeSurface = false } = {}) => {
    const sanitized = sanitizeRichHtml(surface.innerHTML);
    textarea.value = sanitized;
    if (normalizeSurface && surface.innerHTML !== sanitized) {
      surface.innerHTML = sanitized;
    }
    updatePreviewMessage();
  };

  wrapper.querySelectorAll('[data-command]').forEach((button) => {
    button.addEventListener('click', () => {
      surface.focus();
      document.execCommand(button.dataset.command, false);
      sync({ normalizeSurface: true });
    });
  });

  wrapper.querySelector('[data-action="indent"]')?.addEventListener('click', () => {
    surface.focus();
    document.execCommand('indent', false);
    sync({ normalizeSurface: true });
  });

  wrapper.querySelector('[data-action="outdent"]')?.addEventListener('click', () => {
    surface.focus();
    document.execCommand('outdent', false);
    sync({ normalizeSurface: true });
  });

  wrapper.querySelector('[data-action="link"]')?.addEventListener('click', () => {
    surface.focus();
    const existing = window.getSelection()?.toString().trim();
    const href = window.prompt('请输入链接地址', existing && /^(https?:\/\/|mailto:)/i.test(existing) ? existing : 'https://');
    if (!href) {
      return;
    }
    document.execCommand('createLink', false, href);
    sync({ normalizeSurface: true });
  });

  surface.addEventListener('input', () => sync());
  surface.addEventListener('blur', () => sync({ normalizeSurface: true }));
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

function closeAllCustomSelects(exceptSelect = null) {
  document.querySelectorAll('.custom-select.is-open').forEach((selectUi) => {
    const nativeSelect = selectUi.previousElementSibling;
    if (nativeSelect === exceptSelect) {
      return;
    }
    selectUi.classList.remove('is-open');
    selectUi.querySelector('.custom-select-trigger')?.setAttribute('aria-expanded', 'false');
  });
}

function syncCustomSelectSelection(select) {
  const customSelect = select.nextElementSibling;
  if (!customSelect?.classList.contains('custom-select')) {
    return;
  }

  const selectedOption = select.selectedOptions?.[0] || select.options?.[select.selectedIndex] || null;
  const triggerLabel = customSelect.querySelector('.custom-select-value');
  if (triggerLabel) {
    triggerLabel.textContent = selectedOption?.textContent?.trim() || '???';
  }

  customSelect.querySelectorAll('.custom-select-option').forEach((button) => {
    button.classList.toggle('is-selected', button.dataset.value === select.value);
  });
}

function rebuildCustomSelectOptions(select) {
  const customSelect = select.nextElementSibling;
  if (!customSelect?.classList.contains('custom-select')) {
    return;
  }

  const list = customSelect.querySelector('.custom-select-options');
  if (!list) {
    return;
  }

  list.innerHTML = '';
  Array.from(select.options).forEach((option) => {
    const item = document.createElement('button');
    item.type = 'button';
    item.className = 'custom-select-option';
    item.dataset.value = option.value;
    item.textContent = option.textContent || '';
    item.disabled = option.disabled;
    item.classList.toggle('is-selected', option.value === select.value);
    item.addEventListener('click', () => {
      select.value = option.value;
      select.dispatchEvent(new Event('input', { bubbles: true }));
      select.dispatchEvent(new Event('change', { bubbles: true }));
      syncCustomSelectSelection(select);
      closeAllCustomSelects();
    });
      list.appendChild(item);
  });

  syncCustomSelectSelection(select);
}

function toggleCustomSelect(select) {
  const customSelect = select.nextElementSibling;
  if (!customSelect?.classList.contains('custom-select')) {
    return;
  }

  const willOpen = !customSelect.classList.contains('is-open');
  closeAllCustomSelects(willOpen ? select : null);
  customSelect.classList.toggle('is-open', willOpen);
  customSelect.querySelector('.custom-select-trigger')?.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
  if (willOpen) {
    rebuildCustomSelectOptions(select);
  }
}

function ensureCustomSelect(select) {
  if (!select || select.dataset.dateSelect === 'true' || select.multiple) {
    return;
  }

  let customSelect = select.nextElementSibling;
  if (!customSelect?.classList.contains('custom-select')) {
    select.classList.add('custom-select-native');
    customSelect = document.createElement('div');
    customSelect.className = 'custom-select';
    customSelect.innerHTML = `
      <button type="button" class="custom-select-trigger" aria-expanded="false">
        <span class="custom-select-value">???</span>
        <span class="custom-select-chevron" aria-hidden="true"></span>
      </button>
      <div class="custom-select-popover">
        <div class="custom-select-options"></div>
      </div>
    `;
    select.insertAdjacentElement('afterend', customSelect);
    customSelect.querySelector('.custom-select-trigger')?.addEventListener('click', (event) => {
      event.preventDefault();
      toggleCustomSelect(select);
    });
  }

  rebuildCustomSelectOptions(select);
}

function ensureAllCustomSelects() {
  document.querySelectorAll('select:not([data-date-select="true"])').forEach((select) => ensureCustomSelect(select));
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

  picker.querySelectorAll('.month-picker-month').forEach((button) => {
    const buttonYear = Number(button.dataset.year);
    const buttonMonth = Number(button.dataset.month);
    const isSelected = parsed && input.value !== '???' && parsed.year === buttonYear && parsed.month === buttonMonth;
    button.classList.toggle('is-selected', Boolean(isSelected));
  });

  const presentButton = picker.querySelector('.month-picker-present');
  if (presentButton) {
    presentButton.classList.toggle('is-selected', input.value === '???');
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
    setMonthPickerYear(input, parseDateValue(input.value)?.year || new Date().getFullYear());
    rebuildMonthPickerGrid(input);
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
        avatar_crop: { ...DEFAULT_AVATAR_CROP },
      },
      layout: { ...DEFAULT_LAYOUT_SETTINGS },
      education: [],
      experience: [],
      projects: [],
      portfolio: [],
      research: [],
      honors: [],
      custom_sections: [],
      skills: [],
      section_order: [...MOVABLE_SECTION_ORDER],
    },
  };
}

function redirectToLogin() {
  window.location.href = '/login';
}

function applySidebarCollapsed(collapsed) {
  const isCollapsed = Boolean(collapsed);
  elements.editorShell?.classList.toggle('sidebar-collapsed', isCollapsed);
  if (elements.sidebarToggle) {
    elements.sidebarToggle.textContent = isCollapsed ? '>' : '<';
    elements.sidebarToggle.setAttribute('aria-expanded', String(!isCollapsed));
    elements.sidebarToggle.setAttribute('aria-label', isCollapsed ? 'Expand sidebar' : 'Collapse sidebar');
  }
  if (elements.sidebarReopen) {
    elements.sidebarReopen.hidden = !isCollapsed;
    elements.sidebarReopen.style.display = isCollapsed ? 'inline-flex' : 'none';
    elements.sidebarReopen.setAttribute('aria-hidden', String(!isCollapsed));
  }
  if (elements.sidebarLogoToggle) {
    elements.sidebarLogoToggle.setAttribute('aria-label', isCollapsed ? 'Expand sidebar' : 'OfferPilot');
    elements.sidebarLogoToggle.setAttribute('aria-expanded', String(!isCollapsed));
  }
}

function toggleSidebarCollapsed() {
  const collapsed = !elements.editorShell?.classList.contains('sidebar-collapsed');
  applySidebarCollapsed(collapsed);
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, collapsed ? '1' : '0');
}

function showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2400);
}

function isConfirmDialogOpen() {
  return Boolean(elements.confirmDialog && !elements.confirmDialog.hidden);
}

function closeConfirmDialog(confirmed = false) {
  if (!elements.confirmDialog) {
    return;
  }

  elements.confirmDialog.classList.remove('is-visible');
  elements.confirmDialog.hidden = true;
  document.body.classList.remove('dialog-open');

  const resolver = confirmDialogResolver;
  confirmDialogResolver = null;
  resolver?.(confirmed);
}

function openConfirmDialog(options = {}) {
  if (!elements.confirmDialog) {
    return Promise.resolve(window.confirm(options.message || '\u786e\u8ba4\u7ee7\u7eed\u5417\uff1f'));
  }

  if (confirmDialogResolver) {
    closeConfirmDialog(false);
  }

  const {
    title = '\u786e\u8ba4\u64cd\u4f5c',
    message = '\u6b64\u64cd\u4f5c\u6267\u884c\u540e\u5c06\u65e0\u6cd5\u64a4\u9500\uff0c\u662f\u5426\u7ee7\u7eed\uff1f',
    confirmText = '\u786e\u8ba4',
    cancelText = '\u53d6\u6d88',
  } = options;

  elements.confirmDialogTitle.textContent = title;
  elements.confirmDialogMessage.textContent = message;
  elements.confirmDialogConfirm.textContent = confirmText;
  elements.confirmDialogCancel.textContent = cancelText;
  elements.confirmDialog.hidden = false;
  document.body.classList.add('dialog-open');
  requestAnimationFrame(() => {
    elements.confirmDialog.classList.add('is-visible');
    elements.confirmDialogConfirm.focus();
  });

  return new Promise((resolve) => {
    confirmDialogResolver = resolve;
  });
}

function getDeleteLabel(section) {
  return SECTION_DELETE_LABELS[section] || '\u5185\u5bb9';
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
  elements.editorShell?.classList.remove('hidden-auth');
}

function handleUnauthorized() {
  clearToken();
  redirectToLogin();
}

function applyAvatarFrameRatio() {
  const frame = elements.avatarPreview?.closest('.avatar-preview-wrap');
  if (!frame) {
    return;
  }
  frame.style.aspectRatio = String(ONE_INCH_PHOTO_RATIO);
}

function setAvatar(url, crop = state.currentAvatarCrop || DEFAULT_AVATAR_CROP) {
  state.currentAvatarUrl = url || null;
  setAvatarCrop(crop);
  if (state.currentAvatarUrl) {
    elements.avatarPreview.src = buildAvatarDisplayUrl(state.currentAvatarUrl) || state.currentAvatarUrl;
    elements.avatarStatus.textContent = '照片已上传，可按一寸照比例调整后再导出 PDF。';
  } else {
    elements.avatarPreview.src = DEFAULT_AVATAR_PLACEHOLDER;
    elements.avatarStatus.textContent = '未上传照片时，将使用默认占位图。支持图片格式，大小不能超过 5MB。';
  }
}

elements.avatarPreview?.addEventListener('error', () => {
  elements.avatarPreview.src = DEFAULT_AVATAR_PLACEHOLDER;
  elements.avatarStatus.textContent = '照片加载失败，请重新上传。';
});

elements.avatarPreview?.addEventListener('load', () => {
  if (state.currentAvatarUrl) {
    elements.avatarStatus.textContent = '照片已上传，可按一寸照比例调整后再导出 PDF。';
  }
});

function resetPreview() {
  state.currentPdfUrl = null;
  state.renderedPayloadSignature = null;
  elements.downloadLink.removeAttribute('href');
  elements.downloadLink.removeAttribute('download');
  elements.downloadLink.classList.add('hidden-link');
  elements.pdfPreview.removeAttribute('src');
  elements.pdfPreview.classList.add('hidden-preview');
  elements.previewEmpty.classList.remove('hidden-preview');
}


function setHtmlPreview() {
  if (!state.currentResumeId) {
    resetPreview();
    return;
  }
  const previewVersion = encodeURIComponent(shortHash(`${state.currentResumeId}:${Date.now()}`));
  elements.pdfPreview.src = `/api/resumes/${state.currentResumeId}/preview?v=${previewVersion}&token=${encodeURIComponent(state.authToken || "")}` + "#zoom=page-width";
  elements.pdfPreview.classList.remove('hidden-preview');
  elements.previewEmpty.classList.add('hidden-preview');
}
function buildPdfDownloadUrl() {
  if (!state.currentResumeId) {
    return '';
  }
  const fallbackVersion = `${state.currentResumeId}:${Date.now()}`;
  const version = encodeURIComponent(shortHash(state.renderedPayloadSignature || fallbackVersion));
  const token = encodeURIComponent(state.authToken || '');
  return `/api/resumes/${state.currentResumeId}/pdf/download?v=${version}&token=${token}`;
}

function triggerPdfDownload() {
  const downloadUrl = buildPdfDownloadUrl();
  if (!downloadUrl) {
    return;
  }
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = buildResumeFilename();
  link.rel = 'noopener';
  document.body.appendChild(link);
  link.click();
  link.remove();
}

function buildResumeFilename() {
  const name = document.getElementById('basics_name').value.trim();
  const title = document.getElementById('title').value.trim();
  const base = [name, title].filter(Boolean).join('_') || 'resume';
  return `${base}.pdf`;
}

function setPreviewUrl(url) {
  state.currentPdfUrl = url || null;
  if (!state.currentPdfUrl) {
    elements.downloadLink.removeAttribute('href');
    elements.downloadLink.removeAttribute('download');
    elements.downloadLink.classList.add('hidden-link');
    return;
  }

  elements.downloadLink.href = buildPdfDownloadUrl();
  elements.downloadLink.download = buildResumeFilename();
  elements.downloadLink.rel = 'noopener';
  elements.downloadLink.classList.add('hidden-link');
}

function stableStringify(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(',')}]`;
  }
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value ?? null);
}

function shortHash(value) {
  const text = String(value || "");
  let hash = 2166136261;
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16);
}

function getPayloadSignature(payload) {
  return stableStringify(payload);
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

function getRepeatItemTitle(section, item, index = 0) {
  const titleMap = {
    education: '\u6559\u80b2\u6761\u76ee',
    experience: '\u5de5\u4f5c/\u5b9e\u4e60\u6761\u76ee',
    projects: '\u9879\u76ee\u6761\u76ee',
    portfolio: '\u4f5c\u54c1\u6761\u76ee',
    research: '\u79d1\u7814\u6761\u76ee',
    honors: '\u8363\u8a89\u6761\u76ee',
    custom: '\u81ea\u5b9a\u4e49\u6761\u76ee',
  };

  return titleMap[section] || `\u6761\u76ee ${index + 1}`;
}


function syncRepeatItemTitles(container) {
  if (!container) {
    return;
  }

  const items = Array.from(container.querySelectorAll(':scope > .repeat-item'));
  items.forEach((item, index) => {
    const section = item.dataset.section || '';
    const titleNode = item.querySelector('[data-repeat-item-title="true"]');
    if (titleNode) {
      titleNode.textContent = getRepeatItemTitle(section, item, index);
    }
  });
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
    if (input.tagName === 'SELECT') {
      ensureCustomSelect(input);
    }
  }
  input.addEventListener('input', updatePreviewMessage);
  input.addEventListener('change', updatePreviewMessage);
}

function syncRepeatItemMoveButtons(container) {
  if (!container) {
    return;
  }
  const items = Array.from(container.querySelectorAll(':scope > .repeat-item'));
  items.forEach((item, index) => {
    const upButton = item.querySelector('[data-move-item="up"]');
    const downButton = item.querySelector('[data-move-item="down"]');
    if (upButton) {
      upButton.disabled = index === 0;
    }
    if (downButton) {
      downButton.disabled = index === items.length - 1;
    }
  });
}

function moveRepeatItem(item, direction) {
  const container = item?.parentElement;
  if (!container || !item) {
    return;
  }
  const sibling = direction === 'up' ? item.previousElementSibling : item.nextElementSibling;
  if (!sibling) {
    return;
  }
  if (direction === 'up') {
    container.insertBefore(item, sibling);
  } else {
    container.insertBefore(sibling, item);
  }
  syncRepeatItemMoveButtons(container);
  syncRepeatItemTitles(container);
  revealSectionTarget(item);
  updatePreviewMessage();
}

function createRepeatItem(section, data = {}) {
  const template = document.getElementById(`${section}-template`);
  const node = template.content.firstElementChild.cloneNode(true);
  const toolbar = node.querySelector('.repeat-item-toolbar');
  const actions = node.querySelector('.section-order-actions');
  if (toolbar && !toolbar.querySelector('[data-repeat-item-title="true"]')) {
    const title = document.createElement('div');
    title.className = 'repeat-item-title';
    title.dataset.repeatItemTitle = 'true';
    toolbar.insertBefore(title, actions || toolbar.firstChild);
  }
  if (actions) {
    actions.innerHTML = `
      <button type="button" class="icon-button" data-move-item="up" title="上移" aria-label="上移">&#8593;</button>
      <button type="button" class="icon-button" data-move-item="down" title="下移" aria-label="下移">&#8595;</button>
    `;
  }
  node.querySelectorAll('[data-field]').forEach((input) => {
    hydrateDynamicField(input, input.dataset.field, data);
    input.addEventListener('input', () => syncRepeatItemTitles(node.parentElement));
    input.addEventListener('change', () => syncRepeatItemTitles(node.parentElement));
  });
  const titleNode = node.querySelector('[data-repeat-item-title="true"]');
  if (titleNode) {
    titleNode.textContent = getRepeatItemTitle(section, node, 0);
  }
  node.querySelector('[data-move-item="up"]')?.addEventListener('click', () => moveRepeatItem(node, 'up'));
  node.querySelector('[data-move-item="down"]')?.addEventListener('click', () => moveRepeatItem(node, 'down'));
  node.querySelector('.remove-btn')?.addEventListener('click', async () => {
    const confirmed = await openConfirmDialog({
      title: `确认删除${getDeleteLabel(section)}`,
      message: '删除后将无法恢复，确认继续吗？',
      confirmText: '确认删除',
    });
    if (!confirmed) {
      return;
    }
    const container = node.parentElement;
    node.remove();
    syncRepeatItemMoveButtons(container);
    syncRepeatItemTitles(container);
    updatePreviewMessage();
  });
  return node;
}

function mountRepeatList(section, list) {
  const target = elements[`${section}List`];
  target.innerHTML = '';
  list.forEach((item) => target.appendChild(createRepeatItem(section, item)));
  syncRepeatItemMoveButtons(target);
  syncRepeatItemTitles(target);
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

function createCustomSectionCard(section = {}) {
  const normalized = normalizeCustomSections([section])[0] || { id: createCustomSectionId(), title: '', items: [] };
  const card = document.createElement('div');
  card.className = 'full-width section-card';
  card.dataset.collapsible = 'true';
  card.dataset.sectionKey = getCustomSectionKey(normalized.id);
  card.dataset.editorSectionKey = card.dataset.sectionKey;
  card.dataset.customSection = 'true';
  card.dataset.customId = normalized.id;
  card.innerHTML = `
    <div class="section-title-row">
      <button type="button" class="section-toggle" aria-expanded="true">
        <span class="section-toggle-title">${normalized.title || '\u81ea\u5b9a\u4e49\u6a21\u5757'}</span>
        <span class="section-toggle-chevron" aria-hidden="true"></span>
      </button>
      <div class="section-actions">
        <div class="section-order-actions" aria-label="section-order">
          <button type="button" class="icon-button" data-move-section="up" title="up" aria-label="up">&#8593;</button>
          <button type="button" class="icon-button" data-move-section="down" title="down" aria-label="down">&#8595;</button>
        </div>
        <button type="button" class="small-button" data-add-custom-item="true">新增条目</button>
        <button type="button" class="text-button" data-remove-custom-section="true">删除</button>
      </div>
    </div>
    <div class="section-card-body">
      <div class="custom-section-header">
        <label class="full-width">
          <span>模块标题</span>
          <input class="custom-section-title-input" data-custom-section-title="true" value="${escapeHtml(normalized.title || '')}" placeholder="例如：校园经历 / 社团经历 / 证书" />
        </label>
        <p class="custom-section-note">这一类模块会沿用项目经历风格，支持排序，也会一起输出到 PDF。</p>
      </div>
      <div class="repeat-list" data-custom-items="true"></div>
    </div>
  `;
  const list = card.querySelector('[data-custom-items="true"]');
  normalized.items.forEach((item) => list.appendChild(createRepeatItem('custom', item)));
  card.querySelectorAll('[data-move-section]').forEach((button) => {
    button.addEventListener('click', () => moveSection(card.dataset.sectionKey, button.dataset.moveSection));
  });
  card.querySelector('[data-add-custom-item="true"]')?.addEventListener('click', () => {
    expandSectionCard(card);
    const item = createRepeatItem('custom', {});
    list.appendChild(item);
    syncRepeatItemMoveButtons(list);
    revealSectionTarget(item);
    updatePreviewMessage();
  });
  card.querySelector('[data-remove-custom-section="true"]')?.addEventListener('click', async () => {
    const sectionTitle = card.querySelector('[data-custom-section-title="true"]')?.value.trim() || '\u81ea\u5b9a\u4e49\u6a21\u5757';
    const confirmed = await openConfirmDialog({
      title: '\u786e\u8ba4\u5220\u9664\u81ea\u5b9a\u4e49\u6a21\u5757',
      message: `\u6a21\u5757\u201c${sectionTitle}\u201d\u5220\u9664\u540e\uff0c\u91cc\u9762\u7684\u6761\u76ee\u4e5f\u4f1a\u4e00\u8d77\u5220\u9664\u3002\u786e\u8ba4\u7ee7\u7eed\u5417\uff1f`,
      confirmText: '\u786e\u8ba4\u5220\u9664',
    });
    if (!confirmed) {
      return;
    }
    const nextCard = card.previousElementSibling || card.nextElementSibling;
    card.remove();
    state.activeEditorSectionKey = getEditorSectionKey(nextCard) || 'basics';
    syncSectionMoveButtons();
    renderEditorSectionNav();
    updatePreviewMessage();
  });
  card.querySelector('[data-custom-section-title="true"]')?.addEventListener('input', () => {
    syncCustomSectionTitle(card);
    renderEditorSectionNav();
    updatePreviewMessage();
  });
  bindCollapsibleSections();
  syncCustomSectionTitle(card);
  return card;
}

function mountCustomSections(sections) {
  getCustomSectionCards().forEach((card) => card.remove());
  normalizeCustomSections(sections).forEach((section) => {
    elements.sortableSections.appendChild(createCustomSectionCard(section));
  });
  syncSectionMoveButtons();
  renderEditorSectionNav();
}

function collectCustomSections() {
  return getCustomSectionCards().map((card, index) => {
    const titleInput = card.querySelector('[data-custom-section-title="true"]');
    const rawId = card.dataset.customId || `section-${index + 1}`;
    const id = slugifySectionId(rawId) || `section-${index + 1}`;
    card.dataset.customId = id;
    card.dataset.sectionKey = getCustomSectionKey(id);
    card.dataset.editorSectionKey = card.dataset.sectionKey;
    const items = Array.from(card.querySelectorAll('[data-custom-items="true"] .repeat-item')).map((item) => {
      const result = {};
      item.querySelectorAll('[data-field]').forEach((input) => {
        result[input.dataset.field] = input.tagName === 'TEXTAREA' ? getRichTextValue(input) : input.value.trim();
      });
      return result;
    });
    return {
      id,
      title: titleInput?.value.trim() || '',
      items,
    };
  });
}

function getFormPayload() {
  const customSections = collectCustomSections();
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
        avatar_crop: normalizeAvatarCrop(state.currentAvatarCrop),
      },
      layout: {
        section_title_size: document.getElementById('layout_section_title_size').value,
        content_font_size: document.getElementById('layout_content_font_size').value,
        content_line_height: document.getElementById('layout_content_line_height').value,
        section_divider_gap: document.getElementById('layout_section_divider_gap').value,
        font_color: document.getElementById('layout_font_color').value,
      },
      education: collectRepeatList('education'),
      experience: collectRepeatList('experience'),
      projects: collectRepeatList('projects'),
      portfolio: collectRepeatList('portfolio'),
      research: collectRepeatList('research'),
      honors: collectRepeatList('honors'),
      custom_sections: customSections,
      skills: getRichTextValue(document.getElementById('skills')),
      section_order: normalizeSectionOrder(getCurrentSectionOrder(), customSections),
    },
  };
}

function fillForm(resume) {
  const current = resume || defaultResume();
  const renderedSignature = getPayloadSignature({
    title: current.title || '',
    template_id: current.template_id || state.templates[0]?.id || '',
    content: {
      basics: current.content?.basics || {},
      layout: { ...DEFAULT_LAYOUT_SETTINGS, ...(current.content?.layout || {}) },
      education: current.content?.education || [],
      experience: current.content?.experience || [],
      projects: current.content?.projects || [],
      portfolio: current.content?.portfolio || [],
      research: current.content?.research || [],
      honors: current.content?.honors || [],
      custom_sections: normalizeCustomSections(current.content?.custom_sections || []),
      skills: current.content?.skills || [],
      section_order: normalizeSectionOrder(current.content?.section_order, current.content?.custom_sections || []),
    },
  });
  const layout = { ...DEFAULT_LAYOUT_SETTINGS, ...(current.content?.layout || {}) };
  document.getElementById('title').value = current.title || '';
  document.getElementById('template_id').value = current.template_id || state.templates[0]?.id || '';
  document.getElementById('basics_name').value = current.content?.basics?.name || '';
  document.getElementById('basics_phone').value = current.content?.basics?.phone || '';
  document.getElementById('basics_email').value = current.content?.basics?.email || '';
  document.getElementById('basics_location').value = current.content?.basics?.location || '';
  setRichTextValue(document.getElementById('basics_summary'), current.content?.basics?.summary || '');
  document.getElementById('basics_job_target').value = current.content?.basics?.job_target || '';
  document.getElementById('layout_section_title_size').value = layout.section_title_size;
  document.getElementById('layout_content_font_size').value = layout.content_font_size;
  document.getElementById('layout_content_line_height').value = layout.content_line_height;
  document.getElementById('layout_section_divider_gap').value = layout.section_divider_gap;
  document.getElementById('layout_font_color').value = layout.font_color;
  syncLayoutColorValue(layout.font_color);
  ensureAllCustomSelects();
  setRichTextValue(document.getElementById('skills'), current.content?.skills || []);
  mountCustomSections(current.content?.custom_sections || []);
  applySectionOrder(current.content?.section_order, current.content?.custom_sections || []);

  setAvatar(current.content?.basics?.avatar_url || null, current.content?.basics?.avatar_crop || DEFAULT_AVATAR_CROP);
  mountRepeatList('education', current.content?.education || []);
  mountRepeatList('experience', current.content?.experience || []);
  mountRepeatList('projects', current.content?.projects || []);
  mountRepeatList('portfolio', current.content?.portfolio || []);
  mountRepeatList('research', current.content?.research || []);
  mountRepeatList('honors', current.content?.honors || []);

  if (current.rendered_pdf_url) {
    state.renderedPayloadSignature = renderedSignature;
    setPreviewUrl(current.rendered_pdf_url);
  }
  if (current.id) {
    setHtmlPreview();
  } else {
    resetPreview();
  }
  state.activeEditorSectionKey = 'basics';
  renderEditorSectionNav();
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
  ensureCustomSelect(elements.templateSelect);
}

function updatePreviewMessage() {
  if (!state.currentPdfUrl) {
    setPreviewMessage('生成 PDF 后，这里会直接显示简历预览。');
  }
}

function expandSectionCard(card) {
  if (!card) {
    return;
  }
  const toggle = card.querySelector('.section-toggle');
  toggle?.setAttribute('aria-expanded', 'true');
  card.classList.remove('is-collapsed');
}

function revealSectionTarget(target) {
  if (!target) {
    return;
  }
  const card = target.closest('.section-card');
  setActiveEditorSection(getEditorSectionKey(card));
  expandSectionCard(card);
  target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  const focusTarget = target.matches('input, select, textarea, button')
    ? target
    : target.querySelector('input, select, textarea, button');
  focusTarget?.focus({ preventScroll: true });
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

async function uploadAvatar(file, resumeId) {
  const formData = new FormData();
  formData.append('resume_id', resumeId);
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
    throw new Error(error || '照片上传失败');
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

  const currentSectionKey = state.activeEditorSectionKey;
  const path = state.currentResumeId ? `/api/resumes/${state.currentResumeId}` : '/api/resumes';
  const method = state.currentResumeId ? 'PUT' : 'POST';
  const saved = await request(path, { method, body: JSON.stringify(payload) });
  state.currentResumeId = saved.id;
  await loadResumes();
  fillForm(saved);
  if (currentSectionKey) {
    setActiveEditorSection(currentSectionKey);
  }
  setHtmlPreview();

  if (!silent) {
    showToast('简历已保存');
  }
  return saved;
}

async function renderPdf() {
  try {
    elements.renderButton.disabled = true;
    setPreviewMessage('正在生成 PDF，请稍等...');

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
    const payloadSignature = getPayloadSignature(payload);
    if (!payload.title) {
      showToast('标题不能为空');
      return;
    }

    if (state.currentPdfUrl && state.renderedPayloadSignature === payloadSignature) {
      triggerPdfDownload();
      showToast('内容未变化，已复用上次 PDF');
      return;
    }

    const result = await request(`/api/resumes/${state.currentResumeId}/render`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    state.renderedPayloadSignature = payloadSignature;
    if (result.resume) {
      state.currentResumeId = result.resume.id;
      await loadResumes();
      fillForm(result.resume);
    }
    setPreviewUrl(result.pdf_url);
    setHtmlPreview();
    triggerPdfDownload();
    showToast('PDF 已生成并开始下载');
  } catch (error) {
    console.error(error);
    setPreviewMessage(`生成失败：${String(error.message || error)}`);
    showToast('生成 PDF 失败');
  } finally {
    elements.renderButton.disabled = false;
  }
}

async function deleteResume() {
  if (!state.currentResumeId) {
    showToast('\u5f53\u524d\u6ca1\u6709\u53ef\u5220\u9664\u7684\u7b80\u5386');
    return;
  }

  const confirmed = await openConfirmDialog({
    title: '\u786e\u8ba4\u5220\u9664\u7b80\u5386',
    message: '\u5220\u9664\u540e\u8be5\u7b80\u5386\u53ca\u5df2\u751f\u6210\u7684\u9884\u89c8\u5185\u5bb9\u5c06\u65e0\u6cd5\u6062\u590d\uff0c\u786e\u8ba4\u7ee7\u7eed\u5417\uff1f',
    confirmText: '\u786e\u8ba4\u5220\u9664',
  });
  if (!confirmed) {
    return;
  }

  await request(`/api/resumes/${state.currentResumeId}`, { method: 'DELETE' });
  state.currentResumeId = null;
  setAvatar(null, DEFAULT_AVATAR_CROP);
  resetPreview();
  await loadResumes();
  renderResumeList();
  showToast('\u7b80\u5386\u5df2\u5220\u9664');
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
    clearToken();
    redirectToLogin();
    return false;
  }
}

function bindEvents() {
  document.querySelectorAll('[data-rich-text="true"]').forEach((textarea) => ensureRichTextEditor(textarea));
  bindCollapsibleSections();
  applySectionUiLabels();
  ensureAllCustomSelects();

  document.addEventListener('click', (event) => {
    if (!event.target.closest('.month-picker')) {
      closeAllMonthPickers();
    }
    if (!event.target.closest('.custom-select')) {
      closeAllCustomSelects();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      if (isConfirmDialogOpen()) {
        closeConfirmDialog(false);
        return;
      }
      closeAllMonthPickers();
      closeAllCustomSelects();
    }
  });

  elements.confirmDialog?.addEventListener('click', (event) => {
    if (event.target === elements.confirmDialog) {
      closeConfirmDialog(false);
    }
  });
  elements.confirmDialogCancel?.addEventListener('click', () => closeConfirmDialog(false));
  elements.confirmDialogConfirm?.addEventListener('click', () => closeConfirmDialog(true));

  elements.form.addEventListener('input', updatePreviewMessage);
  document.getElementById('layout_font_color')?.addEventListener('input', (event) => {
    syncLayoutColorValue(event.target.value);
  });
  elements.form.addEventListener('change', updatePreviewMessage);
  elements.saveButton.addEventListener('click', () => saveResume());
  elements.renderButton.addEventListener('click', renderPdf);
  elements.deleteButton.addEventListener('click', deleteResume);
  elements.newResumeButton.addEventListener('click', () => {
    state.currentResumeId = null;
    setAvatar(null, DEFAULT_AVATAR_CROP);
    resetPreview();
    fillForm(defaultResume());
    renderResumeList();
  });
  elements.logoutButton.addEventListener('click', () => {
    clearToken();
    redirectToLogin();
  });
  elements.sidebarToggle?.addEventListener('click', toggleSidebarCollapsed);
  elements.sidebarReopen?.addEventListener('click', () => {
    applySidebarCollapsed(false);
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, '0');
  });
  elements.sidebarLogoToggle?.addEventListener('click', () => {
    if (!elements.editorShell?.classList.contains('sidebar-collapsed')) {
      return;
    }
    applySidebarCollapsed(false);
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, '0');
  });
  elements.avatarFile.addEventListener('change', async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    if (file.size > MAX_AVATAR_FILE_SIZE) {
      setAvatar(state.currentAvatarUrl, state.currentAvatarCrop || DEFAULT_AVATAR_CROP);
      elements.avatarStatus.textContent = '上传失败：照片大小不能超过 5MB。';
      showToast('照片大小不能超过 5MB');
      elements.avatarFile.value = '';
      return;
    }

    try {
      elements.avatarStatus.textContent = '照片上传中...';
      if (!state.currentResumeId) {
        await saveResume({ silent: true });
      }
      if (!state.currentResumeId) {
        throw new Error('请先创建简历后再上传照片');
      }
      const autoCrop = await getAutoAvatarCrop(file);
      const result = await uploadAvatar(file, state.currentResumeId);
      setAvatar(result.url, autoCrop);
      showToast('照片上传成功');
    } catch (error) {
      console.error(error);
      setAvatar(state.currentAvatarUrl, state.currentAvatarCrop || DEFAULT_AVATAR_CROP);
      elements.avatarStatus.textContent = `上传失败：${String(error.message || error)}`;
      showToast('照片上传失败');
    } finally {
      elements.avatarFile.value = '';
    }
  });

  elements.avatarClear.addEventListener('click', async () => {
    const confirmed = await openConfirmDialog({
      title: '\u786e\u8ba4\u79fb\u9664\u7167\u7247',
      message: '\u79fb\u9664\u540e\u4f1a\u6062\u590d\u4e3a\u9ed8\u8ba4\u5360\u4f4d\u56fe\uff0c\u786e\u8ba4\u7ee7\u7eed\u5417\uff1f',
      confirmText: '\u786e\u8ba4\u79fb\u9664',
    });
    if (!confirmed) {
      return;
    }
    setAvatar(null, DEFAULT_AVATAR_CROP);
    updatePreviewMessage();
  });

  [elements.avatarScale, elements.avatarOffsetX, elements.avatarOffsetY].forEach((input) => {
    input?.addEventListener('input', () => {
      setAvatarCrop({
        scale: elements.avatarScale.value,
        offset_x: elements.avatarOffsetX.value,
        offset_y: elements.avatarOffsetY.value,
      });
      updatePreviewMessage();
    });
  });

  document.querySelectorAll('[data-add-section]').forEach((button) => {
    button.addEventListener('click', () => {
      const section = button.dataset.addSection;
      const card = button.closest('.section-card');
      expandSectionCard(card);
      const item = createRepeatItem(section, {});
      elements[`${section}List`].appendChild(item);
      syncRepeatItemMoveButtons(elements[`${section}List`]);
      revealSectionTarget(item);
      updatePreviewMessage();
    });
  });
  const handleAddCustomSection = () => {
    const card = createCustomSectionCard({
      id: createCustomSectionId(),
      title: '',
      items: [{}],
    });
    elements.sortableSections.appendChild(card);
    applySectionOrder(getCurrentSectionOrder(), collectCustomSections());
    revealSectionTarget(card.querySelector('[data-custom-section-title="true"]') || card);
    updatePreviewMessage();
  };

  elements.addCustomSectionButton?.addEventListener('click', handleAddCustomSection);
  elements.sectionNavAddCustomButton?.addEventListener('click', handleAddCustomSection);

  document.querySelectorAll('[data-move-section]').forEach((button) => {
    button.addEventListener('click', () => {
      const card = button.closest('[data-section-key]');
      if (!card) {
        return;
      }
      moveSection(card.dataset.sectionKey, button.dataset.moveSection);
    });
  });

  syncSectionMoveButtons();
  renderEditorSectionNav();
}

async function bootstrap() {
  applySidebarCollapsed(localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === '1');
  bindEvents();
  applyAvatarFrameRatio();
  applySectionOrder(MOVABLE_SECTION_ORDER);
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
















