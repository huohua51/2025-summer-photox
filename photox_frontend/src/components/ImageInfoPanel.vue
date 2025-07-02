<template>
  <div class="info-section" :class="{ 'collapsed': !showInfo }">
    <div class="info-toggle" @click="$emit('toggle-info')">
      <span class="material-icons">{{ showInfo ? '>' : '>' }}</span>
    </div>
    <div class="info-card" v-show="showInfo">
      <!-- 上传者信息 -->
      <div class="uploader-info" v-if="image?.user">
        <img 
          class="uploader-avatar" 
          :src="image.user.avatar || '/img/userImage.png'" 
          alt="头像" 
          @click="goToUserProfile"
          :title="`点击查看 ${getUserName} 的主页`"
        />
        <span class="uploader-name">{{ getUserName }}</span>
        <button v-if="showFollowButton" class="follow-btn" @click="toggleFollow">
          {{ isFollowing ? '已关注' : '关注' }}
        </button>
      </div>
      <h2>图片基本信息</h2>
      <div class="info-content">
        <div class="info-group">
          <div class="info-item">
            <span class="label">标题</span>
            <span class="value">{{ image?.title || '无标题' }}</span>
          </div>
          <div class="info-item">
            <span class="label">分类</span>
            <span class="value category-tag">{{ image?.category || '未分类' }}</span>
          </div>
        </div>
        <div class="info-group">
          <div class="info-item">
            <span class="label">标签</span>
            <div class="tags-container">
              <span v-for="(tag, index) in formatTags" :key="index" :class="['tag', tagColorClass(tag)]">
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
        <div class="info-group">
          <div class="info-item">
            <span class="label">创建时间</span>
            <span class="value">{{ formatDate }}</span>
          </div>
          <div class="info-item">
            <span class="label">是否公开</span>
            <span class="value" :class="{ 'public': image?.is_public }">
              {{ image?.is_public ? '是' : '否' }}
            </span>
          </div>
        </div>
        <div class="info-group">
          <div class="info-item">
            <span class="label">尺寸</span>
            <span class="value">{{ imageDimensions.width }} x {{ imageDimensions.height }}</span>
          </div>
          <div class="info-item">
            <span class="label">大小</span>
            <span class="value">{{ imageSizeMB }} MB</span>
          </div>
          <div class="info-item">
            <span class="label">格式</span>
            <span class="value format-tag">{{ imageFormat }}</span>
          </div>
        </div>
        <div class="info-group" v-if="image?.colors?.length">
          <div class="info-item full-width">
            <span class="label">颜色信息</span>
            <div class="colors-container">
              <div v-for="(color, index) in image.colors" :key="index" 
                   class="color-item" 
                   :style="{ backgroundColor: formatColor(color) }"
                   :title="formatColorDisplay(color)">
                <!-- <span class="color-value">{{ formatColorDisplay(color) }}</span> -->
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  image: Object,
  showInfo: Boolean,
  formatTags: Array,
  formatDate: String,
  imageDimensions: Object,
  imageSizeMB: String,
  imageFormat: String,
  formatColor: Function,
  formatColorDisplay: Function,
  currentUser: String,
  currentUserId: [String, Number],
  isFollowing: Boolean
})
console.log(props.formatTags)
console.log('currentUser', props.currentUserId)
const emit = defineEmits(['toggle-info', 'follow-user', 'unfollow-user'])
const router = useRouter()

const showFollowButton = computed(() => {
  // 当前用户未登录，不显示
  if (!props.currentUserId) return false
  // 图片无作者信息，不显示
  if (!props.image?.user) return false
  // 获取图片作者id
  let authorId = null
  if (typeof props.image.user === 'object' && props.image.user.id) {
    authorId = props.image.user.id
  } else if (typeof props.image.user === 'number' || typeof props.image.user === 'string') {
    authorId = props.image.user
  }
  console.log(authorId)
  // 作者id不存在，不显示
  if (!authorId) return false
  // 自己不能关注自己
  return String(props.currentUserId) !== String(authorId)
})

function toggleFollow() {
  console.log('emit follow-user')
  emit('follow-user')
}

// 标签色彩分配
function tagColorClass(tag) {
  if (!tag) return 'tag-blue';
  const t = tag.toLowerCase();
  if (t.includes('风景') || t.includes('蓝')) return 'tag-blue';
  if (t.includes('人物') || t.includes('粉')) return 'tag-pink';
  if (t.includes('动物') || t.includes('绿')) return 'tag-green';
  if (t.includes('艺术') || t.includes('紫')) return 'tag-purple';
  if (t.includes('食品') || t.includes('橙')) return 'tag-orange';
  if (t.includes('建筑') || t.includes('黄')) return 'tag-yellow';
  if (t.includes('电子') || t.includes('青')) return 'tag-cyan';
  if (t.includes('交通') || t.includes('红')) return 'tag-red';
  return 'tag-blue';
}

function goToUserProfile() {
  if (props.image?.user) {
    // 获取用户ID
    let userId = null
    if (typeof props.image.user === 'object' && props.image.user.id) {
      userId = props.image.user.id
    } else if (typeof props.image.user === 'number' || typeof props.image.user === 'string') {
      userId = props.image.user
    }
    
    if (userId) {
      console.log('跳转到用户主页:', userId)
      router.push({ name: 'OtherUserHome', params: { id: userId } })
    } else {
      console.warn('无法获取用户ID')
    }
  }
}

const getUserName = computed(() => {
  if (typeof props.image?.user === 'object' && props.image.user.username) {
    return props.image.user.username
  } else if (typeof props.image?.user === 'string') {
    return props.image.user
  }
  return '用户'
})
</script>

