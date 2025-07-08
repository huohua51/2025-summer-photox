<template>
  <div class="travel-map-container">
    <!-- 页面头部 -->
    <div class="map-header">
      <button @click="goBack" class="back-btn">
        <svg width="20" height="20" viewBox="0 0 24 24">
          <path fill="currentColor" d="M19 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H19v-2z"/>
        </svg>
        返回
      </button>
      <h1 class="page-title">我的旅行轨迹</h1>
      <div class="header-controls">
        <!-- 编号模式切换 -->
        <div class="numbering-mode-selector">
          <label class="mode-label">编号模式:</label>
          <select v-model="numberingMode" @change="onNumberingModeChange" class="mode-select">
            <option value="upload-time">按上传时间</option>
            <option value="map-order">按地图顺序</option>
          </select>
          <div class="mode-tooltip" v-if="numberingMode === 'map-order'">
            <svg width="14" height="14" viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
            </svg>
            <span class="tooltip-text">可拖拽调整顺序</span>
          </div>
        </div>
        <button @click="openImageSelector" class="add-btn">
          <svg width="20" height="20" viewBox="0 0 24 24">
            <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          添加图片
        </button>
      </div>
    </div>

    <!-- 地图容器 -->
    <div class="map-wrapper">
      <div id="travelMap" class="map-container"></div>
      
      <!-- 位置选择提示 -->
      <div v-if="showLocationSelectTip" class="location-select-tip">
        <div class="tip-content">
          <svg width="24" height="24" viewBox="0 0 24 24" class="tip-icon">
            <path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          <div class="tip-text">
            <div class="tip-title">选择图片拍摄位置</div>
            <div class="tip-desc">在地图上点击任意位置完成选择</div>
          </div>
          <button @click="cancelMapSelection" class="cancel-select-btn">
            <svg width="16" height="16" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
            取消
          </button>
        </div>
      </div>
      
      <!-- 图片标记列表 -->
      <div class="marker-list" v-if="markers.length > 0">
        <div class="marker-list-header">
          <h3>旅行足迹</h3>
          <div class="marker-list-controls">
            <span class="marker-count">{{ markers.length }}个地点</span>
            <button 
              v-if="numberingMode === 'map-order'" 
              @click="resetMapOrder" 
              class="reset-order-btn"
              title="重置为上传时间顺序"
            >
              <svg width="14" height="14" viewBox="0 0 24 24">
                <path fill="currentColor" d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
              </svg>
              重置顺序
            </button>
          </div>
        </div>
        <div class="marker-items" :class="{ 'draggable': numberingMode === 'map-order' }">
          <div 
            v-for="(marker, index) in markers" 
            :key="marker.id"
            class="marker-item"
            :class="{ 'draggable-item': numberingMode === 'map-order' }"
            @click="focusMarker(marker)"
            :draggable="numberingMode === 'map-order'"
            @dragstart="onDragStart($event, index)"
            @dragover.prevent
            @drop="onDrop($event, index)"
            @dragenter="onDragEnter($event)"
            @dragleave="onDragLeave($event)"
          >
            <div v-if="numberingMode === 'map-order'" class="drag-handle">
              <svg width="16" height="16" viewBox="0 0 24 24">
                <path fill="currentColor" d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
              </svg>
            </div>
            <img :src="marker.image_url" :alt="marker.title" />
            <div class="marker-info">
              <h4>{{ marker.location_name || '未命名地点' }}</h4>
              <p>{{ formatDate(marker.created_at) }}</p>
              <span class="marker-number">#{{ index + 1 }}</span>
            </div>
            <button @click.stop="removeMarker(marker.id)" class="remove-btn">
              <svg width="16" height="16" viewBox="0 0 24 24">
                <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片选择弹窗 -->
    <div v-if="showImageSelector" class="modal-overlay" @click="closeImageSelector">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>选择图片</h2>
          <button @click="closeImageSelector" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="image-grid">
            <div 
              v-for="image in userImages" 
              :key="image.id"
              class="image-item"
              :class="{ selected: selectedImages.includes(image.id) }"
              @click="toggleImageSelection(image)"
            >
              <img :src="image.image_url" :alt="image.title" />
              <div class="image-overlay">
                <svg v-if="selectedImages.includes(image.id)" width="24" height="24" viewBox="0 0 24 24" class="check-icon">
                  <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeImageSelector" class="btn btn-secondary">取消</button>
          <button @click="confirmImageSelection" class="btn btn-primary" :disabled="selectedImages.length === 0">
            确认选择 ({{ selectedImages.length }})
          </button>
        </div>
      </div>
    </div>

    <!-- 地点输入弹窗 -->
    <div v-if="showLocationInput && !showLocationSelectTip" class="modal-overlay" @click="closeLocationInput">
      <div class="modal-content location-modal" @click.stop>
        <div class="modal-header">
          <h2>设置图片位置</h2>
          <button @click="closeLocationInput" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="location-form">
            <div 
              v-for="image in pendingImages" 
              :key="image.id"
              class="location-item"
            >
              <img :src="image.image_url" :alt="image.title" class="preview-img" />
              <div class="location-inputs">
                <input 
                  v-model="locationData[image.id].name"
                  type="text" 
                  placeholder="地点名称（如：上海外滩）"
                  class="location-name-input"
                />
                <div class="coordinates-input">
                  <input 
                    v-model="locationData[image.id].lat"
                    type="number" 
                    step="0.000001"
                    placeholder="纬度"
                    class="coord-input"
                  />
                  <input 
                    v-model="locationData[image.id].lng"
                    type="number" 
                    step="0.000001"
                    placeholder="经度"
                    class="coord-input"
                  />
                </div>
                <button @click="selectOnMap(image.id)" class="map-select-btn" title="在地图上选择位置">
                  <svg width="16" height="16" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                  </svg>
                  在地图上选择
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeLocationInput" class="btn btn-secondary">取消</button>
          <button @click="saveLocations" class="btn btn-primary">保存位置</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/api'
