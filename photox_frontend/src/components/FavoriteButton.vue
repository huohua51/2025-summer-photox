<template>
  <button 
    @click="toggleFavorite" 
    class="favorite-btn"
    :class="{ 
      'is-favorited': isFavorited, 
      'is-loading': loading,
      'circle-mode': circleMode 
    }"
    :disabled="loading"
  >
    <transition name="star" mode="out-in">
      <svg 
        v-if="!loading"
        :key="isFavorited ? 'filled' : 'outline'"
        class="star-icon"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path 
          v-if="isFavorited"
          d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
          fill="currentColor"
        />
        <path 
          v-else
          d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          fill="none"
        />
      </svg>
      <div v-else class="loading-spinner"></div>
    </transition>
    <span v-if="!circleMode" class="btn-text">{{ isFavorited ? '已收藏' : '收藏' }}</span>
  </button>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiService from '@/api'

const props = defineProps({
  imageId: {
    type: Number,
    required: true
  },
  circleMode: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['favorited', 'unfavorited'])

const isFavorited = ref(false)
const loading = ref(false)

// 检查收藏状态
const checkFavoriteStatus = async () => {
  try {
    const response = await apiService.api.get(`/community/favorites/${props.imageId}/`)
    isFavorited.value = response.favorited
  } catch (error) {
    console.error('检查收藏状态失败:', error)
    // 如果是404错误，说明没有收藏
    if (error.response?.status === 404) {
      isFavorited.value = false
    }
  }
}

// 切换收藏状态
const toggleFavorite = async () => {
  loading.value = true
  
  try {
    if (isFavorited.value) {
      // 取消收藏
      await apiService.api.delete(`/community/favorites/${props.imageId}/`)
      isFavorited.value = false
      emit('unfavorited')
      showToast('已取消收藏')
    } else {
      // 添加收藏
      await apiService.api.post(`/community/favorites/${props.imageId}/`)
      isFavorited.value = true
      emit('favorited')
      showToast('收藏成功')
    }
  } catch (error) {
    console.error('操作失败:', error)
    showToast('操作失败，请重试')
  } finally {
    loading.value = false
  }
}

// 简单的提示函数
const showToast = (message) => {
  // 这里可以替换为更好的提示组件
  const toast = document.createElement('div')
  toast.className = 'favorite-toast'
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
  checkFavoriteStatus()
})
</script>

<style scoped>
.favorite-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.favorite-btn:hover:not(:disabled) {
  border-color: #ec4899;
  color: #ec4899;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(236, 72, 153, 0.15);
}

.favorite-btn.is-favorited {
  background: #fce7f3;
  border-color: #ec4899;
  color: #ec4899;
}

/* 圆形模式样式 */
.favorite-btn.circle-mode {
  width: 40px;
  height: 40px;
  padding: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  backdrop-filter: blur(10px);
  justify-content: center;
}

.favorite-btn.circle-mode:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.favorite-btn.circle-mode.is-favorited {
  background: rgba(236, 72, 153, 0.9);
  border-color: #ec4899;
  color: white;
}

.favorite-btn.circle-mode.is-favorited:hover:not(:disabled) {
  background: #ec4899;
  border-color: #ec4899;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(236, 72, 153, 0.4);
}

.favorite-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.star-icon {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.favorite-btn:hover:not(:disabled) .star-icon {
  transform: scale(1.1);
}

.favorite-btn:active:not(:disabled) .star-icon {
  transform: scale(0.9);
}

/* 星形动画 */
.star-enter-active,
.star-leave-active {
  transition: all 0.3s ease;
}

.star-enter-from {
  transform: scale(0) rotate(-180deg);
  opacity: 0;
}

.star-leave-to {
  transform: scale(0) rotate(180deg);
  opacity: 0;
}

/* 加载动画 */
.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top-color: #ec4899;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 点击时的涟漪效果 */
.favorite-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(236, 72, 153, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.favorite-btn:active::before {
  width: 100px;
  height: 100px;
}

.btn-text {
  font-weight: 500;
}

/* Toast 样式 */
:global(.favorite-toast) {
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

:global(.favorite-toast.show) {
  transform: translateX(-50%) translateY(0);
  opacity: 1;
}

/* 响应式 */
@media (max-width: 768px) {
  .favorite-btn {
    padding: 8px 16px;
    font-size: 14px;
  }
  
  .star-icon {
    width: 18px;
    height: 18px;
  }
}
</style> 