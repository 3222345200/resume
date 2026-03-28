const LOGIN_TOKEN_KEY = 'resume_auth_token';

const loginElements = {
  form: document.getElementById('auth-form'),
  username: document.getElementById('auth-username'),
  password: document.getElementById('auth-password'),
  message: document.getElementById('auth-message'),
  loginButton: document.getElementById('login-btn'),
  registerButton: document.getElementById('register-btn'),
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

function validateCredentials(payload) {
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

async function authenticate(path) {
  const payload = {
    username: loginElements.username.value.trim(),
    password: loginElements.password.value,
  };

  if (!validateCredentials(payload)) {
    return null;
  }

  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorPayload = null;
    try {
      errorPayload = await response.json();
    } catch {
      errorPayload = await response.text();
    }
    throw new Error(readErrorMessage(errorPayload, '认证失败'));
  }

  return response.json();
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
  loginElements.form.addEventListener('submit', async (event) => {
    event.preventDefault();
    loginElements.loginButton.click();
  });

  loginElements.loginButton.addEventListener('click', async () => {
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

  loginElements.registerButton.addEventListener('click', async () => {
    try {
      loginElements.registerButton.disabled = true;
      setLoginMessage('');
      const result = await authenticate('/api/auth/register');
      if (!result) {
        return;
      }
      saveToken(result.access_token);
      goToEditor();
    } catch (error) {
      setLoginMessage(String(error.message || error), true);
    } finally {
      loginElements.registerButton.disabled = false;
    }
  });
}

restoreSession().finally(bindLoginEvents);