import imageService from '@/api/imageService'

const router = useRouter()
const userStore = useUserStore()

// 状态管理
const map = ref(null)
const markers = ref([])
const userImages = ref([])
const selectedImages = ref([])
const pendingImages = ref([])
const locationData = ref({})
const showImageSelector = ref(false)
const showLocationInput = ref(false)
const polyline = ref(null)
const currentSelectingImageId = ref(null)
const showLocationSelectTip = ref(false)
const tempMarker = ref(null)

// 编号模式相关
const numberingMode = ref('upload-time') // 'upload-time' 或 'map-order'
const mapOrderSequence = ref([]) // 存储按地图顺序的图片ID序列

// 返回上一页
const goBack = () => {
  router.back()
}

// 编号模式切换处理
const onNumberingModeChange = () => {
  // 重新加载标记以应用新的编号模式
  loadMarkers()
}

// 保存地图顺序序列到本地存储
const saveMapOrderSequence = () => {
  try {
    localStorage.setItem(`mapOrderSequence_${userStore.userId}`, JSON.stringify(mapOrderSequence.value))
  } catch (error) {
    console.warn('保存地图顺序序列失败:', error)
  }
}

// 从本地存储加载地图顺序序列
const loadMapOrderSequence = () => {
  try {
    const saved = localStorage.getItem(`mapOrderSequence_${userStore.userId}`)
    if (saved) {
      mapOrderSequence.value = JSON.parse(saved)
    }
  } catch (error) {
    console.warn('加载地图顺序序列失败:', error)
    mapOrderSequence.value = []
  }
}

// 初始化地图
const initMap = () => {
  // 这里使用高德地图作为示例，您也可以选择其他地图服务
  const AMap = window.AMap
  if (!AMap) {
    console.error('地图SDK未加载')
    return
  }

  map.value = new AMap.Map('travelMap', {
    center: [116.397428, 39.90923], // 默认北京
    zoom: 5,
    style: 'amap://styles/whitesmoke'
  })

  // 加载已有的标记
  loadMarkers()
}

