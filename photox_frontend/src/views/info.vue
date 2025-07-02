<template>
  <div class="profile-page-fullscreen">

    <main class="profile-main-content">
      <p class="welcome-message" v-if="!isEditing">欢迎回来, {{ user.username }}！在这里管理您的账户信息。</p>
      <p class="editing-intro" v-else>请仔细修改您的账户信息。</p>
      
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-if="!isEditing && !loading" class="display-mode">
        <section class="info-card">
          <h2 class="card-title">账户概览</h2>
          <div class="info-grid">
            <div class="info-item">
              <div class="info-item-header">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" /></svg>
                <span class="info-label">用户名</span>
              </div>
              <p class="info-value">{{ user.username }}</p>
            </div>
            <div class="info-item">
              <div class="info-item-header">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon"><path d="M2.003 5.884L10 2.006l7.997 3.878A2 2 0 0119 7.681V14a2 2 0 01-2 2H3a2 2 0 01-2-2V7.681a2 2 0 011.003-1.797zM10 4L3 7v7h14V7l-7-3z" /></svg>
                <span class="info-label">邮箱地址</span>
              </div>
              <p class="info-value">{{ user.email }}</p>
            </div>
            
            <div class="info-item info-item-full-width">
               <div class="info-item-header">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon"><path fill-rule="evenodd" d="M18 8a6 6 0 01-7.743 5.743L10 14l-1 1-1 1H6v2H2v-4l4.257-4.257A6 6 0 1118 8zm-6-4a1 1 0 100 2 2 2 0 012 2 1 1 0 102 0 4 4 0 00-4-4z" clip-rule="evenodd" /></svg>
                <span class="info-label">账户安全</span>
              </div>
              <p class="info-value">密码已受保护 (••••••••)</p>
            </div>
          </div>
        </section>
        <button @click="startEdit" class="btn btn-primary btn-edit-profile">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon btn-icon"><path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" /><path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" /></svg>
          编辑个人资料
        </button>
      </div>
      <div v-else class="edit-mode">
        <form @submit.prevent="saveChanges" class="edit-form">
          <h2 class="form-title">编辑个人资料</h2>
          
          <section class="form-section">
            <h3 class="section-title">基本信息</h3>
            <div class="form-group">
              <label for="username">用户名</label>
              <div class="input-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="input-icon"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" /></svg>
                <input type="text" id="username" v-model="editableUser.username" required placeholder="输入您的新用户名" />
              </div>
            </div>
            <div class="form-group">
              <label for="email">邮箱地址</label>
              <div class="input-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="input-icon"><path d="M2.003 5.884L10 2.006l7.997 3.878A2 2 0 0119 7.681V14a2 2 0 01-2 2H3a2 2 0 01-2-2V7.681a2 2 0 011.003-1.797zM10 4L3 7v7h14V7l-7-3z" /></svg>
                <input type="email" id="email" v-model="editableUser.email" required placeholder="输入您的新邮箱地址" />
              </div>
            </div>
          </section>
          
          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
          <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
          <div class="form-actions">
            <button type="submit" class="btn btn-success" :disabled="isSaving">
              <span v-if="isSaving" class="btn-loading"></span>
              <template v-else>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon btn-icon"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
                保存更改
              </template>
            </button>
            <button type="button" @click="cancelEdit" class="btn btn-secondary" :disabled="isSaving">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon btn-icon"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                取消
            </button>
          </div>
        </form>
      </div>
    </main>
     <footer class="profile-page-footer">
      <p>&copy; {{ new Date().getFullYear() }} 个人中心. 保留所有权利.</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

const user = reactive({
  username: '',
  email: ''
});

const editableUser = ref({
  username: '',
  email: ''
});

const isEditing = ref(false);
const loading = ref(true);
const isSaving = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    loading.value = true;
    const response = await axios.get('/users/me/');
    if (response.data.code === 0) {
      Object.assign(user, response.data.data);
    } else {
      errorMessage.value = '获取用户信息失败: ' + response.data.message;
    }
  } catch (error) {
    errorMessage.value = '获取用户信息出错: ' + (error.response?.data?.message || error.message);
  } finally {
    loading.value = false;
  }
};

