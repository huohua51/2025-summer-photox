<template>
    <nav class="navbar">
        <div class="nav-container">
            <!-- 网站Logo -->
            <router-link to="/" class="brand">
                <img src="/svg/logo.svg" alt="Logo" class="logo">
                <span>PhotoX</span>
            </router-link>

            <!-- 导航菜单 -->
            <div class="nav-menu">
                <router-link to="/" class="nav-item">首页</router-link>
                <router-link to="/gallery" class="nav-item">个人仓库</router-link>
                <router-link v-if="isLoggedIn" to="/ai-process" class="nav-item">
                    AI处理图片
                </router-link>
                <router-link v-if="isLoggedIn" to="/favorites" class="nav-item">
                    收藏
                </router-link>
                
                <!-- 主题切换按钮 -->
                <button @click="toggleTheme" class="theme-toggle" :title="themeStore.isDarkMode ? '切换到亮色模式' : '切换到暗色模式'">
                    <svg v-if="themeStore.isDarkMode" class="theme-icon" viewBox="0 0 24 24">
                        <path fill="currentColor" d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41.39.39 1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41.39.39 1.03.39 1.41 0l1.06-1.06z"/>
                    </svg>
                    <svg v-else class="theme-icon" viewBox="0 0 24 24">
                        <path fill="currentColor" d="M9.37 5.51c-.18.64-.27 1.31-.27 1.99 0 4.08 3.32 7.4 7.4 7.4.68 0 1.35-.09 1.99-.27C17.45 17.19 14.93 19 12 19c-3.86 0-7-3.14-7-7 0-2.93 1.81-5.45 4.37-6.49zM12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/>
                    </svg>
                </button>

                <div class="user-controls">
                    <!-- 未登录状态 -->
                    <div v-if="!isLoggedIn" class="auth-buttons">
                        <button @click="openLogin" class="auth-btn login">登录</button>
                        <button @click="openRegister" class="auth-btn register">注册</button>
                    </div>

                    <!-- 已登录状态 -->
                    <div v-else class="user-menu-wrapper" @mouseenter="showMenu = true" @mouseleave="showMenu = false">
                        <div class="user-avatar">
                            <img :src="user.avatar || defaultAvatar" alt="用户头像" @error="handleAvatarError">
                        </div>

                        <!-- 下拉菜单 -->
                        <transition name="slide-fade">
                            <div v-show="showMenu" class="user-menu">
                                <div class="user-info">
                                    <p class="username">{{ user.name }}</p>
                                    <p class="email">{{ user.email }}</p>
                                </div>
                                <div class="menu-items">
                                    <router-link to="/profile" class="menu-item">
                                        <img src="/svg/usericon.svg" class="icon" /> 个人中心
                                    </router-link>
                                    <router-link to="/followings" class="menu-item">
                                        <img src="/svg/usericon.svg" class="icon" /> 关注列表
                                    </router-link>
                                    <router-link to="/notifications" class="menu-item">
                                        <img src="/svg/usericon.svg" class="icon" /> 通知列表
                                    </router-link>
                                    <!-- <router-link to="/settings" class="menu-item">
                                        <settings-icon class="icon" /> 账户设置
                                    </router-link> -->
                                    <router-link to="#" @click="logout" class="menu-item logout">
                                        <img src="/svg/logouticon.svg" class="icon" /> 退出登录
                                    </router-link>
                                </div>
                            </div>
                        </transition>
                    </div>
                </div>
            </div>

            <!-- 用户控制区 -->

        </div>
    </nav>
</template>
  
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '../stores/theme'
import { useUserStore } from '../stores/user'
import api from '../api'
//   import UserIcon from '../../public/svg/usericon.svg'
//   import SettingsIcon from '@/assets/icons/settings.svg'
//   import LogoutIcon from '../../public/svg/logouticon.svg'
//   import defaultAvatar from '../../public/img/userImage.png'

const router = useRouter()
const themeStore = useThemeStore()
const userStore = useUserStore()
const showMenu = ref(false)
const defaultAvatar = '/img/userImage.png'

// 获取完整的头像URL
const getFullAvatarUrl = (avatarPath) => {
  if (!avatarPath) return defaultAvatar;
  if (avatarPath.startsWith('http')) return avatarPath;
  return `http://127.0.0.1:8000${avatarPath}`;
};

