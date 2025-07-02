<template>
  <div class="image-menu-container">
    <div class="menu-icon" @click.stop="toggleMenu">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="1"></circle>
        <circle cx="12" cy="5" r="1"></circle>
        <circle cx="12" cy="19" r="1"></circle>
      </svg>
    </div>
    
    <!-- 下拉菜单 -->
    <div v-if="showMenu" class="dropdown-menu" @click.stop>
      <div class="menu-item" @click="downloadImage">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        <span>下载图片</span>
      </div>
      <div class="menu-item" @click="openEditDialog">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
        <span>编辑信息</span>
      </div>
      <div class="menu-item" @click="confirmDelete">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          <line x1="10" y1="11" x2="10" y2="17"></line>
          <line x1="14" y1="11" x2="14" y2="17"></line>
        </svg>
        <span>删除图片</span>
      </div>
    </div>
    
    <!-- 编辑对话框 -->
    <div v-if="showEditDialog" class="edit-dialog" @click.stop>
      <div class="dialog-content">
        <h3>编辑图片信息</h3>
        <div class="edit-form">
          <div class="form-group">
            <label>图片名称</label>
            <input v-model="editTitle" type="text" class="input-field" placeholder="输入图片名称">
          </div>
          <div class="form-group">
            <label>公开状态</label>
            <div class="toggle-switch">
              <input type="checkbox" v-model="editIsPublic" id="edit-public-toggle">
              <label for="edit-public-toggle" class="toggle-label"></label>
              <span class="toggle-text">{{ editIsPublic ? '公开' : '私有' }}</span>
            </div>
          </div>
        </div>
        <div class="dialog-actions">
          <button @click="cancelEdit" class="cancel-btn">取消</button>
          <button @click="saveEdit" class="save-btn">保存</button>
        </div>
      </div>
    </div>
    
    <!-- 确认删除对话框 -->
    <div v-if="showConfirmDialog" class="confirm-dialog" @click.stop>
      <div class="dialog-content">
        <h3>确认删除</h3>
        <p>您确定要删除这张图片吗？此操作无法撤销。</p>
        <div class="dialog-actions">
          <button @click="cancelDelete" class="cancel-btn">取消</button>
          <button @click="deleteImage" class="delete-btn">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import imageService from '../api/imageService'
import { ElMessage } from 'element-plus'

const props = defineProps({
  imageId: {
    type: [Number, String],
    required: true
  },
  imageTitle: {
    type: String,
    required: true
  },
  isPublic: {
    type: Boolean,
    required: true
  },
  imageUrl: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['image-deleted', 'image-updated'])

const showMenu = ref(false)
const showConfirmDialog = ref(false)
const showEditDialog = ref(false)
const editTitle = ref('')
const editIsPublic = ref(false)

// 打开/关闭菜单
const toggleMenu = () => {
  showMenu.value = !showMenu.value
  if (showConfirmDialog.value) {
    showConfirmDialog.value = false
  }
  if (showEditDialog.value) {
    showEditDialog.value = false
  }
}

// 打开编辑对话框
const openEditDialog = () => {
  editTitle.value = props.imageTitle
  editIsPublic.value = props.isPublic
  showEditDialog.value = true
  showMenu.value = false
}

// 取消编辑
const cancelEdit = () => {
  showEditDialog.value = false
}

// 保存编辑
const saveEdit = async () => {
  try {
    // 调用API更新图片信息
    const response = await imageService.updateImage(props.imageId, {
      title: editTitle.value,
      is_public: editIsPublic.value
    })
    console.log(response)
    console.log(editIsPublic.value)
    if (response) {
      // 通知父组件图片已更新
      emit('image-updated', {
        id: props.imageId,
        title: editTitle.value,
        is_public: editIsPublic.value
      })
      showEditDialog.value = false
    } else {
      throw new Error(response.message || '更新失败')
    }
  } catch (error) {
    console.error('更新图片信息失败:', error)
    alert('更新失败，请稍后重试')
  }
}

// 显示确认对话框
const confirmDelete = () => {
  showConfirmDialog.value = true
  showMenu.value = false
}

// 取消删除
const cancelDelete = () => {
  showConfirmDialog.value = false
}

// 删除图片
const deleteImage = async () => {
  try {
    console.log('开始删除图片:', props.imageId)
    const response = await imageService.deleteImage(props.imageId)
    console.log('删除图片响应:', response)
    
    // 删除成功，通知父组件
    emit('image-deleted', props.imageId)
    showConfirmDialog.value = false
    ElMessage.success('删除成功')
  } catch (error) {
    console.error('删除图片失败:', error)
    ElMessage.error('删除失败，请稍后重试')
  }
}

// 下载图片
const downloadImage = async () => {
  try {
    if (!props.imageUrl) {
      throw new Error('图片地址不存在')
    }

    // 创建一个隐藏的 a 标签
    const link = document.createElement('a')
    
    // 确保URL是完整的
    const imageUrl = props.imageUrl.startsWith('http') 
      ? props.imageUrl 
      : `${import.meta.env.VITE_API_BASE_URL}${props.imageUrl}`
    
    link.href = imageUrl
    
    // 从 URL 中提取文件名，如果没有则使用时间戳
    const fileName = props.imageTitle || `image_${Date.now()}`
    let fileExtension = 'jpg' // 默认扩展名
    
    try {
      // 尝试从URL中获取扩展名
      const urlParts = imageUrl.split('.')
      if (urlParts.length > 1) {
        const ext = urlParts[urlParts.length - 1].toLowerCase()
        // 验证扩展名是否合法
        if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) {
          fileExtension = ext
        }
      }
    } catch (e) {
      console.warn('无法从URL获取文件扩展名，使用默认扩展名')
    }
    
    // 设置下载属性
    link.download = `${fileName}.${fileExtension}`
    
    // 添加到文档中并触发点击
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载图片失败:', error)
    ElMessage.error(error.message || '下载失败，请稍后重试')
  }
}

