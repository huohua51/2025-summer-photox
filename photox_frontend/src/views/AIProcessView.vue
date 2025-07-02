<template>
  <div class="ai-process-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">
        图片处理
      </h1>
      <p class="page-subtitle">对图片进行风格转换、参数调节和智能优化</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：图片选择和预览 -->
      <div class="image-section">
        <!-- 图片上传/选择区域 -->
        <div class="upload-section">
          <div v-if="!selectedImage" class="upload-area" @click="selectImage">
            <div class="upload-content">
              <svg class="upload-icon" viewBox="0 0 24 24" width="48" height="48">
                <path fill="currentColor" d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
              </svg>
              <h3>选择要处理的图片</h3>
              <p>点击选择图片或从个人仓库中选择</p>
              <button class="select-btn">选择图片</button>
            </div>
          </div>

          <!-- 图片预览区域 -->
          <div v-else class="image-preview">
            <div class="preview-container">
              <img :src="selectedImage.image_url" :alt="selectedImage.title" class="preview-image" />
              <div class="image-info">
                <h3>{{ selectedImage.title || '未命名图片' }}</h3>
                <p class="image-meta" v-if="selectedImage.width && selectedImage.height">
                  
                  {{ selectedImage.width }}x{{ selectedImage.height }}
                </p>
              </div>
              <button @click="changeImage" class="change-btn">更换图片</button>
            </div>
          </div>
        </div>

        <!-- 我的图片库 -->
        <div class="my-images" v-if="userImages.length > 0">
          <h3>我的图片</h3>
          <div class="images-grid">
            <div 
              v-for="image in userImages" 
              :key="image.id"
              @click="selectImageFromLibrary(image)"
              :class="['image-item', { 'selected': selectedImage?.id === image.id }]"
            >
              <img :src="image.image_url" :alt="image.title" />
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：AI处理选项 -->
      <div class="processing-section">
        <div class="processing-tabs">
          <button 
            v-for="tab in processingTabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="['tab-btn', { 'active': activeTab === tab.id }]"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            {{ tab.name }}
          </button>
        </div>

        <!-- 参数调节 -->
        <div v-if="activeTab === 'adjust'" class="tab-content">
          <h3>参数调节</h3>
          <div class="adjustment-controls">
            <div v-for="param in adjustmentParams" :key="param.id" class="control-group">
              <label class="control-label">
                {{ param.name }}
                <span class="control-value">{{ param.value }}</span>
              </label>
              <input 
                type="range" 
                :min="param.min" 
                :max="param.max" 
                :step="param.step"
                v-model="param.value"
                class="control-slider"
              />
            </div>
          </div>
        </div>

        <!-- 智能增强 -->
        <div v-if="activeTab === 'enhance'" class="tab-content">
          <h3>智能增强</h3>
          <div class="enhance-options">
            <div 
              v-for="option in enhanceOptions" 
              :key="option.id"
              @click="toggleEnhanceOption(option.id)"
              :class="['enhance-item', { 'selected': selectedEnhanceOptions.includes(option.id) }]"
            >
              <div class="enhance-icon">{{ option.icon }}</div>
              <div class="enhance-content">
                <h4>{{ option.name }}</h4>
                <p>{{ option.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 处理按钮 -->
        <div class="action-buttons">
          <button 
            @click="processImage" 
            :disabled="!selectedImage || processing"
            class="process-btn"
          >
            <span v-if="processing" class="loading-spinner"></span>
            {{ processing ? '处理中...' : '开始处理' }}
          </button>
          <button @click="resetSettings" class="reset-btn">重置设置</button>
        </div>
      </div>
    </div>

    <!-- 处理结果 -->
    <div v-if="processedImage" class="result-section">
      <div class="result-header">
        <h2>✨ 处理结果</h2>
        <!-- <p style="font-size: 12px; color: #666;">调试信息: {{ processedImage }}</p> -->
      </div>
      <div class="result-comparison">
        <div class="result-item">
          <div class="result-label">
            <span class="label-icon">📷</span>
            <h3>原图</h3>
          </div>
          <div class="image-wrapper">
            <img :src="selectedImage.image_url" alt="原图" />
            <div class="image-overlay">原始</div>
          </div>
        </div>
        <div class="result-arrow">
          <div class="arrow-icon">⚡</div>
          <div class="arrow-text">图片处理</div>
        </div>
        <div class="result-item">
          <div class="result-label">
            <span class="label-icon">🎨</span>
            <h3>处理后</h3>
          </div>
          <div class="image-wrapper">
            <img :src="processedImage" alt="处理后" @error="handleImageError" />
          </div>
          <div class="result-actions">
            <button @click="downloadResult" class="download-btn">
              <span>📥</span>下载图片
            </button>
            <button @click="saveToLibrary" class="save-btn">
              <span>💾</span>保存到仓库
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片选择器模态框 -->
    <div v-if="showImageSelector" class="modal-overlay" @click="showImageSelector = false">
      <div class="image-selector-modal" @click.stop>
        <div class="modal-header">
          <h3>选择图片</h3>
          <button @click="showImageSelector = false" class="close-btn">×</button>
        </div>
        <div class="modal-content">
          <input type="file" @change="handleFileUpload" accept="image/*" class="file-input" />
          <div class="images-list">
            <div 
              v-for="image in userImages" 
              :key="image.id"
              @click="selectImageFromModal(image)"
              class="modal-image-item"
            >
              <img :src="image.image_url" :alt="image.title" />
              <span class="image-title">{{ image.title || '未命名' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, onBeforeUnmount } from 'vue'
import apiService from '@/api'
import imageService from '@/api/imageService'
import { useRouter, useRoute } from 'vue-router'
import { watch } from 'vue'

// 数据
const selectedImage = ref(null)
const userImages = ref([])
const activeTab = ref('adjust')
const selectedEnhanceOptions = ref([])
const processing = ref(false)
const processedImage = ref(null)
const processedFileName = ref(null)
const showImageSelector = ref(false)
const localImageFile = ref(null)

// 处理标签页
const processingTabs = [
  { id: 'adjust', name: '参数调节', icon: '●' },
  { id: 'enhance', name: '智能增强', icon: '●' }
]

// 参数调节
const adjustmentParams = ref([
  { id: 'brightness', name: '亮度', value: 1.0, min: 0.0, max: 2.0, step: 0.01 },
  { id: 'contrast', name: '对比度', value: 1.0, min: 0.0, max: 2.0, step: 0.01 },
  { id: 'saturation', name: '饱和度', value: 1.0, min: 0.0, max: 2.0, step: 0.01 },
  { id: 'hue', name: '色调', value: 0.0, min:0.0, max: 1.0, step: 0.01 },
  { id: 'sharpness', name: '锐化', value: 1.0, min: 0.0, max: 5.0, step: 0.01 },
  { id: 'blur', name: '模糊', value: 0.0, min: 0.0, max: 20.0, step: 0.1 }
])

// 保存初始值用于重置
const initialParams = [
  { id: 'brightness', value: 1.0 },
  { id: 'contrast', value: 1.0 },
  { id: 'saturation', value: 1.0 },
  { id: 'hue', value: 0.0 },
  { id: 'sharpness', value: 1.0 },
  { id: 'blur', value: 0.0 }
]

// 智能增强选项
const enhanceOptions = [
  { id: 'denoise', name: '智能降噪', description: '去除图片中的噪点，提升画质', icon: '○' },
  { id: 'upscale', name: '超分辨率', description: '提升图片分辨率，保持清晰度', icon: '○' },
  { id: 'color-enhance', name: '色彩增强', description: '自动优化色彩饱和度和对比度', icon: '○' }
]

// 获取用户图片
const fetchUserImages = async () => {
  try {
    const response = await apiService.images.getList({ page_size: 50 })
    userImages.value = response.results || []
  } catch (error) {
    console.error('获取用户图片失败:', error)
  }
}

// 选择图片
const selectImage = () => {
  showImageSelector.value = true
}

// 从库中选择图片
const selectImageFromLibrary = (image) => {
  selectedImage.value = image
}

// 从模态框选择图片
const selectImageFromModal = (image) => {
  selectedImage.value = image
  showImageSelector.value = false
}

// 更换图片
const changeImage = () => {
  // 清理本地图片URL
  cleanupLocalImage()
  selectedImage.value = null
  localImageFile.value = null
  processedImage.value = null
  processedFileName.value = null
}

// 文件上传
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      showToast('请选择图片文件')
      return
    }
    
    // 验证文件大小 (限制为10MB)
    if (file.size > 10 * 1024 * 1024) {
      showToast('图片大小不能超过10MB')
      return
    }
    
    localImageFile.value = file
    
    // 创建本地图片URL用于预览
    const imageUrl = URL.createObjectURL(file)
    selectedImage.value = {
      id: 'local',
      title: file.name,
      image_url: imageUrl,
      width: 0,
      height: 0,
      file_size: file.size
    }
    
    // 获取图片尺寸
    const img = new Image()
    img.onload = () => {
      selectedImage.value.width = img.width
      selectedImage.value.height = img.height
    }
    img.src = imageUrl
    
    showImageSelector.value = false
    showToast('图片选择成功')
  }
}

