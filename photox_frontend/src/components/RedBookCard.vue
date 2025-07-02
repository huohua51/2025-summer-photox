<template>
  <div class="redbook-card" @click="openDetail">
    <!-- 图片容器 -->
    <div class="image-container">
      <img 
        :src="post.image_url" 
        :alt="post.title || '图片'"
        class="card-image"
        @load="onImageLoad"
        @error="handleImageError"
      />
      
      <!-- 悬停遮罩 -->
      <div class="hover-overlay">
        <div class="interaction-stats">
          <div class="stat-item">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path 
                fill="currentColor" 
                d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
              />
            </svg>
            <span>{{ likeCount }}</span>
          </div>
          <div class="stat-item" v-if="commentCount > 0">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path 
                fill="currentColor" 
                d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
              />
            </svg>
            <span>{{ commentCount }}</span>
          </div>
        </div>
        
        <!-- 操作按钮组 -->
        <div class="action-buttons">
          <!-- 点赞按钮 -->
          <button 
            @click.stop="toggleLike" 
            :class="['like-btn', { 'liked': isLiked }]"
            :disabled="likeLoading"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path 
                :fill="isLiked ? '#2196f3' : 'none'" 
                :stroke="isLiked ? '#2196f3' : 'currentColor'"
                stroke-width="2"
                d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
              />
            </svg>
          </button>
          
          <!-- 收藏按钮 -->
          <FavoriteButton 
            :image-id="post.id" 
            :circle-mode="true"
            @click.stop
            class="favorite-btn-overlay"
          />
        </div>
      </div>
    </div>
    
    <!-- 卡片信息 -->
    <div class="card-info">
      <!-- 标题 -->
      <h3 class="card-title" v-if="post.title">{{ post.title }}</h3>
      
      <!-- 标签 -->
      <div class="tags" v-if="post.tags && post.tags.length > 0">
        <span 
          v-for="tag in post.tags.slice(0, 2)" 
          :key="tag" 
          class="tag"
        >
          #{{ tag }}
        </span>
      </div>
      
      <!-- 用户信息 -->
      <div class="user-info">
        <div class="user-avatar" @click.stop="goToUserProfile">
          <img 
            :src="post.user.avatar || '/img/userImage.png'" 
            :alt="post.user.username"
            @error="handleAvatarError"
          />
        </div>
        <div class="user-details">
          <span class="username" @click.stop="goToUserProfile">{{ post.user.username }}</span>
          <span class="post-time">{{ formatTime(post.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import apiService from '@/api'
import FavoriteButton from '@/components/FavoriteButton.vue'

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['imageLoaded'])

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const isLiked = ref(props.post.is_liked || false)
const likeCount = ref(props.post.like_count || 0)
const likeLoading = ref(false)
const commentCount = ref(0)

// 计算属性
const currentUserId = computed(() => userStore.user?.id)

// 格式化时间
const formatTime = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = now - date // 不使用Math.abs，保持时间方向
  
  // 处理未来时间
  if (diffTime < 0) {
    return date.toLocaleDateString('zh-CN')
  }
  
  const diffMinutes = Math.floor(diffTime / (1000 * 60))
  const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  const diffWeeks = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 7))
  const diffMonths = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 30))
  
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
  } else if (diffMonths < 12) {
    return `${diffMonths}月前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
}

// 图片加载完成
const onImageLoad = (event) => {
  emit('imageLoaded', {
    height: event.target.naturalHeight,
    width: event.target.naturalWidth
  })
}

// 切换点赞
const toggleLike = async () => {
  if (likeLoading.value) return
  
  likeLoading.value = true
  try {
    const response = await apiService.api.post('/community/likes/toggle/', {
      like_type: 'image',
      object_id: props.post.id
    })
    
    isLiked.value = response.liked
    likeCount.value = response.like_count
  } catch (error) {
    console.error('切换点赞失败:', error)
  } finally {
    likeLoading.value = false
  }
}

// 打开详情页
const openDetail = () => {
  router.push(`/photodetail/${props.post.id}?fromHome=true`)
}

// 跳转到用户主页
const goToUserProfile = () => {
  router.push(`/user/${props.post.user.id}`)
}

// 图片加载错误处理
const handleImageError = (event) => {
  event.target.src = '/img/black-1072366_12801.jpg'
}

// 头像加载错误处理
const handleAvatarError = (event) => {
  event.target.src = '/img/userImage.png'
}

// 获取评论数量
const loadCommentCount = async () => {
  try {
    const response = await apiService.api.get('/community/comments/', {
      params: { 
        image: props.post.id,
        page_size: 1  // 只需要获取总数
      }
    })
    commentCount.value = response.count || 0
  } catch (error) {
    console.error('获取评论数量失败:', error)
  }
}

// 组件挂载时加载评论数量
onMounted(() => {
  loadCommentCount()
})
</script>

<style scoped>
.redbook-card {
  background: var(--bg-color);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  break-inside: avoid;
  margin-bottom: 16px;
  display: inline-block;
  width: 100%;
  /* border: solid 1px; */
  /* border-color: var(--text-color); */
}

.redbook-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.image-container {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.3s ease;
}

.redbook-card:hover .card-image {
  transform: scale(1.02);
}

.hover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0) 0%,
    rgba(0, 0, 0, 0.1) 50%,
    rgba(0, 0, 0, 0.3) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 16px;
}

.redbook-card:hover .hover-overlay {
  opacity: 1;
}

.interaction-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.stat-item svg {
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.5));
}

/* 右侧按钮组 */
.hover-overlay {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.hover-overlay > :last-child {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.like-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.like-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.like-btn.liked {
  border-color: #2196f3;
  color: white;
}

.like-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}



.card-info {
  padding: 12px 16px 16px;
  background: var(--card-info-bg);
  /* 支持暗色模式下自动适配 */
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.tag {
  background: rgba(33, 150, 243, 0.1);
  color: #2196f3;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.user-avatar:hover {
  transform: scale(1.1);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-color);
  cursor: pointer;
  transition: color 0.2s ease;
  display: block;
  line-height: 1.2;
}

.username:hover {
  color: #2196f3;
}

.post-time {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.2;
  display: block;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .redbook-card {
    box-shadow: 0 2px 8px rgba(255, 255, 255, 0.05);
  }
  
  .redbook-card:hover {
    box-shadow: 0 8px 24px rgba(255, 255, 255, 0.1);
  }
  
  .tag {
    background: rgba(33, 150, 243, 0.2);
  }
  
  .card-info {
    background: var(--card-info-bg);
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .card-info {
    padding: 10px 12px 12px;
  }
  
  .card-title {
    font-size: 13px;
  }
  
  .hover-overlay {
    padding: 12px;
  }
  
  .like-btn {
    width: 36px;
    height: 36px;
  }
  
  .stat-item {
    font-size: 13px;
  }
}
</style> 