// 加载用户图片
const loadUserImages = async () => {
  try {
    const response = await api.images.getList({
      user: userStore.userId,
      page_size: 100
    })
    userImages.value = response.data?.results || response.results || []
  } catch (error) {
    console.error('加载图片失败:', error)
  }
}

// 加载已有标记
const loadMarkers = async () => {
  try {
    const response = await api.images.getList({
      user: userStore.userId,
      has_location: true,
      page_size: 100
    })
    const images = response.data?.results || response.results || []
    
    // 转换为标记数据
    const filteredImages = images.filter(img => img.latitude && img.longitude)
    
    // 根据编号模式进行排序
    let sortedImages
    if (numberingMode.value === 'upload-time') {
      // 按上传时间排序
      sortedImages = filteredImages.sort((a, b) => 
        new Date(a.created_at) - new Date(b.created_at)
      )
    } else {
      // 按地图顺序排序
      sortedImages = sortByMapOrder(filteredImages)
    }
    
    markers.value = sortedImages.map(img => ({
      id: img.id,
      position: [img.longitude, img.latitude],
      image_url: img.image_url,
      title: img.title,
      location_name: img.location_name,
      created_at: img.created_at
    }))

    // 在地图上显示标记
    displayMarkers()
    
    // 生成旅行轨迹
    generatePolyline()
  } catch (error) {
    console.error('加载标记失败:', error)
  }
}

// 按地图顺序排序图片
const sortByMapOrder = (images) => {
  // 如果地图顺序序列为空，则按上传时间排序并初始化序列
  if (mapOrderSequence.value.length === 0) {
    const sortedByTime = images.sort((a, b) => 
      new Date(a.created_at) - new Date(b.created_at)
    )
    mapOrderSequence.value = sortedByTime.map(img => img.id)
    saveMapOrderSequence() // 保存初始序列
    return sortedByTime
  }
  
  // 根据地图顺序序列排序
  const sortedImages = []
  const remainingImages = [...images]
  
  // 先按地图顺序添加已有的图片
  for (const imageId of mapOrderSequence.value) {
    const imageIndex = remainingImages.findIndex(img => img.id === imageId)
    if (imageIndex !== -1) {
      sortedImages.push(remainingImages[imageIndex])
      remainingImages.splice(imageIndex, 1)
    }
  }
  
  // 将剩余的图片按上传时间添加到末尾
  const remainingSorted = remainingImages.sort((a, b) => 
    new Date(a.created_at) - new Date(b.created_at)
  )
  sortedImages.push(...remainingSorted)
  
  // 更新地图顺序序列
  mapOrderSequence.value = sortedImages.map(img => img.id)
  saveMapOrderSequence() // 保存更新后的序列
  
  return sortedImages
}

// 生成旅行轨迹（Leaflet版本）
const generatePolyline = () => {
  if (!map.value || !window.L || markers.value.length < 2) return
  
  // markers.value 已经按时间排序，直接使用
  // 提取路径点（Leaflet使用 [lat, lng] 格式）
  const path = markers.value.map(m => [m.position[1], m.position[0]])
  
  // 创建轨迹线
  polyline.value = window.L.polyline(path, {
    color: '#667eea',
    weight: 4,
    opacity: 0.8,
    dashArray: '10, 5'
  }).addTo(map.value)
}

// 打开图片选择器
const openImageSelector = async () => {
  await loadUserImages()
  showImageSelector.value = true
}

// 关闭图片选择器
const closeImageSelector = () => {
  showImageSelector.value = false
  selectedImages.value = []
}

// 切换图片选择
const toggleImageSelection = (image) => {
  const index = selectedImages.value.indexOf(image.id)
  if (index > -1) {
    selectedImages.value.splice(index, 1)
  } else {
    selectedImages.value.push(image.id)
  }
}

