<template>
  <!-- <Header/> -->
  <div class="container">
    <div class="sidebar-box">
      <Sidebar class="sidebar" :categories="dynamicCategories" :selectedCategory="selectedCategory"
        @select-category="selectCategory" ref="sidebarRef" />
      <AlbumManager :categories="dynamicCategories" :albums="albums" class="album-manager"
        @select-category="handleAlbumCategorySelect" />
      <!-- From Uiverse.io by csemszepp -->
      <Uploader :categories="dynamicCategories" @upload-success="handleUploadSuccess"
        @category-created="addNewCategory">
        <!-- 自定义触发区域 -->
        <!-- <template #trigger>
          <div class="custom-upload-trigger">
            <Uploader />
          </div>
        </template> -->
      </Uploader>
    </div>


    <div class="main" ref="mainRef">
      <!-- <input class="searchBox"
        v-model="searchKeyword" 
        placeholder="输入标签搜索..."
      /> -->

      <div class="input-wrapper-box">
        <button class="back-btn" :disabled="!isSearchActive" @click="resetSearch">
          <img src="/svg/backicon.svg" class="backsvg">

        </button>
        <!-- From Uiverse.io by vinodjangid07 -->
        <div class="input-wrapper">

          <img src="/svg/searchicon.svg" class="icon">
          <input type="text" name="text" class="input" placeholder="输入标签搜索..." v-model="searchKeyword" />
          <button class="Subscribe-btn" @click="performSearch">
            <svg xmlns="http://www.w3.org/2000/svg" width="30" height="10" viewBox="0 0 38 15" class="arrow">
              <path
                d="M10 7.519l-.939-.344h0l.939.344zm14.386-1.205l-.981-.192.981.192zm1.276 5.509l.537.843.148-.094.107-.139-.792-.611zm4.819-4.304l-.385-.923h0l.385.923zm7.227.707a1 1 0 0 0 0-1.414L31.343.448a1 1 0 0 0-1.414 0 1 1 0 0 0 0 1.414l5.657 5.657-5.657 5.657a1 1 0 0 0 1.414 1.414l6.364-6.364zM1 7.519l.554.833.029-.019.094-.061.361-.23 1.277-.77c1.054-.609 2.397-1.32 3.629-1.787.617-.234 1.17-.392 1.623-.455.477-.066.707-.008.788.034.025.013.031.021.039.034a.56.56 0 0 1 .058.235c.029.327-.047.906-.39 1.842l1.878.689c.383-1.044.571-1.949.505-2.705-.072-.815-.45-1.493-1.16-1.865-.627-.329-1.358-.332-1.993-.244-.659.092-1.367.305-2.056.566-1.381.523-2.833 1.297-3.921 1.925l-1.341.808-.385.245-.104.068-.028.018c-.011.007-.011.007.543.84zm8.061-.344c-.198.54-.328 1.038-.36 1.484-.032.441.024.94.325 1.364.319.45.786.64 1.21.697.403.054.824-.001 1.21-.09.775-.179 1.694-.566 2.633-1.014l3.023-1.554c2.115-1.122 4.107-2.168 5.476-2.524.329-.086.573-.117.742-.115s.195.038.161.014c-.15-.105.085-.139-.076.685l1.963.384c.192-.98.152-2.083-.74-2.707-.405-.283-.868-.37-1.28-.376s-.849.069-1.274.179c-1.65.43-3.888 1.621-5.909 2.693l-2.948 1.517c-.92.439-1.673.743-2.221.87-.276.064-.429.065-.492.057-.043-.006.066.003.155.127.07.099.024.131.038-.063.014-.187.078-.49.243-.94l-1.878-.689zm14.343-1.053c-.361 1.844-.474 3.185-.413 4.161.059.95.294 1.72.811 2.215.567.544 1.242.546 1.664.459a2.34 2.34 0 0 0 .502-.167l.15-.076.049-.028.018-.011c.013-.008.013-.008-.524-.852l-.536-.844.019-.012c-.038.018-.064.027-.084.032-.037.008.053-.013.125.056.021.02-.151-.135-.198-.895-.046-.734.034-1.887.38-3.652l-1.963-.384zm2.257 5.701l.791.611.024-.031.08-.101.311-.377 1.093-1.213c.922-.954 2.005-1.894 2.904-2.27l-.771-1.846c-1.31.547-2.637 1.758-3.572 2.725l-1.184 1.314-.341.414-.093.117-.025.032c-.01.013-.01.013.781.624zm5.204-3.381c.989-.413 1.791-.42 2.697-.307.871.108 2.083.385 3.437.385v-2c-1.197 0-2.041-.226-3.19-.369-1.114-.139-2.297-.146-3.715.447l.771 1.846z"
                fill="white">
              </path>
            </svg>搜索
          </button>
        </div>
      </div>



      <!-- 批量操作工具栏 -->
      <div v-if="isSelectionMode" class="batch-toolbar">
        <div class="batch-info">
          <span>已选择 {{ selectedImages.length }} 张图片</span>
          <button 
            v-if="filteredImages.length > 0" 
            @click="toggleSelectAll" 
            class="select-all-btn"
          >
            {{ isAllSelected ? '取消全选' : '全选' }}
          </button>
        </div>
        <div class="batch-actions">
          <button 
            @click="batchFavorite" 
            :disabled="selectedImages.length === 0" 
            class="batch-btn favorite-btn"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
            </svg>
            批量收藏
          </button>
          <button 
            @click="batchDelete" 
            :disabled="selectedImages.length === 0" 
            class="batch-btn delete-btn"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2 2v2"></path>
              <line x1="10" y1="11" x2="10" y2="17"></line>
              <line x1="14" y1="11" x2="14" y2="17"></line>
            </svg>
            批量删除
          </button>
          <button @click="exitSelectionMode" class="batch-btn cancel-btn">
            取消选择
          </button>
        </div>
      </div>

      <!-- 切换选择模式按钮 -->
      <div v-if="!isSelectionMode && filteredImages.length > 0" class="selection-toggle">
        <button @click="enterSelectionMode" class="selection-mode-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 11H3a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-6"></path>
            <path d="M14 3l7 7-10 10H3v-8L13 2l1 1z"></path>
          </svg>
          批量选择
        </button>
      </div>

      <div class="image-grid">
        <transition-group name="image-fade" tag="div" class="image-grid-inner">
          <div 
            v-for="image in filteredImages" 
            :key="image.id" 
            class="image-item" 
            :class="{ 'selection-mode': isSelectionMode, 'selected': selectedImages.includes(image.id) }"
            @click="isSelectionMode ? toggleImageSelection(image.id) : viewDetail(image.id)"
          >
            <!-- 选择模式下的复选框 -->
            <div v-if="isSelectionMode" class="selection-checkbox">
              <input 
                type="checkbox" 
                :checked="selectedImages.includes(image.id)"
                @click.stop="toggleImageSelection(image.id)"
              />
            </div>
            
            <img :src="image.thumbnail" />
            
            <!-- 非选择模式下的操作菜单 -->
            <ImageItemMenu 
              v-if="!isSelectionMode"
              :imageId="image.id"
              :imageTitle="image.title"
              :isPublic="image.is_public"
              :imageUrl="image.image_url"
              @image-deleted="handleImageDelete" 
            />
          </div>
        </transition-group>
      </div>

      <!-- 分页控件 -->
      <div class="pagination" v-if="shouldShowPagination">
        <button 
          class="pagination-btn" 
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          上一页
        </button>
        <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
        <button 
          class="pagination-btn" 
          :disabled="currentPage >= totalPages"
          @click="changePage(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import 'element-plus/dist/index.css'
