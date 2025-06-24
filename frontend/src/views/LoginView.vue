<template>
  <div class="login-container">
    <div class="login-box">
      <h2>系统登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名</label>
          <input 
            v-model="form.username" 
            type="text" 
            placeholder="请输入用户名"
            required
          />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码"
            required
          />
        </div>
        <button type="submit" class="login-btn">登录</button>
      </form>
      <p class="hint">提示：用户名 admin，密码 123456</p>
      <p v-if="message" :class="['message', messageType]">{{ message }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { login, testConnection } from '../api'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const form = ref({
      username: '',
      password: ''
    })
    const message = ref('')
    const messageType = ref('')

    onMounted(async () => {
      // 测试前后端连接
      try {
        const res = await testConnection()
        console.log('连接测试:', res.data)
      } catch (error) {
        console.error('连接失败:', error)
      }
    })

    const handleLogin = async () => {
      try {
        const res = await login(form.value)
        if (res.data.success) {
          message.value = res.data.message
          messageType.value = 'success'
          setTimeout(() => {
            router.push('/home')
          }, 1000)
        }
      } catch (error) {
        message.value = error.response?.data?.message || '登录失败'
        messageType.value = 'error'
      }
    }

    return {
      form,
      message,
      messageType,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #1890ff;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background-color: #40a9ff;
}

.hint {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin-top: 20px;
}

.message {
  text-align: center;
  margin-top: 10px;
  padding: 8px;
  border-radius: 4px;
  font-size: 14px;
}

.message.success {
  color: #52c41a;
  background-color: #f6ffed;
  border: 1px solid #b7eb8f;
}

.message.error {
  color: #f5222d;
  background-color: #fff1f0;
  border: 1px solid #ffa39e;
}
</style>
