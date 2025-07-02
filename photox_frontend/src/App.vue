<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'
import Header from "./components/Header.vue"
import { computed, watchEffect } from 'vue'
import { useThemeStore } from './stores/theme'

const route = useRoute()
const themeStore = useThemeStore()

const showNavbar = computed(() => {
  // 首页始终显示导航栏
  if (route.name === 'home') return true
  // 图片详情页面根据 fromHome 参数决定是否显示导航栏
  if (route.name === 'photodetail' && route.query.fromHome) return false
  // 其他页面根据 meta 配置显示
  return route.meta.showNavbar
})

// 监听主题变化并应用到 <html> 根元素
watchEffect(() => {
  const root = document.documentElement
  if (themeStore.isDarkMode) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
})
</script>

<template>
  <div class="body" :class="{ 'with-navbar': showNavbar }">
    <Header v-if="showNavbar"/>
    <RouterView />
  </div>
</template>

<style>
/* 统一定义所有主题变量 */
:root {
  --bg-color: #ffffff;
  --text-color: #333333;
  --primary-color: #1e90ff;
  --secondary-color: #f5f5f5;
  --border-color: #e0e0e0;
  /* 为浅色模式添加卡片背景 */
  --card-info-bg: rgba(240, 240, 240, 0.85); 
}

:root.dark {
  --bg-color: rgb(38, 38, 38);
  --text-color: #e0e0e0;
  --primary-color: #1e90ff;
  --secondary-color: #333333;
  --border-color: #555555;
  /* 为深色模式添加卡片背景 */
  --card-info-bg: rgba(50, 50, 50, 0.85); 
}

body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s, color 0.3s;
}
</style>

<style scoped>
.body {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  overflow-x: hidden;
  /* 禁止水平滚动条 */
  font-size: 1vw;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s, color 0.3s;
}


</style>
