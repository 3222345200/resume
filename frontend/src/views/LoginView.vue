<template>
  <main class="auth-page auth-page-compass">
    <section class="auth-hero compass-hero">
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
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import brandMark from '../assets/logo.png'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const submitting = ref(false)
const message = ref('')
const isError = ref(false)
const usernameFocused = ref(false)
const passwordFocused = ref(false)
const showPassword = ref(false)

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

const pupilFactors = {
  chicken: { x: 5.4, y: 4.4, focus: -1.2 },
  duck: { x: 5.8, y: 4.8, focus: -0.8 },
  goose: { x: 3.8, y: 2.2, focus: 0.8 },
  dog: { x: 5.6, y: 4.4, focus: 1.3 },
  pig: { x: 5.2, y: 4.2, focus: 1 },
}

const bodyFollowFactors = {
  chicken: { x: 0.7, y: 0.65 },
  duck: { x: 0.86, y: 0.8 },
  goose: { x: 1, y: 0.92 },
  dog: { x: 0.9, y: 0.82 },
  pig: { x: 1.08, y: 0.98 },
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value))
}

function handlePagePointerMove(event) {
  const width = window.innerWidth || document.documentElement.clientWidth || 1
  const height = window.innerHeight || document.documentElement.clientHeight || 1
  const normalizedX = (event.clientX / width) * 2 - 1
  const normalizedY = (event.clientY / height) * 2 - 1

  pointer.x = clamp(normalizedX, -1, 1)
  pointer.y = clamp(normalizedY, -1, 1)
}

function resetHeroPointer() {
  pointer.x = 0
  pointer.y = 0
}

function handlePagePointerOut(event) {
  if (!event.relatedTarget) {
    resetHeroPointer()
  }
}

function pupilStyle(name) {
  const factor = pupilFactors[name]
  const x = pointer.x * factor.x + (usernameFocused.value ? factor.focus : 0)
  const y = pointer.y * factor.y
  const scale = passwordFocused.value && !showPassword.value ? 0.62 : 1
  return {
    transform: `translate(${clamp(x, -factor.x, factor.x)}px, ${clamp(y, -factor.y, factor.y)}px) scale(${scale})`,
  }
}

function headStyle(name) {
  const factor = characterFactors[name]
  const follow = bodyFollowFactors[name]
  const offsetX = pointer.x * 7 * follow.x
  const offsetY = pointer.y * 6 * follow.y
  const rotate = pointer.x * factor.rotate
  const extra = passwordFocused.value && !showPassword.value && (name === 'duck' || name === 'goose') ? -10 : 0
  return {
    transform: `translate(${offsetX}px, ${offsetY + extra}px) rotate(${rotate}deg)`,
  }
}

function characterStyle(name) {
  const factor = characterFactors[name]
  const follow = bodyFollowFactors[name]
  const lift = (passwordFocused.value && !showPassword.value && name === 'goose' ? -16 : 0) + factor.lift
  return {
    transform: `translate(${pointer.x * 12 * follow.x}px, ${pointer.y * 10 * follow.y + lift}px) rotate(${factor.tilt + pointer.x * factor.rotate * 0.6}deg) scale(${factor.scale})`,
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

onMounted(() => {
  window.addEventListener('pointermove', handlePagePointerMove)
  window.addEventListener('pointerout', handlePagePointerOut)
})

onBeforeUnmount(() => {
  window.removeEventListener('pointermove', handlePagePointerMove)
  window.removeEventListener('pointerout', handlePagePointerOut)
})
</script>
