<template>
  <div class="follow-list-page">
    <main class="follow-list-main">
      <h2 class="page-title">
        <span :class="{active: tab==='followings'}" @click="tab='followings'">我的关注<span v-if="!loading">（{{ followings.length }}）</span></span>
        <span class="tab-divider">|</span>
        <span :class="{active: tab==='followers'}" @click="tab='followers'">我的粉丝<span v-if="!loading">（{{ followers.length }}）</span></span>
      </h2>
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      <div v-else>
        <div v-if="tab==='followings'">
          <div v-if="followings.length === 0" class="empty-tip">你还没有关注任何人。</div>
          <div v-else class="user-list">
            <div v-for="item in followings" :key="item.id" class="user-card" @click="goToUserProfile(item.following.id)">
              <img :src="item.following.avatar || defaultAvatar" class="avatar" alt="头像" />
              <div class="user-info">
                <div class="username">{{ item.following.username }}</div>
                <div class="email">{{ item.following.email }}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-else>
          <div v-if="followers.length === 0" class="empty-tip">你还没有粉丝。</div>
          <div v-else class="user-list">
            <div v-for="item in followers" :key="item.id" class="user-card" @click="goToUserProfile(item.follower.id)">
              <img :src="item.follower.avatar || defaultAvatar" class="avatar" alt="头像" />
              <div class="user-info">
                <div class="username">{{ item.follower.username }}</div>
                <div class="email">{{ item.follower.email }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const followings = ref([])
const followers = ref([])
const loading = ref(true)
const defaultAvatar = '/img/userImage.png'
const tab = ref('followings')

const getCurrentUserId = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const userObj = JSON.parse(userStr)
      return userObj.id
    } catch {
      return null
    }
  }
  return null
}

const fetchFollowData = async () => {
  loading.value = true
  try {
    const userId = getCurrentUserId()
    if (!userId) throw new Error('未获取到用户ID')
    const [resFollowings, resFollowers] = await Promise.all([
      api.follow.getFollowings(userId),
      api.follow.getFollowers(userId)
    ])
    followings.value = resFollowings.results || resFollowings.data || []
    followers.value = resFollowers.results || resFollowers.data || []
  } catch (e) {
    followings.value = []
    followers.value = []
  } finally {
    loading.value = false
  }
}

const goToUserProfile = (userId) => {
  // 预留跳转到用户主页
  router.push(`/otheruserhome/${userId}`)
//   alert('跳转到用户主页功能开发中...')
}

onMounted(() => {
  fetchFollowData()
})
</script>

<style scoped>
.follow-list-page {
  width: 100%;
  min-height: 100vh;
  background: var(--bg-color);
  color: var(--text-color);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  display: flex;
  flex-direction: column;
  line-height: 1.6;
  transition: background-color 0.3s, color 0.3s;
}

.follow-list-main {
  width: 100%;
  max-width: 900px;
  margin: 40px auto;
  padding: 40px;
  background-color: var(--secondary-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  transition: background-color 0.3s, border-color 0.3s, color 0.3s;
}

.page-title {
  font-size: 1.3em;
  color: var(--primary-color);
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid var(--border-color);
  text-align: left;
  transition: color 0.3s, border-color 0.3s;
  display: flex;
  gap: 18px;
  align-items: center;
}
.page-title span {
  cursor: pointer;
  padding: 0 8px;
  border-radius: 4px;
  font-weight: 600;
  color: var(--primary-color);
  transition: background 0.2s, color 0.2s;
}
.page-title span.active {
  background: var(--primary-color);
  color: #fff;
}
.tab-divider {
  color: var(--border-color);
  font-weight: 400;
  font-size: 1.1em;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-color);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(74, 158, 255, 0.3);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-tip {
  text-align: center;
  color: var(--text-color);
  opacity: 0.7;
  font-size: 1.2em;
  margin-top: 40px;
}

.user-list {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-top: 24px;
}

.user-card {
  display: flex;
  align-items: center;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 18px 28px;
  cursor: pointer;
  min-width: 260px;
  transition: box-shadow 0.2s, border-color 0.2s, background 0.3s;
}
.user-card:hover {
  box-shadow: 0 4px 16px rgba(74, 158, 255, 0.12);
  border-color: var(--primary-color);
  background: var(--secondary-color);
}
.avatar {
  width: 56px !important;
  height: 56px !important;
  border-radius: 50% !important;
  object-fit: cover !important;
  object-position: center !important;
  margin-right: 20px;
  border: 2px solid var(--primary-color) !important;
  overflow: hidden !important;
  display: block !important;
}
.user-info {
  display: flex;
  flex-direction: column;
}
.username {
  font-size: 1.2em;
  font-weight: 600;
  color: var(--text-color);
}
.email {
  color: var(--text-color);
  opacity: 0.7;
  font-size: 0.95em;
}
</style> 