// 新增：AI识别图片地点
const aiRecognizeLocation = async (imageId, imageTitle) => {
  try {
    const response = await imageService.aiRecognizeLocation(imageId)
    if (response.code === 0) {
      locationData.value[imageId].lat = response.lat
      locationData.value[imageId].lng = response.lng
      locationData.value[imageId].name = response.name || ''
      return true
    } else {
      alert(`图片【${imageTitle}】AI无法识别地点，请手动选择位置`)
      return false
    }
  } catch (e) {
    alert(`图片【${imageTitle}】AI识别地点出错，请手动选择位置`)
    console.error('AI识别地点出错:', e)
    return false
  }
}

// 修改 confirmImageSelection
const confirmImageSelection = async () => {
  pendingImages.value = userImages.value.filter(img => 
    selectedImages.value.includes(img.id)
  )
  // 初始化位置数据并尝试AI识别
  for (const img of pendingImages.value) {
    locationData.value[img.id] = { name: '', lat: '', lng: '' }
    await aiRecognizeLocation(img.id, img.title)
  }
  closeImageSelector()
  showLocationInput.value = true
}

// 关闭位置输入
const closeLocationInput = () => {
  showLocationInput.value = false
  pendingImages.value = []
  locationData.value = {}
  
  // 清理临时标记
  if (tempMarker.value && map.value) {
    map.value.removeLayer(tempMarker.value)
    tempMarker.value = null
  }
  
  // 取消任何正在进行的地图选择
  cancelMapSelection()
}

// 在地图上选择位置
const selectOnMap = (imageId) => {
  console.log('开始选择位置，图片ID:', imageId)
  
  if (!map.value || !window.L) {
    alert('地图尚未加载完成，请稍后再试')
    return
  }
  
  console.log('地图已加载，开始选点模式')
  
  // 设置当前正在选择位置的图片ID
  currentSelectingImageId.value = imageId
  
  // 显示选择提示
  showLocationSelectTip.value = true
  
  // 移除之前的地图点击事件（如果有）
  map.value.off('click', onMapClick)
  
  // 添加新的地图点击事件
  map.value.on('click', onMapClick)
  
  // 改变鼠标样式
  const mapContainer = map.value.getContainer()
  if (mapContainer) {
    mapContainer.style.cursor = 'crosshair'
  }
  
  console.log('选点模式已启用')
}

// 地图点击事件处理
const onMapClick = (e) => {
  console.log('地图被点击:', e.latlng)
  
  if (!currentSelectingImageId.value) {
    console.log('没有正在选择的图片ID')
    return
  }
  
  const { lat, lng } = e.latlng
  console.log('点击位置:', lat, lng)
  
  // 更新对应图片的位置数据
  if (locationData.value[currentSelectingImageId.value]) {
    locationData.value[currentSelectingImageId.value].lat = lat.toFixed(6)
    locationData.value[currentSelectingImageId.value].lng = lng.toFixed(6)
    console.log('位置数据已更新:', locationData.value[currentSelectingImageId.value])
  }
  
  // 清除之前的临时标记
  if (tempMarker.value && map.value) {
    map.value.removeLayer(tempMarker.value)
  }
  
  // 在地图上显示临时标记
  if (window.L) {
    tempMarker.value = window.L.marker([lat, lng], {
      icon: window.L.divIcon({
        className: 'temp-location-marker',
        html: '📍',
        iconSize: [30, 30],
        iconAnchor: [15, 30]
      })
    }).addTo(map.value)
    
    console.log('临时标记已添加')
  }
  
  // 关闭选择模式（这会恢复弹窗显示）
  currentSelectingImageId.value = null
  showLocationSelectTip.value = false
  
  // 移除地图点击事件
  map.value.off('click', onMapClick)
  
  // 恢复鼠标样式
  const mapContainer = map.value.getContainer()
  if (mapContainer) {
    mapContainer.style.cursor = ''
  }
  
  console.log('选择模式已关闭，弹窗已恢复')
  
  // 可选：自动获取地点名称（使用反向地理编码）
  const imageId = Object.keys(locationData.value).find(id => 
    locationData.value[id].lat === lat.toFixed(6) && 
    locationData.value[id].lng === lng.toFixed(6)
  )
  
  if (imageId) {
    reverseGeocode(lat, lng, imageId)
  }
}

