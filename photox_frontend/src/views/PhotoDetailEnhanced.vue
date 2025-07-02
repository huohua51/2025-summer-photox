<template>
  <div class="photo-detail-enhanced">
    <div class="detail-container">
      <!-- 左侧：图片展示 -->
      <div class="image-section">
        <img :src="image.image_url" :alt="image.title" class="main-image" />
      </div>

      <!-- 右侧：信息面板 -->
      <div class="info-section">
        <!-- 图片基本信息 -->
        <div class="image-header">
          <h1 class="image-title">{{ image.title || '未命名作品' }}</h1>
          <div class="image-actions">
            <FavoriteButton :image-id="imageId" />
            <button class="share-btn">
              <svg viewBox="0 0 24 24" class="btn-icon">
                <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/>
              </svg>
              分享
            </button>
          </div>
        </div>

        <!-- 上传者信息 -->
        <div class="uploader-info">
          <img :src="image.user?.avatar || '/img/userImage.png'" class="uploader-avatar" />
          <div class="uploader-details">
            <p class="uploader-name">{{ image.user?.username }}</p>
            <p class="upload-time">{{ formatDate(image.created_at) }}</p>
          </div>
        </div>

        <!-- AI分析面板 -->
        <AIAnalysisPanel 
          :image-id="imageId"
          :colors="image.colors"
        />

        <!-- 标签编辑器 -->
        <TagEditor 
          :image-id="imageId"
          :can-edit="isOwner"
          @tags-updated="handleTagsUpdate"
        />

        <!-- 图片描述 -->
        <div v-if="image.ai_description" class="description-section">
          <h3 class="section-title">图片描述</h3>
          <p class="description-text">{{ image.ai_description }}</p>
        </div>

        <!-- 评论区 -->
        <CommentSection 
          :image-id="imageId"
          class="comment-section"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/api'
import AIAnalysisPanel from '@/components/AIAnalysisPanel.vue'
import TagEditor from '@/components/TagEditor.vue'
import FavoriteButton from '@/components/FavoriteButton.vue'
import CommentSection from '@/components/CommentSection.vue'

const route = useRoute()
const userStore = useUserStore()

const imageId = computed(() => Number(route.params.id))
const image = ref({})
const isOwner = computed(() => image.value.user?.id === userStore.user?.id)

// 获取图片详情
const fetchImageDetail = async () => {
  try {
    const response = await api.get(`/images/${imageId.value}/`)
    image.value = response.data
  } catch (error) {
    console.error('获取图片详情失败:', error)
  }
}

// 处理标签更新
const handleTagsUpdate = (tags) => {
  console.log('标签已更新:', tags)
}

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  fetchImageDetail()
})
</script>

<style scoped>
.photo-detail-enhanced {
  min-height: 100vh;
  background: #f9fafb;
  padding: 24px;
}

.detail-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 480px;
  gap: 32px;
}

/* 图片展示区 */
.image-section {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.main-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  max-height: 80vh;
}

/* 信息面板 */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-height: 80vh;
  overflow-y: auto;
  padding-right: 8px;
}

.info-section::-webkit-scrollbar {
  width: 6px;
}

.info-section::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.info-section::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.info-section::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 图片头部信息 */
.image-header {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.image-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 16px 0;
}

.image-actions {
  display: flex;
  gap: 12px;
}

.share-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #f3f4f6;
  color: #4b5563;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.share-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
  transform: translateY(-2px);
}

.btn-icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

/* 上传者信息 */
.uploader-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.uploader-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.uploader-details {
  flex: 1;
}

.uploader-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 4px 0;
}

.upload-time {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* 描述区域 */
.description-section {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px 0;
}

.description-text {
  font-size: 15px;
  line-height: 1.6;
  color: #4b5563;
  margin: 0;
}

/* 评论区 */
.comment-section {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  padding: 24px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .detail-container {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .info-section {
    max-height: none;
  }
}

@media (max-width: 768px) {
  .photo-detail-enhanced {
    padding: 16px;
  }
  
  .image-title {
    font-size: 20px;
  }
  
  .image-actions {
    flex-direction: column;
  }
  
  .share-btn {
    width: 100%;
  }
}
</style> 