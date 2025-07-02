<template>
  <div class="ai-recommend-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
              <h1 class="page-title">
        AI 智能推荐
      </h1>
        <p class="page-subtitle">基于您的喜好和行为，为您精选的图片</p>
      </div>
      
      <button @click="refreshRecommendations" class="refresh-btn" :disabled="loading">
        <svg class="refresh-icon" :class="{ 'is-spinning': loading }" viewBox="0 0 24 24">
          <path d="M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16" 
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        刷新推荐
      </button>
    </div>

    <!-- 推荐依据 -->
    <div v-if="recommendBasis.categories.length || recommendBasis.tags.length" class="recommend-basis">
      <div class="basis-content">
        <span class="basis-label">推荐依据：</span>
        <div class="basis-items">
          <span v-for="cat in categoryNames" :key="cat" class="basis-tag category-tag">
            📁 {{ cat }}
          </span>
          <span v-for="tag in recommendBasis.tags" :key="tag" class="basis-tag tag-tag">
            🏷️ {{ tag }}
          </span>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && !images.length" class="loading-container">
      <div class="ai-loading">
        <div class="loading-brain">
          <div class="brain-wave"></div>
          <div class="brain-wave"></div>
          <div class="brain-wave"></div>
        </div>
        <p class="loading-text">AI 正在为您挑选图片...</p>
      </div>
    </div>

    <!-- 图片网格 -->
    <div v-else-if="images.length" class="images-grid">
      <div v-for="image in images" :key="image.id" class="image-card">
        <div class="image-wrapper" @click="viewImage(image)">
          <img 
            :src="image.image_url" 
            :alt="image.title || 'Image'"
            class="image-thumb"
            loading="lazy"
          />
          <div class="image-overlay">
            <div class="overlay-content">
              <p class="image-title">{{ image.title || '未命名' }}</p>
              <div class="image-meta">
                <span class="meta-item">
                  <svg class="meta-icon" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                  {{ getCategoryName(image.category_id) }}
                </span>
                <span class="meta-item">
                  <svg class="meta-icon" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                  {{ image.like_count || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 快捷操作 -->
        <div class="card-actions">
          <FavoriteButton :image-id="image.id" />
          <button @click="viewDetails(image)" class="detail-btn">
            查看详情
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">○</div>
      <h3 class="empty-title">暂无推荐</h3>
      <p class="empty-text">多浏览、点赞和收藏图片，AI 会更了解您的喜好</p>
      <router-link to="/explore" class="explore-btn">
        去探索
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import FavoriteButton from '@/components/FavoriteButton.vue'

const router = useRouter()

// 数据
const images = ref([])
const loading = ref(false)
const recommendBasis = ref({
  categories: [],
  tags: []
})

// 类别映射
const categoryMap = {
  0: "风景", 1: "人物肖像", 2: "动物", 3: "交通工具", 4: "食品",
  5: "建筑", 6: "电子产品", 7: "运动器材", 8: "植物花卉", 9: "医疗用品",
  10: "办公用品", 11: "服装鞋帽", 12: "家具家居", 13: "书籍文档", 14: "艺术创作",
  15: "工业设备", 16: "体育赛事", 17: "天文地理", 18: "儿童玩具", 19: "美妆个护",
  20: "军事装备", 21: "宠物用品", 22: "健身器材", 23: "厨房用品", 24: "实验室器材",
  25: "音乐器材", 26: "户外装备", 27: "珠宝首饰", 28: "虚拟场景", 29: "其他"
}

// 计算属性：类别名称
const categoryNames = computed(() => {
  return recommendBasis.value.categories.map(id => categoryMap[id] || '未知')
})

// 获取类别名称
const getCategoryName = (categoryId) => {
  return categoryMap[categoryId] || '未知'
}

// 获取推荐图片
const fetchRecommendations = async () => {
  loading.value = true
  try {
    const response = await api.get('/images/recommendations/')
    images.value = response.data.recommendations || []
    recommendBasis.value = response.data.based_on || { categories: [], tags: [] }
  } catch (error) {
    console.error('获取推荐失败:', error)
  } finally {
    loading.value = false
  }
}

// 刷新推荐
const refreshRecommendations = () => {
  fetchRecommendations()
}

// 查看图片
const viewImage = (image) => {
  router.push(`/photo/${image.id}`)
}

// 查看详情
const viewDetails = (image) => {
  router.push(`/photo/${image.id}`)
}

onMounted(() => {
  fetchRecommendations()
})
</script>

<style scoped>
.ai-recommend-view {
  min-height: 100vh;
  background: #f9fafb;
  padding: 24px;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-icon {
  font-size: 36px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.page-subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #5a67d8;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.refresh-icon {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
}

.refresh-icon.is-spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 推荐依据 */
.recommend-basis {
  margin-bottom: 24px;
  padding: 16px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.basis-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.basis-label {
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
}

.basis-items {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.basis-tag {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.category-tag {
  background: #e0e7ff;
  color: #4338ca;
}

.tag-tag {
  background: #fef3c7;
  color: #92400e;
}

/* 加载状态 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.ai-loading {
  text-align: center;
}

.loading-brain {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  position: relative;
}

.brain-wave {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid #667eea;
  border-radius: 50%;
  opacity: 0;
  animation: brain-pulse 2s ease-out infinite;
}

.brain-wave:nth-child(2) {
  animation-delay: 0.5s;
}

.brain-wave:nth-child(3) {
  animation-delay: 1s;
}

@keyframes brain-pulse {
  0% {
    transform: scale(0.5);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.loading-text {
  font-size: 16px;
  color: #6b7280;
}

/* 图片网格 */
.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.image-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.image-wrapper {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  cursor: pointer;
}

.image-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-wrapper:hover .image-thumb {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 60%, rgba(0, 0, 0, 0.8));
  opacity: 0;
  transition: opacity 0.3s ease;
  display: flex;
  align-items: flex-end;
  padding: 20px;
}

.image-wrapper:hover .image-overlay {
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
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.card-actions {
  padding: 16px;
  display: flex;
  gap: 12px;
}

.detail-btn {
  flex: 1;
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

.detail-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
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

.explore-btn {
  display: inline-block;
  padding: 12px 32px;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.explore-btn:hover {
  background: #5a67d8;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

/* 响应式 */
@media (max-width: 768px) {
  .ai-recommend-view {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .page-title {
    font-size: 24px;
    justify-content: center;
  }
  
  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
  }
}
</style> 