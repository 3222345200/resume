const state = {
  templates: [],
  resumes: [],
  currentResumeId: null,
  currentPdfUrl: null,
};

const elements = {
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
  educationList: document.getElementById('education-list'),
  experienceList: document.getElementById('experience-list'),
  projectsList: document.getElementById('projects-list'),
  researchList: document.getElementById('research-list'),
};

const defaultResume = () => ({
  title: '新建简历',
  template_id: 'neu_resume',
  slug: '',
  language: 'zh-CN',
  status: 'draft',
  rendered_pdf_url: null,
  content: {
    basics: {
      name: '',
      phone: '',
      email: '',
      location: '',
      summary: '',
      job_target: '',
    },
    education: [],
    experience: [],
    projects: [],
    research: [],
    skills: [],
  },
});

function showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2400);
}

function buildPreviewUrl(url) {
  const cacheBusted = `${url}${url.includes('?') ? '&' : '?'}t=${Date.now()}`;
  return `${cacheBusted}#toolbar=0&navpanes=0&scrollbar=0&zoom=page-width`;
}

function setPreviewMessage(message) {
  elements.previewEmpty.textContent = message;
}

function setDownloadLink(url) {
  state.currentPdfUrl = url || null;
  if (state.currentPdfUrl) {
    elements.downloadLink.href = state.currentPdfUrl;
    elements.downloadLink.classList.remove('hidden-link');
    elements.pdfPreview.src = buildPreviewUrl(state.currentPdfUrl);
    elements.pdfPreview.classList.remove('hidden-preview');
    elements.previewEmpty.classList.add('hidden-preview');
  } else {
    elements.downloadLink.removeAttribute('href');
    elements.downloadLink.classList.add('hidden-link');
    elements.pdfPreview.removeAttribute('src');
    elements.pdfPreview.classList.add('hidden-preview');
    elements.previewEmpty.classList.remove('hidden-preview');
  }
}

function multilineToArray(value) {
  return value.split('\n').map((item) => item.trim()).filter(Boolean);
}

function arrayToMultiline(items = []) {
  return items.join('\n');
}

function createRepeatItem(section, data = {}) {
  const template = document.getElementById(`${section}-template`);
  const node = template.content.firstElementChild.cloneNode(true);
  node.querySelectorAll('[data-field]').forEach((input) => {
    const field = input.dataset.field;
    const value = Array.isArray(data[field]) ? arrayToMultiline(data[field]) : (data[field] || '');
    input.value = value;
    input.addEventListener('input', updatePreview);
  });
  node.querySelector('.remove-btn').addEventListener('click', () => {
    node.remove();
    updatePreview();
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
      const field = input.dataset.field;
      result[field] = input.tagName === 'TEXTAREA' ? multilineToArray(input.value) : input.value.trim();
    });
    return result;
  });
}

function getFormPayload() {
  return {
    title: document.getElementById('title').value.trim(),
    template_id: document.getElementById('template_id').value,
    slug: document.getElementById('slug').value.trim() || null,
    language: document.getElementById('language').value.trim() || 'zh-CN',
    status: document.getElementById('status').value,
    content: {
      basics: {
        name: document.getElementById('basics_name').value.trim(),
        phone: document.getElementById('basics_phone').value.trim(),
        email: document.getElementById('basics_email').value.trim(),
        location: document.getElementById('basics_location').value.trim(),
        summary: document.getElementById('basics_summary').value.trim(),
        job_target: document.getElementById('basics_job_target').value.trim(),
      },
      education: collectRepeatList('education'),
      experience: collectRepeatList('experience'),
      projects: collectRepeatList('projects'),
      research: collectRepeatList('research'),
      skills: document.getElementById('skills').value.split(',').map((item) => item.trim()).filter(Boolean),
    },
  };
}

