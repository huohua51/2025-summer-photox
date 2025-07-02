<template>
  <div class="home-container">
    <!-- 欢迎信息 -->
    <div class="welcome-header" v-if="!userStore.isLoggedIn">
      <div class="welcome-content">
        <h1>欢迎来到 PhotoX</h1>
        <p>发现精美图片，分享美好瞬间</p>
        <div class="auth-buttons">
          <router-link to="/login" class="btn btn-primary">登录</router-link>
          <router-link to="/register" class="btn btn-outline">注册</router-link>
        </div>
      </div>
    </div>

    <!-- 小红书风格主体 -->
    <div class="redbook-container" v-if="userStore.isLoggedIn">
      <!-- 顶部搜索栏 -->
      <div class="search-header">
        <div class="search-wrapper">
          <div class="search-input-container">
            <svg class="search-icon" viewBox="0 0 24 24" width="18" height="18">
              <path fill="none" stroke="currentColor" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input
              type="text"
              v-model="searchKeyword"
              placeholder="搜索发现精彩内容"
              @input="handleSearch"
              class="search-input"
            />
            <button 
              v-if="searchKeyword" 
              @click="clearSearch" 
              class="clear-btn"
            >
              ×
            </button>
          </div>
        </div>
      </div>

      <!-- 分类筛选 -->
      <div class="category-filters" v-if="!searchKeyword">
        <div class="filter-tabs">
          <button 
            v-for="category in categories" 
            :key="category.id"
            @click="selectCategory(category.id)"
            :class="['filter-tab', { 'active': selectedCategory === category.id }]"
          >
            {{ category.name }}
          </button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading && filteredPosts.length === 0" class="loading-container">
        <div class="loading-grid">
          <div v-for="n in 8" :key="n" class="skeleton-card">
            <div class="skeleton-image"></div>
            <div class="skeleton-content">
              <div class="skeleton-line short"></div>
              <div class="skeleton-line"></div>
              <div class="skeleton-user">
                <div class="skeleton-avatar"></div>
                <div class="skeleton-name"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && filteredPosts.length === 0 && !searchKeyword" class="empty-state">
        <div class="empty-illustration">
          <svg viewBox="0 0 200 150" width="120" height="90">
            <rect x="20" y="20" width="60" height="80" rx="8" fill="var(--border-color)" opacity="0.3"/>
            <rect x="90" y="30" width="50" height="70" rx="6" fill="var(--border-color)" opacity="0.4"/>
            <rect x="150" y="25" width="40" height="75" rx="5" fill="var(--border-color)" opacity="0.2"/>
            <circle cx="50" cy="140" r="3" fill="var(--primary-color)" opacity="0.6"/>
            <circle cx="115" cy="135" r="3" fill="var(--primary-color)" opacity="0.8"/>
            <circle cx="170" cy="140" r="3" fill="var(--primary-color)" opacity="0.5"/>
          </svg>
        </div>
        <h3>还没有内容</h3>
        <p>关注一些用户或上传你的第一张图片开始使用吧！</p>
        <div class="empty-actions">
          <router-link to="/upload" class="btn btn-primary">上传图片</router-link>
          <button @click="loadRecommendations" class="btn btn-outline">看看推荐</button>
        </div>
      </div>

      <!-- 搜索无结果 -->
      <div v-if="!loading && filteredPosts.length === 0 && searchKeyword" class="no-results">
        <div class="empty-illustration">
          <svg viewBox="0 0 120 120" width="80" height="80">
            <circle cx="60" cy="50" r="30" fill="none" stroke="var(--border-color)" stroke-width="3"/>
            <path d="M85 85l25 25" stroke="var(--border-color)" stroke-width="3" stroke-linecap="round"/>
            <text x="60" y="58" text-anchor="middle" fill="var(--text-secondary)" font-size="18">?</text>
          </svg>
        </div>
        <h3>没有找到相关内容</h3>
        <p>试试其他关键词吧</p>
        <button @click="clearSearch" class="btn btn-outline">清除搜索</button>
      </div>

      <!-- 瀑布流内容 -->
      <div class="masonry-container" v-if="filteredPosts.length > 0">
        <Waterfall
          :list="filteredPosts"
          :column="columnCount"
          :gap="16"
          :width="280"
        >
          <template #item="{ item }">
            <RedBookCard :post="item" :key="item.id" @imageLoaded="onImageLoaded" />
          </template>
        </Waterfall>

        <!-- 加载更多 -->
        <div class="load-more-section" v-if="hasNextPage && !searchKeyword">
          <button 
            @click="loadMore" 
            :disabled="loading"
            class="load-more-btn"
          >
            <span v-if="loading">
              <svg class="spin" viewBox="0 0 24 24" width="16" height="16">
                <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" opacity="0.3"/>
                <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M12 2a10 10 0 0 1 10 10"/>
              </svg>
              加载中...
            </span>
            <span v-else>加载更多</span>
          </button>
        </div>

        <!-- 底部提示 -->
        <div v-if="!hasNextPage && posts.length > 5" class="end-message">
          <div class="end-icon">★</div>
          <p>你已经看完所有内容了！</p>
          <small>去发现更多精彩内容吧</small>
        </div>
      </div>
    </div>

    <!-- 未登录时显示的公开内容 -->
    <div class="public-showcase" v-if="!userStore.isLoggedIn">
      <h2>热门精选</h2>
      <div class="showcase-grid">
        <div 
          v-for="image in publicImages" 
          :key="image.id"
          class="showcase-card"
          @click="openImageDetail(image)"
        >
          <img :src="image.image_url" :alt="image.title" loading="lazy" />
          <div class="showcase-overlay">
            <div class="showcase-info">
              <h4>{{ image.title || '精美图片' }}</h4>
              <div class="showcase-user">
                <img :src="image.user.avatar || '/img/userImage.png'" :alt="image.user.username" />
                <span>{{ image.user.username }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from "vue"
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import RedBookCard from '@/components/RedBookCard.vue'
import imageService from '@/api/imageService'
import api from '@/api'
import { Waterfall } from 'vue-waterfall-plugin-next'
import 'vue-waterfall-plugin-next/dist/style.css'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const posts = ref([])
const publicImages = ref([])
const loading = ref(false)
const searchKeyword = ref("")
const currentPage = ref(1)
const hasNextPage = ref(true)
const selectedCategory = ref('all')
const columnCount = ref(4)

// 分类数据
const categories = ref([
  { id: 'all', name: '推荐' }
])

// 分类映射
const categoryMap = {
  0: "其他", 1: "风景", 2: "人物肖像", 3: "动物", 4: "食品",
  5: "建筑", 6: "电子产品", 7: "植物花卉", 8: "家具家居",
  9: "服装鞋帽", 10: "艺术创作", 11: "运动器材", 12: "交通工具"
}

// 加载分类数据
const loadCategories = async () => {
  try {
    // 获取已有公开图片的分类
    const response = await api.images.getList({
      is_public: true,
      page: 1,
      page_size: 1000  // 获取大量数据来统计分类
    })
    
    const data = response.data || response
    const allPosts = data.results || []
    const categoryStats = new Map()
    
    // 统计各分类的图片数量
    allPosts.forEach(post => {
      const categoryId = post.category_id
      const categoryName = categoryMap[categoryId] || '其他'
      
      if (categoryStats.has(categoryId)) {
        categoryStats.set(categoryId, categoryStats.get(categoryId) + 1)
      } else {
        categoryStats.set(categoryId, 1)
      }
    })
    
    // 生成分类列表，按图片数量排序
    const dynamicCategories = [{ id: 'all', name: '推荐' }]
    
    Array.from(categoryStats.entries())
      .sort(([,a], [,b]) => b - a)  // 按数量降序排序
      .forEach(([categoryId, count]) => {
        if (count > 0) {  // 只显示有图片的分类
          dynamicCategories.push({
            id: categoryId,
            name: categoryMap[categoryId] || '其他',
            count: count
          })
        }
      })
    
    categories.value = dynamicCategories
    console.log('动态分类加载完成:', categories.value)
  } catch (error) {
    console.error('加载分类失败:', error)
    // 使用默认分类
    categories.value = [
      { id: 'all', name: '推荐' },
      { id: 1, name: '风景' },
      { id: 2, name: '人物' },
      { id: 3, name: '动物' },
      { id: 4, name: '美食' }
    ]
  }
}

// 计算属性
const filteredPosts = computed(() => {
  let filtered = posts.value

  // 搜索过滤
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    filtered = filtered.filter(post => {
      return (
        post.user && post.user.username && post.user.username.toLowerCase().includes(keyword) ||
        (post.title && post.title.toLowerCase().includes(keyword)) ||
        (post.tags && post.tags.some(tag => tag.toLowerCase().includes(keyword)))
      )
    })
  }

  // 分类过滤
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(post => {
      // 确保类型匹配，将字符串转换为数字进行比较
      const postCategoryId = typeof post.category_id === 'string' ? parseInt(post.category_id) : post.category_id
      const selectedCategoryId = typeof selectedCategory.value === 'string' ? parseInt(selectedCategory.value) : selectedCategory.value
      return postCategoryId === selectedCategoryId
    })
  }

  // 只保留结构完整的数据
  filtered = filtered.filter(post =>
    post &&
    post.id &&
    post.image_url &&
    post.user &&
    post.user.id &&
    post.user.username
  )

  return filtered
})

