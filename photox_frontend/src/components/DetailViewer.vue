<template>
  <div class="detail-viewer">
    <!-- 返回按钮 -->
    <button v-if="showBackButton" class="back-button" @click="$emit('back')">
      <img src="/svg/return.svg" alt="" style="height: 5vh;">
    </button>

    <!-- 顶部控制栏 -->
    <div class="top-controls">
      <!-- 缩放控制 -->
      <div class="zoom-controls">
        <button class="zoom-button" @click="zoomOut">
          <span class="material-icons">-</span>
        </button>
        <input 
          type="range" 
          v-model="zoomLevel" 
          min="50" 
          max="300" 
          step="10"
          class="zoom-slider"
          @input="handleZoom"
        />
        <span class="zoom-percentage">{{ zoomLevel }}%</span>
        <button class="zoom-button" @click="zoomIn">
          <span class="material-icons">+</span>
        </button>
        <button class="zoom-button reset" @click="resetZoom" title="重置缩放">
          <svg viewBox="0 0 1024 1024" width="20" height="20" fill="currentColor" style="vertical-align:middle;">
            <path d="M524.8 106.666667c-106.666667 0-209.066667 42.666667-285.866667 110.933333l-8.533333-68.266667c0-25.6-21.333333-42.666667-46.933333-38.4-25.6 0-42.666667 21.333333-38.4 46.933334l8.533333 115.2c4.266667 55.466667 51.2 98.133333 106.666667 98.133333h8.533333L384 362.666667c25.6 0 42.666667-21.333333 38.4-46.933334 0-25.6-21.333333-42.666667-46.933333-38.4l-85.333334 4.266667c64-55.466667 145.066667-89.6 230.4-89.6 187.733333 0 341.333333 153.6 341.333334 341.333333s-153.6 341.333333-341.333334 341.333334-341.333333-153.6-341.333333-341.333334c0-25.6-17.066667-42.666667-42.666667-42.666666s-42.666667 17.066666-42.666666 42.666666c0 234.666667 192 426.666667 426.666666 426.666667s426.666667-192 426.666667-426.666667c4.266667-234.666667-187.733333-426.666667-422.4-426.666666z"></path>
          </svg>
        </button>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button class="action-button" @click="onDownload">
          <svg viewBox="0 0 1024 1024" width="20px" height="20px" style="margin-right:6px;vertical-align:middle;">
            <path d="M476.724047 726.89122 476.724047 105.931034C476.724047 86.429678 492.534219 70.62069 512.037041 70.62069 531.539862 70.62069 547.350034 86.429678 547.350034 105.931034L547.350034 717.284052 936.527978 328.135256C950.318557 314.345719 972.677508 314.345719 986.468087 328.135256 1000.258666 341.924811 1000.258666 364.282086 986.468087 378.07164L537.007086 827.498955C528.886996 835.618445 517.796193 838.957056 507.233103 837.514787 496.669996 838.957056 485.579211 835.618445 477.459103 827.498955L27.998102 378.07164C14.207523 364.282086 14.207523 341.924811 27.998102 328.135256 41.788681 314.345719 64.147633 314.345719 77.938211 328.135256L476.724047 726.89122 476.724047 726.89122ZM88.281159 900.413793C68.778319 900.413793 52.968166 916.222782 52.968166 935.724138 52.968166 955.225494 68.778319 971.034483 88.281159 971.034483L935.792922 971.034483C955.295744 971.034483 971.105916 955.225494 971.105916 935.724138 971.105916 916.222782 955.295744 900.413793 935.792922 900.413793L88.281159 900.413793 88.281159 900.413793Z"></path>
          </svg>
          <span class="action-text">下载</span>
        </button>
        <button class="action-button" @click="onSave">
          <svg viewBox="0 0 1024 1024" width="20" height="20" style="margin-right:6px;vertical-align:middle;">
            <path d="M925.248 356.928l-258.176-258.176a64 64 0 0 0-45.248-18.752H144a64 64 0 0 0-64 64v736a64 64 0 0 0 64 64h736a64 64 0 0 0 64-64V402.176a64 64 0 0 0-18.752-45.248zM288 144h192V256H288V144z m448 736H288V736h448v144z m144 0H800V704a32 32 0 0 0-32-32H256a32 32 0 0 0-32 32v176H144v-736H224V288a32 32 0 0 0 32 32h256a32 32 0 0 0 32-32V144h77.824l258.176 258.176V880z"></path>
          </svg>
          <span class="action-text">保存</span>
        </button>
      </div>
    </div>

    <!-- 图片容器 -->
    <div class="image-container">
      <div class="image-wrapper" 
           :style="{ transform: `scale(${zoomLevel / 100}) translate(${translateX}px, ${translateY}px)` }"
           @mousedown="startDrag"
           @mousemove="onDrag"
           @mouseup="stopDrag"
           @mouseleave="stopDrag"
           @wheel.prevent="handleWheel">
        <img
          v-if="currentImage"
          :src="currentImage"
          :alt="'图片详情'"
          class="detail-image"
        />
        <div v-else class="no-image">
          <span class="material-icons">image_not_supported</span>
          <p>图片加载失败</p>
        </div>
      </div>
    </div>

    <!-- 导航按钮 -->
    <div v-if="showNavigation" class="navigation-buttons">
      <button class="nav-button prev" @click="onPrevious">
        <img src="/svg/left.svg" alt="" style="height: 6vh;">
      </button>
      <button class="nav-button next" @click="onNext">
        <img src="/svg/right.svg" alt="" style="height: 6vh;">
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  currentImage: {
    type: String,
    required: true
  },
  showNavigation: {
    type: Boolean,
    default: true
  },
  showBackButton: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['previous', 'next', 'back', 'download', 'save'])

