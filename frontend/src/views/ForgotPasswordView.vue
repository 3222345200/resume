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
          <p class="eyebrow">Forgot password</p>
          <h2>重置密码</h2>
          <p class="muted-copy">输入注册邮箱，完成验证码校验后即可设置一个新密码。</p>
        </div>

        <form class="auth-form compass-auth-form" @submit.prevent="handleResetPassword">
          <label>
            <span>注册邮箱</span>
            <input v-model.trim="form.email" type="email" autocomplete="email" placeholder="name@example.com" />
          </label>

          <label>
            <span>新密码</span>
            <input v-model="form.newPassword" type="password" autocomplete="new-password" placeholder="至少 8 位" />
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
            {{ submitting ? '重置中...' : '确认重置密码' }}
          </button>
          <RouterLink class="ghost-button compass-secondary-button" to="/login">返回登录</RouterLink>
        </form>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import brandMark from '../assets/logo.png'
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
  email: '',
  newPassword: '',
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

function validateForm() {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    setMessage('邮箱格式不正确', true)
    return false
  }
  if (form.newPassword.length < 8) {
    setMessage('新密码至少需要 8 位', true)
    return false
  }
  return true
}

async function refreshCaptcha() {
  try {
    captchaLoading.value = true
    form.captchaAnswer = ''
    form.emailCode = ''
    await authStore.loadCaptchaForPurpose('password_reset')
  } catch (error) {
    setMessage(String(error.message || error), true)
  } finally {
    captchaLoading.value = false
  }
}

async function sendCode() {
  if (!validateForm()) {
    return
  }
  if (!form.captchaAnswer) {
    setMessage('请先输入字母验证码', true)
    return
  }

  try {
    sendingCode.value = true
    const resultMessage = await authStore.sendPasswordResetCode({
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

async function handleResetPassword() {
  if (!validateForm()) {
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
    const result = await authStore.resetPassword({
      email: form.email.trim().toLowerCase(),
      email_code: form.emailCode,
      new_password: form.newPassword,
    })
    setMessage(result.message || '密码重置成功', false)
    setTimeout(() => {
      router.push('/login')
    }, 800)
  } catch (error) {
    setMessage(String(error.message || error), true)
  } finally {
    submitting.value = false
  }
}

onMounted(refreshCaptcha)
</script>