<style scoped>
.info-section {
  width: 30vw;
  background-color: var(--secondary-color);
  border-left: 1px solid var(--border-color);
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
  flex-shrink: 0;
  border-top-left-radius: 20px;
  border-bottom-left-radius: 20px;
  color: var(--text-color);
}
.info-section.collapsed {
  width: 40px;
}
.info-section.collapsed::before {
  content: '图片基本信息';
  position: absolute;
  left: 0;
  top: 30px;
  width: 40px;
  writing-mode: vertical-lr;
  text-orientation: upright;
  color: #1e90ff;
  font-size: 1.4em;
  font-weight: bold;
  letter-spacing: 2px;
  padding: 10px 0;
  white-space: nowrap;
  text-align: center;
  z-index: 1;
}
.info-toggle {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 60px;
  background-color: var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 0 4px 4px 0;
  z-index: 2;
  transition: all 0.3s ease;
  color: var(--text-color);
}
.info-toggle:hover {
  background-color: var(--primary-color);
}
.info-toggle .material-icons {
  color: var(--text-color);
  font-size: 20px;
  transition: transform 0.3s ease;
}
.info-section.collapsed .info-toggle .material-icons {
  transform: rotate(180deg);
}
.info-card {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
  margin-left: 20px;
  width: calc(100% - 40px);
  color: var(--text-color);
  border-radius: 24px;
  box-shadow: 0 4px 32px var(--shadow-color);
  background: var(--card-color);
}
.info-card h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: var(--primary-color);
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 12px;
  transition: color 0.3s, border-color 0.3s;
}
.info-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.info-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  background: var(--card-gradient);
  border-radius: 16px;
  box-shadow: 0 2px 8px var(--shadow-color);
  margin-bottom: 8px;
}
.info-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.info-item.full-width {
  width: 100%;
}
.label {
  color: var(--text-color);
  opacity: 0.7;
  width: 80px;
  flex-shrink: 0;
  font-size: 14px;
  transition: color 0.3s;
}
.value {
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.5;
  transition: color 0.3s;
}
.category-tag, .format-tag {
  background: rgba(23, 111, 212, 0.08);
  color: var(--button-text-color);
  border-radius: 12px;
  padding: 2px 14px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(23, 111, 212, 0.2);
  transition: all 0.2s;
}
.format-tag {
  background-color: rgba(82, 196, 26, 0.08);
  color: var(--text-color);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.3s ease;
  border: 1px solid rgba(82, 196, 26, 0.2);
}
.public {
  color: var(--success-color);
  transition: color 0.3s;
}
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tag {
  padding: 4px 14px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  margin-bottom: 2px;
  margin-right: 6px;
  transition: all 0.2s;
  color: #fff;
  box-shadow: 0 2px 8px var(--shadow-color);
  display: inline-block;
}
.tag-blue {
  background: linear-gradient(90deg, #6ec6ff 0%, #1e90ff 100%);
}
.tag-green {
  background: linear-gradient(90deg, #a8e063 0%, #56ab2f 100%);
}
.tag-pink {
  background: linear-gradient(90deg, #ffb6c1 0%, #ff69b4 100%);
}
.tag-purple {
  background: linear-gradient(90deg, #a18cd1 0%, #6d5bba 100%);
}
.tag-orange {
  background: linear-gradient(90deg, #f7b267 0%, #f4845f 100%);
}
.tag-yellow {
  background: linear-gradient(90deg, #ffe259 0%, #ffa751 100%);
  color: #7a4e00;
}
.tag-cyan {
  background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%);
  color: #005a4e;
}
.tag-red {
  background: linear-gradient(90deg, #ff5858 0%, #f857a6 100%);
}
.tag:hover {
  filter: brightness(1.1) drop-shadow(0 2px 8px #0002);
  transform: scale(1.07);
  box-shadow: 0 4px 16px var(--shadow-color-hover);
}
.colors-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}
.color-item {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid var(--card-color);
  transition: transform 0.2s, box-shadow 0.2s;
}
.color-item:hover {
  transform: scale(1.08);
  box-shadow: 0 4px 16px var(--shadow-color-hover);
}
.color-value {
  color: var(--button-text-color);
  font-size: 12px;
  font-weight: 600;
  text-shadow: 0 1px 4px #0008;
}
.uploader-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 12px 0 12px 0;
  border-bottom: 1.5px solid var(--border-color);
}
.uploader-avatar {
  width: 56px !important;
  height: 56px !important;
  border-radius: 50% !important;
  object-fit: cover !important;
  object-position: center !important;
  border: 3px solid !important;
  border-image: var(--primary-gradient) 1 !important;
  box-shadow: 0 2px 12px var(--shadow-color) !important;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden !important;
  display: block !important;
}
.uploader-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 20px var(--shadow-color-hover);
  border-image: var(--primary-gradient-reverse) 1;
}
.uploader-name {
  color: var(--text-color);
  font-size: 20px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  background-clip: text;
}
.follow-btn {
  margin-left: 16px;
  padding: 6px 18px;
  border-radius: 16px;
  border: none;
  background: linear-gradient(90deg, #1e90ff 0%, #6ec6ff 100%);
  color: #fff;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}
.follow-btn:hover {
  background: linear-gradient(90deg, #6ec6ff 0%, #1e90ff 100%);
  color: #fff;
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 16px var(--shadow-color-hover);
}
@media (max-width: 900px) {
  .info-section {
    width: 100vw;
    border-radius: 0;
  }
  .info-card {
    border-radius: 0;
  }
}
</style> 