function fillForm(resume) {
  const current = resume || defaultResume();
  document.getElementById('title').value = current.title || '';
  document.getElementById('template_id').value = current.template_id || state.templates[0]?.id || '';
  document.getElementById('slug').value = current.slug || '';
  document.getElementById('language').value = current.language || 'zh-CN';
  document.getElementById('status').value = current.status || 'draft';
  document.getElementById('basics_name').value = current.content?.basics?.name || '';
  document.getElementById('basics_phone').value = current.content?.basics?.phone || '';
  document.getElementById('basics_email').value = current.content?.basics?.email || '';
  document.getElementById('basics_location').value = current.content?.basics?.location || '';
  document.getElementById('basics_summary').value = current.content?.basics?.summary || '';
  document.getElementById('basics_job_target').value = current.content?.basics?.job_target || '';
  document.getElementById('skills').value = (current.content?.skills || []).join(', ');
  mountRepeatList('education', current.content?.education || []);
  mountRepeatList('experience', current.content?.experience || []);
  mountRepeatList('projects', current.content?.projects || []);
  mountRepeatList('research', current.content?.research || []);
  setDownloadLink(current.rendered_pdf_url || null);
  updatePreview();
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
  elements.templateSelect.innerHTML = state.templates.map((template) => `<option value="${template.id}">${template.name}</option>`).join('');
}

function updatePreview() {
  if (!state.currentPdfUrl) {
    setPreviewMessage('生成 PDF 后，这里会直接显示简历预览。');
  }
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || '请求失败');
  }
  if (response.status === 204) return null;
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

async function fetchCurrentResume() {
  if (!state.currentResumeId) return null;
  return request(`/api/resumes/${state.currentResumeId}`);
}

async function saveResume({ silent = false } = {}) {
  const payload = getFormPayload();
  if (!payload.title) {
    showToast('标题不能为空');
    return null;
  }
  const path = state.currentResumeId ? `/api/resumes/${state.currentResumeId}` : '/api/resumes';
  const method = state.currentResumeId ? 'PUT' : 'POST';
  const saved = await request(path, { method, body: JSON.stringify(payload) });
  state.currentResumeId = saved.id;
  await loadResumes();
  fillForm(saved);
  if (!silent) {
    showToast('已保存');
  }
  return saved;
}

async function renderPdf() {
  try {
    elements.renderButton.disabled = true;
    setPreviewMessage('正在生成 PDF，请稍等...');
    elements.previewEmpty.classList.remove('hidden-preview');
    elements.pdfPreview.classList.add('hidden-preview');

    if (!state.currentResumeId) {
      await saveResume({ silent: true });
    }
    if (!state.currentResumeId) return;

    await saveResume({ silent: true });
    const result = await request(`/api/resumes/${state.currentResumeId}/render`, { method: 'POST' });
    setDownloadLink(result.pdf_url);

    const latest = await fetchCurrentResume();
    if (latest) {
      const index = state.resumes.findIndex((item) => item.id === latest.id);
      if (index >= 0) {
        state.resumes[index] = latest;
      }
      fillForm(latest);
      renderResumeList();
    }

    showToast('PDF 已生成');
  } catch (error) {
    console.error(error);
    setDownloadLink(null);
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
  setDownloadLink(null);
  await loadResumes();
  renderResumeList();
  showToast('已删除');
}

function bindEvents() {
  elements.form.addEventListener('input', updatePreview);
  elements.saveButton.addEventListener('click', () => saveResume());
  elements.renderButton.addEventListener('click', renderPdf);
  elements.deleteButton.addEventListener('click', deleteResume);
  elements.newResumeButton.addEventListener('click', () => {
    state.currentResumeId = null;
    setDownloadLink(null);
    fillForm(defaultResume());
    renderResumeList();
  });
  document.querySelectorAll('[data-add-section]').forEach((button) => {
    button.addEventListener('click', () => {
      const section = button.dataset.addSection;
      elements[`${section}List`].appendChild(createRepeatItem(section, {}));
      updatePreview();
    });
  });
}

async function bootstrap() {
  bindEvents();
  await loadTemplates();
  await loadResumes();
  updatePreview();
}

bootstrap().catch((error) => {
  console.error(error);
  showToast('页面初始化失败，请检查后端服务');
});
