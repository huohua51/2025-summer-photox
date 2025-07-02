<template>
  <div class="tag-editor">
    <div class="editor-header">
      <h3 class="editor-title">
        <i class="icon-tag"></i>
        标签管理
      </h3>
      <button 
        v-if="!isEditing && canEdit" 
        @click="startEditing" 
        class="edit-btn"
      >
        <i class="icon-edit"></i>
        编辑标签
      </button>
    </div>

    <!-- 标签展示 -->
    <div class="tags-container">
      <!-- AI生成的标签 -->
      <div v-if="aiTags.length" class="tag-group">
        <p class="tag-group-label">
          <i class="icon-ai-small"></i>
          AI 标签
        </p>
        <div class="tags-list">
          <span 
            v-for="(tag, index) in aiTags" 
            :key="`ai-${index}`"
            class="tag ai-tag"
          >
            {{ tag }}
          </span>
        </div>
      </div>

      <!-- 用户自定义标签 -->
      <div class="tag-group">
        <p class="tag-group-label">
          <i class="icon-user"></i>
          自定义标签
        </p>
        <div class="tags-list">
          <span 
            v-for="(tag, index) in userTags" 
            :key="`user-${index}`"
            class="tag user-tag"
          >
            {{ tag }}
            <button 
              v-if="isEditing" 
              @click="removeTag(tag)" 
              class="tag-remove"
            >
              ×
            </button>
          </span>
          <div v-if="!userTags.length && !isEditing" class="empty-tags">
            暂无自定义标签
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑模式 -->
    <div v-if="isEditing" class="edit-section">
      <div class="tag-input-wrapper">
        <input 
          v-model="newTag"
          @keyup.enter="addTag"
          @input="onTagInput"
          type="text"
          class="tag-input"
          placeholder="输入标签，按回车添加"
        />
        <button 
          @click="addTag" 
          :disabled="!newTag.trim()"
          class="add-tag-btn"
        >
          添加
        </button>
      </div>

      <!-- 标签建议 -->
      <div v-if="tagSuggestions.length" class="tag-suggestions">
        <p class="suggestions-label">推荐标签：</p>
        <div class="suggestions-list">
          <button 
            v-for="(suggestion, index) in tagSuggestions" 
            :key="index"
            @click="addSuggestedTag(suggestion)"
            class="suggestion-tag"
          >
            + {{ suggestion }}
          </button>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="edit-actions">
        <button @click="saveChanges" class="save-btn">
          保存更改
        </button>
        <button @click="cancelEditing" class="cancel-btn">
          取消
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'

const props = defineProps({
  imageId: {
    type: Number,
    required: true
  },
  canEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['tags-updated'])

// 数据
const aiTags = ref([])
const userTags = ref([])
const originalUserTags = ref([])
const isEditing = ref(false)
const newTag = ref('')
const tagSuggestions = ref([])

// 常用标签建议库
const commonTags = [
  '风景', '人像', '街拍', '建筑', '美食', '旅行', '日常', '黑白',
  '自然', '城市', '夜景', '微距', '动物', '植物', '艺术', '创意',
  '复古', '极简', '温馨', '唯美', '纪实', '情绪', '光影', '色彩'
]

// 获取标签
const fetchTags = async () => {
  try {
    const response = await api.get(`/images/${props.imageId}/tags/`)
    aiTags.value = response.data.ai_tags || []
    userTags.value = response.data.user_tags || []
    originalUserTags.value = [...userTags.value]
  } catch (error) {
    console.error('获取标签失败:', error)
  }
}

// 开始编辑
const startEditing = () => {
  isEditing.value = true
  originalUserTags.value = [...userTags.value]
  updateSuggestions()
}

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false
  userTags.value = [...originalUserTags.value]
  newTag.value = ''
}

// 添加标签
const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !userTags.value.includes(tag) && !aiTags.value.includes(tag)) {
    userTags.value.push(tag)
    newTag.value = ''
    updateSuggestions()
  }
}

// 添加建议标签
const addSuggestedTag = (tag) => {
  if (!userTags.value.includes(tag) && !aiTags.value.includes(tag)) {
    userTags.value.push(tag)
    updateSuggestions()
  }
}

// 移除标签
const removeTag = (tag) => {
  const index = userTags.value.indexOf(tag)
  if (index > -1) {
    userTags.value.splice(index, 1)
    updateSuggestions()
  }
}

// 更新标签建议
const updateSuggestions = () => {
  const allTags = [...aiTags.value, ...userTags.value]
  tagSuggestions.value = commonTags
    .filter(tag => !allTags.includes(tag))
    .slice(0, 8)
}