// 切换增强选项
const toggleEnhanceOption = (optionId) => {
  const index = selectedEnhanceOptions.value.indexOf(optionId)
  if (index > -1) {
    selectedEnhanceOptions.value.splice(index, 1)
  } else {
    selectedEnhanceOptions.value.push(optionId)
  }
}

// 处理图片
const processImage = async () => {
  if (!selectedImage.value) return
  processing.value = true
  try {
    let response
    
    if (selectedImage.value.id === 'local') {
      // 处理本地图片
      const formData = new FormData()
      formData.append('image', localImageFile.value)
      
      // 添加参数
      const params = {
        adjustments: adjustmentParams.value.reduce((acc, param) => {
          acc[param.id] = param.value
          return acc
        }, {}),
        enhancements: selectedEnhanceOptions.value
      }
      formData.append('params', JSON.stringify(params))
      
      console.log('发送本地图片处理请求，参数:', params)
      response = await imageService.aiProcessLocal(formData)
      console.log('本地图片处理响应:', response)
    } else {
      // 处理用户库中的图片
      const params = {
        adjustments: adjustmentParams.value.reduce((acc, param) => {
          acc[param.id] = param.value
          return acc
        }, {}),
        enhancements: selectedEnhanceOptions.value
      }
      console.log('发送用户图片处理请求，参数:', params)
      response = await imageService.aiProcess(selectedImage.value.id, params)
      console.log('用户图片处理响应:', response)
    }
    
    console.log('设置处理结果:', {
      processed_image_url: response.processed_image_url,
      file_name: response.file_name
    })
    
    processedImage.value = response.processed_image_url
    processedFileName.value = response.file_name
    showToast('图片处理完成！')
  } catch (error) {
    console.error('图片处理失败:', error)
    showToast('处理失败，请重试')
  } finally {
    processing.value = false
  }
}

