<template>
  <div class="category-detail-container">
    <h1 class="category-title">{{ categoryName }}</h1>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else>
      <div v-if="images.length === 0" class="no-images">该分类暂无图片</div>
      <div class="masonry-grid">
        <div 
          v-for="img in images" 
          :key="img.id" 
          class="masonry-item"
          :style="{ gridRowEnd: `span ${img.span || 2}` }"
          @click="openPhotoDetail(img.id)"
        >
          <img 
            :src="img.img" 
            :alt="categoryName"
            @load="onImageLoad($event, img)" 
          />
        </div>
      </div>
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="page === 1" @click="changePage(page - 1)">上一页</button>
        <span>第 {{ page }} 页 / 共 {{ totalPages }} 页</span>
        <button :disabled="page === totalPages" @click="changePage(page + 1)">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const categoryName = ref(route.params.name)
const images = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const totalPages = ref(1)

// 计算图片在瀑布流中占据的行数
const calculateSpan = (img) => {
  const height = img.naturalHeight
  const width = img.naturalWidth
  const ratio = height / width
  // 根据图片比例决定占据的行数
  return Math.ceil(ratio * 2)
}

// 图片加载完成后计算其占据的行数
const onImageLoad = (event, img) => {
  const span = calculateSpan(event.target)
  img.span = span
}

// 打开图片详情
const openPhotoDetail = (id) => {
  router.push(`/photodetail/${id}?fromCategory=true`)
}

const fetchImages = async () => {
  loading.value = true
  try {
    const res = await api.images.getList({
      category: categoryName.value,
      is_public: true,
      page: page.value,
      page_size: pageSize
    })
    const list = res.results || res.data?.results || []
    images.value = list.map(img => ({
      id: img.id,
      img: img.image_url,
      span: 2 // 默认占据2行，加载完成后会重新计算
    }))
    total.value = res.count || res.data?.count || list.length
    totalPages.value = Math.ceil(total.value / pageSize)
  } catch (e) {
    images.value = []
    total.value = 0
    totalPages.value = 1
  } finally {
    loading.value = false
  }
}

const changePage = (p) => {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  fetchImages()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(fetchImages)
watch(() => route.params.name, (newName) => {
  categoryName.value = newName
  page.value = 1
  fetchImages()
})
</script>

<style scoped>
.category-detail-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 32px 16px;
}

.category-title {
  font-size: 2rem;
  margin-bottom: 32px;
  text-align: center;
}

.masonry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  grid-auto-rows: 20px;
  grid-gap: 16px;
}

.masonry-item {
  width: 100%;
  cursor: pointer;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  transition: transform 0.3s ease;
  background: #f5f5f5;
}

.masonry-item:hover {
  transform: translateY(-4px);
}

.masonry-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.loading, .no-images {
  text-align: center;
  margin: 40px 0;
  color: #888;
  font-size: 1.2rem;
}

.pagination {
  margin: 32px 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.pagination button {
  padding: 8px 16px;
  border: none;
  background: #333;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .masonry-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
  
  .category-title {
    font-size: 1.5rem;
    margin-bottom: 24px;
  }
}
</style> 