// 取消地图选择模式
const cancelMapSelection = () => {
  console.log('取消选择模式')
  
  if (!map.value) return
  
  currentSelectingImageId.value = null
  showLocationSelectTip.value = false
  
  // 移除地图点击事件
  map.value.off('click', onMapClick)
  
  // 恢复鼠标样式
  const mapContainer = map.value.getContainer()
  if (mapContainer) {
    mapContainer.style.cursor = ''
  }
  
  // 清除临时标记（但不关闭位置输入弹窗）
  if (tempMarker.value && map.value) {
    map.value.removeLayer(tempMarker.value)
    tempMarker.value = null
  }
  
  console.log('选择模式已取消')
}

// 反向地理编码获取地点名称
const reverseGeocode = async (lat, lng, imageId) => {
  try {
    // 使用免费的Nominatim服务进行反向地理编码
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
      {
        headers: {
          'User-Agent': 'PhotoX Travel Map'
        }
      }
    )
    
    if (response.ok) {
      const data = await response.json()
      if (data && data.display_name && locationData.value[imageId]) {
        // 提取简化的地点名称
        const address = data.address || {}
        const locationName = address.tourism || 
                           address.amenity || 
                           address.shop || 
                           address.building || 
                           address.house_number && address.road ? `${address.house_number} ${address.road}` :
                           address.road || 
                           address.neighbourhood || 
                           address.suburb || 
                           address.city || 
                           address.town || 
                           address.village || 
                           data.display_name.split(',')[0]
        
        locationData.value[imageId].name = locationName
      }
    }
  } catch (error) {
    console.warn('获取地点名称失败:', error)
  }
}

// 保存位置信息
const saveLocations = async () => {
  try {
    // 批量更新图片位置信息
    const updates = pendingImages.value.map(async (image) => {
      const location = locationData.value[image.id]
      if (location.lat && location.lng) {
        await api.api.put(`/images/${image.id}/`, {
          latitude: parseFloat(location.lat),
          longitude: parseFloat(location.lng),
          location_name: location.name
        })
      }
    })
    
    await Promise.all(updates)
    
    // 清理临时标记
    if (tempMarker.value && map.value) {
      map.value.removeLayer(tempMarker.value)
      tempMarker.value = null
    }
    
    // 如果是按地图顺序模式，将新添加的图片ID添加到序列末尾
    if (numberingMode.value === 'map-order') {
      const newImageIds = pendingImages.value.map(img => img.id)
      mapOrderSequence.value.push(...newImageIds)
      saveMapOrderSequence() // 保存更新后的序列
    }
    
    // 重新加载标记
    await loadMarkers()
    
    closeLocationInput()
  } catch (error) {
    console.error('保存位置失败:', error)
    alert('保存位置失败，请检查网络连接后重试')
  }
}

// 移除标记
const removeMarker = async (markerId) => {
  if (!confirm('确定要移除这个位置标记吗？')) return
  
  try {
    await api.api.put(`/images/${markerId}/`, {
      latitude: null,
      longitude: null,
      location_name: null
    })
    
    // 如果是按地图顺序模式，从序列中移除该图片ID
    if (numberingMode.value === 'map-order') {
      const index = mapOrderSequence.value.indexOf(markerId)
      if (index !== -1) {
        mapOrderSequence.value.splice(index, 1)
        saveMapOrderSequence() // 保存更新后的序列
      }
    }
    
    // 重新加载标记
    await loadMarkers()
  } catch (error) {
    console.error('移除标记失败:', error)
  }
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 使用Leaflet替代高德地图
const initLeafletMap = () => {
  console.log('开始初始化Leaflet地图')
  
  // 动态加载Leaflet CSS
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css'
  document.head.appendChild(link)
  
  // 动态加载Leaflet JS
  const script = document.createElement('script')
  script.src = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js'
  script.onload = () => {
    console.log('Leaflet库已加载')
    
    if (window.L) {
      console.log('开始创建地图')
      
      // 创建地图
      map.value = window.L.map('travelMap', {
        center: [39.9042, 116.4074],
        zoom: 5,
        zoomControl: true
      })
      
      console.log('地图实例已创建')
      
      // 添加OpenStreetMap图层
      const tileLayer = window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
      })
      
      tileLayer.addTo(map.value)
      
      console.log('地图图层已添加')
      
      // 等待地图完全加载后再加载标记
      map.value.whenReady(() => {
        console.log('地图已准备就绪，开始加载标记')
        loadMarkers()
      })
    } else {
      console.error('Leaflet库未能正确加载')
    }
  }
  
  script.onerror = () => {
    console.error('Leaflet库加载失败')
    alert('地图加载失败，请检查网络连接')
  }
  
  document.head.appendChild(script)
}

