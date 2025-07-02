<template>
  <div class="favorites-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">
        我的收藏
      </h1>
      <p class="page-subtitle">您收藏的所有美好瞬间</p>
    </div>

    <!-- 统计信息 -->
    <div v-if="images.length > 0" class="stats-bar">
      <div class="stat-item">
        <span class="stat-value">{{ images.length }}</span>
        <span class="stat-label">收藏总数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ recentCount }}</span>
        <span class="stat-label">本月新增</span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">加载收藏中...</p>
    </div>

    <!-- 收藏列表 -->
    <div v-else-if="images.length" class="favorites-grid">
      <transition-group name="fade-slide">
        <div v-for="image in images" :key="image.id" class="favorite-card">
          <div class="card-image" @click="viewImage(image)">
            <img 
              :src="image.image_url" 
              :alt="image.title || 'Image'"
              loading="lazy"
            />
            <div class="image-overlay">
              <div class="overlay-info">
                <p class="image-title">{{ image.title || '未命名' }}</p>
                <p class="image-date">{{ formatDate(image.created_at) }}</p>
              </div>
            </div>
          </div>
          
          <div class="card-content">
            <!-- 标签 -->
            <div v-if="getImageTags(image).length" class="card-tags">
              <span 
                v-for="(tag, index) in getImageTags(image).slice(0, 3)" 
                :key="index"
                class="tag"
              >
                {{ tag }}
              </span>
              <span v-if="getImageTags(image).length > 3" class="more-tags">
                +{{ getImageTags(image).length - 3 }}
              </span>
            </div>
            
            <!-- 操作按钮 -->
            <div class="card-actions">
              <button @click="viewDetails(image)" class="action-btn view-btn">
                <svg viewBox="0 0 24 24" class="btn-icon">
                  <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                </svg>
                查看
              </button>
              <button @click="removeFavorite(image)" class="action-btn remove-btn">
                <svg viewBox="0 0 24 24" class="btn-icon">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
                移除
              </button>
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">☆</div>
      <h3 class="empty-title">还没有收藏</h3>
      <p class="empty-text">浏览图片时点击收藏按钮，保存您喜欢的作品</p>
      <router-link to="/" class="browse-btn">
        去浏览图片
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '@/api'

const router = useRouter()

// 数据
const images = ref([])
const loading = ref(false)

// 计算属性
const recentCount = computed(() => {
  const oneMonthAgo = new Date()
  oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1)
  
  return images.value.filter(img => {
    return new Date(img.created_at) > oneMonthAgo
  }).length
})

// 获取收藏列表
const fetchFavorites = async () => {
  loading.value = true
  try {
    console.log('开始获取收藏列表...')
    const response = await apiService.api.get('/community/favorites/')
    console.log('收藏列表完整响应:', response)
    console.log('响应类型:', typeof response)
    console.log('响应键:', Object.keys(response))
    
    // 根据后端返回的数据结构调整
    if (response && response.results) {
      images.value = response.results
      console.log('设置收藏图片列表:', response.results)
    } else if (Array.isArray(response)) {
      images.value = response
      console.log('设置收藏图片列表(数组):', response)
    } else {
      console.warn('意外的响应格式:', response)
      images.value = []
    }
  } catch (error) {
    console.error('获取收藏列表失败:', error)
    console.error('错误详情:', error.response?.data)
  } finally {
    loading.value = false
  }
}

// 移除收藏
const removeFavorite = async (image) => {
  if (!confirm('确定要取消收藏这张图片吗？')) {
    return
  }
  
  try {
    await apiService.api.delete(`/community/favorites/${image.id}/`)
    // 从列表中移除
    const index = images.value.findIndex(img => img.id === image.id)
    if (index > -1) {
      images.value.splice(index, 1)
    }
    showToast('已取消收藏')
  } catch (error) {
    console.error('取消收藏失败:', error)
    showToast('操作失败，请重试')
  }
}

// 查看图片
const viewImage = (image) => {
  router.push(`/photo/${image.id}`)
}

// 查看详情
const viewDetails = (image) => {
  router.push(`/photo/${image.id}`)
}

// 获取图片标签
const getImageTags = (image) => {
  try {
    if (typeof image.tags === 'string') {
      return JSON.parse(image.tags)
    }
    return image.tags || []
  } catch {
    return []
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  
  // 小于1小时
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000))
    return `${minutes} 分钟前`
  }
  
  // 小于24小时
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000))
    return `${hours} 小时前`
  }
  
  // 小于30天
  if (diff < 30 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000))
    return `${days} 天前`
  }
  
  // 其他情况显示日期
  return date.toLocaleDateString('zh-CN')
}