// 重置设置
const resetSettings = () => {
  adjustmentParams.value.forEach(param => {
    const initialParam = initialParams.find(ip => ip.id === param.id)
    if (initialParam) {
      param.value = initialParam.value
    }
  })
  selectedEnhanceOptions.value = []
  showToast('设置已重置')
}

// 删除处理后的图片
const deleteProcessedImage = async () => {
  if (!processedFileName.value) return
  try {
    await imageService.deleteProcessedImage({ file_name: processedFileName.value })
    processedImage.value = null
    processedFileName.value = null
  } catch (error) {
    console.error('删除处理图片失败:', error)
  }
}

// 下载后自动删除
const downloadResult = async () => {
  if (processedImage.value) {
    try {
      // 获取图片数据
      const response = await fetch(processedImage.value)
      const blob = await response.blob()
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `processed_${selectedImage.value.title || 'image'}.jpg`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      // 删除处理后的图片
      await deleteProcessedImage()
      showToast('下载完成')
    } catch (error) {
      console.error('下载失败:', error)
      showToast('下载失败，请重试')
    }
  }
}

// 关闭时自动删除
const closeResult = async () => {
  await deleteProcessedImage()
}

// 保存到仓库
const saveToLibrary = async () => {
  if (!processedImage.value) return
  
  try {
    // 获取处理后的图片数据
    const response = await fetch(processedImage.value)
    const blob = await response.blob()
    
    // 创建FormData上传到用户库
    const formData = new FormData()
    formData.append('image', blob, `processed_${selectedImage.value.title || 'image'}.jpg`)
    formData.append('title', `处理后_${selectedImage.value.title || '图片'}`)
    
    // 调用上传API
    const uploadResponse = await apiService.images.upload(formData)
    
    // 删除临时处理图片
    await deleteProcessedImage()
    
    // 刷新用户图片列表
    await fetchUserImages()
    
    showToast('已保存到个人仓库')
  } catch (error) {
    console.error('保存失败:', error)
    showToast('保存失败，请重试')
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

// 提示消息
const showToast = (message) => {
  // 简单的提示实现
  const toast = document.createElement('div')
  toast.className = 'toast-message'
  toast.textContent = message
  document.body.appendChild(toast)
  
  setTimeout(() => toast.classList.add('show'), 10)
  setTimeout(() => {
    toast.classList.remove('show')
    setTimeout(() => document.body.removeChild(toast), 300)
  }, 2000)
}

// 处理图片加载错误
const handleImageError = (event) => {
  console.error('图片加载失败:', event.target.src)
  showToast('处理后图片加载失败')
}

// 清理本地图片URL
const cleanupLocalImage = () => {
  if (selectedImage.value && selectedImage.value.id === 'local' && selectedImage.value.image_url) {
    URL.revokeObjectURL(selectedImage.value.image_url)
  }
}

// 初始化界面状态
const initializeView = () => {
  selectedImage.value = null
  userImages.value = []
  activeTab.value = 'adjust'
  selectedEnhanceOptions.value = []
  processing.value = false
  processedImage.value = null
  processedFileName.value = null
  showImageSelector.value = false
  localImageFile.value = null
  
  // 重置参数到初始值
  adjustmentParams.value.forEach(param => {
    const initialParam = initialParams.find(ip => ip.id === param.id)
    if (initialParam) {
      param.value = initialParam.value
    }
  })
}

// 清理所有资源
const cleanupAll = async () => {
  try {
    // 清理本地图片URL
    cleanupLocalImage()
    
    // 删除处理后的临时图片
    if (processedFileName.value) {
      await deleteProcessedImage()
    }
    
    // 初始化界面状态
    initializeView()
    
    console.log('界面清理完成')
  } catch (error) {
    console.error('清理界面时出错:', error)
  }
}

// 组件卸载时清理
onUnmounted(() => {
  cleanupAll()
})

// 组件即将卸载时也执行清理
onBeforeUnmount(() => {
  cleanupAll()
})

onMounted(() => {
  fetchUserImages()
  
  // 初始化路由监听
  const router = useRouter()
  const route = useRoute()
  
  // 监听路由变化
  watch(() => route.path, (newPath, oldPath) => {
    // 如果从AI处理页面离开到其他页面
    if (oldPath && oldPath.includes('/ai-process') && !newPath.includes('/ai-process')) {
      cleanupAll()
    }
  }, { immediate: false })
  
  // 监听页面卸载事件
  window.addEventListener('beforeunload', () => {
    cleanupAll()
  })
})
</script>

<style scoped>
.ai-process-view {
  min-height: 100vh;
  background: var(--bg-color);
  color: var(--text-color);
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

.ai-icon {
  font-size: 40px;
  animation: rotate 3s ease-in-out infinite;
}

@keyframes rotate {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(10deg); }
}

.page-subtitle {
  color: var(--text-color);
  opacity: 0.7;
  font-size: 18px;
  margin: 0;
}

/* 主要内容 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-bottom: 40px;
  background: var(--bg-color);
  color: var(--text-color);
  transition: background 0.3s, color 0.3s;
}

/* 图片区域 */
.image-section {
  background: var(--secondary-color);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color);
  transition: background 0.3s, border-color 0.3s;
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  background: var(--secondary-color);
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: var(--primary-color);
  background: var(--bg-color);
}

.upload-icon {
  color: #9ca3af;
  margin-bottom: 16px;
}

.upload-content h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color) !important;
  margin: 0 0 8px 0;
}