import Sidebar from '@/components/Sidebar.vue'
import Uploader from '@/components/Uploader.vue'
import Header from "../components/Header.vue"
import ImageItemMenu from '../components/ImageItemMenu.vue'
import AlbumManager from '../components/AlbumManager.vue'
import imageService from '../api/imageService'
import albumService from '../api/albumService'

const router = useRouter()
const images = ref([])
const loading = ref(false)
const error = ref(null)

// 批量操作相关状态
const isSelectionMode = ref(false)
const selectedImages = ref([])

// 维护一个全局的分类集合
const allCategories = ref(['全部'])

// 动态分类列表（实际用于 Sidebar 和 Uploader）
const dynamicCategories = allCategories

// 从图片列表中提取所有分类
const extractCategories = (imageList) => {
  const categories = new Set(['全部'])
  imageList.forEach(image => {
    if (image.category) {
      categories.add(image.category)
    }
  })
  return Array.from(categories)
}

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(12) // 每页显示12张图片
const totalImages = ref(0)
const totalPages = computed(() => Math.ceil(totalImages.value / pageSize.value))

// 搜索和分类相关状态
const selectedCategory = ref('全部')
const searchKeyword = ref('')
const isSearchActive = ref(false)

// 监听搜索和分类变化
watch([searchKeyword, selectedCategory], () => {
  currentPage.value = 1 // 重置页码
  fetchImages()
})

