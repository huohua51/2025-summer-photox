import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import HomeView from '../views/HomeView.vue'
import PersonStoreView from '../views/PersonStoreView.vue'
import PhotoDetailView from '../views/PhotoDetailView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        requiresAuth: false,
        title: '首页',
        showNavbar: true
      }
    },
    {
      path: '/gallery',
      name: 'gallery',
      component: PersonStoreView,
      meta: {
        requiresAuth: true,
        title: '个人仓库',
        showNavbar: true
      }
    },
    {
      path: '/photodetail/:id',
      name: 'photodetail',
      component: PhotoDetailView,
      props: true,
      meta: {
        requiresAuth: false,
        showNavbar: true
      }
    },
    {
      path: '/photo/:id',
      name: 'photo',
      component: PhotoDetailView,
      props: true,
      meta: {
        requiresAuth: false,
        showNavbar: true
      }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: {
        requiresAuth: false,
        showNavbar: false
      }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        requiresAuth: false,
        showNavbar: false
      }
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('@/views/Profile.vue'),
      meta: {
        requiresAuth: true,
        title: '个人中心',
        showNavbar: true
      }
    },
    {
      path: '/category/:name',
      name: 'category-detail',
      component: () => import('@/views/CategoryDetailView.vue'),
      meta: {
        requiresAuth: false,
        title: '分类详情',
        showNavbar: true
      }
    },
    {
      path: '/followings',
      name: 'FollowList',
      component: () => import('@/views/FollowList.vue'),
      meta: {
        requiresAuth: true,
        title: '关注列表',
        showNavbar: true
      }
    },
    {
      path: '/notifications',
      name: 'NotificationList',
      component: () => import('@/views/NotificationList.vue'),
      meta: {
        requiresAuth: true,
        title: '通知列表',
        showNavbar: true
      }
    }, 
    {
      path: '/otheruserhome/:id',
      name: 'OtherUserHome',
      component: () => import('@/views/OtherUserHomeView.vue'),
      meta: {
        requiresAuth: true,
        title: '他人主页',
        showNavbar: true
      }
    },
    {
      path: '/user/:id',
      name: 'user',
      component: () => import('@/views/OtherUserHomeView.vue'),
      meta: {
        requiresAuth: true,
        title: '用户主页',
        showNavbar: true
      }
    },
    {
      path: '/ai-process',
      name: 'ai-process',
      component: () => import('@/views/AIProcessView.vue'),
      meta: {
        requiresAuth: true,
        title: 'AI处理图片',
        showNavbar: true
      }
    },
    {
      path: '/favorites',
      name: 'favorites',
      component: () => import('@/views/FavoritesView.vue'),
      meta: {
        requiresAuth: true,
        title: '我的收藏',
        showNavbar: true
      }
    },
    {
      path: '/explore',
      name: 'explore',
      component: () => import('@/views/ExploreView.vue'),
      meta: {
        requiresAuth: false,
        title: '探索发现',
        showNavbar: true
      }
    }
  ],
})

router.beforeEach(async (to, from, next) => {
  // 如果目标页面不需要认证，直接放行
  if (!to.meta.requiresAuth) {
    next()
    return
  }

  // 需要认证的页面，检查登录状态
  const userStore = useUserStore()
  await userStore.initialize()

  if (!userStore.isLoggedIn) {
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
    return
  }

  next()
})

export default router
