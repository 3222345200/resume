<template>
  <main class="auth-page auth-page-compass">
    <section
      ref="heroRef"
      class="auth-hero compass-hero"
      @pointermove="handleHeroPointerMove"
      @pointerleave="resetHeroPointer"
    >
      <div class="compass-hero-noise"></div>

      <div class="compass-scene">
        <div class="compass-glow compass-glow-left"></div>
        <div class="compass-glow compass-glow-right"></div>

        <div class="compass-characters">
          <div class="compass-character chicken" :style="characterStyle('chicken')">
            <div class="compass-character-shadow"></div>
            <div class="compass-character-body"></div>
            <div class="compass-character-leg left"></div>
            <div class="compass-character-leg right"></div>
            <div class="compass-character-arm left" :style="armStyle('chicken', 'left')"></div>
            <div class="compass-character-arm right" :style="armStyle('chicken', 'right')"></div>
            <div class="compass-character-head" :style="headStyle('chicken')">
              <div class="compass-cat-ear left"></div>
              <div class="compass-cat-ear right"></div>
              <div class="compass-face compass-cat-face">
                <span class="compass-eye"><i :style="pupilStyle('chicken')"></i></span>
                <span class="compass-eye"><i :style="pupilStyle('chicken')"></i></span>
              </div>
              <div class="compass-cat-nose"></div>
              <div class="compass-mouth smile"></div>
              <div class="compass-cat-whiskers left"></div>
              <div class="compass-cat-whiskers right"></div>
            </div>
          </div>

          <div
            class="compass-character duck"
            :class="{ 'is-password-focused': passwordFocused && !showPassword }"
            :style="characterStyle('duck')"
          >
            <div class="compass-character-shadow"></div>
            <div class="compass-character-body"></div>
            <div class="compass-character-leg left"></div>
            <div class="compass-character-leg right"></div>
            <div class="compass-character-arm left" :style="armStyle('duck', 'left')"></div>
            <div class="compass-character-arm right" :style="armStyle('duck', 'right')"></div>
            <div class="compass-character-head" :style="headStyle('duck')">
              <div class="compass-frog-eye-dome left">
                <span class="compass-eye"><i :style="pupilStyle('duck')"></i></span>
              </div>
              <div class="compass-frog-eye-dome right">
                <span class="compass-eye"><i :style="pupilStyle('duck')"></i></span>
              </div>
              <div class="compass-frog-cheek left"></div>
              <div class="compass-frog-cheek right"></div>
              <div class="compass-mouth smile"></div>
            </div>
          </div>

          <div
            class="compass-character goose"
            :class="{ 'is-password-focused': passwordFocused && !showPassword }"
            :style="characterStyle('goose')"
          >
            <div class="compass-character-shadow"></div>
            <div class="compass-character-body"></div>
            <div class="compass-character-leg left"></div>
            <div class="compass-character-leg right"></div>
            <div class="compass-character-arm left" :style="armStyle('goose', 'left')"></div>
            <div class="compass-character-arm right" :style="armStyle('goose', 'right')"></div>
            <div class="compass-character-head" :style="headStyle('goose')">
              <div class="compass-fox-ear left"></div>
              <div class="compass-fox-ear right"></div>
              <div class="compass-fox-mask"></div>
              <div class="compass-face compass-fox-face">
                <span class="compass-eye"><i :style="pupilStyle('goose')"></i></span>
                <span class="compass-eye"><i :style="pupilStyle('goose')"></i></span>
              </div>
              <div class="compass-fox-snout"></div>
            </div>
          </div>

          <div class="compass-character dog" :class="{ 'is-looking': usernameFocused }" :style="characterStyle('dog')">
            <div class="compass-character-shadow"></div>
            <div class="compass-character-body"></div>
            <div class="compass-character-leg left"></div>
            <div class="compass-character-leg right"></div>
            <div class="compass-character-arm left" :style="armStyle('dog', 'left')"></div>
            <div class="compass-character-arm right" :style="armStyle('dog', 'right')"></div>
            <div class="compass-character-head" :style="headStyle('dog')">
              <div class="compass-owl-tuft left"></div>
              <div class="compass-owl-tuft right"></div>
              <div class="compass-owl-eye-ring left">
                <span class="compass-eye"><i :style="pupilStyle('dog')"></i></span>
              </div>
              <div class="compass-owl-eye-ring right">
                <span class="compass-eye"><i :style="pupilStyle('dog')"></i></span>
              </div>
              <div class="compass-owl-beak"></div>
            </div>
          </div>

          <div class="compass-character pig" :style="characterStyle('pig')">
            <div class="compass-character-shadow"></div>
            <div class="compass-character-body"></div>
            <div class="compass-character-leg left"></div>
            <div class="compass-character-leg right"></div>
            <div class="compass-character-arm left" :style="armStyle('pig', 'left')"></div>
            <div class="compass-character-arm right" :style="armStyle('pig', 'right')"></div>
            <div class="compass-character-head" :style="headStyle('pig')">
              <div class="compass-ear left"></div>
              <div class="compass-ear right"></div>
              <div class="compass-pig-blush left"></div>
              <div class="compass-pig-blush right"></div>
              <div class="compass-face">
                <span class="compass-eye"><i :style="pupilStyle('pig')"></i></span>
                <span class="compass-eye"><i :style="pupilStyle('pig')"></i></span>
              </div>
              <div class="compass-snout"></div>
              <div class="compass-mouth"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="auth-panel compass-panel">
      <div class="auth-card compass-auth-card">
        <div class="compass-panel-top">
          <div class="compass-panel-logo">
            <img class="brand-logo" :src="brandMark" alt="" aria-hidden="true" />
            <span>职跃 OfferPilot</span>
          </div>
          <RouterLink class="compass-register-link" to="/register">Create account</RouterLink>
        </div>

        <div class="compass-form-copy">
          <p class="eyebrow">Welcome back</p>
          <h2>登录你的求职工作台</h2>
          <p class="muted-copy">继续编辑简历、调整版式，并回到你上次的工作进度。</p>
        </div>

        <form class="auth-form compass-auth-form" @submit.prevent="handleLogin">
          <label>
            <span>用户名</span>
            <input
              v-model.trim="form.username"
              autocomplete="username"
              placeholder="例如：zhangsan01"
              @focus="usernameFocused = true"
              @blur="usernameFocused = false"
            />
          </label>

          <label class="compass-password-field">
            <span>密码</span>
            <div class="compass-password-wrap">
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="至少 8 位"
                @focus="passwordFocused = true"
                @blur="passwordFocused = false"
              />
              <button type="button" class="compass-toggle-password" @click="showPassword = !showPassword">
                {{ showPassword ? '隐藏' : '显示' }}
              </button>
            </div>
          </label>

          <div class="compass-forgot-row">
            <RouterLink class="compass-forgot-link" to="/forgot-password">忘记密码</RouterLink>
          </div>

          <p class="auth-message" :class="{ danger: isError }">{{ message }}</p>

          <button class="primary-button compass-submit-button" type="submit" :disabled="submitting">
            {{ submitting ? '登录中...' : '登录' }}
          </button>
          <RouterLink class="ghost-button compass-secondary-button" to="/register">没有账号？去注册</RouterLink>
        </form>

        <p class="compass-attribution">
          Visual direction inspired by
          <a href="https://github.com/arsh342/careercompass" target="_blank" rel="noreferrer">careercompass</a>
        </p>
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
const usernameFocused = ref(false)
const passwordFocused = ref(false)
const showPassword = ref(false)
const heroRef = ref(null)