// 缩放相关
const zoomLevel = ref(100)
const isDragging = ref(false)
const startX = ref(0)
const startY = ref(0)
const translateX = ref(0)
const translateY = ref(0)

const zoomIn = () => {
  if (zoomLevel.value < 300) {
    zoomLevel.value = Math.min(300, zoomLevel.value + 10)
  }
}

const zoomOut = () => {
  if (zoomLevel.value > 50) {
    zoomLevel.value = Math.max(50, zoomLevel.value - 10)
  }
}

const handleZoom = (event) => {
  // 确保值在有效范围内
  const value = parseInt(event.target.value)
  zoomLevel.value = Math.min(300, Math.max(50, value))
  // 重置拖动位置
  translateX.value = 0
  translateY.value = 0
}

// 拖动相关
const startDrag = (e) => {
  if (zoomLevel.value <= 100) return
  if (e.button !== 0) return // 只响应鼠标左键
  
  isDragging.value = true
  startX.value = e.clientX
  startY.value = e.clientY
}

const onDrag = (e) => {
  if (!isDragging.value || zoomLevel.value <= 100) return

  // 计算鼠标移动的距离
  const deltaX = e.clientX - startX.value
  const deltaY = e.clientY - startY.value

  // 获取图片容器的尺寸
  const container = e.currentTarget.parentElement
  const containerRect = container.getBoundingClientRect()
  const imageRect = e.currentTarget.getBoundingClientRect()

  // 计算缩放后的图片尺寸
  const scaledWidth = imageRect.width
  const scaledHeight = imageRect.height

  // 计算可移动的范围
  const maxX = Math.max(0, (scaledWidth - containerRect.width) / 2)
  const maxY = Math.max(0, (scaledHeight - containerRect.height) / 2)

  // 更新位置
  translateX.value = Math.max(-maxX, Math.min(maxX, translateX.value + deltaX))
  translateY.value = Math.max(-maxY, Math.min(maxY, translateY.value + deltaY))

  // 更新起始点
  startX.value = e.clientX
  startY.value = e.clientY
}

const stopDrag = () => {
  isDragging.value = false
}

const onPrevious = () => {
  console.log('Previous button clicked')
  resetImageState()
  emit('previous')
}

const onNext = () => {
  console.log('Next button clicked')
  resetImageState()
  emit('next')
}

const onBack = () => emit('back')
const onDownload = () => emit('download')
const onSave = () => emit('save')

// 滚轮缩放处理
const handleWheel = (e) => {
  // 获取鼠标在图片上的位置
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  // 根据滚轮方向调整缩放级别
  if (e.deltaY < 0) {
    // 向上滚动，放大
    if (zoomLevel.value < 300) {
      zoomLevel.value = Math.min(300, zoomLevel.value + 10)
    }
  } else {
    // 向下滚动，缩小
    if (zoomLevel.value > 50) {
      zoomLevel.value = Math.max(50, zoomLevel.value - 10)
    }
  }
}

// 重置缩放
const resetZoom = () => {
  zoomLevel.value = 100
  translateX.value = 0
  translateY.value = 0
}

