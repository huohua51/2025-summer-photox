<template>
  <div class="notification-list-page">
    <main class="notification-list-main">
      <div class="header-row">
        <h2 class="page-title">通知列表</h2>
        <button class="btn-mark-all" @click="markAllRead" :disabled="loading || notifications.length===0">全部标为已读</button>
        <span class="unread-count" v-if="unreadCount > 0">未读：{{ unreadCount }}</span>
      </div>
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      <div v-else>
        <div v-if="notifications.length === 0" class="empty-tip">暂无通知。</div>
        <div v-else class="notification-list">
          <div v-for="item in notifications" :key="item.id" :class="['notification-item', {unread: !item.is_read}]">
            <div class="notification-content">
              <span class="type-badge">{{ typeText(item.notification_type) }}</span>
              <span class="content">{{ item.content }}</span>
              <span class="sender" v-if="item.sender">来自：{{ item.sender.username }}</span>
              <span class="created-at">{{ formatTime(item.created_at) }}</span>
            </div>
            <button v-if="!item.is_read" class="btn-mark-read" @click="markRead(item.id)">标为已读</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const notifications = ref([])
const loading = ref(true)
const unreadCount = ref(0)

const fetchNotifications = async () => {
  loading.value = true
  try {
    const res = await api.notification.getList()
    notifications.value = res.results || res.data || []
    await fetchUnreadCount()
  } catch (e) {
    notifications.value = []
  } finally {
    loading.value = false
  }
}

const fetchUnreadCount = async () => {
  try {
    const res = await api.notification.getUnreadCount()
    unreadCount.value = res.unread_count || 0
  } catch {
    unreadCount.value = 0
  }
}

const markAllRead = async () => {
  if (loading.value) return
  await api.notification.markAllRead()
  await fetchNotifications()
}

const markRead = async (id) => {
  await api.notification.markRead(id)
  await fetchNotifications()
}

const typeText = (type) => {
  switch(type) {
    case 'like': return '点赞';
    case 'comment': return '评论';
    case 'follow': return '关注';
    case 'reply': return '回复';
    case 'system': return '系统';
    default: return type;
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  
  const date = new Date(timeStr)
  const now = new Date()
  const diffTime = now - date
  
  // 处理未来时间
  if (diffTime < 0) {
    return date.toLocaleDateString('zh-CN')
  }
  
  const diffMinutes = Math.floor(diffTime / (1000 * 60))
  const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  const diffWeeks = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 7))
  
  if (diffMinutes < 1) {
    return '刚刚'
  } else if (diffMinutes < 60) {
    return `${diffMinutes}分钟前`
  } else if (diffHours < 24) {
    return `${diffHours}小时前`
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else if (diffWeeks < 4) {
    return `${diffWeeks}周前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notification-list-page {
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

.notification-list-main {
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
.header-row {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 24px;
}
.page-title {
  font-size: 1.5em;
  color: var(--primary-color);
  flex: 1;
}
.btn-mark-all {
  background: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 18px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}
.btn-mark-all:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.unread-count {
  color: var(--error-color);
  font-weight: 600;
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
.notification-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.notification-item {
  display: flex;
  align-items: center;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 18px 28px;
  transition: box-shadow 0.2s, border-color 0.2s, background 0.3s;
}
.notification-item.unread {
  border-color: var(--error-color);
  background: #fff3f3;
  color: var(--error-color);
}
.notification-content {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}
.type-badge {
  background: var(--primary-color);
  color: #fff;
  border-radius: 4px;
  padding: 2px 10px;
  font-size: 0.95em;
  font-weight: 600;
}
.content {
  font-size: 1.1em;
  font-weight: 500;
}
.sender {
  color: var(--primary-color);
  font-size: 0.95em;
}
.created-at {
  color: var(--text-color);
  opacity: 0.7;
  font-size: 0.95em;
}
.btn-mark-read {
  background: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 6px 14px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}
.btn-mark-read:hover {
  background: var(--success-color);
}
</style> 