// 简单提示
const showToast = (message) => {
  const toast = document.createElement('div')
  toast.className = 'toast-message'
  toast.textContent = message
  document.body.appendChild(toast)
  
  setTimeout(() => {
    toast.classList.add('show')
  }, 10)
  
  setTimeout(() => {
    toast.classList.remove('show')
    setTimeout(() => {
      document.body.removeChild(toast)
    }, 300)
  }, 2000)
}

onMounted(() => {
  fetchFavorites()
})
</script>

<style scoped>
.favorites-view {
  background: var(--bg-color);
  color: var(--text-color);
  min-height: 100vh;
  transition: background 0.3s, color 0.3s;
  padding: 24px;
}

/* 页面头部 */
.page-header {
  background: var(--secondary-color);
  border-bottom: 1px solid var(--border-color);
  padding: 32px 0 16px 0;
  text-align: center;
}

.page-title {
  color: var(--primary-color);
  font-size: 2.2em;
  margin-bottom: 0.2em;
}

.heart-icon {
  font-size: 40px;
  animation: heartbeat 1.5s ease-in-out infinite;
}

@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.page-subtitle {
  color: var(--text-color);
  opacity: 0.7;
}

/* 统计信息 */
.stats-bar {
  display: flex;
  gap: 32px;
  justify-content: center;
  background: var(--secondary-color);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 0;
}

.stat-item {
  color: var(--text-color);
}

.stat-value {
  color: var(--primary-color);
  font-weight: bold;
  font-size: 1.2em;
}

.stat-label {
  font-size: 14px;
  color: var(--text-color);
}

/* 加载状态 */
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
  border: 4px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  color: var(--text-color);
}

/* 收藏网格 */
.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
  padding: 32px 0;
}

.favorite-card {
  background: var(--secondary-color);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: box-shadow 0.3s, border-color 0.3s, background 0.3s;
}

.favorite-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  border-color: var(--primary-color);
}

.card-image {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  cursor: pointer;
  background: var(--bg-color);
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px 12px 0 0;
}

.image-overlay {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  background: linear-gradient(transparent, var(--secondary-color));
  color: var(--text-color);
  padding: 12px;
  border-radius: 0 0 12px 12px;
}

.overlay-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.image-title {
  font-weight: bold;
  color: var(--text-color);
}

.image-date {
  font-size: 0.9em;
  color: var(--text-color);
  opacity: 0.7;
}

.card-content {
  padding: 16px;
  background: var(--bg-color);
  color: var(--text-color);
}

.card-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.tag {
  background: var(--primary-color);
  color: white;
  border-radius: 8px;
  padding: 2px 8px;
  font-size: 0.9em;
}

.more-tags {
  color: var(--primary-color);
  font-size: 0.9em;
}

.card-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.action-btn {
  background: var(--secondary-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 6px 16px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
}

.action-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.remove-btn {
  color: #e53935;
  border-color: #e53935;
}

.remove-btn:hover {
  background: #e53935;
  color: white;
}

/* 过渡动画 */
.fade-slide-move,
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* 空状态 */
.empty-state {
  text-align: center;
  color: var(--text-color);
  opacity: 0.7;
  font-size: 1.2em;
  margin-top: 40px;
}

.empty-icon {
  font-size: 3em;
  color: var(--primary-color);
  margin-bottom: 12px;
}

.empty-title {
  color: var(--text-color);
  font-weight: bold;
  margin-bottom: 8px;
}

.empty-text {
  color: var(--text-color);
  opacity: 0.7;
}

.browse-btn {
  display: inline-block;
  margin-top: 18px;
  background: var(--primary-color);
  color: white;
  border-radius: 8px;
  padding: 8px 24px;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.2s;
}

.browse-btn:hover {
  background: #176fd4;
}

/* Toast提示 */
:global(.toast-message) {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%) translateY(100px);
  background: #1f2937;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  opacity: 0;
  transition: all 0.3s ease;
  z-index: 9999;
}

:global(.toast-message.show) {
  transform: translateX(-50%) translateY(0);
  opacity: 1;
}

/* 响应式 */
@media (max-width: 768px) {
  .favorites-view {
    padding: 16px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .stats-bar {
    flex-direction: column;
    gap: 24px;
  }
  
  .favorites-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
</style> 