.upload-content p {
  color: var(--text-color);
  opacity: 0.7;
  margin: 0 0 20px 0;
}

.select-btn {
  padding: 12px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s ease;
}

.select-btn:hover {
  background: #176fd4;
}

/* 图片预览 */
.preview-container {
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}

.image-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 4px 0;
}

.image-meta {
  color: #6b7280;
  font-size: 14px;
  margin: 0 0 16px 0;
}

.change-btn {
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.change-btn:hover {
  background: #176fd4;
}

/* 我的图片 */
.my-images {
  margin-top: 24px;
}

.my-images h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 16px 0;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 12px;
}

.image-item {
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.image-item:hover {
  transform: scale(1.05);
}

.image-item.selected {
  border-color: #667eea;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 处理区域 */
.processing-section {
  background: var(--secondary-color);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color);
  transition: background 0.3s, border-color 0.3s;
}

.processing-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: var(--bg-color);
  padding: 4px;
  border-radius: 12px;
}

.tab-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn.active {
  background: var(--secondary-color);
  color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-icon {
  font-size: 16px;
}

/* 标签内容 */
.tab-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 0 20px 0;
}

/* 参数调节 */
.adjustment-controls {
  space-y: 20px;
}

.control-group {
  margin-bottom: 20px;
}

.control-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 8px;
}