// 开始编辑
const startEdit = () => {
  editableUser.value = {
    username: user.username,
    email: user.email
  };
  errorMessage.value = '';
  successMessage.value = '';
  isEditing.value = true;
};

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false;
  errorMessage.value = '';
  successMessage.value = '';
};

// 保存更改
const saveChanges = async () => {
  errorMessage.value = '';
  successMessage.value = '';
  
  // 验证表单
  if (!editableUser.value.username.trim() || !editableUser.value.email.trim()) {
    errorMessage.value = '用户名和邮箱不能为空。';
    return;
  }
  
  if (!/^\S+@\S+\.\S+$/.test(editableUser.value.email)) {
    errorMessage.value = '请输入有效的邮箱地址。';
    return;
  }
  
  try {
    isSaving.value = true;
    
    // 准备更新数据
    const updateData = {
      username: editableUser.value.username.trim(),
      email: editableUser.value.email.trim()
    };
    
    // 调用API更新用户信息
    const response = await axios.put('/users/me/', updateData);
    
    if (response.data.code === 0) {
      // 更新成功，同步本地数据
      Object.assign(user, response.data.data);
      successMessage.value = '用户信息已成功保存！';
      setTimeout(() => {
        isEditing.value = false;
        successMessage.value = '';
      }, 2000);
    } else {
      errorMessage.value = '更新失败: ' + response.data.message;
    }
  } catch (error) {
    errorMessage.value = '更新出错: ' + (error.response?.data?.message || error.message);
  } finally {
    isSaving.value = false;
  }
};

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUserInfo();
});
</script>

<style>
/* Global reset and base for full page */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  background-color: rgb(30, 30, 30); /* 更深的页面背景 */
  color-scheme: dark; /* 提示浏览器使用深色主题的默认控件样式 */
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #b0b0b0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 191, 255, 0.3);
  border-radius: 50%;
  border-top-color: #00bfff;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-loading {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

.btn[disabled] {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

*, *::before, *::after {
  box-sizing: border-box;
}

.profile-page-fullscreen {
  width: 100%;
  min-height: 100vh; 
  background: linear-gradient(135deg, rgb(38, 38, 38) 0%, rgb(28, 28, 28) 100%);
  color: #e0e0e0; 
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  display: flex;
  flex-direction: column;
  line-height: 1.6;
}

.profile-page-header {
  background-color: rgba(25, 25, 25, 0.85);
  padding: 20px 0;
  text-align: center;
  width: 100%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(5px); /* 毛玻璃效果 */
  border-bottom: 1px solid rgba(255,255,255,0.1);
  z-index: 100; /* 确保在最上层 */
}
.header-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #00bfff; /* 深天蓝 */
}
.header-icon {
  width: 32px;
  height: 32px;
}
.profile-page-header h1 { /* 修改了选择器 */
  margin: 0;
  font-size: 2.2em;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.profile-main-content {
  width: 100%;
  max-width: 850px; 
  margin: 50px auto; 
  padding: 35px 45px; 
  background-color: rgba(45, 45, 45, 0.9);
  border-radius: 12px; 
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); 
  flex-grow: 1;
  border: 1px solid rgba(255,255,255,0.08);
}

.welcome-message, .editing-intro {
  font-size: 1.1em;
  color: #b0b0b0;
  text-align: center;
  margin-bottom: 30px;
  padding: 10px;
  background-color: rgba(255,255,255,0.03);
  border-radius: 6px;
}

/* Display Mode */
.info-card {
  background-color: transparent; /* 使用 main-content 的背景 */
  padding: 10px 0; /* 减少内边距，靠grid管理 */
  border-radius: 8px;
  margin-bottom: 35px;
}
.card-title {
  font-size: 1.6em;
  color: #00bfff;
  margin-bottom: 25px;
  padding-bottom: 10px;
  border-bottom: 2px solid #00bfff; /* 更明显的标题下划线 */
  text-align: left;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); /* 响应式网格 */
  gap: 25px;
}
.info-item {
  background-color: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.1);
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
.info-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0,0,0,0.3);
}
.info-item-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.info-label {
  color: #c0c0c0; 
  font-weight: 600;
  font-size: 0.95em;
  margin-left: 8px;
}
.info-value {
  color: #f0f0f0;
  font-size: 1.1em;
  word-break: break-all;
}
.info-item-full-width {
  grid-column: 1 / -1; /* 占满整行 */
}


