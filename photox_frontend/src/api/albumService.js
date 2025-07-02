import apiService from './index'
const api = apiService.api

/**
 * 相册服务API
 * 提供相册的创建、获取、修改功能
 */
const albumService = {
  /**
   * 创建新相册
   * @param {Object} albumData - 相册数据
   * @param {string} albumData.title - 相册标题
   * @param {string} albumData.description - 相册描述
   * @param {boolean} albumData.is_public - 是否公开
   * @returns {Promise<Object>} 创建成功的相册信息
   */
  createAlbum: async (albumData) => {
    try {
      return await api.post('/albums/', albumData)
    } catch (error) {
      console.error('创建相册失败', error)
      throw error
    }
  },
  
  /**
   * 获取当前用户的相册列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.pageSize - 每页数量
   * @returns {Promise<Object>} 分页的相册列表
   */
  getUserAlbums: async (params = {}) => {
    try {
      return await api.get('/albums/', { params })
    } catch (error) {
      console.error('获取用户相册列表失败', error)
      throw error
    }
  },
  
  /**
   * 获取相册详情（包含图片列表）
   * @param {number|string} albumId - 相册ID
   * @returns {Promise<Object>} 相册详情
   */
  getAlbumDetails: async (albumId) => {
    try {
      return await api.get(`/albums/${albumId}/`)
    } catch (error) {
      console.error(`获取相册 ${albumId} 详情失败`, error)
      throw error
    }
  },
  
  /**
   * 修改相册信息
   * @param {number|string} albumId - 相册ID
   * @param {Object} updateData - 要更新的相册信息
   * @param {string} updateData.title - 相册标题
   * @param {string} updateData.description - 相册描述
   * @param {boolean} updateData.is_public - 是否公开
   * @returns {Promise<Object>} 更新后的相册信息
   */
  updateAlbum: async (albumId, updateData) => {
    try {
      return await api.put(`/albums/${albumId}/`, updateData)
    } catch (error) {
      console.error(`修改相册 ${albumId} 信息失败`, error)
      throw error
    }
  },
  
  /**
   * 向相册添加图片
   * @param {number|string} albumId - 相册ID
   * @param {number|string} imageId - 图片ID
   * @returns {Promise<Object>} 添加结果
   */
  addImageToAlbum: async (albumId, imageId) => {
    try {
      return await api.post(`/albums/${albumId}/add_image/`, { image_id: imageId })
    } catch (error) {
      console.error(`向相册 ${albumId} 添加图片 ${imageId} 失败`, error)
      throw error
    }
  },
  
  /**
   * 从相册移除图片
   * @param {number|string} albumId - 相册ID
   * @param {number|string} imageId - 图片ID
   * @returns {Promise<Object>} 移除结果
   */
  removeImageFromAlbum: async (albumId, imageId) => {
    try {
      return await api.post(`/albums/${albumId}/remove_image/`, { image_id: imageId })
    } catch (error) {
      console.error(`从相册 ${albumId} 移除图片 ${imageId} 失败`, error)
      throw error
    }
  },
  
  /**
   * 获取指定用户的相册列表（用于他人主页）
   * @param {number|string} userId - 用户ID
   * @returns {Promise<Object>} 该用户的相册列表
   */
  getAlbumsByUserId: async (userId) => {
    try {
      return await api.get(`/community/users/${userId}/albums/`)
    } catch (error) {
      console.error(`获取用户 ${userId} 的相册列表失败`, error)
      throw error
    }
  }
}

export default albumService 