// 标签输入时更新建议
const onTagInput = () => {
  const input = newTag.value.trim().toLowerCase()
  if (input) {
    const allTags = [...aiTags.value, ...userTags.value]
    tagSuggestions.value = commonTags
      .filter(tag => 
        tag.toLowerCase().includes(input) && 
        !allTags.includes(tag)
      )
      .slice(0, 8)
  } else {
    updateSuggestions()
  }
}

// 保存更改
const saveChanges = async () => {
  try {
    // 计算新增和删除的标签
    const tagsToAdd = userTags.value.filter(tag => !originalUserTags.value.includes(tag))
    const tagsToRemove = originalUserTags.value.filter(tag => !userTags.value.includes(tag))

    // 添加新标签
    if (tagsToAdd.length > 0) {
      await api.post(`/images/${props.imageId}/tags/`, {
        tags: tagsToAdd
      })
    }

    // 删除标签
    if (tagsToRemove.length > 0) {
      await api.delete(`/images/${props.imageId}/tags/`, {
        data: { tags: tagsToRemove }
      })
    }

    originalUserTags.value = [...userTags.value]
    isEditing.value = false
    emit('tags-updated', { aiTags: aiTags.value, userTags: userTags.value })
    
    // 显示成功提示
    alert('标签保存成功！')
  } catch (error) {
    console.error('保存标签失败:', error)
    alert('保存失败，请重试')
  }
}

onMounted(() => {
  fetchTags()
})
</script>

<style scoped>
.tag-editor {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.editor-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.icon-tag {
  width: 20px;
  height: 20px;
  background: #667eea;
  -webkit-mask: url('/svg/tag-icon.svg') no-repeat center;
  mask: url('/svg/tag-icon.svg') no-repeat center;
}

.edit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #f3f4f6;
  color: #4b5563;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.icon-edit {
  width: 14px;
  height: 14px;
  background: currentColor;
  -webkit-mask: url('/svg/edit-icon.svg') no-repeat center;
  mask: url('/svg/edit-icon.svg') no-repeat center;
}

/* 标签容器 */
.tags-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tag-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tag-group-label {
  font-size: 14px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
}

.icon-ai-small,
.icon-user {
  width: 16px;
  height: 16px;
  background: currentColor;
}

.icon-ai-small {
  -webkit-mask: url('/svg/ai-icon.svg') no-repeat center;
  mask: url('/svg/ai-icon.svg') no-repeat center;
}

.icon-user {
  -webkit-mask: url('/svg/user-icon.svg') no-repeat center;
  mask: url('/svg/user-icon.svg') no-repeat center;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.ai-tag {
  background: #ede9fe;
  color: #7c3aed;
}

.user-tag {
  background: #e0f2fe;
  color: #0284c7;
}

.tag-remove {
  width: 18px;
  height: 18px;
  background: rgba(0, 0, 0, 0.2);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.tag-remove:hover {
  background: rgba(0, 0, 0, 0.3);
  transform: scale(1.1);
}

.empty-tags {
  color: #9ca3af;
  font-size: 14px;
}

/* 编辑区域 */
.edit-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.tag-input-wrapper {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.tag-input {
  flex: 1;
  padding: 10px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;
}

.tag-input:focus {
  border-color: #667eea;
}

.add-tag-btn {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-tag-btn:hover:not(:disabled) {
  background: #5a67d8;
  transform: translateY(-1px);
}

.add-tag-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 标签建议 */
.tag-suggestions {
  margin-bottom: 20px;
}

.suggestions-label {
  font-size: 13px;
  color: #6b7280;
  margin: 0 0 8px 0;
}

.suggestions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.suggestion-tag {
  padding: 6px 12px;
  background: #f3f4f6;
  color: #4b5563;
  border: 1px dashed #d1d5db;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-tag:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
  color: #1f2937;
}

/* 操作按钮 */
.edit-actions {
  display: flex;
  gap: 12px;
}

.save-btn,
.cancel-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.save-btn {
  background: #10b981;
  color: white;
}

.save-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

.cancel-btn {
  background: #f3f4f6;
  color: #6b7280;
}

.cancel-btn:hover {
  background: #e5e7eb;
  color: #4b5563;
}

/* 响应式 */
@media (max-width: 768px) {
  .tag-editor {
    padding: 16px;
  }
  
  .tag-input-wrapper {
    flex-direction: column;
  }
  
  .add-tag-btn {
    width: 100%;
  }
  
  .edit-actions {
    flex-direction: column;
  }
  
  .save-btn,
  .cancel-btn {
    width: 100%;
  }
}
</style>