// 在地图上显示标记（Leaflet版本）
const displayMarkers = () => {
  console.log('开始显示标记，标记数量:', markers.value.length)
  
  if (!map.value || !window.L) {
    console.error('地图或Leaflet库未准备好')
    return
  }
  
  // 清除现有标记
  map.value.eachLayer((layer) => {
    if (layer instanceof window.L.Marker) {
      map.value.removeLayer(layer)
    }
  })
  
  // 清除轨迹线
  if (polyline.value) {
    map.value.removeLayer(polyline.value)
    polyline.value = null
  }
  
  if (markers.value.length === 0) {
    console.log('没有标记需要显示')
    return
  }
  
  const customIcon = window.L.divIcon({
    className: 'custom-leaflet-marker',
    html: '',
    iconSize: [50, 50],
    iconAnchor: [25, 50]
  })
  
  // 添加新标记（按时间顺序，从1开始编号）
  markers.value.forEach((marker, index) => {
    const markerNumber = index + 1 // 从1开始编号
    console.log(`添加标记 ${markerNumber}:`, marker.location_name, marker.position)
    
    try {
      const mapMarker = window.L.marker([marker.position[1], marker.position[0]], {
        icon: customIcon
      })
      .bindPopup(`
        <div class="marker-popup">
          <img src="${marker.image_url}" alt="${marker.title}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px;">
          <h4>${marker.location_name || '未命名地点'}</h4>
          <p>${formatDate(marker.created_at)}</p>
        </div>
      `)
      .addTo(map.value)
      
      // 自定义标记样式
      const markerElement = mapMarker.getElement()
      if (markerElement) {
        markerElement.style.backgroundImage = `url(${marker.image_url})`
        markerElement.style.backgroundSize = 'cover'
        markerElement.style.backgroundPosition = 'center'
        markerElement.style.border = '3px solid white'
        markerElement.style.borderRadius = '50%'
        markerElement.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)'
        markerElement.innerHTML = `<span class="marker-number-leaflet">${markerNumber}</span>`
      }
      
      console.log(`标记 ${markerNumber} 添加成功`)
    } catch (error) {
      console.error(`添加标记 ${markerNumber} 失败:`, error)
    }
  })
  
  // 自适应显示所有标记
  if (markers.value.length > 0) {
    try {
      // 创建包含所有标记的边界
      const bounds = window.L.latLngBounds()
      markers.value.forEach(marker => {
        bounds.extend([marker.position[1], marker.position[0]])
      })
      
      // 设置地图视图以包含所有标记
      map.value.fitBounds(bounds, {
        padding: [20, 20],
        maxZoom: 15
      })
      
      console.log('地图视图已调整以包含所有标记')
    } catch (error) {
      console.error('调整地图视图失败:', error)
    }
  }
}

// 聚焦到特定标记（Leaflet版本）
const focusMarker = (marker) => {
  if (!map.value) return
  
  map.value.setView([marker.position[1], marker.position[0]], 13)
}

// 拖拽相关函数
const draggedIndex = ref(null)

const onDragStart = (event, index) => {
  draggedIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
  event.target.classList.add('dragging')
}