// 获取图片列表
const fetchImages = async () => {
  loading.value = true
  error.value = null
  try {
    // 获取所有图片，不进行分页
    const response = await imageService.getUserImages({
      category: selectedCategory.value === '全部' ? undefined : selectedCategory.value,
      search: searchKeyword.value || undefined,
      page_size: 1000 // 设置一个足够大的数字以获取所有图片
    })

    if (!response) {
      throw new Error('获取图片列表失败：响应为空')
    }

    // 确保response.results存在
    const imageList = response.results || []
    if (!Array.isArray(imageList)) {
      console.error('图片列表格式错误:', imageList)
      throw new Error('获取图片列表失败：数据格式错误')
    }
    // 更新图片列表
    images.value = imageList.map(image => ({
      id: image.id,
      thumbnail: image.image_url,
      title: image.title || '未命名',
      is_public: image.is_public || false,
      image_url: image.image_url,
      category: image.category || '未分类',
      tags: parseTags(image.tags),
      size: formatFileSize(image.file_size),
      dimensions: `${image.width || 0}x${image.height || 0}`,
      type: image.file_type || '未知',
      createdAt: new Date(image.created_at).toLocaleString()
    }))

    // 更新分类列表
    const extracted = extractCategories(images.value)
    allCategories.value = Array.from(new Set([...allCategories.value, ...extracted]))

    // 如果没有图片，显示提示信息
    if (images.value.length === 0) {
      ElMessage.info('当前没有图片，请上传新图片')
    }
  } catch (err) {
    console.error('获取图片列表失败:', err)
    error.value = err.message || '获取图片列表失败，请稍后重试'
    images.value = []
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 切换页面
const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  // 滚动到顶部
  if (mainRef.value) {
    mainRef.value.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }
}

// 文件大小格式化
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

// 添加parseTags函数
const parseTags = (tags) => {
  if (!tags) return []
  
  try {
    // 如果已经是数组，直接返回
    if (Array.isArray(tags)) {
      return tags
    }
    
    // 如果是字符串，尝试解析JSON
    if (typeof tags === 'string') {
      try {
        const parsedTags = JSON.parse(tags)
        if (Array.isArray(parsedTags)) {
          return parsedTags.flatMap(tag => {
            // 如果标签包含冒号，提取冒号后的值
            if (typeof tag === 'string' && tag.includes(':')) {
              const value = tag.split(':')[1].trim()
              return value.replace(/['"]/g, '')
                .split(',')
                .map(t => t.trim())
                .filter(t => t)
            }
            return [tag]
          })
        }
        return [parsedTags]
      } catch {
        // 如果JSON解析失败，按逗号分隔
        return tags.split(',')
          .map(tag => tag.trim())
          .filter(tag => tag)
      }
    }
    
    return []
  } catch (error) {
    console.error('标签解析错误:', error)
    return []
  }
}

// 修改 filteredImages 计算属性
const filteredImages = computed(() => {
  // 先进行过滤
  const filtered = images.value.filter(img => {
    const matchesCategory = selectedCategory.value === '全部' || img.category === selectedCategory.value
    
    let matchesTag = true
    if (searchKeyword.value) {
      const searchTerm = searchKeyword.value.toLowerCase()
      matchesTag = Array.isArray(img.tags) && img.tags.some(tag => 
        String(tag).toLowerCase().includes(searchTerm)
      )
    }

    return matchesCategory && matchesTag
  })

  // 更新总数 - 使用过滤后的数量
  totalImages.value = filtered.length

  // 计算分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value

  console.log('分页信息:', {
    totalImages: totalImages.value,
    currentPage: currentPage.value,
    pageSize: pageSize.value,
    start,
    end,
    filteredLength: filtered.length,
    resultLength: filtered.slice(start, end).length
  })

  // 返回当前页的数据
  return filtered.slice(start, end)
})

// 添加 refs
const mainRef = ref(null)
const sidebarRef = ref(null)
const categoryRefs = ref({})

// 修改 selectCategory 函数
const selectCategory = (category) => {
  selectedCategory.value = category
  currentPage.value = 1 // 重置页码
  fetchImages()
}

// 添加滚动到指定分类的方法
const scrollToCategory = (category) => {
  // 获取该分类下的第一个图片元素
  const targetElement = categoryRefs.value[category]
  if (targetElement && mainRef.value) {
    // 计算目标位置
    const containerRect = mainRef.value.getBoundingClientRect()
    const targetRect = targetElement.getBoundingClientRect()
    const scrollTop = targetRect.top - containerRect.top + mainRef.value.scrollTop

    // 使用平滑滚动
    mainRef.value.scrollTo({
      top: scrollTop,
      behavior: 'smooth'
    })
  }
}

// 修改 handleAlbumCategorySelect 函数
const handleAlbumCategorySelect = (category) => {
  selectedCategory.value = category
  currentPage.value = 1 // 重置页码
  fetchImages()
}

// 修改 performSearch 函数
function performSearch() {
  isSearchActive.value = true
  currentPage.value = 1 // 重置页码
  fetchImages()
}

function resetSearch() {
  searchKeyword.value = ''
  isSearchActive.value = false
  currentPage.value = 1 // 重置页码
  fetchImages()
}

// 查看图片详情
const viewDetail = (id) => {
  router.push(`/photodetail/${id}?fromGallery=true`)
}

const handleUploadSuccess = async (uploadedImages) => {
  console.log('上传成功，重新获取图片列表和相册列表')
  await Promise.all([
    fetchImages(),
    fetchAlbums()
  ])
}

const addNewCategory = (newCategory) => {
  const category = newCategory.toString().trim()
  if (!category) return

  console.log('添加新分类:', category)

  // 避免重复
  if (!allCategories.value.includes(category)) {
    allCategories.value.push(category)
    console.log('更新后的分类列表:', allCategories.value)
  }
  // 自动选中新分类
  selectedCategory.value = category
  console.log('当前选中的分类:', selectedCategory.value)
  // 更新过滤后的图片列表
  performSearch()
}

const selectedImage = ref(null)

// 选择图片来显示菜单
const selectImage = (image) => {
  selectedImage.value = image
}

// 处理图片删除
const handleImageDelete = async (imageId) => {
  try {
    console.log('开始处理图片删除:', imageId)
    // 直接从列表中移除图片
    images.value = images.value.filter(img => img.id !== imageId)
    console.log('已从列表中移除图片，剩余图片数:', images.value.length)

    // 重新获取图片列表以确保数据同步
    await fetchImages()
    console.log('图片列表已更新')
  } catch (error) {
    console.error('处理图片删除失败:', error)
    // 如果更新失败，尝试重新获取图片列表
    try {
      await fetchImages()
    } catch (refreshError) {
      console.error('刷新图片列表失败:', refreshError)
      ElMessage.error('更新图片列表失败，请刷新页面')
    }
  }
}

const albums = ref([])

// 获取相册列表
const fetchAlbums = async () => {
  try {
    const response = await albumService.getUserAlbums()
    console.log('获取相册列表响应:', response)

    if (response && response.data) {
      // 处理相册数据，确保包含分类信息
      albums.value = response.data.map(album => {
        const category = album.title.replace('相册', '').trim()
        console.log('处理相册数据:', {
          id: album.id,
          title: album.title,
          category: category
        })
        return {
          ...album,
          category: category,
          title: album.title // 保持原始标题
        }
      })
      console.log('处理后的相册列表:', albums.value)
    } else {
      console.error('获取相册列表失败：响应格式错误', response)
    }
  } catch (error) {
    console.error('获取相册列表失败:', error)
  }
}

// 监听分类变化，更新相册列表
watch(selectedCategory, async (newCategory) => {
  console.log('分类变化:', newCategory)
  // 只在初始加载时获取所有相册
  if (albums.value.length === 0) {
    await fetchAlbums()
  }
})

// 批量操作方法
const enterSelectionMode = () => {
  isSelectionMode.value = true
  selectedImages.value = []
}

const exitSelectionMode = () => {
  isSelectionMode.value = false
  selectedImages.value = []
}

const toggleImageSelection = (imageId) => {
  const index = selectedImages.value.indexOf(imageId)
  if (index > -1) {
    selectedImages.value.splice(index, 1)
  } else {
    selectedImages.value.push(imageId)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedImages.value = []
  } else {
    selectedImages.value = filteredImages.value.map(img => img.id)
  }
}

const batchDelete = async () => {
  if (selectedImages.value.length === 0) {
    ElMessage.warning('请选择要删除的图片')
    return
  }

  // 确认对话框
  if (!confirm(`确定要删除选中的 ${selectedImages.value.length} 张图片吗？此操作无法撤销。`)) {
    return
  }

  try {
    loading.value = true
    const result = await imageService.batchDeleteImages(selectedImages.value)
    
    if (result.successful > 0) {
      ElMessage.success(`成功删除 ${result.successful} 张图片`)
      
      // 从本地列表中移除已删除的图片
      const deletedIds = new Set(selectedImages.value)
      images.value = images.value.filter(img => !deletedIds.has(img.id))
      
      // 重新获取图片列表以确保数据同步
      await fetchImages()
    }
    
    if (result.failed > 0) {
      ElMessage.warning(`${result.failed} 张图片删除失败`)
    }
    
    // 退出选择模式
    exitSelectionMode()
  } catch (error) {
    console.error('批量删除失败:', error)
    ElMessage.error('批量删除失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const batchFavorite = async () => {
  if (selectedImages.value.length === 0) {
    ElMessage.warning('请选择要收藏的图片')
    return
  }

  try {
    loading.value = true
    const result = await imageService.batchFavorite(selectedImages.value)
    if (result.successful > 0) {
      ElMessage.success(`成功收藏 ${result.successful} 张图片`)
    }
    if (result.failed > 0) {
      ElMessage.warning(`${result.failed} 张图片收藏失败`)
    }
    exitSelectionMode()
  } catch (error) {
    console.error('批量收藏失败:', error)
    ElMessage.error('批量收藏失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 在组件挂载时获取图片列表
onMounted(async () => {
  await Promise.all([
    fetchImages(),
    fetchAlbums()
  ])
})

// 添加计算属性判断是否显示分页
const shouldShowPagination = computed(() => {
  return totalImages.value > pageSize.value
})

// 批量操作相关计算属性
const isAllSelected = computed(() => {
  return filteredImages.value.length > 0 && selectedImages.value.length === filteredImages.value.length
})
</script>

<style scoped>
.person-store {
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s, color 0.3s;
}

.store-header {
  background-color: var(--secondary-color);
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.3s, border-color 0.3s;
}

.store-title {
  color: var(--text-color);
}

.store-description {
  color: var(--text-color);
  opacity: 0.8;
}

.upload-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  transition: background-color 0.3s;
}

.upload-btn:hover {
  background-color: var(--primary-color);
  opacity: 0.9;
}

.image-grid {
  background-color: var(--bg-color);
  transition: background-color 0.3s;
}

.image-card {
  background-color: var(--secondary-color);
  border: 1px solid var(--border-color);
  transition: background-color 0.3s, border-color 0.3s;
}

.image-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.image-title {
  color: var(--text-color);
}

.image-description {
  color: var(--text-color);
  opacity: 0.8;
}

.image-actions button {
  color: var(--text-color);
  background: none;
  border: none;
  transition: color 0.3s;
}

.image-actions button:hover {
  color: var(--primary-color);
}

.container {
  display: flex;
  height: 90vh;
  overflow: hidden;
  width: 100%;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s, color 0.3s;
}

.sidebar-box {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
  padding: 16px;
  width: 240px;
  background-color: var(--secondary-color);
  color: var(--text-color);
  transition: background-color 0.3s, border-color 0.3s, color 0.3s;

  .sidebar {
    flex: 1;
    margin-bottom: 20px;
  }

  .album-manager {
    margin-bottom: 20px;
  }

  /* From Uiverse.io by csemszepp */
  .custum-file-upload {
    height: 25vh;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: space-between;
    gap: 20px;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    border: 2px solid #3a3a3a;
    border-radius: 8px;
    background-color: rgb(38, 38, 38);
    transition: all 0.3s ease;
  }

  .custum-file-upload:hover {
    border-color: #176fd4;
    background-color: #303030;
  }

  .custum-file-upload .icon {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .custum-file-upload .icon svg {
    height: 80px;
    fill: #e8e8e8;
  }

  .custum-file-upload .text {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .custum-file-upload .text span {
    font-weight: 400;
    color: #e8e8e8;
  }

  .custum-file-upload input {
    display: none;
  }
}

.main {
  scroll-behavior: smooth;
  overflow-y: auto;
  flex: 1;
  padding: 20px 24px;
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) var(--bg-color);
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s, color 0.3s;
}

.main::-webkit-scrollbar {
  width: 8px;
}

.main::-webkit-scrollbar-track {
  background: var(--bg-color);
}

.main::-webkit-scrollbar-thumb {
  background-color: var(--border-color);
  border-radius: 4px;
}

.image-grid {
  width: 100%;
  padding: 10px 0;
}

.image-grid-inner {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  grid-gap: 24px;
}

.image-item {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  transition: all 0.3s ease;
  background-color: var(--secondary-color);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.image-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
  border-color: var(--primary-color);
}

.image-item img {
  width: 100%;
  height: 240px;
  object-fit: cover;
  transition: all 0.5s ease;
}

.image-item:hover img {
  transform: scale(1.05);
}

.meta {
  padding: 12px 16px;
  font-size: 0.9em;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  background-color: #2b2b2b;
  color: #e8e8e8;
  border-top: 1px solid #3a3a3a;
}

.searchBox {
  margin-top: 10px;
  margin-bottom: 10px;
  height: 25px;
}

.input-wrapper-box {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 24px;
}

.back-btn {
  margin-right: 12px;
  padding: 8px 14px;
  background-color: var(--secondary-color);
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  color: var(--text-color);
  transition: all 0.3s ease;
}

.back-btn:hover:not(:disabled) {
  background-color: var(--primary-color);
  color: white;
}

.back-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  color: var(--text-color);
}

.backsvg {
  height: 20px;
  margin-right: 8px;
  filter: brightness(0.6);
  transition: filter 0.3s ease;
}

.back-btn:hover:not(:disabled) .backsvg {
  filter: brightness(1);
}

.input-wrapper {
  width: fit-content;
  height: 48px;
  border-radius: 24px;
  padding: 5px;
  box-sizing: content-box;
  display: flex;
  align-items: center;
  background-color: var(--secondary-color);
  color: var(--text-color);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.input-wrapper:focus-within {
  box-shadow: 0 2px 15px rgba(23, 111, 212, 0.3);
}

.icon {
  width: 30px;
  fill: rgb(255, 255, 255);
  margin-left: 12px;
  transition: all 0.3s;
  filter: brightness(0.6);
}

.input-wrapper:focus-within .icon {
  filter: brightness(1);
}

.input {
  width: 200px;
  height: 100%;
  border: none;
  outline: none;
  padding-left: 15px;
  background-color: transparent;
  color: var(--text-color);
  font-size: 1em;
  transition: color 0.3s;
}

.input:-webkit-autofill {
  -webkit-box-shadow: 0 0 0px 1000px var(--secondary-color) inset;
  -webkit-text-fill-color: var(--text-color);
}

.Subscribe-btn {
  height: 80%;
  padding: 0 20px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  background-color: var(--primary-color);
  color: var(--text-color);
  font-weight: 500;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s;
  margin-right: 6px;
}

.Subscribe-btn:hover {
  background-color: var(--primary-color);
  opacity: 0.9;
}

.arrow {
  position: absolute;
  margin-right: 150px;
  transition: all 0.3s;
}

.input-wrapper:active .icon {
  transform: scale(1.3);
}

.Subscribe-btn:hover {
  background-color: #2180ea;
}

.Subscribe-btn:hover .arrow {
  margin-right: 0;
  animation: jello-vertical 0.9s both;
  transform-origin: right;
}

@keyframes jello-vertical {
  0% {
    transform: scale3d(1, 1, 1);
  }

  30% {
    transform: scale3d(0.75, 1.25, 1);
  }

  40% {
    transform: scale3d(1.25, 0.75, 1);
  }

  50% {
    transform: scale3d(0.85, 1.15, 1);
  }

  65% {
    transform: scale3d(1.05, 0.95, 1);
  }

  75% {
    transform: scale3d(0.95, 1.05, 1);
  }

  100% {
    transform: scale3d(1, 1, 1);
  }
}

.Subscribe-btn:active {
  transform: scale(0.95);
}

/* 添加淡入淡出动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .container {
    flex-direction: column;
  }

  .sidebar-box {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid #3a3a3a;
  }

  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }
}

/* 图片项过渡动画 */
.image-fade-move {
  transition: transform 0.5s ease;
}

.image-fade-enter-active {
  transition: all 0.5s ease;
}

.image-fade-leave-active {
  transition: all 0.3s ease;
  position: absolute;
}

.image-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.image-fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* 添加分类标记样式 */
.image-item[data-category] {
  scroll-margin-top: 20px;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 16px;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--secondary-color);
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-color);
  font-size: 14px;
}

/* 批量操作样式 */
.batch-toolbar {
  background-color: var(--secondary-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  transition: background-color 0.3s, border-color 0.3s;
}

.batch-info {
  display: flex;
  align-items: center;
  gap: 16px;
  color: var(--text-color);
  font-size: 14px;
}

.select-all-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: opacity 0.3s;
}

.select-all-btn:hover {
  opacity: 0.9;
}

.batch-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.batch-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.batch-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.favorite-btn {
  background-color: #ff6b35;
  color: white;
}

.favorite-btn:hover:not(:disabled) {
  background-color: #e55a2e;
  transform: translateY(-1px);
}

.delete-btn {
  background-color: var(--error-color);
  color: white;
}

.delete-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.cancel-btn {
  background-color: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.cancel-btn:hover {
  background-color: var(--border-color);
}

.selection-toggle {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.selection-mode-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.selection-mode-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* 选择模式下的图片项样式 */
.image-item.selection-mode {
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.image-item.selection-mode:hover {
  border-color: var(--primary-color);
  transform: scale(1.02);
}

.image-item.selected {
  border-color: var(--primary-color) !important;
  background-color: rgba(23, 111, 212, 0.1);
}

.selection-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  padding: 4px;
  transition: background-color 0.3s;
}

.selection-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--primary-color);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .batch-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .batch-actions {
    justify-content: center;
  }

  .batch-btn {
    flex: 1;
    justify-content: center;
    min-width: 0;
  }
}
</style>