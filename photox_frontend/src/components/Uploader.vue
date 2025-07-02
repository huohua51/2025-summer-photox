<template>
  <div class="uploader">
    <!-- 上传触发区域 -->
    <div class="upload-trigger" @click="triggerFileInput" @dragover.prevent="onDragOver" @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop" :class="{ 'drag-hover': isDragHovering }">
      <slot name="trigger">
        <div class="default-trigger">
          <UploadIcon />
        </div>
      </slot>
    </div>

    <!-- 隐藏的input -->
    <input ref="fileInput" type="file" multiple accept="image/*" @change="handleFileInput" style="display: none">

    <!-- 上传对话框 -->
    <transition name="fade">
      <div v-if="showDialog" class="upload-dialog">
        <div class="dialog-content">
          <h3>上传设置 ({{ files.length }}个文件)</h3>

          <!-- 文件列表 -->
          <div class="file-list" v-if="files.length > 0">
            <div class="file-item" v-for="(file, index) in files" :key="index">
              <div class="file-info">
                <span class="file-index">{{ index + 1 }}.</span>
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
              </div>
              <div class="file-title-input">
                <span class="file-title-label">标题</span>
                <input 
                  v-model="fileTitles[index]" 
                  :placeholder="`输入标题 (默认: ${file.name})`" 
                  class="title-input-field"
                >
              </div>
            </div>
          </div>

          <div class="upload-options">
            <!-- 是否公开选项 -->
            <div class="option-group">
              <label>是否公开</label>
              <div class="toggle-switch">
                <input type="checkbox" v-model="isPublic" id="public-toggle">
                <label for="public-toggle" class="toggle-label"></label>
                <span class="toggle-text">{{ isPublic ? '公开' : '私有' }}</span>
              </div>
            </div>
          </div>

          <div class="progress-section" v-if="isUploading">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
              <span class="progress-text">{{ Math.round(progress) }}%</span>
            </div>
            <div class="upload-status">
              正在上传 {{ files.length }} 个文件...
            </div>
          </div>

          <div class="dialog-actions">
            <button @click="cancelUpload" class="cancel-btn">取消</button>
            <button @click="startUpload" :disabled="isUploading" class="upload-btn">
              {{ isUploading ? '上传中...' : '开始上传' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>
  
<script setup>
import { ref, computed } from 'vue'
import UploadIcon from './UploadIcon.vue'
import axios from 'axios'
import imageService from '../api/imageService'

const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  maxSize: {
    type: Number,
    default: 5 // 单位MB
  },
  token: {
    type: String,
    default: ''
  }
})

const emit = defineEmits([
  'upload-start',
  'upload-progress',
  'upload-success',
  'upload-error',
  'category-created'
])

const fileInput = ref(null)
const showDialog = ref(false)
const files = ref([])
const isPublic = ref(false)
const isUploading = ref(false)
const isDragHovering = ref(false)
const progress = ref(0)
const fileTitles = ref([])

// 拖入时高亮提示
const onDragOver = () => {
  isDragHovering.value = true
}

// 拖离时移除高亮
const onDragLeave = () => {
  isDragHovering.value = false
}

// 拖拽释放时处理文件
const onDrop = async (e) => {
  isDragHovering.value = false
  const droppedFiles = Array.from(e.dataTransfer.files)
  handleFiles(droppedFiles)
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value.click()
}

// 处理文件选择
const handleFileInput = (e) => {
  const inputFiles = Array.from(e.target.files)
  handleFiles(inputFiles)
}

// 抽离为通用文件处理方法
const handleFiles = async (rawFiles) => {
  if (!rawFiles.length) return

  const validFiles = []
  for (const file of rawFiles) {
    if (file.size > props.maxSize * 1024 * 1024) {
      emit('upload-error', {
        file,
        error: `文件大小超过${props.maxSize}MB限制`
      })
      continue
    }
    if (!file.type.startsWith('image/')) {
      emit('upload-error', {
        file,
        error: '仅支持图片文件'
      })
      continue
    }
    validFiles.push(file)
  }

  if (validFiles.length) {
    files.value = validFiles
    // 为每个文件初始化标题，默认使用原文件名
    fileTitles.value = validFiles.map(file => file.name)
    showDialog.value = true
  }
}

