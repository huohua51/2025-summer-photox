<template>
  <div class="explore-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">探索发现</h1>
      <p class="page-subtitle">发现更多精彩作品</p>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label class="filter-label">排序方式：</label>
        <select v-model="sortBy" @change="fetchImages" class="filter-select">
          <option value="created_at">最新上传</option>
          <option value="like_count">最受欢迎</option>
          <option value="random">随机排序</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label class="filter-label">分类筛选：</label>
        <select v-model="categoryFilter" @change="fetchImages" class="filter-select">
          <option value="">全部分类</option>
          <option v-for="(name, id) in categoryMap" :key="id" :value="id">
            {{ name }}
          </option>
        </select>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载精彩内容...</p>
    </div>

    <!-- 图片网格 -->
    <div v-else-if="images.length" class="images-grid">
      <div v-for="image in images" :key="image.id" class="image-card">
        <div class="card-image" @click="viewImage(image)">
          <img 
            :src="image.image_url" 
            :alt="image.title || 'Image'"
            loading="lazy"
          />
          <div class="image-overlay">
            <div class="overlay-content">
              <p class="image-title">{{ image.title || '未命名' }}</p>
              <div class="image-meta">
                <span class="meta-item">
                  <svg class="meta-icon" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                  {{ image.like_count || 0 }}
                </span>
                <span class="meta-item">
                  <svg class="meta-icon" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                  {{ getCategoryName(image.category_id) }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 图片信息和操作 -->
        <div class="card-content">
          <div class="uploader-info">
            <img :src="image.user?.avatar || '/img/userImage.png'" class="uploader-avatar" />
            <div class="uploader-details">
              <p class="uploader-name">{{ image.user?.username }}</p>
              <p class="upload-time">{{ formatDate(image.created_at) }}</p>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="card-actions">
            <FavoriteButton :image-id="image.id" />
            <button @click="viewImage(image)" class="view-btn">
              <svg viewBox="0 0 24 24" class="btn-icon">
                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5z"/>
              </svg>
              查看详情
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">○</div>
      <h3 class="empty-title">暂无内容</h3>
      <p class="empty-text">还没有公开的图片，快去上传第一张吧！</p>
      <router-link to="/gallery" class="upload-btn">
        去上传
      </router-link>
    </div>

    <!-- 加载更多 -->
    <div v-if="hasMore && !loading" class="load-more">
      <button @click="loadMore" class="load-more-btn" :disabled="loadingMore">
        {{ loadingMore ? '加载中...' : '加载更多' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import FavoriteButton from '@/components/FavoriteButton.vue'

const router = useRouter()

// 数据
const images = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)
const currentPage = ref(1)
const sortBy = ref('created_at')
const categoryFilter = ref('')

// 类别映射
const categoryMap = {
  0: "风景", 1: "人物肖像", 2: "动物", 3: "交通工具", 4: "食品",
  5: "建筑", 6: "电子产品", 7: "运动器材", 8: "植物花卉", 9: "医疗用品",
  10: "办公用品", 11: "服装鞋帽", 12: "家具家居", 13: "书籍文档", 14: "艺术创作",
  15: "工业设备", 16: "体育赛事", 17: "天文地理", 18: "儿童玩具", 19: "美妆个护",
  20: "军事装备", 21: "宠物用品", 22: "健身器材", 23: "厨房用品", 24: "实验室器材",
  25: "音乐器材", 26: "户外装备", 27: "珠宝首饰", 28: "虚拟场景", 29: "其他"
}

// 获取类别名称
const getCategoryName = (categoryId) => {
  return categoryMap[categoryId] || '未知'
}

// 获取图片列表
const fetchImages = async (reset = true) => {
  if (reset) {
    loading.value = true
    currentPage.value = 1
    images.value = []
  } else {
    loadingMore.value = true
  }

  try {
    const params = {
      is_public: true,
      page: currentPage.value,
      page_size: 20
    }

    if (sortBy.value === 'like_count') {
      params.order_by = 'like_count'
    } else if (sortBy.value === 'random') {
      params.order_by = 'random'
    }

    if (categoryFilter.value) {
      params.category_id = categoryFilter.value
    }

    const response = await api.get('/images/', { params })
    
    if (reset) {
      images.value = response.data.results || []
    } else {
      images.value.push(...(response.data.results || []))
    }

    hasMore.value = !!response.data.next
    
  } catch (error) {
    console.error('获取图片失败:', error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// 加载更多
const loadMore = () => {
  if (hasMore.value && !loadingMore.value) {
    currentPage.value++
    fetchImages(false)
  }
}

// 查看图片
const viewImage = (image) => {
  router.push(`/photo/${image.id}`)
}

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000))
    return `${minutes} 分钟前`
  }
  
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000))
    return `${hours} 小时前`
  }
  
  if (diff < 30 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000))
    return `${days} 天前`
  }
  
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchImages()
})
</script>

<style scoped>
.explore-view {
  min-height: 100vh;
  background: #f9fafb;
  padding: 24px;
}

/* 页面头部 */
.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 12px 0;
}

.page-subtitle {
  font-size: 18px;
  color: #6b7280;
  margin: 0;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
}

.filter-select {
  padding: 8px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  color: #6b7280;
}

/* 图片网格 */
.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.image-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-image {
  position: relative;
  aspect-ratio: 4/3;
  overflow: hidden;
  cursor: pointer;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.card-image:hover img {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 50%, rgba(0, 0, 0, 0.7));
  opacity: 0;
  transition: opacity 0.3s ease;
  display: flex;
  align-items: flex-end;
  padding: 20px;
}

.card-image:hover .image-overlay {
  opacity: 1;
}

.overlay-content {
  color: white;
  width: 100%;
}

.image-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.image-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-icon {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.card-content {
  padding: 20px;
}

.uploader-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.uploader-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.uploader-details {
  flex: 1;
}

.uploader-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 2px 0;
}

.upload-time {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.view-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  background: #f3f4f6;
  color: #4b5563;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.btn-icon {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.empty-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.empty-text {
  font-size: 16px;
  color: #6b7280;
  margin: 0 0 32px 0;
}

.upload-btn {
  display: inline-block;
  padding: 12px 32px;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.upload-btn:hover {
  background: #5a67d8;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

/* 加载更多 */
.load-more {
  text-align: center;
  margin-top: 32px;
}

.load-more-btn {
  padding: 12px 32px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.load-more-btn:hover:not(:disabled) {
  background: #5a67d8;
  transform: translateY(-2px);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式 */
@media (max-width: 768px) {
  .explore-view {
    padding: 16px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .filter-bar {
    flex-direction: column;
    gap: 16px;
  }
  
  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }
}
</style> 