const onDrop = (event, dropIndex) => {
  event.preventDefault()
  
  if (draggedIndex.value === null || draggedIndex.value === dropIndex) {
    return
  }
  
  // 重新排序标记
  const newMarkers = [...markers.value]
  const draggedMarker = newMarkers[draggedIndex.value]
  newMarkers.splice(draggedIndex.value, 1)
  newMarkers.splice(dropIndex, 0, draggedMarker)
  
  // 更新地图顺序序列
  mapOrderSequence.value = newMarkers.map(marker => marker.id)
  saveMapOrderSequence()
  
  // 更新标记显示
  markers.value = newMarkers
  displayMarkers()
  generatePolyline()
  
  // 清理拖拽状态
  draggedIndex.value = null
  const draggingElements = document.querySelectorAll('.dragging')
  draggingElements.forEach(el => el.classList.remove('dragging'))
}

const onDragEnter = (event) => {
  if (draggedIndex.value !== null) {
    event.currentTarget.classList.add('drag-over')
  }
}

const onDragLeave = (event) => {
  event.currentTarget.classList.remove('drag-over')
}

// 重置地图顺序
const resetMapOrder = () => {
  if (!confirm('确定要重置为上传时间顺序吗？这将清除自定义的排序。')) {
    return
  }
  
  // 清空地图顺序序列
  mapOrderSequence.value = []
  saveMapOrderSequence()
  
  // 重新加载标记（会按上传时间排序）
  loadMarkers()
}

onMounted(() => {
  // 加载用户的地图顺序序列
  loadMapOrderSequence()
  
  // 使用Leaflet地图作为替代方案（不需要API密钥）
  initLeafletMap()
})

onUnmounted(() => {
  // 清理地图事件和临时标记
  if (map.value) {
    cancelMapSelection()
    if (tempMarker.value) {
      map.value.removeLayer(tempMarker.value)
    }
    map.value.remove()
  }
})
</script>

<style scoped>
.travel-map-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-color);
  color: var(--text-color);
}

/* 页面头部 */
.map-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: var(--secondary-color);
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.numbering-mode-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mode-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
  white-space: nowrap;
}

.mode-select {
  padding: 6px 12px;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-color);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.mode-select:hover {
  border-color: #667eea;
}

.mode-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.mode-tooltip {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
  font-size: 12px;
  position: relative;
}

.mode-tooltip svg {
  cursor: help;
}

.tooltip-text {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
  z-index: 1000;
}

.mode-tooltip:hover .tooltip-text {
  opacity: 1;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.back-btn, .add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  font-weight: 500;
}

.back-btn:hover, .add-btn:hover {
  background: var(--border-color);
}

.add-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.add-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 地图容器 */
.map-wrapper {
  flex: 1;
  position: relative;
  display: flex;
}

.map-container {
  flex: 1;
  height: 100%;
  position: relative;
  z-index: 1;
  background: #f0f0f0;
}

/* 位置选择提示 */
.location-select-tip {
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  z-index: 1000;
  background: rgba(102, 126, 234, 0.95);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.tip-content {
  display: flex;
  align-items: center;
  gap: 16px;
  color: white;
  font-size: 16px;
  font-weight: 600;
}

.tip-text {
  flex: 1;
  text-align: left;
}

.tip-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 4px;
}

.tip-desc {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 400;
}

.tip-icon {
  color: white;
  animation: pulse 2s infinite;
  flex-shrink: 0;
}

.cancel-select-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  flex-shrink: 0;
}

