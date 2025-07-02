import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import MasonryWall from 'vue-masonry-wall'



const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.component('MasonryWall', MasonryWall)
app.mount('#app')

// 添加全局头像样式
const globalAvatarStyles = `
/* 全局头像圆形样式 */
.avatar, .user-avatar, .uploader-avatar, [class*="avatar"] img, img[alt*="头像"], img[alt*="avatar"] {
  border-radius: 50% !important;
  object-fit: cover !important;
  object-position: center !important;
  overflow: hidden !important;
}

/* 头像容器样式 */
.avatar-container, .user-avatar, .uploader-avatar, [class*="avatar"] {
  border-radius: 50% !important;
  overflow: hidden !important;
}

/* 强制圆形头像样式 - 最高优先级 */
img[src*="avatar"], img[class*="avatar"], .avatar > img, .user-avatar > img {
  width: 100% !important;
  height: 100% !important;
  border-radius: 50% !important;
  object-fit: cover !important;
  object-position: center !important;
  display: block !important;
}
`

// 将样式注入到页面中
const styleElement = document.createElement('style')
styleElement.textContent = globalAvatarStyles
document.head.appendChild(styleElement) 