// 开始上传
const startUpload = async () => {
  isUploading.value = true
  progress.value = 0
  emit('upload-start', {
    files: files.value
  })

  try {
    // 准备每个文件的标题
    const filesWithTitles = files.value.map((file, index) => ({
      file,
      title: fileTitles.value[index] || file.name
    }))

    // 使用批量上传API
    const result = await imageService.uploadImagesWithTitles(filesWithTitles, {
      is_public: isPublic.value,
      onProgress: (percent) => {
        progress.value = percent
        emit('upload-progress', {
          progress: percent,
          currentFile: null,
          totalFiles: files.value.length
        })
      }
    })

    // 处理批量上传结果
    if (result.success > 0) {
      emit('upload-success', result.results)
    }
    
    if (result.failed > 0) {
      emit('upload-error', {
        message: `部分文件上传失败`,
        errors: result.errors
      })
    }

    // 显示上传结果
    console.log('批量上传完成:', result)
    
  } catch (error) {
    emit('upload-error', error)
  } finally {
    resetState()
  }
}

// 重置状态
const resetState = () => {
    isUploading.value = false
    progress.value = 0
    files.value = []
    showDialog.value = false
    isPublic.value = false
    fileTitles.value = []
}

// 取消上传
const cancelUpload = () => {
  resetState()
  emit('upload-error', '用户取消上传')
}

// 文件大小格式化
const formatFileSize = (bytes) => {
  const units = ['B', 'KB', 'MB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

// 监听新分类输入
const handleNewCategoryInput = (event) => {
  newCategory.value = event.target.value
  selectedCategory.value = '' // 清空已选分类
  console.log('新分类输入:', newCategory.value)
}

// 监听分类选择
const handleCategorySelect = (event) => {
  selectedCategory.value = event.target.value
  newCategory.value = '' // 清空新分类输入
  console.log('选择分类:', selectedCategory.value)
}
</script>
  
<style scoped>
.uploader {
  width: 100%;
  height: 200px;
  position: relative;
  transition: all 0.3s ease;
}

.upload-trigger {
  width: 100%;
  height: 100%;
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: var(--secondary-color);
}

.upload-trigger:hover {
  border-color: var(--primary-color);
  background-color: var(--bg-color);
}

.upload-trigger.drag-hover {
  border-color: var(--primary-color);
  background-color: var(--bg-color);
  transform: scale(0.98);
}

.default-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 100%;
  color: var(--text-color);
  transition: color 0.3s;
}

.upload-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.dialog-content {
  background: var(--secondary-color);
  padding: 2rem;
  border-radius: 12px;
  width: 500px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.dialog-content h3 {
  margin: 0 0 1.5rem;
  color: var(--text-color);
  transition: color 0.3s;
}

.upload-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.option-group label {
  color: var(--text-color);
  font-size: 0.9em;
  transition: color 0.3s;
}

.input-field {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: all 0.3s ease;
}

.input-field:focus {
  outline: none;
  border-color: var(--primary-color);
}

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-label {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  background-color: var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-label:after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: white;
  top: 2px;
  left: 2px;
  transition: all 0.3s ease;
}

input[type="checkbox"] {
  display: none;
}

input[type="checkbox"]:checked + .toggle-label {
  background-color: var(--primary-color);
}

input[type="checkbox"]:checked + .toggle-label:after {
  transform: translateX(20px);
}

.toggle-text {
  color: var(--text-color);
  font-size: 0.9em;
  transition: color 0.3s;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.cancel-btn, .upload-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.cancel-btn {
  background-color: var(--border-color);
  color: var(--text-color);
}

.cancel-btn:hover {
  background-color: var(--bg-color);
}

.upload-btn {
  background-color: var(--primary-color);
  color: white;
}

.upload-btn:hover {
  background-color: var(--primary-hover);
}

.upload-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.progress-section {
  margin: 1rem 0;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background-color: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.8em;
  color: var(--text-color);
  font-weight: 500;
}

.upload-status {
  text-align: center;
  margin-top: 0.5rem;
  font-size: 0.9em;
  color: var(--text-color);
}

.file-list {
  max-height: 300px;
  overflow-y: auto;
  margin: 1rem 0;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background-color: var(--bg-color);
}

.file-item {
  padding: 0.5rem;
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.3s ease;
}

.file-item:last-child {
  border-bottom: none;
}

.file-item:hover {
  background-color: var(--secondary-color);
}

.file-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.file-index {
  font-size: 0.9em;
  color: var(--text-muted);
  margin-right: 0.5rem;
}

.file-name {
  font-size: 0.9em;
  color: var(--text-color);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 0.8em;
  color: var(--text-muted);
  margin-left: 1rem;
}

.file-title-input {
  margin-top: 0.5rem;
}

.title-input-field {
  width: 80%;
  padding: 6px 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--bg-color);
  color: var(--text-color);
  font-size: 0.9em;
  transition: all 0.3s ease;
}

.title-input-field:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb), 0.1);
}

.file-title-label {
  margin-right: 0.5rem;
  font-size: 0.9em;
  color: var(--text-color);
}
</style>