// 重置图片状态
const resetImageState = () => {
  zoomLevel.value = 100
  translateX.value = 0
  translateY.value = 0
  isDragging.value = false
}
</script>

<style scoped>
.detail-viewer {
  background: var(--card-color);
  border-radius: 24px;
  box-shadow: 0 8px 32px var(--shadow-color);
  padding: 0;
  position: relative;
  min-height: 60vh;
  height: 100%;
  display: flex;
  flex-direction: column;
  width: 90%;
}

.back-button {
  position: absolute;
  top: 0;
  left: 0;
  background: rgba(0, 0, 0, 0);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: background-color 0.3s;
  z-index: 10;
  img{
    transition: 0.2s;
  }
}

.back-button:hover img{
  scale: 1.2;
}

.top-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 80%;
  margin-bottom: 8px;
  padding-top: 4px;
  z-index: 9;
}

.zoom-controls, .action-buttons {
  margin-left: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.zoom-button, .action-button {
  background: var(--primary-gradient);
  color: var(--button-text-color);
  border: none;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px var(--shadow-color);
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.zoom-button:hover, .action-button:hover {
  background: var(--primary-gradient-reverse);
  transform: scale(1.08);
  box-shadow: 0 4px 16px var(--shadow-color-hover);
}

.zoom-slider {
  width: 120px;
  accent-color: var(--primary-color);
  height: 6px;
  border-radius: 6px;
  background: var(--primary-gradient);
  box-shadow: 0 2px 8px var(--shadow-color);
}

.zoom-percentage {
  font-size: 1rem;
  color: var(--primary-color);
  font-weight: 600;
  margin: 0 8px;
}

.image-container {
  flex: 1 1 0;
  min-height: 0;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-gradient);
  border-radius: 24px;
  box-shadow: 0 4px 32px var(--shadow-color);
  margin: 0;
  width: 100%;
  height: 100%;
  transition: background 0.3s;
}

.image-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
  transform-origin: center center;
  position: relative;
  cursor: move;
}

.detail-image {
  border-radius: 20px;
  box-shadow: 0 2px 12px var(--shadow-color);
  max-width: 98%;
  max-height: 80vh;
  width: auto;
  height: auto;
  object-fit: contain;
  background: var(--card-color);
  margin: 0 auto;
  display: block;
  transition: transform 0.3s, box-shadow 0.3s;
}

.detail-image:hover {
  transform: scale(1.02);
  box-shadow: 0 6px 24px var(--shadow-color-hover);
}

.no-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 1.2em;
}

.no-image .material-icons {
  font-size: 48px;
}

.navigation-buttons {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}

.nav-button {
  pointer-events: auto;
  background: var(--primary-gradient);
  color: var(--button-text-color);
  border: none;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px var(--shadow-color-hover);
  cursor: pointer;
  font-size: 2rem;
  transition: all 0.2s;
}

.nav-button:hover {
  background: var(--primary-gradient-reverse);
  transform: scale(1.10);
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.action-button {
  /* background: rgba(0, 0, 0, 0.436); */
  border: none;
  border-radius: 8px;
  /* padding: 8px 16px; */
  margin: 0 10px;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.action-button:hover {
  background: rgba(0, 0, 0, 0.431);
}

.action-button .material-icons {
  font-size: 1.1rem;
  font-weight: bold;
}

.zoom-button.reset {
  margin-left: 8px;
  padding: 4px;
  border-radius: 50%;
}

.zoom-button.reset:hover {
  background: rgba(255, 255, 255, 0.2);
}

.action-text {
  display: inline;
  writing-mode: horizontal-tb;
  white-space: nowrap;
  font-size: 1rem;
  letter-spacing: 0.05em;
  color: var(--button-text-color);
}

.action-button svg {
  color: var(--button-text-color) !important;
  fill: currentColor !important;
  stroke: currentColor !important;
  width: 20px !important;
  height: 20px !important;
  min-width: 20px;
  min-height: 20px;
  vertical-align: middle;
  transition: color 0.3s;
}

@media (max-width: 900px) {
  .detail-viewer {
    border-radius: 0;
    padding: 0;
    min-height: 40vh;
  }
  .image-container {
    border-radius: 0;
    max-width: 100vw;
    max-height: 40vh;
    min-height: 200px;
  }
  .detail-image {
    border-radius: 0;
    max-height: 38vh;
  }
}
</style> 