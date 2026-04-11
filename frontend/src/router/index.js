import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import ApplicationsView from '../views/ApplicationsView.vue'
import DashboardView from '../views/DashboardView.vue'
import ForgotPasswordView from '../views/ForgotPasswordView.vue'
import LoginView from '../views/LoginView.vue'
import InterviewsView from '../views/InterviewsView.vue'
import RegisterView from '../views/RegisterView.vue'
import EditorView from '../views/EditorView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/applications', component: ApplicationsView, meta: { requiresAuth: true } },
    { path: '/interviews', component: InterviewsView, meta: { requiresAuth: true } },
    { path: '/login', component: LoginView, meta: { guestOnly: true } },
    { path: '/forgot-password', component: ForgotPasswordView, meta: { guestOnly: true } },
    { path: '/register', component: RegisterView, meta: { guestOnly: true } },
    { path: '/editor', component: EditorView, meta: { requiresAuth: true } },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchCurrentUser()
    } catch {
      authStore.logout()
    }
  }

  if (to.meta.requiresAuth && !authStore.isAuthed) {
    return '/login'
  }

  if (to.meta.guestOnly && authStore.isAuthed) {
    return '/dashboard'
  }

  return true
})

export default router