// 点击文档其他地方关闭菜单
const handleClickOutside = (e) => {
  if (showMenu.value || showConfirmDialog.value || showEditDialog.value) {
    showMenu.value = false
    showConfirmDialog.value = false
    showEditDialog.value = false
  }
}

// 添加和移除全局点击事件监听器
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.image-menu-container {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-item:hover .image-menu-container {
  opacity: 1;
}

.menu-icon {
  width: 2.5em;
  height: 2.5em;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-color);
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.menu-icon:hover {
  background-color: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

.menu-icon svg {
  width: 1.2em;
  height: 1.2em;
}

.dropdown-menu {
  position: absolute;
  top: 3em;
  right: 0;
  width: 12em;
  background-color: var(--secondary-color);
  border-radius: 0.8em;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
  z-index: 100;
  border: 1px solid var(--border-color);
  animation: fadeInMenu 0.2s ease;
  overflow: hidden;
}

@keyframes fadeInMenu {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.8em;
  padding: 0.8em 1em;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.menu-item:hover {
  background-color: var(--bg-color);
}

.menu-item:first-child {
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.menu-item:last-child {
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
}

.menu-item svg {
  width: 1.2em;
  height: 1.2em;
  flex-shrink: 0;
}

.menu-item:first-child svg {
  color: var(--success-color);
}

.menu-item:last-child svg {
  color: var(--error-color);
}

.edit-dialog {
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
}

.dialog-content {
  background: var(--secondary-color);
  border-radius: 0.8em;
  padding: 1.2em;
  width: 85%;
  max-width: 20em;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
}

.dialog-content h3 {
  color: var(--text-color);
  font-size: 1.1em;
  margin-bottom: 1em;
  font-weight: 600;
}

.edit-form {
  margin-bottom: 1.2em;
}

.form-group {
  margin-bottom: 1em;
}

.form-group label {
  display: block;
  color: var(--text-color);
  margin-bottom: 0.4em;
  font-weight: 500;
  font-size: 0.9em;
}

.input-field {
  width: 100%;
  padding: 0.6em;
  border: 1px solid var(--border-color);
  border-radius: 0.4em;
  background: var(--bg-color);
  color: var(--text-color);
  font-size: 0.9em;
  transition: all 0.3s ease;
}

.input-field:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 2px rgba(23, 111, 212, 0.1);
}

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 0.8em;
}

.toggle-switch input[type="checkbox"] {
  display: none;
}

.toggle-label {
  position: relative;
  display: inline-block;
  width: 2.6em;
  height: 1.4em;
  background: var(--bg-color);
  border-radius: 0.7em;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-label:after {
  content: '';
  position: absolute;
  width: 1.2em;
  height: 1.2em;
  border-radius: 50%;
  background: var(--text-color);
  top: 0.1em;
  left: 0.1em;
  transition: all 0.3s ease;
}

.toggle-switch input[type="checkbox"]:checked + .toggle-label {
  background: var(--primary-color);
}

.toggle-switch input[type="checkbox"]:checked + .toggle-label:after {
  transform: translateX(1.2em);
}

.toggle-text {
  color: var(--text-color);
  font-size: 0.85em;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.6em;
  margin-top: 1.2em;
}

.dialog-actions button {
  padding: 0.5em 1em;
  border-radius: 0.4em;
  font-weight: 500;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.cancel-btn:hover {
  background: var(--secondary-color);
}

.save-btn {
  background: var(--primary-color);
  color: white;
  border: none;
}

.save-btn:hover {
  opacity: 0.9;
}

.delete-btn {
  background-color: var(--error-color);
  color: var(--text-color);
}

.delete-btn:hover {
  background-color: var(--error-color);
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(255, 77, 79, 0.4);
}

.delete-btn:active, .cancel-btn:active, .save-btn:active {
  transform: translateY(0);
}
</style> 