<template>
  <main class="dashboard-page">
    <header class="dashboard-hero-card">
      <div class="dashboard-brand-row">
        <div class="brand-badge">
          <img class="brand-logo" :src="brandMark" alt="职跃 OfferPilot 标志" />
          <span class="brand-name">职跃 OfferPilot</span>
        </div>

        <RouterLink class="ghost-button dashboard-logout" to="/dashboard">返回工作台</RouterLink>
      </div>

      <p class="eyebrow">Applications</p>
      <h1>投递管理</h1>
      <p class="dashboard-subtitle">投递记录、状态流转、渠道筛选和基础统计后续都放在这个页面。</p>
    </header>
  </main>
</template>

<script setup>
import brandMark from '../assets/brand-mark.svg'
</script>
