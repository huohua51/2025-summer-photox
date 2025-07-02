<template>
  <div class="ai-analysis-panel">
    <!-- AI分析标题 -->
    <div class="panel-header">
      <h3 class="panel-title">
        <i class="icon-ai"></i>
        AI 智能分析
      </h3>
      <button 
        v-if="!analysisData.style_analysis" 
        @click="fetchStyleAnalysis" 
        class="analyze-btn"
        :disabled="loading"
      >
        {{ loading ? '分析中...' : '开始分析' }}
      </button>
    </div>

    <!-- 加载动画 -->
    <div v-if="loading" class="loading-container">
      <div class="ai-loader">
        <div class="loader-dot"></div>
        <div class="loader-dot"></div>
        <div class="loader-dot"></div>
      </div>
      <p class="loading-text">AI 正在分析图片...</p>
    </div>

    <!-- 分析结果 -->
    <div v-else-if="analysisData.style_analysis" class="analysis-content">
      <!-- 风格分析卡片 -->
      <div class="analysis-card style-card">
                    <h4 class="card-title">风格分析</h4>
        <div class="style-grid">
          <div class="style-item">
            <span class="style-label">艺术风格</span>
            <span class="style-value">{{ analysisData.style_analysis.art_style }}</span>
          </div>
          <div class="style-item">
            <span class="style-label">摄影风格</span>
            <span class="style-value">{{ analysisData.style_analysis.photography_style }}</span>
          </div>
          <div class="style-item">
            <span class="style-label">色彩风格</span>
            <span class="style-value">{{ analysisData.style_analysis.color_style }}</span>
          </div>
          <div class="style-item">
            <span class="style-label">构图方式</span>
            <span class="style-value">{{ analysisData.style_analysis.composition }}</span>
          </div>
        </div>
        
        <!-- 技术特征标签 -->
        <div v-if="analysisData.style_analysis.technique_features?.length" class="technique-tags">
          <span class="tag-label">技术特征：</span>
          <span 
            v-for="(feature, index) in analysisData.style_analysis.technique_features" 
            :key="index"
            class="technique-tag"
          >
            {{ feature }}
          </span>
        </div>
      </div>

      <!-- 情感分析卡片 -->
      <div class="analysis-card emotion-card">
        <h4 class="card-title">情感分析</h4>
        <div class="emotion-content">
          <div class="emotion-primary">
                          <span class="emotion-icon">○</span>
            <div class="emotion-info">
              <p class="emotion-label">主要情感</p>
              <p class="emotion-value">{{ analysisData.emotion_analysis.primary_emotion }}</p>
            </div>
          </div>
          
          <div v-if="analysisData.emotion_analysis.atmosphere" class="atmosphere">
            <p class="atmosphere-label">氛围描述</p>
            <p class="atmosphere-text">{{ analysisData.emotion_analysis.atmosphere }}</p>
          </div>

          <div v-if="analysisData.emotion_analysis.story_hint" class="story-hint">
            <p class="story-label">故事暗示</p>
            <p class="story-text">{{ analysisData.emotion_analysis.story_hint }}</p>
          </div>

          <!-- 次要情感标签 -->
          <div v-if="analysisData.emotion_analysis.secondary_emotions?.length" class="secondary-emotions">
            <span 
              v-for="(emotion, index) in analysisData.emotion_analysis.secondary_emotions" 
              :key="index"
              class="emotion-tag"
            >
              {{ emotion }}
            </span>
          </div>
        </div>
      </div>

      <!-- 色彩分析卡片 -->
      <div v-if="colors && colors.length" class="analysis-card color-card">
                    <h4 class="card-title">色彩分析</h4>
        <div class="color-palette">
          <div 
            v-for="(color, index) in colors" 
            :key="index"
            class="color-item"
            :style="{ backgroundColor: color }"
            :title="color"
          >
            <span class="color-code">{{ color }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">○</div>
      <p class="empty-text">点击"开始分析"让 AI 深度解析这张图片</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '@/api'

const props = defineProps({
  imageId: {
    type: Number,
    required: true
  },
  colors: {
    type: Array,
    default: () => []
  }
})

const loading = ref(false)
const analysisData = reactive({
  style_analysis: null,
  emotion_analysis: null
})

const fetchStyleAnalysis = async () => {
  loading.value = true
  try {
    const response = await api.post(`/images/${props.imageId}/style-analysis/`)
    if (response.data) {
      analysisData.style_analysis = response.data.style_analysis
      analysisData.emotion_analysis = response.data.emotion_analysis
    }
  } catch (error) {
    console.error('获取AI分析失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.ai-analysis-panel {
  background: var(--bg-color);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
  color: var(--text-color);
  transition: background 0.3s, color 0.3s;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.panel-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.icon-ai {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-mask: url('/svg/ai-icon.svg') no-repeat center;
  mask: url('/svg/ai-icon.svg') no-repeat center;
}

.analyze-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.analyze-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 加载动画 */
.loading-container {
  text-align: center;
  padding: 48px 0;
}

.ai-loader {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}

.loader-dot {
  width: 12px;
  height: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  animation: dot-pulse 1.4s ease-in-out infinite;
}

.loader-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.loader-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dot-pulse {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

.loading-text {
  color: #666;
  font-size: 14px;
}

/* 分析内容 */
.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-card {
  background: #f8f9fb;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e8eaed;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 16px 0;
}

/* 风格分析 */
.style-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.style-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.style-label {
  font-size: 12px;
  color: #666;
}

.style-value {
  font-size: 14px;
  color: #1a1a1a;
  font-weight: 500;
}

.technique-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-label {
  font-size: 12px;
  color: #666;
}

.technique-tag {
  padding: 4px 12px;
  background: #e8eaed;
  border-radius: 16px;
  font-size: 12px;
  color: #333;
}

/* 情感分析 */
.emotion-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.emotion-primary {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.emotion-icon {
  font-size: 32px;
}

.emotion-info {
  flex: 1;
}

.emotion-label {
  font-size: 12px;
  color: #666;
  margin: 0 0 4px 0;
}

.emotion-value {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.atmosphere,
.story-hint {
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
}

.atmosphere-label,
.story-label {
  font-size: 12px;
  color: #666;
  margin: 0 0 4px 0;
}

.atmosphere-text,
.story-text {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
  margin: 0;
}

.secondary-emotions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.emotion-tag {
  padding: 6px 16px;
  background: #fef3e2;
  color: #f59e0b;
  border-radius: 20px;
  font-size: 13px;
}

/* 色彩分析 */
.color-palette {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 4px;
}

.color-item {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.color-item:hover {
  transform: scale(1.05);
}

.color-code {
  font-size: 11px;
  color: white;
  background: rgba(0, 0, 0, 0.5);
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 48px 0;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  color: #666;
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 768px) {
  .style-grid {
    grid-template-columns: 1fr;
  }
  
  .color-palette {
    flex-wrap: wrap;
  }
  
  .color-item {
    width: 60px;
    height: 60px;
  }
}
</style> 