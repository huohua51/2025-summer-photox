<template>
  <div class="instagram-post">
    <!-- 帖子头部 -->
    <div class="post-header">
      <div class="user-info">
        <div class="avatar-container" @click="goToUserProfile">
          <img 
            :src="post.user.avatar || '/img/userImage.png'" 
            :alt="post.user.username"
            class="user-avatar"
            @error="handleAvatarError"
          />
        </div>
        <div class="user-details">
          <div class="username" @click="goToUserProfile">{{ post.user.username }}</div>
          <div class="post-time">{{ formatTime(post.created_at) }}</div>
        </div>
      </div>
      <div class="follow-btn" v-if="post.user.id !== currentUserId">
        <button 
          @click="toggleFollow" 
          :class="['follow-button', { 'following': post.is_following_author }]"
          :disabled="followLoading"
        >
          {{ followLoading ? '...' : (post.is_following_author ? '已关注' : '关注') }}
        </button>
      </div>
    </div>

    <!-- 图片 -->
    <div class="post-image-container">
      <img 
        :src="post.image_url" 
        :alt="post.title || '用户图片'"
        class="post-image"
        @click="openImageDetail"
        @error="handleImageError"
      />
    </div>

    <!-- 操作按钮 -->
    <div class="post-actions">
      <div class="action-buttons">
        <button 
          @click="toggleLike" 
          :class="['action-btn', 'like-btn', { 'liked': isLiked }]"
          :disabled="likeLoading"
        >
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path 
              :fill="isLiked ? '#2196f3' : 'none'" 
              :stroke="isLiked ? '#2196f3' : 'currentColor'"
              stroke-width="2"
              d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
            />
          </svg>
        </button>
        <button @click="toggleComments" class="action-btn comment-btn">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path 
              fill="none" 
              stroke="currentColor" 
              stroke-width="2"
              d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
            />
          </svg>
        </button>
        <button @click="sharePost" class="action-btn share-btn">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path 
              fill="none" 
              stroke="currentColor" 
              stroke-width="2"
              d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v13"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- 点赞数和基本信息 -->
    <div class="post-info">
      <div class="like-count" v-if="likeCount > 0">
        <strong>{{ likeCount }} 个赞</strong>
      </div>
      <div class="post-content" v-if="post.title">
        <span class="username">{{ post.user.username }}</span>
        <span class="content">{{ post.title }}</span>
      </div>
      <div class="post-tags" v-if="post.tags && post.tags.length > 0">
        <span 
          v-for="tag in post.tags.slice(0, 3)" 
          :key="tag" 
          class="tag"
        >
          #{{ tag }}
        </span>
      </div>
    </div>

    <!-- 评论区 -->
    <div class="comments-section" v-if="showComments">
      <div class="comments-list" v-if="comments.length > 0">
        <div 
          v-for="comment in comments.slice(0, 3)" 
          :key="comment.id" 
          class="comment-item"
        >
          <span class="comment-username">{{ comment.user.username }}</span>
          <span class="comment-content">{{ comment.content }}</span>
        </div>
        <div class="view-all-comments" v-if="totalComments > 3" @click="openImageDetail">
          查看全部 {{ totalComments }} 条评论
        </div>
      </div>
      
      <!-- 添加评论 -->
      <div class="add-comment">
        <input 
          v-model="newComment"
          @keyup.enter="addComment"
          placeholder="添加评论..."
          class="comment-input"
          :disabled="commentLoading"
        />
        <button 
          @click="addComment" 
          :disabled="!newComment.trim() || commentLoading"
          class="comment-submit"
        >
          发布
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import apiService from '@/api'

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const isLiked = ref(props.post.is_liked || false)
const likeCount = ref(props.post.like_count || 0)
const likeLoading = ref(false)
const followLoading = ref(false)
const showComments = ref(false)
const comments = ref([])
const totalComments = ref(0)
const newComment = ref('')
const commentLoading = ref(false)

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

// 切换关注
const toggleFollow = async () => {
  if (followLoading.value) return
  
  followLoading.value = true
  try {
    const response = await apiService.api.post(`/community/follows/${props.post.user.id}/toggle/`)
    props.post.is_following_author = response.following
  } catch (error) {
    console.error('切换关注失败:', error)
  } finally {
    followLoading.value = false
  }
}

// 切换评论显示
const toggleComments = async () => {
  showComments.value = !showComments.value
  if (showComments.value && comments.value.length === 0) {
    await loadComments()
  }
}