/* Edit Mode */
.edit-form .form-title {
  font-size: 1.6em;
  color: #00bfff;
  margin-bottom: 30px;
  text-align: center;
}
.form-section {
  margin-bottom: 30px;
  padding: 25px;
  background-color: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.07);
}
.section-title {
  font-size: 1.3em;
  color: #d0d0d0;
  margin-bottom: 20px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255,255,255,0.15);
  padding-bottom: 8px;
}
.section-divider {
  border: none;
  height: 1px;
  background-color: rgba(255,255,255,0.1);
  margin: 35px 0;
}

.form-group {
  margin-bottom: 22px;
}
.form-group label {
  display: block;
  color: #b8b8b8;
  margin-bottom: 10px;
  font-size: 1em;
  font-weight: 500;
}
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #777;
}
.form-group input[type="text"],
.form-group input[type="email"] {
  width: 100%;
  padding: 14px 18px 14px 45px; /* 增加左内边距给图标空间 */
  background-color: #1e1e1e; 
  border: 1px solid #555; 
  border-radius: 6px;
  color: #e0e0e0;
  font-size: 1em;
  transition: border-color 0.25s ease, box-shadow 0.25s ease, background-color 0.25s ease;
}
.form-group input:focus {
  outline: none;
  border-color: #00bfff; 
  background-color: #2a2a2a;
  box-shadow: 0 0 0 4px rgba(0, 191, 255, 0.15); 
}
.form-group input::placeholder {
  color: #777;
  font-style: italic;
}


/* Buttons */
.btn {
  padding: 12px 28px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.05em;
  font-weight: 600; /* 加粗 */
  letter-spacing: 0.5px;
  transition: all 0.25s ease;
  display: inline-flex; 
  align-items: center;
  justify-content: center;
  text-transform: capitalize; /* 首字母大写 */
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.btn:active {
  transform: translateY(0px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.btn-edit-profile {
  display: block; 
  width: fit-content; /* 适应内容宽度 */
  margin: 20px auto 0; /* 居中 */
  padding: 14px 35px; /* 更大的编辑按钮 */
}

.btn-primary {
  background: linear-gradient(145deg, #007bff, #0056b3);
  color: white;
}
.btn-primary:hover {
  background: linear-gradient(145deg, #0069d9, #004085);
}

.btn-success {
  background: linear-gradient(145deg, #28a745, #1e7e34);
  color: white;
}
.btn-success:hover {
  background: linear-gradient(145deg, #218838, #155724);
}

.btn-secondary {
  background: linear-gradient(145deg, #6c757d, #545b62);
  color: white;
}
.btn-secondary:hover {
  background: linear-gradient(145deg, #5a6268, #303336);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 20px; 
  margin-top: 35px;
  padding-top: 20px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.error-message, .success-message { /* 合并错误和成功消息样式 */
  border: 1px solid;
  padding: 15px 20px;
  border-radius: 8px;
  margin: 25px 0;
  text-align: center;
  font-size: 1em;
  font-weight: 500;
}
.error-message {
  background-color: rgba(255, 77, 79, 0.1);
  border-color: #ff4d4f;
  color: #ff7875; 
}
.success-message { /* 新增成功消息样式 */
   background-color: rgba(40, 167, 69, 0.1);
   border-color: #28a745;
   color: #52c41a;
}

/* Footer */
.profile-page-footer {
  text-align: center;
  padding: 25px 0;
  margin-top: auto; /* 推到底部 */
  width: 100%;
  background-color: rgba(25, 25, 25, 0.7);
  border-top: 1px solid rgba(255,255,255,0.08);
  font-size: 0.9em;
  color: #888;
}

.icon {
  width: 22px; /* 稍大一点的图标 */
  height: 22px;
  margin-right: 10px;
  color: #00bfff; 
}
.btn-icon {
  margin-right: 10px;
  vertical-align: middle;
  width: 18px; 
  height: 18px;
}
</style>