<template>
  <main class="auth-page auth-page-compass">
    <AuthAnimalScene />

    <section class="auth-panel compass-panel">
      <div class="auth-card compass-auth-card">
        <div class="compass-panel-top">
          <div class="compass-panel-logo">
            <img class="brand-logo" :src="brandMark" alt="职跃 OfferPilot 标志" />
            <span>职跃 OfferPilot</span>
          </div>
          <RouterLink class="compass-register-link" to="/login">Back to login</RouterLink>
        </div>

        <div class="compass-form-copy">
          <p class="eyebrow">Create account</p>
          <h2>创建一个新账号</h2>
          <p class="muted-copy">填写基础信息并完成邮箱验证，即可进入求职工作台。</p>
        </div>

        <form class="auth-form compass-auth-form" @submit.prevent="handleRegister">
          <label>
            <span>用户名</span>
            <input v-model.trim="form.username" autocomplete="username" placeholder="例如：zhangsan01" />
          </label>

          <label>
            <span>密码</span>
            <input v-model="form.password" type="password" autocomplete="new-password" placeholder="至少 8 位" />
          </label>

          <label>
            <span>个人邮箱</span>
            <input v-model.trim="form.email" type="email" autocomplete="email" placeholder="name@example.com" />
          </label>

          <div class="captcha-grid">
            <label>
              <span>字母验证码</span>
              <input v-model.trim="form.captchaAnswer" autocomplete="off" placeholder="输入图片里的字母" />
            </label>
            <div class="captcha-box">
              <img v-if="captchaImageUrl" :src="captchaImageUrl" alt="字母验证码" />
            </div>
            <button class="ghost-button inline-action" type="button" :disabled="captchaLoading" @click="refreshCaptcha">
              {{ captchaLoading ? '刷新中...' : '刷新验证码' }}
            </button>
          </div>

          <div class="code-grid">
            <label>
              <span>邮箱验证码</span>
              <input v-model.trim="form.emailCode" inputmode="numeric" autocomplete="one-time-code" placeholder="6 位验证码" />
            </label>
            <button class="ghost-button inline-action" type="button" :disabled="sendingCode" @click="sendCode">
              {{ sendingCode ? '发送中...' : '发送邮箱验证码' }}
            </button>
          </div>

          <p class="auth-message" :class="{ danger: isError }">{{ message }}</p>

          <button class="primary-button compass-submit-button" type="submit" :disabled="submitting">
            {{ submitting ? '注册中...' : '注册并登录' }}
          </button>
          <RouterLink class="ghost-button compass-secondary-button" to="/login">已有账号？返回登录</RouterLink>
        </form>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import brandMark from '../assets/logo-new.png'
import AuthAnimalScene from '../components/AuthAnimalScene.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const submitting = ref(false)
const sendingCode = ref(false)
const captchaLoading = ref(false)
const message = ref('')
const isError = ref(false)
const form = reactive({
  username: '',
  password: '',
  email: '',
  captchaAnswer: '',
  emailCode: '',
})

const captchaImageUrl = computed(() => {
  if (!authStore.captchaSvg) {
    return ''
  }
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(authStore.captchaSvg)}`
})

function setMessage(text, danger = false) {
  message.value = text
  isError.value = danger
}

function validateAccount() {
  if (!/^[A-Za-z0-9]{4,20}$/.test(form.username)) {
    setMessage('用户名只能是 4 到 20 位英文或数字', true)
    return false
  }
  if (form.password.length < 8) {
    setMessage('密码至少需要 8 位', true)
    return false
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    setMessage('邮箱格式不正确', true)
    return false
  }
  return true
}

async function refreshCaptcha() {
  try {
    captchaLoading.value = true
    form.captchaAnswer = ''
    form.emailCode = ''
    await authStore.loadCaptcha()
  } catch (error) {
    setMessage(String(error.message || error), true)
  } finally {
    captchaLoading.value = false
  }
}

async function sendCode() {
  if (!validateAccount()) {
    return
  }
  if (!form.captchaAnswer) {
    setMessage('请先输入字母验证码', true)
    return
  }

  try {
    sendingCode.value = true
    const resultMessage = await authStore.sendRegisterCode({
      email: form.email.trim().toLowerCase(),
      captchaAnswer: form.captchaAnswer,
    })
    setMessage(resultMessage, false)
  } catch (error) {
    setMessage(String(error.message || error), true)
    await refreshCaptcha()
  } finally {
    sendingCode.value = false
  }
}

async function handleRegister() {
  if (!validateAccount()) {
    return
  }
  if (!/^\d{6}$/.test(form.emailCode)) {
    setMessage('请输入 6 位邮箱验证码', true)
    return
  }
  if (!authStore.verificationId) {
    setMessage('请先发送邮箱验证码', true)
    return
  }

  try {
    submitting.value = true
    await authStore.register({
      username: form.username,
      password: form.password,
      email: form.email.trim().toLowerCase(),
      email_code: form.emailCode,
    })
    await router.push('/dashboard')
  } catch (error) {
    setMessage(String(error.message || error), true)
  } finally {
    submitting.value = false
  }
}

onMounted(refreshCaptcha)
</script>