// 加载评论
const loadComments = async () => {
  try {
    const response = await apiService.api.get('/community/comments/', {
      params: { image: props.post.id }
    })
    comments.value = response.results || response.data || []
    totalComments.value = response.count || comments.value.length
  } catch (error) {
    console.error('加载评论失败:', error)
  }
}

// 添加评论
const addComment = async () => {
  if (!newComment.value.trim() || commentLoading.value) return
  
  commentLoading.value = true
  try {
    const response = await apiService.api.post('/community/comments/', {
      image: props.post.id,
      content: newComment.value.trim()
    })
    
    comments.value.unshift(response)
    totalComments.value += 1
    newComment.value = ''
  } catch (error) {
    console.error('添加评论失败:', error)
  } finally {
    commentLoading.value = false
  }
}

// 分享帖子
const sharePost = () => {
  if (navigator.share) {
    navigator.share({
      title: props.post.title || '分享图片',
      text: `来自 ${props.post.user.username} 的图片`,
      url: window.location.origin + `/photo/${props.post.id}`
    })
  } else {
    // 复制链接到剪贴板
    const url = window.location.origin + `/photo/${props.post.id}`
    navigator.clipboard.writeText(url).then(() => {
      alert('链接已复制到剪贴板')
    })
  }
}

// 打开图片详情
const openImageDetail = () => {
  router.push(`/photo/${props.post.id}`)
}

// 跳转到用户主页
const goToUserProfile = () => {
  router.push(`/user/${props.post.user.id}`)
}

// 头像加载错误处理
const handleAvatarError = (event) => {
  event.target.src = '/img/userImage.png'
}

// 图片加载错误处理
const handleImageError = (event) => {
  event.target.src = '/img/black-1072366_12801.jpg'
}
</script>

<style scoped>
.instagram-post {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 24px;
  overflow: hidden;
  transition: background-color 0.3s, border-color 0.3s;
}

.post-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-container {
  cursor: pointer;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50% !important;
  object-fit: cover !important;
  object-position: center !important;
  border: 2px solid var(--border-color);
  transition: border-color 0.3s;
}

.user-avatar:hover {
  border-color: var(--primary-color);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.username {
  font-weight: 600;
  color: var(--text-color);
  cursor: pointer;
  transition: color 0.3s;
}

.username:hover {
  color: var(--primary-color);
}

.post-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.follow-button {
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 16px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.follow-button:hover {
  background: var(--primary-color-dark);
}

.follow-button.following {
  background: transparent;
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.follow-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.post-image-container {
  width: 100%;
  max-height: 600px;
  overflow: hidden;
}

.post-image {
  width: 100%;
  height: auto;
  display: block;
  cursor: pointer;
  transition: transform 0.3s;
}

.post-image:hover {
  transform: scale(1.02);
}

.post-actions {
  padding: 16px 16px 8px;
}

.action-buttons {
  display: flex;
  gap: 16px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s;
  color: var(--text-color);
}

.action-btn:hover {
  background: var(--secondary-color);
  transform: scale(1.1);
}

.like-btn.liked {
  color: #2196f3;
}

.post-info {
  padding: 0 16px 16px;
}

.like-count {
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--text-color);
}

.post-content {
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.4;
}

.post-content .username {
  font-weight: 600;
  margin-right: 8px;
}

.post-content .content {
  color: var(--text-color);
}

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.tag {
  color: var(--primary-color);
  font-size: 13px;
  cursor: pointer;
  transition: color 0.3s;
}

.tag:hover {
  color: var(--primary-color-dark);
}

.comments-section {
  border-top: 1px solid var(--border-color);
  padding: 16px;
}

.comments-list {
  margin-bottom: 16px;
}

.comment-item {
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.4;
}

.comment-username {
  font-weight: 600;
  margin-right: 8px;
  color: var(--text-color);
}

.comment-content {
  color: var(--text-color);
}

.view-all-comments {
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  margin-top: 8px;
  transition: color 0.3s;
}

.view-all-comments:hover {
  color: var(--text-color);
}

.add-comment {
  display: flex;
  gap: 12px;
  align-items: center;
}

.comment-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 8px 0;
  background: transparent;
  color: var(--text-color);
  font-size: 14px;
}

.comment-input::placeholder {
  color: var(--text-secondary);
}

.comment-submit {
  background: none;
  border: none;
  color: var(--primary-color);
  font-weight: 600;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.comment-submit:hover:not(:disabled) {
  background: var(--secondary-color);
}

.comment-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .post-actions {
    padding: 12px 16px 8px;
  }
  
  .action-buttons {
    gap: 12px;
  }
  
  .post-info {
    padding: 0 16px 12px;
  }
  
  .comments-section {
    padding: 12px 16px;
  }
}
</style> 