// 加载信息流数据
const loadFeed = async (page = 1, append = false) => {
  if (loading.value) return
  
  loading.value = true
  try {
    // 获取所有用户的公开图片，而不是私有图片
    const response = await api.images.getList({ 
      is_public: true,
      page: page,
      page_size: 20,
      ordering: '-created_at'
    })
    
    const data = response.data || response
    const newPosts = data.results || []
    
    if (append) {
      posts.value = [...posts.value, ...newPosts]
    } else {
      posts.value = newPosts
    }
    
    hasNextPage.value = !!data.next
    currentPage.value = page
    
    // 等待DOM更新后重新排列瀑布流
    await nextTick()
  } catch (error) {
    console.error('加载信息流失败:', error)
    if (error.response?.status === 401) {
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

// 加载推荐内容
const loadRecommendations = async () => {
  try {
    const response = await api.images.getList({ 
      is_public: true,
      page: 1,
      page_size: 20,
      ordering: '-created_at'
    })
    const data = response.data || response
    posts.value = data.results || []
    hasNextPage.value = !!data.next
  } catch (error) {
    console.error("获取推荐内容失败:", error)
  }
}

// 加载公开图片（未登录用户显示）
const loadPublicImages = async () => {
  try {
    const response = await api.images.getList({ 
      is_public: true,
      page_size: 12,
      ordering: '-created_at'
    })
    const data = response.data || response
    publicImages.value = data.results || []
  } catch (error) {
    console.error("获取公开图片失败:", error)
  }
}

// 加载更多
const loadMore = () => {
  if (hasNextPage.value && !loading.value) {
    loadFeed(currentPage.value + 1, true)
  }
}

// 搜索处理
const handleSearch = () => {
  // 前端过滤，无需重新请求
}

// 清除搜索
const clearSearch = () => {
  searchKeyword.value = ""
}

// 选择分类
const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId
}

// 打开图片详情
const openImageDetail = (image) => {
  router.push(`/photodetail/${image.id}?fromHome=true`)
}

// 监听登录状态变化
watch(() => userStore.isLoggedIn, (newValue) => {
  if (newValue) {
    // 登录用户：加载信息流和分类
    loadFeed()
    loadCategories()
  } else {
    // 未登录用户：清空信息流，加载公开图片
    posts.value = []
    currentPage.value = 1
    hasNextPage.value = true
    loadPublicImages()
  }
}, { immediate: true })

// 组件挂载
onMounted(() => {
  if (userStore.isLoggedIn) {
    // 登录用户：加载信息流和分类
    loadFeed()
    loadCategories()
  } else {
    // 未登录用户：加载公开图片
    loadPublicImages()
  }
  updateColumnCount()
  window.addEventListener('resize', updateColumnCount)
})

const updateColumnCount = () => {
  const width = window.innerWidth
  if (width < 600) columnCount.value = 1
  else if (width < 900) columnCount.value = 2
  else if (width < 1200) columnCount.value = 3
  else columnCount.value = 4
}
</script>

<style scoped>
.home-container {
  background: var(--bg-color);
  color: var(--text-color);
  min-height: 100vh;
  transition: background 0.3s, color 0.3s;
}

/* 欢迎头部 */
.welcome-header {
  background: var(--secondary-color);
  border-bottom: 1px solid var(--border-color);
  padding: 32px 0 16px 0;
  text-align: center;
}

.welcome-content h1 {
  color: var(--primary-color);
  font-size: 2.2em;
  margin-bottom: 0.2em;
}

.welcome-content p {
  color: var(--text-color);
  opacity: 0.7;
}

.auth-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 32px;
  border-radius: 25px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-block;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  border-radius: 8px;
  padding: 8px 24px;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #176fd4;
}

.btn-outline {
  background: transparent;
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
}

.btn-outline:hover {
  background: var(--primary-color);
  color: white;
}

/* 小红书风格容器 */
.redbook-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 搜索头部 */
.search-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--bg-color);
  padding: 16px 0;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.search-wrapper {
  display: flex;
  justify-content: center;
}

