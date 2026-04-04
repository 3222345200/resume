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
        <span class="premium-status">Career Workspace</span>
      </div>

      <div class="premium-copy">
        <p class="premium-kicker">CAREER TOOLS FOR AMBITIOUS CANDIDATES</p>
        <h1>更快写出一份清爽、有重点的简历。</h1>
        <p class="auth-copy">
          管理多份简历版本，实时预览 PDF 效果，把排版和内容一起打磨到位。
        </p>
      </div>

      <div class="premium-metrics">
        <div class="premium-metric"><strong>01</strong><span>账号密码登录</span></div>
        <div class="premium-metric"><strong>02</strong><span>邮箱验证码注册</span></div>
        <div class="premium-metric"><strong>03</strong><span>验证后进入工作台</span></div>
      </div>
    </section>

    <section class="auth-panel">
      <div class="auth-card">
        <p class="eyebrow">Sign In</p>
        <h2>进入你的求职工作台</h2>
        <p class="muted-copy">欢迎回来，继续完善你的简历内容。</p>

        <form class="auth-form" @submit.prevent="handleLogin">
          <label>
            <span>用户名</span>
            <input v-model.trim="form.username" autocomplete="username" placeholder="例如：zhangsan01" />
          </label>

          <label>
            <span>密码</span>
            <input v-model="form.password" type="password" autocomplete="current-password" placeholder="至少 8 位" />
          </label>

          <p class="auth-message" :class="{ danger: isError }">{{ message }}</p>

          <button class="primary-button" type="submit" :disabled="submitting">
            {{ submitting ? '登录中...' : '登录' }}
          </button>
          <RouterLink class="ghost-button" to="/register">没有账号？去注册</RouterLink>
        </form>
      </div>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import brandMark from '../assets/brand-mark.svg'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const submitting = ref(false)
const message = ref('')
const isError = ref(false)
const form = reactive({
  username: '',
  password: '',
})

function validateForm() {
  if (!/^[A-Za-z0-9]{4,20}$/.test(form.username)) {
    message.value = '用户名只能是 4 到 20 位英文或数字'
    isError.value = true
    return false
  }
  if (form.password.length < 8) {
    message.value = '密码至少需要 8 位'
    isError.value = true
    return false
  }
  return true
}

async function handleLogin() {
  if (!validateForm()) {
    return
  }

  try {
    submitting.value = true
    message.value = ''
    isError.value = false
    await authStore.login(form)
    await router.push('/editor')
  } catch (error) {
    message.value = String(error.message || error)
    isError.value = true
  } finally {
    submitting.value = false
  }
}
</script>
