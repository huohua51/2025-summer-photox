<template>
  <div class="home-container">
    <h1>欢迎来到首页</h1>
    <p>登录成功！这是一个Django + Vue的前后端分离项目模板。</p>
    <button @click="logout" class="logout-btn">退出登录</button>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'HomeView',
  setup() {
    const router = useRouter()

    const logout = () => {
      router.push('/login')
    }

    return {
      logout
    }
  }
}
</script>

<style scoped>
.home-container {
  max-width: 800px;
  margin: 50px auto;
  padding: 20px;
  text-align: center;
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

.logout-btn {
  margin-top: 30px;
  padding: 10px 20px;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.logout-btn:hover {
  background-color: #ff7875;
}
</style>
