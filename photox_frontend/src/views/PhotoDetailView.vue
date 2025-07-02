<template>
  <!-- 彻底移除全局loading蒙层 -->

  <!-- 错误状态 -->
  <div v-if="error" class="error-container">
    <div class="error-icon">⚠️</div>
    <h3>加载失败</h3>
    <p>{{ error }}</p>
    <button @click="fetchImageDetail" class="retry-btn">重试</button>
  </div>

  <!-- 图片详情内容 -->
  <div v-else-if="image" class="detail-container">
    <!-- 左侧图片区域 -->
    <div class="image-section" :class="{ 'expanded': !showInfo }">
      <DetailViewer
        :currentImage="currentImage"
        @previous="goToPrevious"
        @next="goToNext"
        @back="goBack"
        @download="downloadImage"
        @save="saveToAlbum"
        :showNavigation="currentImageList.length > 1"
        :showBackButton="true"
      />
    </div>

    <!-- 右侧信息区域组件化 -->
    <ImageInfoPanel :image="image" :showInfo="showInfo" :formatTags="formatTags" :formatDate="formatDate"
      :imageDimensions="imageDimensions" :imageSizeMB="imageSizeMB" :imageFormat="imageFormat"
      :formatColor="formatColor" :formatColorDisplay="formatColorDisplay" :currentUser="currentUser.username"
      :currentUserId="currentUser.id" :isFollowing="isFollowing" @toggle-info="toggleInfo" @follow-user="toggleFollowUser" @unfollow-user="toggleFollowUser" />
  </div>

  <!-- 评论区/相关推荐切换按钮 -->
  <div class="toggle-section" v-if="!loading && image">
    <button :class="['btn-comment', { active: showCommentSection }]" @click="showCommentSection = true">评论区</button>
    <button :class="['btn-related', { active: !showCommentSection }]" @click="showCommentSection = false">相关推荐</button>
  </div>

  <!-- 评论区组件 -->
  <CommentSection v-if="showCommentSection && image" :comments="comments" :likeCount="likeCount" :likedByMe="likedByMe"
    :currentUser="currentUser" @toggle-like="toggleLike" @toggle-comment-like="toggleCommentLike"
    @toggle-reply-like="toggleReplyLike" @submit-comment="submitComment" @submit-reply="submitReply"
    @delete-comment="deleteComment" @delete-reply="deleteReply" />

  <!-- 相关推荐 -->
  <RelatedImages v-if="!loading && !showCommentSection && image" :currentImage="image"
    :formatTags="formatTags" :loading="false" />
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiService from '@/api'
import DetailViewer from '@/components/DetailViewer.vue'
import CommentSection from '@/components/CommentSection.vue'
import ImageInfoPanel from '@/components/ImageInfoPanel.vue'
import RelatedImages from '@/components/RelatedImages.vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const image = ref(null)
const loading = ref(true)
const error = ref(null)

// 添加图片列表状态
const currentImageList = ref([])
const currentImageIndex = ref(-1)

// 当前图片信息
const currentImage = computed(() => {
  if (!image.value) return ''
  return image.value.image_url || ''
})

// 标签值映射
const tagMap = {
  '968': 'cup',
  '549': 'envelope',
  '446': 'binder, ring-binder',
  '794': 'shower curtain',
  '844': 'switch, electric switch, electrical switch'
}

