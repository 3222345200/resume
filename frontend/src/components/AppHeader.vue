<template>
  <header class="header">
    <div class="logo">
      <router-link to="/">
        <img src="../assets/logo-new.png" alt="职跃 OfferPilot Logo" />
        <span>职跃 · OfferPilot</span>
      </router-link>
    </div>

    <nav class="nav">
      <ul>
        <li>
          <router-link to="/dashboard" class="nav-item">
            <span class="icon">🏠</span>
            <span>求职总览</span>
          </router-link>
        </li>
        <li>
          <router-link to="/editor" class="nav-item">
            <span class="icon">📄</span>
            <span>我的简历</span>
          </router-link>
        </li>
        <li>
          <router-link to="/applications" class="nav-item">
            <span class="icon">📬</span>
            <span>投递进度</span>
          </router-link>
        </li>
        <li>
          <router-link to="/interviews" class="nav-item">
            <span class="icon">📅</span>
            <span>面试安排</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <div class="user-actions">
      <!-- <div class="username">
        <p>你好，{{ authStore.user?.username || '用户' }}</p>
      </div> -->
      <button class="logout-btn" @click="handleLogout">退出</button>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 0 0 auto;
  padding: 1rem 2rem;
  background: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  min-height: 72px;
}

.logo {
  flex-shrink: 0;
  z-index: 2;
}

.logo a {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #222;
  font-weight: 700;
  font-size: 18px;
}

.logo img {
  height: 40px;
  width: 40px;
  object-fit: contain;
}

.nav {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.nav ul {
  list-style: none;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  padding: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border-radius: 999px;
  text-decoration: none;
  color: #444;
  font-weight: 500;
  font-size: 14px;
  background: #f5f7fb;
  transition: all 0.25s ease;
}

.nav-item:hover {
  background: #eaf2ff;
  color: #1677ff;
  transform: translateY(-1px);
}

.nav-item.router-link-exact-active {
  background: linear-gradient(135deg, #1677ff, #4096ff);
  color: #fff;
  box-shadow: 0 6px 16px rgba(22, 119, 255, 0.22);
}

.icon {
  font-size: 16px;
  line-height: 1;
}

.user-actions {
  margin-left: auto;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  max-width: 160px;
}

.username p {
  margin: 0;
  color: #333;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  padding: 8px 14px;
  border: 1px solid #1677ff;
  background: #fff;
  color: #1677ff;
  border-radius: 999px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.25s ease;
}

.logout-btn:hover {
  background: #1677ff;
  color: #fff;
  box-shadow: 0 4px 10px rgba(22, 119, 255, 0.18);
}

@media (max-width: 1024px) {
  .header {
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 12px;
    padding: 1rem;
  }

  .nav {
    position: static;
    transform: none;
    order: 3;
    width: 100%;
  }

  .nav ul {
    justify-content: center;
    flex-wrap: wrap;
    row-gap: 10px;
  }
}

@media (max-width: 640px) {
  .header {
    gap: 10px;
  }

  .logo {
    min-width: 0;
  }

  .logo a span {
    font-size: 16px;
  }

  .nav {
    width: 100%;
  }

  .nav ul {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }

  .nav li {
    min-width: 0;
  }

  .nav-item {
    width: 100%;
    min-width: 0;
    justify-content: center;
    font-size: 13px;
    padding: 8px 12px;
    white-space: nowrap;
  }

  .username {
    display: none;
  }
}
</style>