.control-value {
  color: var(--primary-color);
  font-weight: 600;
}

.control-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--border-color);
  outline: none;
  cursor: pointer;
}

.control-slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary-color);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

/* 智能增强 */
.enhance-options {
  space-y: 12px;
}

.enhance-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 12px;
  background: var(--secondary-color);
  color: var(--text-color);
}

.enhance-item:hover {
  border-color: var(--primary-color);
  background: var(--bg-color);
}

.enhance-item.selected {
  border-color: var(--primary-color);
  background: var(--secondary-color);
}

.enhance-icon {
  font-size: 24px;
  width: 40px;
  text-align: center;
}

.enhance-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 0 4px 0;
}

.enhance-content p {
  font-size: 14px;
  color: var(--text-color);
  opacity: 0.7;
  margin: 0;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.process-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.process-btn:hover:not(:disabled) {
  background: #176fd4;
  transform: translateY(-2px);
}

.process-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.reset-btn {
  padding: 16px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reset-btn:hover {
  background: #176fd4;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 处理结果 */
.result-section {
  background: var(--secondary-color);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  color: var(--text-color);
  transition: background 0.3s, color 0.3s;
}

.result-section h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0 0 24px 0;
  text-align: center;
}

.result-comparison {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
}

.result-item {
  text-align: center;
}

.result-item h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 0 16px 0;
}

.result-item img {
  max-width: 300px;
  max-height: 300px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.result-arrow {
  font-size: 32px;
  color: #667eea;
  font-weight: bold;
}

.result-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: center;
}

.download-btn, .save-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.download-btn {
  background: #10b981;
  color: white;
}

.download-btn:hover {
  background: #059669;
}

.save-btn {
  background: #f59e0b;
  color: white;
}

.save-btn:hover {
  background: #d97706;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-selector-modal {
  background: var(--bg-color) !important;
  border-radius: 16px;
  padding: 24px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
}

.file-input {
  width: 90%;
  padding: 12px;
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  margin-bottom: 20px;
  background: var(--secondary-color);
  color: var(--text-color);
  transition: background 0.3s, color 0.3s, border-color 0.3s;
}

.images-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 16px;
}

.modal-image-item {
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s ease, background 0.3s;
  background: var(--secondary-color) !important;
  border-radius: 8px;
}

.modal-image-item:hover {
  transform: scale(1.05);
  background: var(--bg-color) !important;
}

.modal-image-item img {
  width: 100%;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 8px;
}

.image-title {
  font-size: 12px;
  color: var(--text-color);
}

/* Toast */
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
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .result-comparison {
    flex-direction: column;
    gap: 20px;
  }
  
  .result-arrow {
    transform: rotate(90deg);
  }
}

@media (max-width: 768px) {
  .ai-process-view {
    padding: 16px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}

body.dark, :root.dark {
  /* 再次声明变量，确保全局生效 */
}

:root.dark .image-selector-modal .modal-header h3,
body.dark .image-selector-modal .modal-header h3,
.image-selector-modal .modal-header h3 {
  color: #fff !important;
}

.image-selector-modal .modal-header h3 {
  color: var(--text-color);
}
</style> 