// 格式化标签显示
const formatTags = computed(() => {
  console.log('image.value.tags', image.value)
  if (!image.value?.tags) return []
  let tags = []

  try {
    // 尝试解析标签
    if (typeof image.value.tags === 'string') {
      try {
        // 首先尝试解析JSON
        const parsedTags = JSON.parse(image.value.tags)
        // 处理标签格式
        if (Array.isArray(parsedTags)) {
          tags = parsedTags.flatMap(tag => {
            // 如果标签是字符串且包含冒号，提取冒号后的值
            if (typeof tag === 'string' && tag.includes(':')) {
              const value = tag.split(':')[1].trim()
              // 移除引号，并按逗号分割成多个标签
              return value.replace(/['"]/g, '')
                .split(',')
                .map(t => t.trim())
                .filter(t => t) // 过滤掉空值
            }
            return [tag]
          })
        } else {
          tags = [parsedTags]
        }
      } catch {
        // 如果JSON解析失败，尝试按逗号分隔
        tags = image.value.tags.split(',').map(tag => tag.trim())
      }
    } else if (Array.isArray(image.value.tags)) {
      tags = image.value.tags.flatMap(tag => {
        if (typeof tag === 'string' && tag.includes(':')) {
          const value = tag.split(':')[1].trim()
          return value.replace(/['"]/g, '')
            .split(',')
            .map(t => t.trim())
            .filter(t => t) // 过滤掉空值
        }
        return [tag]
      })
    } else {
      return []
    }

    // 过滤掉空值并确保所有标签都是字符串
    return tags.map(tag => String(tag)).filter(tag => tag)
  } catch (error) {
    console.error('标签解析错误:', error)
    return []
  }
})

// 格式化日期显示
const formatDate = computed(() => {
  if (!image.value?.created_at) return '未知'
  return new Date(image.value.created_at).toLocaleString()
})

// 响应式图片信息
const imageDimensions = ref({ width: 0, height: 0 })
const imageSizeMB = ref('未知')
const imageFormat = ref('未知')

// 相关图片数据
const relatedImages = ref([])
const MAX_RELATED_IMAGES = 12
const MIN_TAG_MATCH_SCORE = 30 // 最小匹配度百分比

// 获取图片详情
const firstLoad = ref(true)

const fetchImageDetail = async (showLoading = true) => {
  try {
    if (showLoading) {
      loading.value = true
      firstLoad.value = true
    }
    error.value = null
    const id = Number(route.params.id)
    console.log('获取图片详情ID:', id)

    if (!id || isNaN(id)) {
      throw new Error('无效的图片ID')
    }

    // 使用正确的API调用方式
    const response = await apiService.api.get(`/images/${id}/`)
    console.log('获取图片详情响应:', response)

    if (!response) {
      throw new Error('获取图片信息失败：响应为空')
    }

    // 直接使用响应数据，因为拦截器已经返回了response.data
    image.value = response
    console.log('图片详情更新成功:', image.value)
    
    // 设置关注状态
    isFollowing.value = !!response.is_following_author
    console.log('设置关注状态:', isFollowing.value)

    // 获取相关图片列表用于导航
    await fetchRelatedImageList()
  } catch (err) {
    console.error('获取图片详情失败:', err)
    if (err.response?.status === 404) {
      error.value = '图片不存在或已被删除'
    } else if (err.response?.status === 401) {
      error.value = '请先登录后查看图片详情'
    } else {
      error.value = err.message || '获取图片信息失败，请稍后重试'
    }
  } finally {
    if (showLoading) loading.value = false
    firstLoad.value = false
  }
}

// 获取相关图片列表
const fetchRelatedImageList = async () => {
  try {
    console.log('开始获取相关图片列表')
    const id = Number(route.params.id)
    
    // 根据来源获取不同的图片列表
    let response
    
    // 获取当前用户信息
    const userStr = localStorage.getItem('user')
    let currentUserId = null
    if (userStr) {
      try {
        const userObj = JSON.parse(userStr)
        currentUserId = userObj.id
      } catch (e) {
        console.warn('解析用户信息失败:', e)
      }
    }
    
    if (route.query.fromHome) {
      // 从首页进入，获取公开图片列表
      response = await apiService.images.getList({
        is_public: true,
        ordering: '-created_at',
        page_size: 1000 // 获取足够多的图片
      })
    } else if (route.query.fromGallery) {
      // 从画廊进入，获取用户自己的图片
      response = await apiService.images.getList({
        ordering: '-created_at',
        page_size: 1000
      })
    } else if (route.query.fromCategory) {
      // 从分类详情页进入，获取公开图片列表
      response = await apiService.images.getList({
        is_public: true,
        ordering: '-created_at',
        page_size: 1000
      })
    } else if (route.query.fromOtherUser) {
      // 从其他用户主页进入，获取公开图片列表
      response = await apiService.images.getList({
        is_public: true,
        ordering: '-created_at',
        page_size: 1000
      })
    } else if (route.query.fromRelated) {
      // 从相关推荐进入，获取公开图片列表
      response = await apiService.images.getList({
        is_public: true,
        ordering: '-created_at',
        page_size: 1000
      })
    } else {
      // 没有查询参数时，需要智能判断
      // 首先检查当前图片的所有者
      if (image.value && image.value.user) {
        const imageOwnerId = typeof image.value.user === 'object' ? image.value.user.id : image.value.user
        
        if (currentUserId && imageOwnerId === currentUserId) {
          // 当前图片属于当前用户，获取用户自己的图片列表
          console.log('检测到当前图片属于当前用户，获取个人图片列表')
          response = await apiService.images.getList({
            ordering: '-created_at',
            page_size: 1000
          })
        } else {
          // 当前图片属于其他用户，获取公开图片列表
          console.log('检测到当前图片属于其他用户，获取公开图片列表')
          response = await apiService.images.getList({
            is_public: true,
            ordering: '-created_at',
            page_size: 1000
          })
        }
      } else {
        // 无法确定图片所有者，默认获取公开图片列表
        console.log('无法确定图片所有者，默认获取公开图片列表')
        response = await apiService.images.getList({
          is_public: true,
          ordering: '-created_at',
          page_size: 1000
        })
      }
    }

    console.log('获取图片列表响应:', response)
    
    if (!response) {
      console.error('获取图片列表失败：响应为空')
      return
    }

    // 获取图片列表数据
    const images = response.results || response
    console.log('图片列表:', images)

    if (!Array.isArray(images)) {
      console.error('获取图片列表失败：数据格式错误')
      return
    }

    // 更新当前图片列表
    currentImageList.value = images
    
    // 找到当前图片在列表中的索引
    const index = images.findIndex(img => img.id === id)
    currentImageIndex.value = index
    console.log('当前图片索引:', index, '列表长度:', images.length)
  } catch (error) {
    console.error('获取相关图片列表失败:', error)
    currentImageList.value = []
    currentImageIndex.value = -1
  }
}

// 读取图片尺寸
const loadImageDimensions = (imgSrc) =>
  new Promise((resolve) => {
    const tempImg = new Image()
    tempImg.src = imgSrc
    tempImg.onload = () => {
      resolve({ width: tempImg.naturalWidth, height: tempImg.naturalHeight })
    }
    tempImg.onerror = () => {
      resolve({ width: 0, height: 0 })
    }
  })

// 读取图片大小
async function loadImageSize(imgSrc) {
  try {
    const response = await fetch(imgSrc)
    if (response.ok) {
      const blob = await response.blob()
      const sizeInMB = (blob.size / (1024 * 1024)).toFixed(2)
      return sizeInMB
    }
  } catch (e) {
    console.warn('获取图片大小失败:', e)
  }
  return '未知'
}

// 检测图片格式
function detectImageFormat(imgSrc) {
  const ext = imgSrc.split('.').pop().toUpperCase()
  const commonFormats = ['JPG', 'JPEG', 'PNG', 'GIF', 'WEBP', 'BMP', 'SVG']
  if (commonFormats.includes(ext)) return ext
  return '未知'
}

// 下载图片
const downloadImage = () => {
  if (!currentImage.value) return

  const link = document.createElement('a')
  link.href = currentImage.value

  // 创建有意义的文件名：分类名_标题.jpg
  const fileName = `${image.value?.category || 'untitled'}_${image.value?.title || 'untitled'}.jpg`

  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 转存图片
const saveToAlbum = async () => {
  try {
    if (!image.value?.image_url) {
      alert('图片数据不完整，无法保存');
      return;
    }

    // 检查个人仓库中是否已有此图片
    const myImages = await apiService.images.getList();

    // 获取当前图片的原始URL（去除查询参数）
    const currentImageUrl = new URL(image.value.image_url);
    const currentImagePath = currentImageUrl.pathname;

    // 检查是否存在相同路径的图片
    const existingImage = myImages.results.find(img => {
      if (!img.image_url) return false;
      try {
        const imgUrl = new URL(img.image_url);
        return imgUrl.pathname === currentImagePath;
      } catch {
        return false;
      }
    });

    if (existingImage) {
      alert('该图片已存在于您的个人仓库中');
      return;
    }

    // 1. 下载图片为 blob
    const response = await fetch(image.value.image_url);
    if (!response.ok) {
      throw new Error('下载图片失败');
    }
    const blob = await response.blob();

    // 2. 构造 File 对象
    const fileName = `${image.value?.category || 'untitled'}_${image.value?.title || 'untitled'}.jpg`;
    const file = new File([blob], fileName, { type: blob.type });

    // 3. 构造 FormData
    const formData = new FormData();
    formData.append('image', file);
    formData.append('title', image.value.title || '');
    if (image.value.category) formData.append('category', image.value.category);
    formData.append('is_public', false); // 默认设置为私有

    // 4. 上传到后端
    const uploadResp = await apiService.images.upload(formData);

    if (uploadResp?.data?.id || uploadResp?.data?.data?.id) {
      alert('图片已成功保存到个人仓库！');
    } else {
      throw new Error('上传失败');
    }
  } catch (err) {
    console.error('保存到个人仓库失败:', err);
    if (err.message === '下载图片失败') {
      alert('下载图片失败，请检查网络连接');
    } else if (err.message === '上传失败') {
      alert('上传失败，请稍后重试');
    } else {
      alert('保存失败，请检查网络或登录状态');
    }
  }
};

// 格式化颜色值
const formatColor = (color) => {
  // 如果已经是有效的颜色值，直接返回
  if (/^#([0-9A-F]{3}){1,2}$/i.test(color) ||
    /^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$/i.test(color) ||
    /^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$/i.test(color)) {
    return color
  }

  // 如果是数字数组格式 [r, g, b]
  if (Array.isArray(color) && color.length >= 3) {
    return `rgb(${color[0]}, ${color[1]}, ${color[2]})`
  }

  // 如果是对象格式 {r: 255, g: 255, b: 255}
  if (typeof color === 'object' && color !== null) {
    if ('r' in color && 'g' in color && 'b' in color) {
      return `rgb(${color.r}, ${color.g}, ${color.b})`
    }
  }

  // 默认返回黑色
  return '#000000'
}

// 格式化颜色显示值
const formatColorDisplay = (color) => {
  const formattedColor = formatColor(color)
  if (formattedColor.startsWith('rgb')) {
    // 将 rgb 转换为 hex
    const rgb = formattedColor.match(/\d+/g)
    if (rgb && rgb.length >= 3) {
      const hex = '#' + rgb.map(x => {
        const hex = parseInt(x).toString(16)
        return hex.length === 1 ? '0' + hex : hex
      }).join('')
      return hex.toUpperCase()
    }
  }
  return formattedColor.toUpperCase()
}

// 监听图片变化
watch(
  currentImage,
  async (newSrc) => {
    if (!newSrc) return
    imageDimensions.value = await loadImageDimensions(newSrc)
    // 使用后端返回的图片大小数据
    if (image.value?.size) {
      imageSizeMB.value = (image.value.size / (1024 * 1024)).toFixed(2)
    } else {
      imageSizeMB.value = await loadImageSize(newSrc)
    }
    imageFormat.value = detectImageFormat(newSrc)
  },
  { immediate: true }
)

// 导航功能
const goBack = () => {
  if (route.query.fromHome) {
    router.push('/')
  } else if (route.query.fromGallery) {
    router.push('/gallery');
  } else {
    router.back();
  }
};

// 切换到上一张图片
const goToPrevious = async () => {
  try {
    console.log('开始获取上一张图片')
    
    if (currentImageIndex.value <= 0) {
      console.log('已经是第一张图片')
      return
    }

    const previousImage = currentImageList.value[currentImageIndex.value - 1]
    console.log('上一张图片:', previousImage)

    if (!previousImage) {
      console.error('未找到上一张图片')
      return
    }

    try {
      // 更新路由参数
      await router.replace({
        path: `/photodetail/${previousImage.id}`,
        query: route.query
      })
      console.log('路由更新成功')

      // 重新获取图片详情（不显示loading）
      await fetchImageDetail(false)
      console.log('图片详情更新完成')
    } catch (error) {
      console.error('更新图片失败:', error)
    }
  } catch (error) {
    console.error('获取上一张图片失败:', error)
  }
}

// 切换到下一张图片
const goToNext = async () => {
  try {
    console.log('开始获取下一张图片')
    
    if (currentImageIndex.value >= currentImageList.value.length - 1) {
      console.log('已经是最后一张图片')
      return
    }

    const nextImage = currentImageList.value[currentImageIndex.value + 1]
    console.log('下一张图片:', nextImage)

    if (!nextImage) {
      console.error('未找到下一张图片')
      return
    }

    try {
      // 更新路由参数
      await router.replace({
        path: `/photodetail/${nextImage.id}`,
        query: route.query
      })
      console.log('路由更新成功')

      // 重新获取图片详情（不显示loading）
      await fetchImageDetail(false)
      console.log('图片详情更新完成')
    } catch (error) {
      console.error('更新图片失败:', error)
    }
  } catch (error) {
    console.error('获取下一张图片失败:', error)
  }
}

// 键盘导航支持
const handleKeyDown = (e) => {
  if (e.key === 'Escape') goBack()
  if (e.key === 'ArrowLeft') goToPrevious()
  if (e.key === 'ArrowRight') goToNext()
}

// 添加信息面板状态控制
const showInfo = ref(true)

const toggleInfo = () => {
  showInfo.value = !showInfo.value
}

// 点赞和评论相关响应式数据
const likeCount = ref(0)
const likedByMe = ref(false)
const comments = ref([])
const newComment = ref('')

// 获取点赞状态和数量（真实API）
async function fetchLikeStatus() {
  if (!image.value) return
  try {
    // 检查是否已点赞并获取点赞数
    const res = await apiService.api.get('/community/likes/check/', {
      params: {
        like_type: 'image',
        object_id: image.value.id
      }
    })
    likedByMe.value = res.liked
    likeCount.value = res.like_count || 0
  } catch (e) {
    likeCount.value = 0
    likedByMe.value = false
  }
}

// 切换点赞（真实API）
async function toggleLike() {
  if (!image.value) return

  // 检查登录状态
  const token = localStorage.getItem('token')
  if (!token) {
    alert('请先登录后再点赞')
    return
  }

  try {
    const res = await apiService.api.post('/community/likes/toggle/', {
      like_type: 'image',
      object_id: image.value.id
    })
    likedByMe.value = res.liked
    likeCount.value = res.like_count
  } catch (e) {
    console.error('图片点赞失败:', e)
    if (e.response?.status === 401) {
      alert('登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    } else {
      alert('点赞失败，请稍后重试')
    }
  }
}

// 获取评论（真实API）
async function fetchComments() {
  if (!image.value) return
  try {
    const res = await apiService.api.get('/community/comments/', { params: { image: image.value.id } })
    comments.value = (res.results || res.data || []).map(c => ({
      ...c,
      author: c.user?.username || '匿名',
      time: formatTime(c.created_at),
      likeCount: c.like_count || 0,
      likedByMe: c.is_liked || false,
      replies: (c.replies || []).map(r => ({
        ...r,
        author: r.user?.username || '匿名',
        time: formatTime(r.created_at),
        likeCount: r.like_count || 0,
        likedByMe: r.is_liked || false
      }))
    }))
  } catch (e) {
    console.error('获取评论失败:', e)
    comments.value = []
  }
}

// 格式化时间
function formatTime(timeStr) {
  if (!timeStr) return '未知时间'
  try {
    const date = new Date(timeStr)
    const now = new Date()
    const diff = now - date

    // 小于1分钟
    if (diff < 60000) {
      return '刚刚'
    }
    // 小于1小时
    if (diff < 3600000) {
      return `${Math.floor(diff / 60000)}分钟前`
    }
    // 小于24小时
    if (diff < 86400000) {
      return `${Math.floor(diff / 3600000)}小时前`
    }
    // 小于30天
    if (diff < 2592000000) {
      return `${Math.floor(diff / 86400000)}天前`
    }
    // 超过30天，显示具体日期
    return date.toLocaleDateString('zh-CN')
  } catch (e) {
    return '未知时间'
  }
}

// 发布评论（真实API）
async function submitComment(content) {
  if (!content.trim() || !image.value) return

  // 检查登录状态
  const token = localStorage.getItem('token')
  if (!token) {
    alert('请先登录后再发表评论')
    return
  }

  try {
    await apiService.api.post('/community/comments/', { image: image.value.id, content })
    await fetchComments()
  } catch (e) {
    console.error('发表评论失败:', e)
    if (e.response?.status === 401) {
      alert('登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    } else {
      alert('发表评论失败，请稍后重试')
    }
  }
}

// 评论点赞（真实API）
async function toggleCommentLike(comment) {
  // 检查登录状态
  const token = localStorage.getItem('token')
  if (!token) {
    alert('请先登录后再点赞')
    return
  }

  try {
    const res = await apiService.api.post('/community/likes/toggle/', {
      like_type: 'comment',
      object_id: comment.id
    })
    comment.likedByMe = res.liked
    comment.likeCount = res.like_count
  } catch (e) {
    console.error('评论点赞失败:', e)
    if (e.response?.status === 401) {
      alert('登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    } else {
      alert('点赞失败，请稍后重试')
    }
  }
}

// 回复点赞（真实API）
async function toggleReplyLike(comment, reply) {
  // 检查登录状态
  const token = localStorage.getItem('token')
  if (!token) {
    alert('请先登录后再点赞')
    return
  }

  try {
    const res = await apiService.api.post('/community/likes/toggle/', {
      like_type: 'comment',
      object_id: reply.id
    })
    reply.likedByMe = res.liked
    reply.likeCount = res.like_count
  } catch (e) {
    console.error('回复点赞失败:', e)
    if (e.response?.status === 401) {
      alert('登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    } else {
      alert('点赞失败，请稍后重试')
    }
  }
}

// 回复评论（真实API）
async function submitReply(comment, replyContent) {
  if (!replyContent.trim() || !image.value) return

  // 检查登录状态
  const token = localStorage.getItem('token')
  if (!token) {
    alert('请先登录后再回复评论')
    return
  }

  try {
    await apiService.api.post('/community/comments/', {
      image: image.value.id,
      content: replyContent,
      parent: comment.id
    })
    await fetchComments()
  } catch (e) {
    console.error('回复评论失败:', e)
    if (e.response?.status === 401) {
      alert('登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    } else {
      alert('回复评论失败，请稍后重试')
    }
  }
}

// 监听图片变化，刷新点赞和评论
watch(() => image.value, () => {
  if (image.value) {
    fetchLikeStatus()
    fetchComments()
  }
}, { immediate: true })

const showCommentSection = ref(true)

const allImages = ref([])

// 拉取全部图片
const fetchAllImages = async () => {
  try {
    const response = await apiService.images.getList({ is_public: true, page_size: 1000 })
    allImages.value = response.results || response.data?.results || []
  } catch (e) {
    allImages.value = []
  }
}

// 获取当前用户信息（包含id和username）
const userStr = localStorage.getItem('user')
const currentUser = ref({ id: '', username: '' })
if (userStr) {
  try {
    const userObj = JSON.parse(userStr)
    currentUser.value = {
      id: userObj.id || '',
      username: userObj.username || ''
    }
  } catch {
    currentUser.value = { id: '', username: '' }
  }
}

async function deleteComment(comment) {
  const token = localStorage.getItem('token')
  if (!token) {
    alert('请先登录后再删除评论')
    return
  }
  try {
    await apiService.api.delete(`/community/comments/${comment.id}/`)
    alert('删除成功')
    await fetchComments()
  } catch (e) {
    console.error('删除评论失败:', e)
    alert('删除失败，请稍后重试')
  }
}

async function deleteReply(comment, reply) {
  const token = localStorage.getItem('token')
  if (!token) {
    alert('请先登录后再删除回复')
    return
  }
  try {
    await apiService.api.delete(`/community/comments/${reply.id}/`)
    alert('删除成功')
    await fetchComments()
  } catch (e) {
    console.error('删除回复失败:', e)
    alert('删除失败，请稍后重试')
  }
}

const isFollowing = ref(false)

// 监听图片详情中的关注状态变化（用于后续更新）
watch(() => image.value?.is_following_author, (val) => {
  if (val !== undefined) {
    isFollowing.value = !!val
    console.log('watch更新关注状态:', isFollowing.value, '来自:', val)
  }
})

// 关注/取关用户（toggle）
async function toggleFollowUser() {
  console.log('toggleFollowUser called', image.value?.user)
  if (!image.value?.user) return
  
  // 获取用户ID
  let userId = null
  if (typeof image.value.user === 'object' && image.value.user.id) {
    userId = image.value.user.id
  } else if (typeof image.value.user === 'number' || typeof image.value.user === 'string') {
    userId = image.value.user
  }
  
  if (!userId) {
    console.warn('无法获取用户ID')
    return
  }
  
  try {
    console.log('准备请求关注/取消关注用户:', userId)
    const res = await apiService.follow.toggleFollow(userId)
    isFollowing.value = !!res.following
    alert(res.message || (isFollowing.value ? '关注成功' : '已取消关注'))
    
    // 重新获取图片详情以更新关注状态
    await fetchImageDetail()
  } catch (e) {
    console.error('关注操作失败:', e)
    alert('操作失败，请稍后重试')
  }
}

onMounted(() => {
  fetchImageDetail(true)
  fetchAllImages()
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

// 监听路由参数变化
watch(() => route.params.id, (newId, oldId) => {
  if (newId !== oldId && newId) {
    console.log('路由参数变化，重新加载图片详情:', newId)
    fetchImageDetail(true)
  }
}, { immediate: true })

// 监听图片列表变化，更新当前图片索引
watch(() => currentImageList.value, (newList) => {
  if (newList.length > 0 && image.value) {
    const index = newList.findIndex(img => img.id === image.value.id)
    currentImageIndex.value = index
    console.log('图片列表更新，当前索引:', index)
  }
}, { deep: true })
</script>

<style scoped>
.detail-container {
  display: flex;
  flex-direction: row;
  min-height: 80vh;
  background: var(--bg-gradient);
  border-radius: 24px;
  box-shadow: 0 8px 32px var(--shadow-color);
  padding: 32px 0 32px 0;
  gap: 0;
  position: relative;
}

.image-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--card-color);
  border-radius: 24px 0 0 24px;
  box-shadow: 0 4px 32px var(--shadow-color);
  margin-left: 32px;
  margin-right: 0;
  min-width: 0;
  overflow: hidden;
}

.toggle-section {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin: 32px 0 0 0;
}

.toggle-section button {
  padding: 10px 32px;
  border-radius: 24px;
  border: none;
  font-size: 1.1rem;
  font-weight: 600;
  box-shadow: 0 2px 8px var(--shadow-color);
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.toggle-section .btn-comment {
  background: linear-gradient(90deg, #1e90ff 0%, #6ec6ff 100%);
  color: #fff;
}

.toggle-section .btn-related {
  background: linear-gradient(90deg, #f7b267 0%, #f4845f 100%);
  color: #fff;
}

.toggle-section .btn-comment.active,
.toggle-section .btn-comment:hover {
  background: linear-gradient(90deg, #6ec6ff 0%, #1e90ff 100%);
  color: #fff;
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 16px var(--shadow-color-hover);
}

.toggle-section .btn-related.active,
.toggle-section .btn-related:hover {
  background: linear-gradient(90deg, #f4845f 0%, #f7b267 100%);
  color: #fff;
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 16px var(--shadow-color-hover);
}

@media (max-width: 900px) {
  .detail-container {
    flex-direction: column;
    border-radius: 0;
    padding: 0;
  }

  .image-section {
    border-radius: 0;
    margin-left: 0;
    margin-right: 0;
  }
}

.related-images {
  margin-top: 40px;
  padding: 20px;
  background: var(--bg-color);
  border-radius: 12px;
}

.related-images h3 {
  font-size: 1.5rem;
  margin-bottom: 20px;
  color: var(--text-color);
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  margin-top: 16px;
}

.related-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  aspect-ratio: 4/3;
}

.related-item:hover {
  transform: translateY(-4px);
}

.related-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px;
  background: linear-gradient(0deg, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0) 100%);
  color: white;
}

.match-score {
  font-size: 0.9rem;
  opacity: 0.9;
}

.matched-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}

.matched-tag {
  font-size: 0.8rem;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
}

@media (max-width: 768px) {
  .related-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }

  .related-info {
    padding: 8px;
  }
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  font-size: 16px;
  margin: 0;
}

/* 错误状态样式 */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 40px 20px;
  text-align: center;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.error-container h3 {
  color: var(--text-color);
  margin-bottom: 12px;
  font-size: 1.5rem;
}

.error-container p {
  color: var(--text-secondary);
  margin-bottom: 24px;
  max-width: 400px;
  line-height: 1.5;
}

.retry-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.retry-btn:hover {
  background: var(--primary-color-dark);
  transform: translateY(-1px);
}
</style>