import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1', // 使用相对路径，通过代理访问
  timeout: 30000, // 超时时间30秒
})

// 是否正在刷新token
let isRefreshing = false
// 重试队列
let retryRequests = []

// 刷新token的函数
const refreshToken = async () => {
  try {
    const refresh = localStorage.getItem('refresh_token')
    if (!refresh) {
      throw new Error('No refresh token')
    }
    
    const response = await api.post('/users/token/refresh/', {
      refresh: refresh
    })
    
    const { access } = response.data
    localStorage.setItem('token', access)
    return access
  } catch (error) {
    console.error('刷新token失败:', error)
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
    throw error
  }
}

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从localStorage获取token并添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 如果是 FormData，删除 Content-Type 让浏览器自动设置
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 直接返回响应数据
    return response.data
  },
  async error => {
    console.error('响应错误:', error)
    
    // 如果是 401 未授权，可能是 token 过期
    if (error.response && error.response.status === 401) {
      console.log('Token可能已过期，尝试刷新...')
      // 这里可以添加自动刷新token的逻辑
      // ...
    }
    
    // 如果是 500 错误，打印更详细的信息
    if (error.response && error.response.status === 500) {
      console.error('服务器错误详情:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers
      })
    }
    
    // 构建更友好的错误对象
    const enhancedError = error
    if (error.response) {
      enhancedError.statusCode = error.response.status
      enhancedError.data = error.response.data
      enhancedError.message = error.response.data?.message || error.message
    }
    
    return Promise.reject(enhancedError)
  }
)

// 导出API模块
const apiService = {
  // 认证相关
  auth: {
    // 登录
    login: async (username, password) => {
      try {
        const response = await api.post('/users/login/', { username, password })
        return response
      } catch (error) {
        console.error('登录请求失败:', error)
        throw error
      }
    },
    
    // 注册
    register: async (userData) => {
      try {
        const response = await api.post('/users/register/', userData)
        return response
      } catch (error) {
        console.error('注册请求失败:', error)
        throw error
      }
    },
    
    // 获取当前用户信息
    getCurrentUser: async () => {
      try {
        const response = await api.get('/users/me/')
        return response
      } catch (error) {
        console.error('获取用户信息失败:', error)
        throw error
      }
    },
    
    // 更新用户信息
    updateUser: async (userData) => {
      try {
        const response = await api.put('/users/me/', userData)
        return response
      } catch (error) {
        console.error('更新用户信息失败:', error)
        throw error
      }
    },
    
    // 修改密码
    changePassword: async (passwordData) => {
      try {
        const response = await api.put('/users/password/change/', passwordData)
        return response
      } catch (error) {
        console.error('修改密码失败:', error)
        throw error
      }
    },
    
    // 刷新token
    refreshToken: async () => {
      try {
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) {
          throw new Error('No refresh token')
        }
        
        const response = await api.post('/users/token/refresh/', { refresh })
        return response
      } catch (error) {
        console.error('刷新token失败:', error)
        throw error
      }
    }
  },
  
  // 图片相关
  images: {
    // 获取图片列表
    getList: async (params) => {
      try {
        const response = await api.get('/images/', { params })
        return response
      } catch (error) {
        console.error('获取图片列表失败:', error)
        throw error
      }
    },
    
    // 上传图片
    upload: async (formData) => {
      try {
        const response = await api.post('/images/upload/', formData)
        return response
      } catch (error) {
        console.error('上传图片失败:', error)
        throw error
      }
    },
    
    // 获取图片详情
    getDetail: async (id) => {
      try {
        const response = await api.get(`/images/${id}/`)
        return response
      } catch (error) {
        console.error('获取图片详情失败:', error)
        throw error
      }
    },

    // 点赞/取消点赞图片
    toggleLike: async (id) => {
      try {
        const response = await api.post('/community/likes/toggle/', {
          like_type: 'image',
          object_id: id
        })
        return response
      } catch (error) {
        console.error('点赞/取消点赞失败:', error)
        throw error
      }
    },

    // 获取图片评论
    getComments: async (id) => {
      try {
        const response = await api.get(`/images/${id}/comments/`)
        return response
      } catch (error) {
        console.error('获取评论失败:', error)
        throw error
      }
    },

    // 发布评论
    postComment: async (id, content) => {
      try {
        const response = await api.post(`/images/${id}/comments/`, { content })
        return response
      } catch (error) {
        console.error('发布评论失败:', error)
        throw error
      }
    },

    // AI 智能分析
    aiDescription: async (imageId) => {
      try {
        const response = await api.post(`/images/${imageId}/ai_description/`)
        return response
      } catch (error) {
        console.error('AI智能分析失败:', error)
        throw error
      }
    }
  },
  
  // 评论相关
  comments: {
    // 删除评论
    delete: async (id) => {
      try {
        await api.delete(`/comments/${id}/`)
      } catch (error) {
        console.error('删除评论失败:', error)
        throw error
      }
    },

    // 点赞/取消点赞评论
    toggleLike: async (id) => {
      try {
        const response = await api.post('/community/likes/toggle/', {
          like_type: 'comment',
          object_id: id
        })
        return response
      } catch (error) {
        console.error('评论点赞失败:', error)
        throw error
      }
    }
  },
  
  // 关注相关
  follow: {
    // 获取关注列表
    getFollowings: async (userId) => {
      try {
        const response = await api.get(`/community/follows/${userId}/following/`)
        return response
      } catch (error) {
        console.error('获取关注列表失败:', error)
        throw error
      }
    },
    // 获取粉丝列表
    getFollowers: async (userId) => {
      try {
        const response = await api.get(`/community/follows/${userId}/followers/`)
        return response
      } catch (error) {
        console.error('获取粉丝列表失败:', error)
        throw error
      }
    },
    // 关注/取消关注用户
    toggleFollow: async (userId) => {
      try {
        const response = await api.post(`/community/follows/${userId}/toggle/`)
        return response
      } catch (error) {
        console.error('关注/取消关注失败:', error)
        throw error
      }
    }
  },
  
  // 用户相关
  users: {
    // 获取当前用户信息
    getCurrentUser: async () => {
      try {
        const response = await api.get('/community/users/me/')
        return response
      } catch (error) {
        console.error('获取当前用户信息失败:', error)
        throw error
      }
    },
    // 获取指定用户信息
    getUserById: async (userId) => {
      try {
        const response = await api.get(`/community/users/${userId}/`)
        return response
      } catch (error) {
        console.error('获取用户信息失败:', error)
        throw error
      }
    }
  },
  
  // 通知相关
  notification: {
    // 获取通知列表
    getList: async () => {
      try {
        const response = await api.get('/community/notifications/')
        return response
      } catch (error) {
        console.error('获取通知列表失败:', error)
        throw error
      }
    },
    // 标记全部为已读
    markAllRead: async () => {
      try {
        const response = await api.post('/community/notifications/mark_all_read/')
        return response
      } catch (error) {
        console.error('标记全部通知为已读失败:', error)
        throw error
      }
    },
    // 标记单条为已读
    markRead: async (id) => {
      try {
        const response = await api.post(`/community/notifications/${id}/mark_read/`)
        return response
      } catch (error) {
        console.error('标记通知为已读失败:', error)
        throw error
      }
    },
    // 获取未读数量
    getUnreadCount: async () => {
      try {
        const response = await api.get('/community/notifications/unread_count/')
        return response
      } catch (error) {
        console.error('获取未读通知数量失败:', error)
        throw error
      }
    }
  },
  
  // 导出原始api实例
  api
}

export default apiService