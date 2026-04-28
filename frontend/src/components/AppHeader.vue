<template>
  <header class="app-header">
    <div class="app-header__inner">
      <router-link to="/dashboard" class="brand" aria-label="职跃 OfferPilot 首页">
        <span class="brand-mark">
          <img src="../assets/logo-new.png" alt="职跃 OfferPilot" />
        </span>
        <span class="brand-copy">
          <strong>职跃 OfferPilot</strong>
          <small>整理题库、记录与面试节奏</small>
        </span>
      </router-link>

      <nav class="primary-nav" aria-label="主导航">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="primary-nav__item"
          :class="{ 'is-active': route.path === item.to }"
        >
          <span class="primary-nav__label primary-nav__label--full">{{ item.label }}</span>
          <span class="primary-nav__label primary-nav__label--short">{{ item.shortLabel }}</span>
        </router-link>
      </nav>

      <div class="app-header__actions">
        <button class="logout-btn" type="button" @click="handleLogout">退出登录</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const navItems = [
  { to: '/dashboard', label: '求职总览', shortLabel: '总览' },
  { to: '/editor', label: '简历编辑', shortLabel: '简历' },
  { to: '/applications', label: '投递追踪', shortLabel: '投递' },
  { to: '/interviews', label: '面试安排', shortLabel: '面试' },
]

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0 16px;
  background: rgba(245, 240, 235, 0.7);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(128, 119, 110, 0.08);
}

.app-header__inner {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 20px;
  min-height: 56px;
}

.brand {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2f2b28;
  justify-self: start;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(143, 131, 121, 0.08);
  overflow: hidden;
}

.brand-mark img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.28);
}

.brand-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-copy strong {
  font-size: 0.92rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.brand-copy small {
  color: #746b64;
  font-size: 0.66rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.primary-nav {
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  justify-self: stretch;
  flex-wrap: nowrap;
  overflow-x: auto;
  padding-bottom: 2px;
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.primary-nav::-webkit-scrollbar {
  display: none;
}

.primary-nav__item {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  gap: 6px;
  padding: 6px 11px;
  border-radius: 9px;
  color: #6e645d;
  transition:
    background-color 0.22s ease,
    color 0.22s ease;
}

.primary-nav__item:hover {
  background: rgba(255, 255, 255, 0.52);
  color: #2f2a27;
}

.primary-nav__item.is-active,
.primary-nav__item.router-link-exact-active {
  background: rgba(255, 255, 255, 0.82);
  color: #2d2926;
  box-shadow: inset 0 0 0 1px rgba(128, 118, 109, 0.08);
}

.primary-nav__label {
  display: block;
  font-size: 0.84rem;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
}

.primary-nav__label--short {
  display: none;
}

.app-header__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  justify-self: end;
}

.logout-btn {
  border: 1px solid rgba(129, 118, 108, 0.14);
  border-radius: 9px;
  padding: 7px 11px;
  background: rgba(255, 255, 255, 0.58);
  color: #514942;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    background-color 0.22s ease,
    color 0.22s ease,
    border-color 0.22s ease;
}

.logout-btn:hover {
  background: #fff;
  color: #2f2a27;
  border-color: rgba(129, 118, 108, 0.24);
}

@media (max-width: 1180px) {
  .app-header {
    padding: 0 16px;
  }

  .app-header__inner {
    grid-template-columns: auto minmax(0, 1fr) auto;
    gap: 12px;
    padding: 10px 0;
    min-height: 56px;
  }

  .app-header__actions {
    justify-content: flex-end;
  }
}

@media (max-width: 760px) {
  .app-header {
    padding: 0 10px;
  }

  .app-header__inner {
    grid-template-columns: auto minmax(0, 1fr) auto;
    gap: 8px;
    padding: 8px 0;
  }

  .brand-copy {
    display: none;
  }

  .primary-nav {
    justify-content: flex-start;
    gap: 4px;
  }

  .primary-nav__label--full {
    display: none;
  }

  .primary-nav__label--short {
    display: block;
  }

  .app-header__actions {
    flex-direction: row;
    align-items: center;
    justify-content: flex-end;
  }

  .logout-btn {
    width: auto;
    white-space: nowrap;
  }
}

@media (max-width: 480px) {
  .brand {
    align-items: center;
  }

  .brand-mark {
    width: 28px;
    height: 28px;
  }

  .brand-mark img {
    transform: scale(1.25);
  }

  .primary-nav__item {
    padding: 6px 9px;
  }
}
</style>
