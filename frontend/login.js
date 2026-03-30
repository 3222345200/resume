const LOGIN_TOKEN_KEY = 'resume_auth_token';
const AUTH_MODE = window.location.pathname === '/register' ? 'register' : 'login';

const loginElements = {
  page: document.querySelector('[data-auth-mode]'),
  form: document.getElementById('auth-form'),
  username: document.getElementById('auth-username'),
  password: document.getElementById('auth-password'),
  email: document.getElementById('auth-email'),
  captchaAnswer: document.getElementById('auth-captcha-answer'),
  captchaImage: document.getElementById('captcha-image'),
  emailCode: document.getElementById('auth-email-code'),
  message: document.getElementById('auth-message'),
  loginButton: document.getElementById('login-btn'),
  registerSubmitButton: document.getElementById('register-submit-btn'),
  refreshCaptchaButton: document.getElementById('refresh-captcha-btn'),
  sendCodeButton: document.getElementById('send-code-btn'),
  registerOnly: Array.from(document.querySelectorAll('.register-only')),
  eyebrow: document.getElementById('auth-eyebrow'),
  heroTitle: document.getElementById('auth-hero-title'),
  heroCopy: document.getElementById('auth-hero-copy'),
  noteCopy: document.getElementById('auth-note-copy'),
  panelTitle: document.getElementById('auth-panel-title'),
  panelCopy: document.getElementById('auth-panel-copy'),
  footerCopy: document.getElementById('auth-footer-copy'),
};

const registerState = {
  captchaId: '',
  verificationId: '',
};

function setLoginMessage(message, isError = false) {
  loginElements.message.textContent = message || '';
  loginElements.message.classList.toggle('auth-error', Boolean(isError));
}

function saveToken(token) {
  localStorage.setItem(LOGIN_TOKEN_KEY, token);
}

function goToEditor() {
  window.location.href = '/editor';
}

function readErrorMessage(payload, fallback) {
  if (!payload) {
    return fallback;
  }
  if (typeof payload === 'string') {
    return payload;
  }
  if (typeof payload.detail === 'string') {
    return payload.detail;
  }
  return fallback;
}

function validateUsernameAndPassword(payload) {
  if (!payload.username || !payload.password) {
    setLoginMessage('请输入账号和密码', true);
    return false;
  }
  if (!/^[A-Za-z0-9]{4,20}$/.test(payload.username)) {
    setLoginMessage('用户名只能是 4 到 20 位英文或数字', true);
    return false;
  }
  if (payload.password.length < 8) {
    setLoginMessage('密码至少需要 8 位', true);
    return false;
  }
  return true;
}

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function applyAuthMode() {
  const isRegister = AUTH_MODE === 'register';
  document.title = isRegister ? '注册 - 职跃 OfferPilot' : '登录 - 职跃 OfferPilot';

  if (loginElements.page) {
    loginElements.page.dataset.authMode = AUTH_MODE;
  }

  loginElements.registerOnly.forEach((element) => {
    element.classList.toggle('hidden-auth', !isRegister);
  });
  loginElements.loginButton.classList.toggle('hidden-auth', isRegister);
  loginElements.registerSubmitButton.classList.toggle('hidden-auth', !isRegister);
  document.getElementById('go-register-link')?.classList.toggle('hidden-auth', isRegister);
  document.getElementById('go-login-link')?.classList.toggle('hidden-auth', !isRegister);

  if (!isRegister) {
    loginElements.eyebrow.textContent = 'Sign In';
    loginElements.heroTitle.textContent = '把经历组织好，剩下的交给职业表达。';
    loginElements.heroCopy.textContent = '登录页只保留账号密码入口。没有账号时，点击注册进入单独的注册页，再完成邮箱验证流程。';
    loginElements.noteCopy.textContent = '登录与注册拆分后，首次访问更简单，注册流程也更清晰。';
    loginElements.panelTitle.textContent = '进入你的求职工作台';
    loginElements.panelCopy.textContent = '输入账号和密码即可登录。如果还没有账号，请先进入注册页完成邮箱验证。';
    loginElements.footerCopy.textContent = '你的登录状态会保存在当前浏览器，下次打开可直接回到编辑页。';
    return;
  }

  loginElements.eyebrow.textContent = 'Register';
  loginElements.heroTitle.textContent = '先注册，再开始整理你的简历资产。';
  loginElements.heroCopy.textContent = '注册页会要求填写邮箱、完成字母验证码，并通过邮箱验证码完成账号验证。';
  loginElements.noteCopy.textContent = '完成验证后，系统会自动登录并进入编辑页。';
  loginElements.panelTitle.textContent = '创建一个新账号';
  loginElements.panelCopy.textContent = '填写用户名、密码和邮箱，然后完成验证码验证。已有账号可直接返回登录页。';
  loginElements.footerCopy.textContent = '新账号完成邮箱验证后才能正常进入系统。';
}

async function fetchJson(path, options = {}, fallbackMessage = '请求失败') {
  const response = await fetch(path, options);
  if (!response.ok) {
    let errorPayload = null;
    try {
      errorPayload = await response.json();
    } catch {
      errorPayload = await response.text();
    }
    throw new Error(readErrorMessage(errorPayload, fallbackMessage));
  }
  return response.json();
}