.cancel-select-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* 临时位置标记样式 */
:global(.temp-location-marker) {
  font-size: 24px;
  text-align: center;
  line-height: 30px;
  animation: bounce 1s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 标记列表 */
.marker-list {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 320px;
  max-height: 60%;
  background: var(--secondary-color);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.marker-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.marker-list-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.marker-list-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.marker-count {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.reset-order-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.reset-order-btn:hover {
  background: var(--border-color);
  color: var(--text-color);
}

.marker-items {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.marker-items.draggable {
  min-height: 200px;
}

.marker-items.draggable .marker-item {
  user-select: none;
}

.marker-items.draggable .marker-item.dragging {
  opacity: 0.5;
  transform: rotate(5deg);
}

.marker-items.draggable .marker-item.drag-over {
  border: 2px dashed #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.marker-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-color);
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.marker-item:hover {
  background: var(--border-color);
  transform: translateX(-4px);
}

.marker-item.draggable-item {
  cursor: grab;
}

.marker-item.draggable-item:active {
  cursor: grabbing;
}

.drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  color: var(--text-secondary);
  cursor: grab;
  flex-shrink: 0;
}

.drag-handle:active {
  cursor: grabbing;
}

.marker-number {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
}

.marker-item img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
}

.marker-info {
  flex: 1;
}

.marker-info h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.marker-info p {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
}

.remove-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 50%;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.remove-btn:hover {
  background: rgba(255, 0, 0, 0.1);
  color: #ff4444;
}

/* 自定义地图标记 */
:global(.custom-marker) {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 3px solid white;
  background-size: cover;
  background-position: center;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: transform 0.3s;
}

:global(.custom-marker:hover) {
  transform: scale(1.1);
}

:global(.marker-number) {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  border: 2px solid white;
}

/* Leaflet地图标记样式 */
:global(.custom-leaflet-marker) {
  width: 50px !important;
  height: 50px !important;
  border-radius: 50%;
  border: 3px solid white;
  background-size: cover;
  background-position: center;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: transform 0.3s;
}

:global(.custom-leaflet-marker:hover) {
  transform: scale(1.1);
}

:global(.marker-number-leaflet) {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  border: 2px solid white;
}

/* 地图弹窗样式 */
:global(.marker-popup) {
  text-align: center;
  min-width: 120px;
}

:global(.marker-popup h4) {
  margin: 8px 0 4px 0;
  font-size: 14px;
  font-weight: 600;
}

:global(.marker-popup p) {
  margin: 0;
  font-size: 12px;
  color: #666;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--secondary-color);
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.location-modal {
  max-width: 600px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 50%;
  font-size: 24px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.close-btn:hover {
  background: var(--border-color);
  color: var(--text-color);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

/* 图片选择网格 */
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  border: 3px solid transparent;
}

.image-item:hover {
  transform: scale(1.05);
}

.image-item.selected {
  border-color: #667eea;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-item.selected .image-overlay {
  opacity: 1;
}

.check-icon {
  color: white;
}

/* 位置输入表单 */
.location-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.location-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--bg-color);
  border-radius: 8px;
}

.preview-img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
}

.location-inputs {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.location-name-input {
  width: 100%;
  padding: 10px 12px;
  background: var(--secondary-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-color);
  font-size: 14px;
}

.coordinates-input {
  display: flex;
  gap: 8px;
}

.coord-input {
  flex: 1;
  min-width: 0;
  padding: 8px 12px;
  background: var(--secondary-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-color);
  font-size: 14px;
}

.map-select-btn {
  width: 100%;
  margin-top: 8px;
  padding: 10px 16px;
  background: var(--secondary-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-color);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 500;
}

.map-select-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

/* 按钮样式 */
.btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--border-color);
  color: var(--text-color);
}

.btn-secondary:hover {
  background: var(--text-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .map-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-controls {
    justify-content: space-between;
  }
  
  .numbering-mode-selector {
    flex: 1;
    max-width: 200px;
  }
  
  .mode-select {
    flex: 1;
    min-width: 0;
  }
  
  .marker-list {
    position: relative;
    width: 100%;
    max-height: 200px;
    top: auto;
    right: auto;
    margin-top: 12px;
    border-radius: 0;
  }
  
  .map-wrapper {
    flex-direction: column;
  }
  
  .map-container {
    height: 60vh;
  }
  
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
  
  .location-item {
    flex-direction: column;
  }
  
  .preview-img {
    width: 100%;
    height: 120px;
  }
  
  .coordinates-input {
    flex-direction: column;
    gap: 8px;
  }
  
  .coord-input {
    flex: none;
  }
  
  .map-select-btn {
    width: 100%;
    min-width: auto;
  }
}
</style> 