const form = reactive({
  username: '',
  password: '',
})

const pointer = reactive({
  x: 0,
  y: 0,
})

const characterFactors = {
  chicken: { x: -0.44, y: -0.24, rotate: -4.2, tilt: -10, lift: 0, scale: 0.84 },
  duck: { x: -0.22, y: 0.28, rotate: -2.4, tilt: -6, lift: 0, scale: 1.12 },
  goose: { x: 0.1, y: 0.1, rotate: 1.6, tilt: 2, lift: 0, scale: 1.62 },
  dog: { x: 0.34, y: -0.22, rotate: 3.8, tilt: 12, lift: 0, scale: 1.3 },
  pig: { x: 0.32, y: 0.2, rotate: 3.2, tilt: 7, lift: 0, scale: 1.92 },
}

function handleHeroPointerMove(event) {
  const hero = heroRef.value
  if (!hero) {
    return
  }

  const rect = hero.getBoundingClientRect()
  const normalizedX = ((event.clientX - rect.left) / rect.width) * 2 - 1
  const normalizedY = ((event.clientY - rect.top) / rect.height) * 2 - 1

  pointer.x = Math.max(-1, Math.min(1, normalizedX))
  pointer.y = Math.max(-1, Math.min(1, normalizedY))
}

function resetHeroPointer() {
  pointer.x = 0
  pointer.y = 0
}

function pupilStyle(name) {
  const factor = characterFactors[name]
  const x = pointer.x * 10 * factor.x + (usernameFocused.value ? factor.rotate * 1.5 : 0)
  const y = pointer.y * 8 * factor.y
  const scale = passwordFocused.value && !showPassword.value ? 0.62 : 1
  return {
    transform: `translate(${x}px, ${y}px) scale(${scale})`,
  }
}

function headStyle(name) {
  const factor = characterFactors[name]
  const offsetX = pointer.x * 14 * factor.x
  const offsetY = pointer.y * 10 * factor.y
  const rotate = pointer.x * factor.rotate
  const extra = passwordFocused.value && !showPassword.value && (name === 'duck' || name === 'goose') ? -10 : 0
  return {
    transform: `translate(${offsetX}px, ${offsetY + extra}px) rotate(${rotate}deg)`,
  }
}

function characterStyle(name) {
  const factor = characterFactors[name]
  const lift = (passwordFocused.value && !showPassword.value && name === 'goose' ? -16 : 0) + factor.lift
  return {
    transform: `translate(${pointer.x * 16 * factor.x}px, ${pointer.y * 14 * factor.y + lift}px) rotate(${factor.tilt + pointer.x * factor.rotate * 0.6}deg) scale(${factor.scale})`,
  }
}

function armStyle(name, side) {
  const sign = side === 'left' ? -1 : 1
  if (passwordFocused.value && !showPassword.value && (name === 'duck' || name === 'goose')) {
    const rotate = name === 'duck' ? 56 * sign : 72 * sign
    const translateX = name === 'duck' ? 22 * sign : 28 * sign
    return {
      transform: `translate(${translateX}px, -46px) rotate(${rotate}deg)`,
    }
  }

  return {
    transform: `translate(${pointer.x * 7 * sign}px, ${pointer.y * 5}px) rotate(${16 * sign + pointer.x * 8 * sign}deg)`,
  }
}

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
    await router.push('/dashboard')
  } catch (error) {
    message.value = String(error.message || error)
    isError.value = true
  } finally {
    submitting.value = false
  }
}
</script>