.search-input-container {
  position: relative;
  width: 100%;
  max-width: 500px;
  display: flex;
  align-items: center;
  background: var(--secondary-color);
  border-radius: 20px;
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  transition: all 0.3s;
}

.search-input-container:focus-within {
  border-color: #2196f3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.search-icon {
  color: var(--text-secondary);
  margin-right: 12px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  color: var(--text-color);
  font-size: 15px;
}

.search-input::placeholder {
  color: var(--text-secondary);
}

.clear-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 18px;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: var(--border-color);
  color: var(--text-color);
}

/* 分类筛选 */
.category-filters {
  margin-bottom: 24px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.filter-tab {
  background: var(--secondary-color);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 8px 16px;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
  font-size: 14px;
  font-weight: 500;
}

.filter-tab:hover {
  border-color: #2196f3;
  color: #2196f3;
}

.filter-tab.active {
  background: #2196f3;
  border-color: #2196f3;
  color: white;
}

/* 加载状态 */
.loading-container {
  padding: 20px 0;
}

.loading-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  column-gap: 16px;
}

.skeleton-card {
  background: var(--secondary-color);
  border-radius: 12px;
  overflow: hidden;
  animation: pulse 1.5s ease-in-out infinite;
}

.skeleton-image {
  width: 100%;
  height: 200px;
  background: var(--border-color);
}