// 从 store 中获取用户数据和登录状态
const isLoggedIn = computed(() => userStore.isLoggedIn)
const user = computed(() => ({
    name: userStore.user?.username || userStore.user?.nickname || '',
    email: userStore.user?.email || '',
    avatar: getFullAvatarUrl(userStore.user?.avatar)
}))

onMounted(() => {
    // 初始化用户状态
    userStore.initialize()
})

// 头像加载失败处理
const handleAvatarError = (e) => {
    e.target.src = defaultAvatar
}

// 打开登录模态框
const openLogin = () => {
    router.push('/login')
}

// 打开注册页面
const openRegister = () => {
    router.push('/register')
}

// 退出登录
const logout = () => {
    userStore.logout()
    router.push('/login')
}

// 切换主题
const toggleTheme = () => {
    themeStore.toggleTheme()
}
</script>
  
<style scoped>
.navbar {
    background: var(--bg-color);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    width: 100%;
    top: 0;
    z-index: 1000;
    transition: background-color 0.3s;
}

.nav-container {
    max-width: 1440px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 10vh;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--text-color);
    text-decoration: none;
    font-size: 1.5rem;
    font-weight: 600;
    margin-left: 20px;
    transition: color 0.3s ease;
}

.logo {
    height: 40px;
    width: auto;
}

.nav-menu {
    display: flex;
    gap: 2rem;
    margin-right: 3vw;
}

.nav-item {
    color: var(--text-color);
    font-weight: bold;
    text-decoration: none;
    font-size: 1.1rem;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 6px;
}

.nav-icon {
    font-size: 1.2rem;
}

.nav-item:hover {
    background: var(--primary-color);
    color: white;
    opacity: 1;
}

.router-link-active {
    color: var(--primary-color);
    font-weight: 500;
}

.auth-buttons {
    display: flex;
    gap: 1rem;
}

.auth-btn {
    padding: 0.6rem 1.5rem;
    border-radius: 20px;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
}

.login {
    background: var(--primary-color);
    color: var(--text-color);
}

.register {
    background: var(--secondary-color);
    color: var(--text-color);
    border: 1px solid var(--border-color);
}

.user-menu-wrapper {
    position: relative;
}

.user-avatar {
    width: 45px !important;
    height: 45px !important;
    border-radius: 50% !important;
    overflow: hidden !important;
    cursor: pointer;
    border: 2px solid #176fd4 !important;
    display: block !important;
}

.user-avatar img {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    object-position: center !important;
    border-radius: 50% !important;
    display: block !important;
}

.user-menu {
    position: absolute;
    right: 0;
    top: 55px;
    background: var(--secondary-color);
    border-radius: 8px;
    width: 240px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    padding: 1rem;
    z-index: 100;
    border: 1px solid var(--border-color);
    transition: all 0.3s ease;
}

.user-info {
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
}

.username {
    color: var(--text-color);
    font-weight: 600;
    margin-bottom: 0.3rem;
}

.email {
    color: var(--text-color);
    opacity: 0.7;
    font-size: 0.9rem;
}

.menu-items {
    padding-top: 0.8rem;
}

.menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.8rem;
    font-weight: bold;
    color: var(--text-color);
    text-decoration: none;
    border-radius: 6px;
    transition: all 0.3s ease;
}

.menu-item:hover {
    background: var(--primary-color);
    color: white;
}

.logout {
    color: var(--error-color);
}

.logout:hover {
    background: var(--primary-color);
    color: white;
}

.icon {
    width: 18px;
    height: 18px;
    fill: currentColor;
    filter: brightness(0.6);
    transition: filter 0.3s ease;
}

.menu-item:hover .icon {
    filter: brightness(1);
}

/* 过渡动画 */
.slide-fade-enter-active {
    transition: all 0.2s ease-out;
}

.slide-fade-leave-active {
    transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
    transform: translateY(-10px);
    opacity: 0;
}

@media (max-width: 768px) {
    .nav-menu {
        display: none;
    }

    .brand span {
        display: none;
    }
}

.theme-toggle {
    background: none;
    border: none;
    color: var(--text-color);
    cursor: pointer;
    padding: 8px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.3s;
}

.theme-toggle:hover {
    background-color: var(--secondary-color);
}

.theme-icon {
    width: 24px;
    height: 24px;
}
</style>