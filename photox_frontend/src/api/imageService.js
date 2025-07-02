import apiService from './index'
const { api, images } = apiService


// 工具函数：格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 工具函数：获取图片尺寸
const getImageDimensions = (file) => {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      resolve(`${img.width}x${img.height}`)
      URL.revokeObjectURL(img.src)
    }
    img.src = URL.createObjectURL(file)
  })
}

/**
 * 图片服务API
 * 提供图片上传、获取、修改和删除功能
 */
const imageService = {
  /**
   * 上传单张图片
   * @param {File} imageFile - 要上传的图片文件
   * @param {Object} options - 上传选项
   * @param {string} options.title - 图片标题（可选）
   * @param {Function} options.onProgress - 上传进度回调（可选）
   * @returns {Promise<Object>} 上传成功的图片信息
   */
  uploadImage: async (imageFile, options = {}) => {
    try {
      console.log('开始上传图片...', {
        fileName: imageFile.name,
        fileSize: imageFile.size,
        fileType: imageFile.type
      })
      
      // 验证文件是否为图片
      if (!imageFile.type.startsWith('image/')) {
        throw new Error('仅支持图片文件')
      }
      
      // 检查是否有token
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('请先登录')
      }
      
      // 创建FormData
      const formData = new FormData()
      formData.append('image', imageFile)
      
      // 添加标题（可选）
      if (options.title) {
        formData.append('title', options.title)
      }
      
      // 添加公开状态（可选，默认为false）
      if (options.is_public !== undefined) {
        formData.append('is_public', options.is_public)
      }

      // 打印FormData内容
      for (let pair of formData.entries()) {
        console.log('FormData内容:', pair[0], pair[1])
      }

      // 使用 api.post 直接上传
      const response = await api.post('/images/upload/', formData, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        // 保持原始 FormData 格式，不进行任何转换
        transformRequest: [(data) => data],
        onUploadProgress: (progressEvent) => {
          if (options.onProgress) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            options.onProgress(percentCompleted)
          }
        }
      })
      
      console.log('上传响应:', response)
      
      // 检查响应格式
      if (!response) {
        throw new Error('无效的响应格式')
      }
      
      // 返回标准化的图片数据
      return {
        id: response.id,
        thumbnail: response.image_url,
        url: response.image_url,
        size: formatFileSize(imageFile.size),
        dimensions: await getImageDimensions(imageFile),
        type: imageFile.type.split('/')[1].toUpperCase(),
        createdAt: new Date().toLocaleString()
      }
    } catch (error) {
      console.error('图片上传服务失败:', error)
      if (error.response) {
        console.error('错误响应:', error.response.data)
        console.error('错误状态:', error.response.status)
        console.error('错误头信息:', error.response.headers)
        console.error('请求头信息:', error.config?.headers)
        
        // 处理特定错误
        if (error.response.status === 401) {
          throw new Error('登录已过期，请重新登录')
        } else if (error.response.status === 413) {
          throw new Error('文件太大，请选择小于5MB的图片')
        } else if (error.response.status === 415) {
          throw new Error('不支持的图片格式')
        } else if (error.response.status === 500) {
          const errorMessage = error.response.data?.message || '服务器错误，请稍后重试'
          throw new Error(errorMessage)
        }
      }
      throw error
    }
  },
  
  /**
   * 获取单张图片详情
   * @param {number|string} imageId - 图片ID
   * @returns {Promise<Object>} 图片详情
   */
  getImageDetail: async (imageId) => {
    try {
      const response = await api.get(`/images/${imageId}/`)
      console.log('获取图片详情响应:', response)
      return response
    } catch (error) {
      console.error('获取图片详情失败', error)
      throw error
    }
  },
  
  /**
   * 修改图片信息
   * @param {number|string} imageId - 图片ID
   * @param {Object} updateData - 要更新的图片信息
   * @param {string} updateData.title - 图片标题
   * @returns {Promise<Object>} 更新后的图片信息
   */
  updateImage: async (imageId, updateData) => {
    try {
      return await api.put(`/images/${imageId}/`, updateData)
    } catch (error) {
      console.error(`修改图片 ${imageId} 信息失败`, error)
      throw error
    }
  },
  
  /**
   * 删除图片
   * @param {number|string} imageId - 要删除的图片ID
   * @returns {Promise<void>}
   */
  deleteImage: async (imageId) => {
    try {
      console.log('发送删除请求:', imageId)
      await api.delete(`/images/${imageId}/`)
      // 204 状态码表示删除成功，不需要返回任何数据
      return true
    } catch (error) {
      console.error(`删除图片 ${imageId} 失败:`, error)
      if (error.response) {
        console.error('错误响应:', error.response.data)
        console.error('错误状态:', error.response.status)
      }
      throw error
    }
  },
  
  /**
   * 获取当前用户的图片列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码或下一页的URL
   * @param {number} params.pageSize - 每页数量
   * @param {string} params.ordering - 排序方式，如"-created_at"按创建时间倒序
   * @returns {Promise<Object>} 分页的图片列表
   */
  getUserImages: async (params = {}) => {
    try {
      let url = '/images/'
      let config = {}
      
      // 如果提供了完整的下一页URL，直接使用它
      if (typeof params.page === 'string' && params.page.startsWith('http')) {
        url = params.page
      } else {
        // 否则构建查询参数
        config = { params }
      }
      
      const response = await api.get(url, config)
      console.log('API响应:', response)
      
      // 确保返回正确的数据结构
      if (response && response.data) {
        return response.data
      } else if (response && response.results) {
        return response
      } else {
        throw new Error('无效的响应格式')
      }
    } catch (error) {
      console.error('获取用户图片列表失败', error)
      throw error
    }
  },
  
  /**
   * 获取图片分类
   * @returns {Promise<Object>} 图片分类列表
   */
  getImageCategories: async () => {
    try {
      const response = await api.images.getCategories()
      console.log('获取分类响应:', response)
      return response
    } catch (error) {
      console.error('获取图片分类失败', error)
      throw error
    }
  },
  
  /**
   * 获取指定用户的公开图片
   * @param {number|string} userId - 用户ID
   * @param {object} params - 额外参数（如分页）
   * @returns {Promise<Object>} 公开图片列表
   */
  getUserPublicImages: async (userId, params = {}) => {
    return api.get('/images/', {
      params: {
        user: userId,
        is_public: true,
        ...params
      }
    })
  },

  /**
   * 批量删除图片
   * @param {Array<number|string>} imageIds - 要删除的图片ID数组
   * @returns {Promise<Object>} 删除结果
   */
  batchDeleteImages: async (imageIds) => {
    try {
      console.log('批量删除图片:', imageIds)
      const deletePromises = imageIds.map(id => 
        api.delete(`/images/${id}/`)
      )
      
      const results = await Promise.allSettled(deletePromises)
      
      // 统计成功和失败的数量
      const successful = results.filter(result => result.status === 'fulfilled').length
      const failed = results.filter(result => result.status === 'rejected').length
      
      console.log(`批量删除完成: 成功 ${successful} 张, 失败 ${failed} 张`)
      
      return {
        successful,
        failed,
        total: imageIds.length,
        results
      }
    } catch (error) {
      console.error('批量删除图片失败:', error)
      throw error
    }
  },

  /**
   * 批量收藏图片
   * @param {Array<number|string>} imageIds - 要收藏的图片ID数组
   * @returns {Promise<Object>} 操作结果
   */
  batchFavorite: async (imageIds) => {
    try {
      const favoritePromises = imageIds.map(id =>
        api.post(`/community/favorites/${id}/`)
      )
      const results = await Promise.allSettled(favoritePromises)
      const successful = results.filter(r => r.status === 'fulfilled').length
      const failed = results.filter(r => r.status === 'rejected').length
      return {
        successful,
        failed,
        total: imageIds.length,
        results
      }
    } catch (error) {
      console.error('批量收藏图片失败:', error)
      throw error
    }
  },

  /**
   * 获取Instagram风格的信息流
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.page_size - 每页数量
   * @returns {Promise<Object>} 信息流数据
   */
  getFeed: async (params = {}) => {
    try {
      const response = await api.get('/images/feed/', { params })
      console.log('信息流响应:', response)
      
      // 确保返回正确的数据结构
      if (response && response.data) {
        return response.data
      } else if (response && response.results) {
        return response
      } else {
        throw new Error('无效的响应格式')
      }
    } catch (error) {
      console.error('获取信息流失败', error)
      throw error
    }
  },

  /**
   * 图片处理
   * @param {number|string} imageId - 图片ID
   * @param {Object} params - 处理参数
   * @param {string} params.style - 风格类型
   * @param {Object} params.adjustments - 参数调节
   * @param {Array} params.enhancements - 智能增强选项
   * @returns {Promise<Object>} 处理结果
   */
  aiProcess: async (imageId, params = {}) => {
    try {
      console.log('开始处理图片:', imageId, params)
      const response = await api.post(`/images/${imageId}/ai-process/`, params)
      console.log('AI处理响应:', response)
      return response
    } catch (error) {
      console.error('图片处理失败:', error)
      throw error
    }
  },

  /**
   * 处理本地图片
   * @param {FormData} formData - 包含图片文件和参数的FormData
   * @returns {Promise<Object>} 处理结果
   */
  aiProcessLocal: async (formData) => {
    try {
      console.log('开始处理本地图片')
      const response = await api.post('/images/ai-process-local/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      console.log('本地图片处理响应:', response)
      return response
    } catch (error) {
      console.error('本地图片处理失败:', error)
      throw error
    }
  },

  /**
   * 删除处理后的图片
   * @param {Object} params - 参数
   * @param {string} params.file_name - 文件名
   * @returns {Promise<Object>} 删除结果
   */
  deleteProcessedImage: async (params) => {
    try {
      console.log('删除处理后的图片:', params.file_name)
      const response = await api.delete('/images/delete-processed/', { data: params })
      console.log('删除处理后图片响应:', response)
      return response
    } catch (error) {
      console.error('删除处理后图片失败:', error)
      throw error
    }
  },

  /**
   * 获取图片标签
   * @param {number|string} imageId - 图片ID
   * @returns {Promise<Object>} 标签数据
   */
  getImageTags: async (imageId) => {
    try {
      const response = await api.get(`/images/${imageId}/tags/`)
      return response
    } catch (error) {
      console.error('获取图片标签失败:', error)
      throw error
    }
  },



  /**
   * 添加用户标签
   * @param {number|string} imageId - 图片ID
   * @param {Array} tags - 标签数组
   * @returns {Promise<Object>} 添加结果
   */
  addUserTags: async (imageId, tags) => {
    try {
      const response = await api.post(`/images/${imageId}/tags/`, { tags })
      return response
    } catch (error) {
      console.error('添加用户标签失败:', error)
      throw error
    }
  },

  /**
   * 删除用户标签
   * @param {number|string} imageId - 图片ID
   * @param {Array} tags - 要删除的标签数组
   * @returns {Promise<Object>} 删除结果
   */
  removeUserTags: async (imageId, tags) => {
    try {
      const response = await api.delete(`/images/${imageId}/tags/`, { data: { tags } })
      return response
    } catch (error) {
      console.error('删除用户标签失败:', error)
      throw error
    }
  },

  /**
   * AI风格分析
   * @param {number|string} imageId - 图片ID
   * @returns {Promise<Object>} 分析结果
   */
  styleAnalysis: async (imageId) => {
    try {
      const response = await api.post(`/images/${imageId}/style-analysis/`)
      return response
    } catch (error) {
      console.error('AI风格分析失败:', error)
      throw error
    }
  },

  /**
   * 获取AI推荐图片
   * @returns {Promise<Object>} 推荐结果
   */
  getRecommendations: async () => {
    try {
      const response = await api.get('/images/recommendations/')
      return response
    } catch (error) {
      console.error('获取AI推荐失败:', error)
      throw error
    }
  },

  /**
   * 批量上传图片
   * @param {Array<File>} imageFiles - 要上传的图片文件数组
   * @param {Object} options - 上传选项
   * @param {string} options.title - 图片标题（可选，会应用到所有图片）
   * @param {boolean} options.is_public - 是否公开（可选）
   * @param {Function} options.onProgress - 上传进度回调（可选）
   * @param {Function} options.onFileProgress - 单个文件上传进度回调（可选）
   * @returns {Promise<Object>} 批量上传结果
   */
  uploadImages: async (imageFiles, options = {}) => {
    try {
      console.log('开始批量上传图片...', {
        fileCount: imageFiles.length,
        files: imageFiles.map(f => ({ name: f.name, size: f.size, type: f.type }))
      })
      
      // 验证文件
      for (const file of imageFiles) {
        if (!file.type.startsWith('image/')) {
          throw new Error(`文件 ${file.name} 不是图片格式`)
        }
      }
      
      // 检查是否有token
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('请先登录')
      }
      
      // 创建FormData
      const formData = new FormData()
      
      // 添加所有图片文件
      imageFiles.forEach((file, index) => {
        formData.append('images', file)
      })
      
      // 添加其他参数
      if (options.title) {
        formData.append('title', options.title)
      }
      
      if (options.is_public !== undefined) {
        formData.append('is_public', options.is_public)
      }

      // 打印FormData内容
      for (let pair of formData.entries()) {
        console.log('FormData内容:', pair[0], pair[1])
      }

      // 发送批量上传请求
      const response = await api.post('/images/batch-upload/', formData, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        transformRequest: [(data) => data],
        onUploadProgress: (progressEvent) => {
          if (options.onProgress) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            options.onProgress(percentCompleted)
          }
        }
      })
      
      console.log('批量上传响应:', response)
      
      // 处理响应结果
      if (!response) {
        throw new Error('无效的响应格式')
      }
      
      // 返回标准化的批量上传结果
      return {
        success: response.success_count || 0,
        failed: response.error_count || 0,
        total: imageFiles.length,
        results: response.results || [],
        errors: response.errors || [],
        message: response.message || '批量上传完成'
      }
      
    } catch (error) {
      console.error('批量图片上传服务失败:', error)
      if (error.response) {
        console.error('错误响应:', error.response.data)
        console.error('错误状态:', error.response.status)
        
        // 处理特定错误
        if (error.response.status === 401) {
          throw new Error('登录已过期，请重新登录')
        } else if (error.response.status === 413) {
          throw new Error('文件太大，请选择小于5MB的图片')
        } else if (error.response.status === 415) {
          throw new Error('不支持的图片格式')
        } else if (error.response.status === 500) {
          const errorMessage = error.response.data?.message || '服务器错误，请稍后重试'
          throw new Error(errorMessage)
        }
      }
      throw error
    }
  },
  
  /**
   * 批量上传图片（支持每个文件独立标题）
   * @param {Array<Object>} filesWithTitles - 包含文件和标题的对象数组
   * @param {Array<Object>} filesWithTitles[].file - 图片文件
   * @param {string} filesWithTitles[].title - 图片标题
   * @param {Object} options - 上传选项
   * @param {boolean} options.is_public - 是否公开（可选）
   * @param {Function} options.onProgress - 上传进度回调（可选）
   * @returns {Promise<Object>} 批量上传结果
   */
  uploadImagesWithTitles: async (filesWithTitles, options = {}) => {
    try {
      console.log('开始批量上传图片（独立标题）...', {
        fileCount: filesWithTitles.length,
        files: filesWithTitles.map(f => ({ 
          name: f.file.name, 
          size: f.file.size, 
          type: f.file.type,
          title: f.title 
        }))
      })
      
      // 验证文件
      for (const item of filesWithTitles) {
        if (!item.file.type.startsWith('image/')) {
          throw new Error(`文件 ${item.file.name} 不是图片格式`)
        }
      }
      
      // 检查是否有token
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('请先登录')
      }
      
      // 逐个上传文件，因为每个文件需要不同的标题
      const results = []
      const errors = []
      let successCount = 0
      let failedCount = 0
      
      for (let i = 0; i < filesWithTitles.length; i++) {
        const { file, title } = filesWithTitles[i]
        
        try {
          console.log(`上传第 ${i + 1} 个文件: ${file.name}, 标题: ${title}`)
          
          // 创建FormData
          const formData = new FormData()
          formData.append('image', file)
          formData.append('title', title)
          
          if (options.is_public !== undefined) {
            formData.append('is_public', options.is_public)
          }

          // 发送单个文件上传请求
          const response = await api.post('/images/upload/', formData, {
            headers: {
              'Authorization': `Bearer ${token}`
            },
            transformRequest: [(data) => data]
          })
          
          // 处理成功响应
          const imageData = {
            id: response.id,
            thumbnail: response.image_url,
            url: response.image_url,
            size: formatFileSize(file.size),
            dimensions: await getImageDimensions(file),
            type: file.type.split('/')[1].toUpperCase(),
            createdAt: new Date().toLocaleString(),
            title: title
          }
          
          results.push(imageData)
          successCount++
          
          // 更新进度
          if (options.onProgress) {
            const progress = Math.round(((i + 1) / filesWithTitles.length) * 100)
            options.onProgress(progress)
          }
          
        } catch (error) {
          console.error(`上传文件 ${file.name} 失败:`, error)
          errors.push({
            file: file.name,
            error: error.message || '上传失败'
          })
          failedCount++
        }
      }
      
      // 返回标准化的批量上传结果
      return {
        success: successCount,
        failed: failedCount,
        total: filesWithTitles.length,
        results: results,
        errors: errors,
        message: `批量上传完成，成功 ${successCount} 个，失败 ${failedCount} 个`
      }
      
    } catch (error) {
      console.error('批量图片上传服务失败:', error)
      throw error
    }
  },

  batchFavorite: async (imageIds) => {
    try {
      const favoritePromises = imageIds.map(id =>
        api.post(`/community/favorites/${id}/`)
      )
      const results = await Promise.allSettled(favoritePromises)
      const successful = results.filter(r => r.status === 'fulfilled').length
      const failed = results.filter(r => r.status === 'rejected').length
      return {
        successful,
        failed,
        total: imageIds.length,
        results
      }
    } catch (error) {
      console.error('批量收藏图片失败:', error)
      throw error
    }
  }
}

export default imageService 