.skeleton-content {
  padding: 12px;
}

.skeleton-line {
  height: 10px;
  background: var(--border-color);
  border-radius: 5px;
  margin-bottom: 8px;
}

.skeleton-line.short {
  width: 60%;
}

.skeleton-user {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}

.skeleton-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--border-color);
}

.skeleton-name {
  width: 80px;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* 空状态和无结果 */
.empty-state, .no-results {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-illustration {
  margin-bottom: 24px;
  opacity: 0.6;
}

.empty-state h3, .no-results h3 {
  margin-bottom: 12px;
  color: var(--text-color);
  font-size: 1.5rem;
  font-weight: 600;
}

.empty-state p, .no-results p {
  margin-bottom: 24px;
  font-size: 1rem;
}

.empty-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 瀑布流布局 */
.masonry-container,
.waterfall-list {
  background: var(--bg-color);
  transition: background 0.3s;

}
.masonry-grid {
  display: none;
}

/* 加载更多 */
.load-more-section {
  text-align: center;
  padding: 40px 20px;
}

.load-more-btn {
  background: var(--secondary-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 25px;
  padding: 12px 32px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 0 auto;
}

.load-more-btn:hover:not(:disabled) {
  border-color: #2196f3;
  color: #2196f3;
  transform: translateY(-1px);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 底部提示 */
.end-message {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.end-icon {
  font-size: 2rem;
  margin-bottom: 12px;
}

.end-message p {
  margin-bottom: 4px;
  font-weight: 500;
}

.end-message small {
  font-size: 13px;
  opacity: 0.8;
}

/* 公开展示区 */
.public-showcase {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.public-showcase h2 {
  text-align: center;
  margin-bottom: 32px;
  color: var(--text-color);
  font-size: 2rem;
  font-weight: 700;
}

.showcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.showcase-card {
  position: relative;
  aspect-ratio: 3/4;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.showcase-card:hover {
  transform: scale(1.02);
}

.showcase-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.showcase-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  color: white;
  padding: 24px;
  transform: translateY(50%);
  transition: transform 0.3s;
}

.showcase-card:hover .showcase-overlay {
  transform: translateY(0);
}

.showcase-info h4 {
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 600;
}

.showcase-user {
  display: flex;
  align-items: center;
  gap: 8px;
}

.showcase-user img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid white;
}

.showcase-user span {
  font-size: 14px;
  opacity: 0.9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .redbook-container {
    padding: 12px;
  }
  
  .search-header {
    padding: 12px 0;
  }
  
  .masonry-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }
  
  .filter-tabs {
    gap: 6px;
  }
  
  .filter-tab {
    padding: 6px 12px;
    font-size: 13px;
  }
  
  .showcase-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .welcome-content h1 {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .masonry-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .empty-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .auth-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style> 