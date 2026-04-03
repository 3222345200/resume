<template>
  <main class="auth-page auth-page-premium">
    <section class="auth-hero premium-hero">
      <div class="premium-orb premium-orb-one"></div>
      <div class="premium-orb premium-orb-two"></div>
      <div class="premium-grid"></div>

      <div class="premium-topline">
        <div class="brand-badge premium-badge">
          <img class="brand-logo" :src="brandMark" alt="职跃 OfferPilot 标志" />
          <span class="brand-name">职跃 OfferPilot</span>
        </div>
        <span class="premium-status">Create Account</span>
      </div>

      <div class="premium-copy">
        <p class="premium-kicker">EMAIL VERIFIED REGISTRATION</p>
        <h1>先注册，再开始整理你的简历资产。</h1>
        <p class="auth-copy">
          注册页会校验图形验证码和邮箱验证码，验证通过后自动进入编辑工作台。
        </p>
      </div>

      <div class="premium-metrics">
        <div class="premium-metric"><strong>01</strong><span>填写账号和邮箱</span></div>
        <div class="premium-metric"><strong>02</strong><span>发送邮箱验证码</span></div>
        <div class="premium-metric"><strong>03</strong><span>完成注册并登录</span></div>
      </div>
    </section>

    <section class="auth-panel">
      <div class="auth-card">
        <p class="eyebrow">Register</p>
        <h2>创建一个新账号</h2>
        <p class="muted-copy">填写用户名、密码和邮箱，然后完成验证码验证。</p>

        <form class="auth-form" @submit.prevent="handleRegister">
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

          <button class="primary-button" type="submit" :disabled="submitting">
            {{ submitting ? '注册中...' : '注册并登录' }}
          </button>
          <RouterLink class="ghost-button" to="/login">已有账号？返回登录</RouterLink>
        </form>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import brandMark from '../assets/brand-mark.svg'
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
    await router.push('/editor')
  } catch (error) {
    setMessage(String(error.message || error), true)
  } finally {
    submitting.value = false
  }
}

onMounted(refreshCaptcha)
</script>