function renderCaptcha(svgMarkup) {
  if (loginElements.captchaImage) {
    loginElements.captchaImage.src = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svgMarkup)}`;
  }
}

async function loadCaptcha() {
  const result = await fetchJson('/api/auth/captcha', {}, '获取验证码失败');
  registerState.captchaId = result.captcha_id;
  registerState.verificationId = '';
  if (loginElements.captchaAnswer) {
    loginElements.captchaAnswer.value = '';
  }
  if (loginElements.emailCode) {
    loginElements.emailCode.value = '';
  }
  renderCaptcha(result.captcha_svg);
}

async function authenticate(path) {
  const payload = {
    username: loginElements.username.value.trim(),
    password: loginElements.password.value,
  };

  if (!validateUsernameAndPassword(payload)) {
    return null;
  }

  return fetchJson(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }, '认证失败');
}

async function sendRegisterCode() {
  const email = loginElements.email.value.trim().toLowerCase();
  const captchaAnswer = loginElements.captchaAnswer.value.trim();

  if (!email) {
    setLoginMessage('请先填写个人邮箱', true);
    return;
  }
  if (!validateEmail(email)) {
    setLoginMessage('邮箱格式不正确', true);
    return;
  }
  if (!captchaAnswer) {
    setLoginMessage('请先输入字母验证码', true);
    return;
  }
  if (!registerState.captchaId) {
    setLoginMessage('验证码会话已失效，请刷新后重试', true);
    return;
  }

  const result = await fetchJson('/api/auth/send-register-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      captcha_id: registerState.captchaId,
      captcha_answer: captchaAnswer,
    }),
  }, '发送邮箱验证码失败');

  registerState.verificationId = result.verification_id;
  setLoginMessage(result.message || '邮箱验证码已发送，请查收');
}

async function register() {
  const payload = {
    username: loginElements.username.value.trim(),
    password: loginElements.password.value,
    email: loginElements.email.value.trim().toLowerCase(),
    verification_id: registerState.verificationId,
    email_code: loginElements.emailCode.value.trim(),
  };

  if (!validateUsernameAndPassword(payload)) {
    return null;
  }
  if (!payload.email) {
    setLoginMessage('注册时必须填写个人邮箱', true);
    return null;
  }
  if (!validateEmail(payload.email)) {
    setLoginMessage('邮箱格式不正确', true);
    return null;
  }
  if (!payload.verification_id) {
    setLoginMessage('请先通过字母验证码并发送邮箱验证码', true);
    return null;
  }
  if (!/^\d{6}$/.test(payload.email_code)) {
    setLoginMessage('请输入 6 位邮箱验证码', true);
    return null;
  }

  return fetchJson('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }, '注册失败');
}

async function restoreSession() {
  const token = localStorage.getItem(LOGIN_TOKEN_KEY);
  if (!token) {
    return;
  }

  const response = await fetch('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.ok) {
    goToEditor();
    return;
  }

  localStorage.removeItem(LOGIN_TOKEN_KEY);
}

function bindLoginEvents() {
  if (!loginElements.form) {
    return;
  }

  loginElements.form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (AUTH_MODE === 'register') {
      loginElements.registerSubmitButton?.click();
      return;
    }
    loginElements.loginButton?.click();
  });

  loginElements.loginButton?.addEventListener('click', async () => {
    try {
      loginElements.loginButton.disabled = true;
      setLoginMessage('');
      const result = await authenticate('/api/auth/login');
      if (!result) {
        return;
      }
      saveToken(result.access_token);
      goToEditor();
    } catch (error) {
      setLoginMessage(String(error.message || error), true);
    } finally {
      loginElements.loginButton.disabled = false;
    }
  });

  if (AUTH_MODE !== 'register') {
    return;
  }

  loginElements.refreshCaptchaButton?.addEventListener('click', async () => {
    try {
      loginElements.refreshCaptchaButton.disabled = true;
      setLoginMessage('');
      await loadCaptcha();
    } catch (error) {
      setLoginMessage(String(error.message || error), true);
    } finally {
      loginElements.refreshCaptchaButton.disabled = false;
    }
  });

  loginElements.sendCodeButton?.addEventListener('click', async () => {
    try {
      loginElements.sendCodeButton.disabled = true;
      setLoginMessage('');
      await sendRegisterCode();
    } catch (error) {
      setLoginMessage(String(error.message || error), true);
      await loadCaptcha().catch(() => {});
    } finally {
      loginElements.sendCodeButton.disabled = false;
    }
  });

  loginElements.registerSubmitButton?.addEventListener('click', async () => {
    try {
      loginElements.registerSubmitButton.disabled = true;
      setLoginMessage('');
      const result = await register();
      if (!result) {
        return;
      }
      saveToken(result.access_token);
      goToEditor();
    } catch (error) {
      setLoginMessage(String(error.message || error), true);
    } finally {
      loginElements.registerSubmitButton.disabled = false;
    }
  });
}

applyAuthMode();
restoreSession()
  .then(async () => {
    if (AUTH_MODE === 'register') {
      await loadCaptcha();
    }
  })
  .catch(async () => {
    if (AUTH_MODE === 'register') {
      await loadCaptcha();
    }
  })
  .finally(bindLoginEvents);