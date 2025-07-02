<template>
  <div v-if="!isExpanded" class="category-cover-card" @click="goToCategoryDetail">
    <img class="cover-img" :src="coverImg" :alt="category.name" />
    <div class="cover-info">
      <span class="cover-title">{{ category.name }}</span>
      <span class="cover-count">{{ category.images.length }} PIXS</span>
    </div>
  </div>
  <div v-else>
    <!-- 分类详情页模式，显示全部图片 -->
    <div class="image-grid">
      <div
        v-for="(img, idx) in displayImages"
        :key="idx"
        class="image-item"
        @click="navigateToDetail(img)"
      >
        <img :src="img.img" :alt="`${category.name} - ${idx + 1}`" />
      </div>
    </div>
    <!-- 分页控件等可保留 -->
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  category: Object,
  isExpanded: Boolean
})
const router = useRouter()

const coverImg = computed(() => props.category.images[0]?.img || '')

const goToCategoryDetail = () => {
  router.push({ name: 'category-detail', params: { name: props.category.name } })
}

// 详情页模式下的图片展示逻辑可保留
const displayImages = computed(() => props.category.images)
const navigateToDetail = (img) => {
  if (img.id) {
    window.open(`/photodetail/${img.id}?fromHome=true`, '_blank')
  }
}
</script>

<style scoped>
.category-cover-card {
  position: relative;
  width: 100%;
  height: 260px;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 2px 16px rgba(0,0,0,0.18);
  cursor: pointer;
  transition: transform 0.2s;
  background: #222;
  display: flex;
  align-items: flex-end;
}

.category-cover-card:hover {
  transform: translateY(-4px) scale(1.03);
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  left: 0;
  top: 0;
  z-index: 1;
}

.cover-info {
  position: relative;
  z-index: 2;
  width: 100%;
  padding: 24px 28px;
  background: linear-gradient(0deg, rgba(0,0,0,0.65) 80%, rgba(0,0,0,0.1) 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 100%;
}

.cover-title {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.cover-count {
  font-size: 1rem;
  opacity: 0.85;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

@media (max-width: 1200px) {
  .category-cover-card {
    height: 240px;
  }
  .cover-title {
    font-size: 1.6rem;
  }
}

@media (max-width: 768px) {
  .category-cover-card {
    height: 220px;
  }
  .cover-title {
    font-size: 1.4rem;
  }
  .cover-info {
    padding: 20px 24px;
  }
}
</style> 