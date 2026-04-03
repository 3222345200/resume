import { defineStore } from 'pinia'
import { clearToken, getToken, requestJson, saveToken } from '../api/request'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getToken(),
    user: null,
    captchaId: '',
    captchaSvg: '',
    verificationId: '',
  }),

  getters: {
    isAuthed: (state) => Boolean(state.token),
  },

  actions: {
    setToken(token) {
      this.token = token || ''
      if (this.token) {
        saveToken(this.token)
      } else {
        clearToken()
      }
    },

    async fetchCurrentUser() {
      if (!this.token) {
        this.user = null
        return null
      }
      try {
        this.user = await requestJson('/api/auth/me')
        return this.user
      } catch (error) {
        if (error.status === 401) {
          this.logout()
        }
        throw error
      }
    },

    async login(payload) {
      const result = await requestJson('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      this.setToken(result.access_token)
      await this.fetchCurrentUser()
    },

    async loadCaptcha() {
      const result = await requestJson('/api/auth/captcha')
      this.captchaId = result.captcha_id
      this.captchaSvg = result.captcha_svg
      this.verificationId = ''
    },

    async sendRegisterCode({ email, captchaAnswer }) {
      const result = await requestJson('/api/auth/send-register-code', {
        method: 'POST',
        body: JSON.stringify({
          email,
          captcha_id: this.captchaId,
          captcha_answer: captchaAnswer,
        }),
      })
      this.verificationId = result.verification_id
      return result.message || '邮箱验证码已发送，请查收'
    },

    async register(payload) {
      const result = await requestJson('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          ...payload,
          verification_id: this.verificationId,
        }),
      })
      this.setToken(result.access_token)
      await this.fetchCurrentUser()
    },

    logout() {
      this.user = null
      this.captchaId = ''
      this.captchaSvg = ''
      this.verificationId = ''
      this.setToken('')
    },
  },
})
