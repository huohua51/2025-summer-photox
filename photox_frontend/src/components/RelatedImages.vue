<template>
    <div class="related-images-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-section">
            <div class="loading-spinner"></div>
            <p>正在为您寻找相关内容...</p>
        </div>
        
        <!-- 相关推荐内容 -->
        <div v-else class="related-content">
            <div class="section-header">
                <h3>相关推荐</h3>
                <div class="recommendation-filters">
                    <button 
                        v-for="filter in filterTypes" 
                        :key="filter.key"
                        :class="['filter-btn', { active: activeFilter === filter.key }]"
                        @click="setFilter(filter.key)"
                    >
                        <span class="filter-icon">{{ filter.icon }}</span>
                        {{ filter.label }}
                    </button>
                </div>
            </div>

            <!-- AI智能分析结果区域 -->
            <div v-if="activeFilter === 'ai'" class="ai-description-section">
                <div v-if="aiLoading" class="loading-section">
                    <div class="loading-spinner"></div>
                    <p>AI智能分析中...</p>
                </div>
                <div v-else>
                    <h4>AI智能分析结果</h4>
                    <p>{{ aiDescription }}</p>
                </div>
            </div>

            <!-- 推荐图片网格 -->
            <div v-if="displayImages.length > 0" class="related-grid">
                <div 
                    v-for="img in displayImages" 
                    :key="img.id" 
                    class="related-item" 
                    @click="navigateToImage(img.id)"
                >
                    <div class="image-container">
                        <img :src="img.image_url" :alt="img.title || '相关图片'" />
                        <div class="image-overlay"></div>

                        <!-- 操作按钮 -->
                        <div class="action-buttons">
                            <button class="action-btn favorite-btn" @click.stop="toggleFavorite(img.id)">
                                <svg class="heart-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                                </svg>
                            </button>
                            <button class="action-btn share-btn" @click.stop="shareImage(img)">
                                <svg class="share-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <circle cx="18" cy="5" r="3"></circle>
                                    <circle cx="6" cy="12" r="3"></circle>
                                    <circle cx="18" cy="19" r="3"></circle>
                                    <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                                    <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                                </svg>
                            </button>
                            <button class="action-btn download-btn" @click.stop="downloadImage(img)">
                                <svg class="download-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                    <polyline points="7,10 12,15 17,10"></polyline>
                                    <line x1="12" y1="15" x2="12" y2="3"></line>
                                </svg>
                            </button>
                        </div>

                        <!-- 推荐标签 -->
                        <div class="recommendation-badge">
                            <span>{{ getRecommendationLabel(img) }}</span>
                        </div>

                        <!-- 匹配度指示器 -->
                        <div class="match-indicator">
                            <div class="match-score">{{ img.matchScore }}%</div>
                        </div>
                    </div>

                    <!-- 图片信息 -->
                    <div class="related-info">
                        <div class="info-header">
                            <h4 class="image-title">{{ img.title || '精选图片' }}</h4>
                            <div class="image-stats">
                                <span v-if="img.like_count" class="stat-item">
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                                    </svg>
                                    {{ img.like_count }}
                                </span>
                            </div>
                        </div>
                        
                        <div class="image-meta">
                            <span class="category-tag">{{ img.category || '推荐' }}</span>
                            <span v-if="img.user" class="author-info">
                                by {{ typeof img.user === 'object' ? img.user.username : img.user }}
                            </span>
                        </div>

                        <div v-if="img.matchedTags && img.matchedTags.length" class="matched-tags">
                            <span v-for="tag in img.matchedTags.slice(0, 3)" :key="tag" class="matched-tag">
                                {{ tag }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 空状态 -->
            <div v-else class="empty-state">
                <div class="empty-icon">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="M21 21l-4.35-4.35"></path>
                    </svg>
                </div>
                <h4>暂无相关推荐</h4>
                <p>我们正在为您寻找更多精彩内容</p>
                <button @click="refreshRecommendations" class="refresh-btn">
                    刷新推荐
                </button>
            </div>

            <!-- 加载更多按钮 -->
            <div v-if="hasMore && displayImages.length > 0" class="load-more-section">
                <button @click="loadMoreImages" :disabled="loadingMore" class="load-more-btn">
                    <span v-if="loadingMore">加载中...</span>
                    <span v-else>查看更多推荐</span>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '@/api'

const props = defineProps({
    currentImage: Object,
    allImages: Array,
    formatTags: Array,
    loading: Boolean
})

const router = useRouter()
const favorites = ref(new Set())
const activeFilter = ref('similar')
const loadingMore = ref(false)
const hasMore = ref(true)
const relatedImages = ref([])
const aiDescription = ref('')
const aiLoading = ref(false)

// 推荐类型过滤器
const filterTypes = [
    { key: 'similar', label: '相似内容', icon: '●' },
    { key: 'category', label: '同类推荐', icon: '●' },
    { key: 'author', label: '作者其他作品', icon: '●' },
    { key: 'popular', label: '热门推荐', icon: '●' },
    { key: 'ai', label: 'AI智能分析', icon: '●' }
]

// 获取推荐图片
const fetchRelatedImages = async () => {
    if (!props.currentImage) return

    try {
        const params = {
            exclude_id: props.currentImage.id,
            limit: 12,
            is_public: true // 强制只查公开图片
        }

        // 根据不同过滤器添加不同参数
        switch (activeFilter.value) {
            case 'similar':
                if (props.formatTags && props.formatTags.length > 0) {
                    params.tags = props.formatTags.join(',')
                }
                break
            case 'category':
                if (props.currentImage.category_id) {
                    params.category_id = props.currentImage.category_id
                }
                break
            case 'author':
                if (props.currentImage.user) {
                    const userId = typeof props.currentImage.user === 'object' 
                        ? props.currentImage.user.id 
                        : props.currentImage.user
                    params.user_id = userId
                }
                break
            case 'popular':
                params.order_by = 'like_count'
                break
        }

        const response = await apiService.images.getList(params)
        const images = response.results || response.data?.results || []
        
        // 为图片添加推荐相关信息
        relatedImages.value = images.map(img => ({
            ...img,
            matchScore: calculateMatchScore(img),
            matchedTags: getMatchedTags(img),
            recommendationType: activeFilter.value
        }))
        hasMore.value = images.length >= 12
    } catch (e) {
        relatedImages.value = []
        hasMore.value = false
    }
}

// 计算匹配度
const calculateMatchScore = (image) => {
    if (!props.formatTags || props.formatTags.length === 0) {
        return Math.floor(Math.random() * 30) + 70
    }

    const imageTags = Array.isArray(image.tags) ? image.tags : []
    if (imageTags.length === 0) {
        return Math.floor(Math.random() * 40) + 50
    }

    const matchedCount = imageTags.filter(tag => 
        props.formatTags.some(currentTag => 
            currentTag.toLowerCase().includes(tag.toLowerCase()) || 
            tag.toLowerCase().includes(currentTag.toLowerCase())
        )
    ).length

    const matchPercentage = (matchedCount / Math.max(props.formatTags.length, imageTags.length)) * 100
    return Math.min(95, Math.max(45, Math.floor(matchPercentage)))
}

// 获取匹配的标签
const getMatchedTags = (image) => {
    if (!props.formatTags || !image.tags) return []
    
    const imageTags = Array.isArray(image.tags) ? image.tags : []
    return imageTags.filter(tag => 
        props.formatTags.some(currentTag => 
            currentTag.toLowerCase().includes(tag.toLowerCase()) || 
            tag.toLowerCase().includes(currentTag.toLowerCase())
        )
    ).slice(0, 3)
}

// 获取推荐标签
const getRecommendationLabel = (image) => {
    const labels = {
        similar: '相似推荐',
        category: '同类精选',
        author: '作者作品',
        popular: '热门推荐'
    }
    return labels[image.recommendationType] || '推荐'
}

// 显示的图片列表
const displayImages = computed(() => {
    return relatedImages.value
})

// 设置过滤器
const setFilter = async (filterKey) => {
    activeFilter.value = filterKey
    if (filterKey === 'ai') {
        aiLoading.value = true
        aiDescription.value = ''
        try {
            // 调用后端AI分析接口
            const res = await apiService.images.aiDescription(props.currentImage.id)
            aiDescription.value = res.description || '暂无分析结果'
        } catch (e) {
            aiDescription.value = 'AI分析失败'
        }
        aiLoading.value = false
    } else {
        fetchRelatedImages()
    }
}

// 刷新推荐
const refreshRecommendations = () => {
    fetchRelatedImages()
}

// 加载更多
const loadMoreImages = async () => {
    loadingMore.value = true
    // 这里可以实现分页加载逻辑
    setTimeout(() => {
        loadingMore.value = false
        hasMore.value = false // 演示：加载一次后就没有更多了
    }, 1000)
}

// 导航到图片
const navigateToImage = (id) => {
    router.push(`/photodetail/${id}?fromRelated=true`)
}

// 收藏功能
const toggleFavorite = async (id) => {
    try {
        await apiService.images.toggleLike(id)
        if (favorites.value.has(id)) {
            favorites.value.delete(id)
        } else {
            favorites.value.add(id)
        }
    } catch (error) {
        console.error('收藏操作失败:', error)
    }
}

// 分享图片
const shareImage = (img) => {
    const url = `${window.location.origin}/photodetail/${img.id}`
    if (navigator.share) {
        navigator.share({
            title: img.title || '精选图片',
            text: '发现精彩内容',
            url
        }).catch(console.error)
    } else {
        navigator.clipboard.writeText(url).then(() => {
            // 这里可以显示一个 toast 提示
            console.log('链接已复制到剪贴板')
        }).catch(console.error)
    }
}

// 下载图片
const downloadImage = (img) => {
    const link = document.createElement('a')
    link.href = img.image_url
    link.download = img.title || `image_${img.id}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
}

// 监听当前图片变化
watch(() => props.currentImage, () => {
    if (props.currentImage) {
        fetchRelatedImages()
    }
}, { immediate: true })

// 监听过滤器变化
watch(activeFilter, () => {
    fetchRelatedImages()
})

onMounted(() => {
    if (props.currentImage) {
        fetchRelatedImages()
    }
})
</script>

<style scoped>
.related-images-container {
    margin-top: 40px;
    padding: 32px;
    background: var(--bg-color);
    border-radius: 16px;
    color: var(--text-color);
}

/* 加载状态 */
.loading-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 60px 20px;
    color: var(--text-color);
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(74, 158, 255, 0.3);
    border-radius: 50%;
    border-top-color: var(--primary-color);
    animation: spin 1s ease-in-out infinite;
    margin-bottom: 16px;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* 节标题 */
.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
    flex-wrap: wrap;
    gap: 16px;
}

.section-header h3 {
    font-size: 1.8rem;
    margin: 0;
    color: var(--text-color);
    font-weight: 700;
}

/* 推荐过滤器 */
.recommendation-filters {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.filter-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border: 2px solid var(--border-color);
    border-radius: 20px;
    background: var(--secondary-color);
    color: var(--text-color);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.filter-btn:hover {
    border-color: var(--primary-color);
    transform: translateY(-1px);
}

.filter-btn.active {
    border-color: var(--primary-color);
    background: var(--primary-color);
    color: white;
}

.filter-icon {
    font-size: 16px;
}

/* 图片网格 */
.related-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
}

.related-item {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    cursor: pointer;
    background: var(--secondary-color);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.related-item:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.image-container {
    position: relative;
    aspect-ratio: 4/3;
    overflow: hidden;
}

.related-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.6s ease;
}

.related-item:hover img {
    transform: scale(1.1);
}

.image-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.7) 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.related-item:hover .image-overlay {
    opacity: 1;
}

/* 操作按钮 */
.action-buttons {
    position: absolute;
    top: 12px;
    right: 12px;
    display: flex;
    gap: 8px;
    opacity: 0;
    transform: translateY(-10px);
    transition: all 0.3s ease;
}

.related-item:hover .action-buttons {
    opacity: 1;
    transform: translateY(0);
}

.action-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    color: #333;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.action-btn:hover {
    background: white;
    transform: scale(1.1);
}

.action-btn svg {
    width: 16px;
    height: 16px;
    stroke-width: 2;
}

.favorite-btn:hover { color: #ff4757; }
.share-btn:hover { color: #5352ed; }
.download-btn:hover { color: #2ed573; }

/* 推荐标签 */
.recommendation-badge {
    position: absolute;
    top: 12px;
    left: 12px;
    opacity: 0;
    transform: translateX(-10px);
    transition: all 0.3s ease;
}

.related-item:hover .recommendation-badge {
    opacity: 1;
    transform: translateX(0);
}

.recommendation-badge span {
    padding: 4px 8px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #333;
}

/* 匹配度指示器 */
.match-indicator {
    position: absolute;
    bottom: 12px;
    right: 12px;
    opacity: 0;
    transition: all 0.3s ease;
}

.related-item:hover .match-indicator {
    opacity: 1;
}

.match-score {
    padding: 4px 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    color: white;
    font-size: 0.75rem;
    font-weight: 600;
}

/* 图片信息 */
.related-info {
    padding: 16px;
}

.info-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
}

.image-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0;
    line-height: 1.3;
    flex: 1;
}

.image-stats {
    display: flex;
    gap: 8px;
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.75rem;
    color: #666;
}

.image-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}

.category-tag {
    font-size: 0.75rem;
    padding: 2px 8px;
    background: var(--primary-color);
    color: white;
    border-radius: 8px;
    font-weight: 500;
}

.author-info {
    font-size: 0.75rem;
    color: #666;
}

.matched-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

.matched-tag {
    font-size: 0.7rem;
    padding: 2px 6px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 8px;
    color: white;
    font-weight: 500;
}

/* 空状态 */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-color);
}

.empty-icon {
    margin-bottom: 16px;
    opacity: 0.5;
}

.empty-state h4 {
    margin: 0 0 8px 0;
    font-size: 1.2rem;
    color: var(--text-color);
}

.empty-state p {
    margin: 0 0 20px 0;
    color: #666;
}

.refresh-btn {
    padding: 10px 20px;
    border: 2px solid var(--primary-color);
    border-radius: 20px;
    background: transparent;
    color: var(--primary-color);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.refresh-btn:hover {
    background: var(--primary-color);
    color: white;
}

/* 加载更多 */
.load-more-section {
    text-align: center;
}

.load-more-btn {
    padding: 12px 24px;
    border: 2px solid var(--primary-color);
    border-radius: 24px;
    background: var(--primary-color);
    color: white;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.load-more-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.load-more-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .related-images-container {
        padding: 20px;
    }
    
    .section-header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .related-grid {
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 16px;
    }
    
    .recommendation-filters {
        width: 100%;
        justify-content: center;
    }
}
</style>