import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 登录接口
export const login = (data) => {
  return api.post('/login/', data)
}

// 测试连接接口
export const testConnection = () => {
  return api.get('/test/')
}

export default api
