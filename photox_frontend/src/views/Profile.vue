<template>
  <div class="profile-page-fullscreen">
    
    <main class="profile-main-content">
      <p class="welcome-message" v-if="!isEditing">欢迎回来, {{ user.nickname || user.username }}！在这里管理您的账户信息。</p>
      <p class="editing-intro" v-else>请仔细修改您的账户信息。</p>
      
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-if="!isEditing && !loading" class="display-mode">
        <section class="info-card">
          <h2 class="card-title">账户概览</h2>
          
          <div class="avatar-container">
            <img v-if="user.avatar" :src="getFullAvatarUrl(user.avatar)" alt="用户头像" class="user-avatar" />
            <div v-else class="avatar-placeholder">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
          
          <div class="info-grid">
            <!-- <div class="info-item">
              <div class="info-item-header">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon">
                  <path d="M10 12a5 5 0 100-10 5 5 0 000 10z"/>
                </svg>
                <span class="info-label">昵称</span>
              </div>
              <p class="info-value">{{ user.nickname || '未设置' }}</p>
            </div> -->
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
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon"><path fill-rule="evenodd" d="M18 13V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h3l3 3 3-3h3a2 2 0 002-2zM5 7a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm1 3a1 1 0 100 2h3a1 1 0 100-2H6z" clip-rule="evenodd" /></svg>
                <span class="info-label">个人简介</span>
              </div>
              <p class="info-value bio-text">{{ user.bio || '暂无简介' }}</p>
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
              <label for="nickname">昵称</label>
              <div class="input-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="input-icon"><path d="M10 12a5 5 0 100-10 5 5 0 000 10z"/></svg>
                <input type="text" id="nickname" v-model="editableUser.nickname" placeholder="输入您的昵称" />
              </div>
            </div>
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
            <div class="form-group">
              <label for="avatar">头像</label>
              <input type="file" id="avatar" @change="onAvatarChange" accept="image/*" />
              <img v-if="avatarPreview" :src="avatarPreview" class="avatar-preview" />
            </div>
            <div class="form-group">
              <label for="bio">个人简介</label>
              <div class="input-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="input-icon"><path fill-rule="evenodd" d="M18 13V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h3l3 3 3-3h3a2 2 0 002-2zM5 7a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm1 3a1 1 0 100 2h3a1 1 0 100-2H6z" clip-rule="evenodd" /></svg>
                <textarea id="bio" v-model="editableUser.bio" rows="4" placeholder="介绍一下自己吧..." class="bio-input"></textarea>
              </div>
            </div>
          </section>
          
          <!-- 添加修改密码部分 -->
          <section class="form-section">
            <h3 class="section-title">修改密码</h3>
            <div class="form-group">
              <label for="old_password">当前密码</label>
              <div class="input-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="input-icon">
                  <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                </svg>
                <input type="password" id="old_password" v-model="passwordData.old_password" placeholder="输入当前密码" />
              </div>
            </div>
            <div class="form-group">
              <label for="new_password">新密码</label>
              <div class="input-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="input-icon">
                  <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                </svg>
                <input type="password" id="new_password" v-model="passwordData.new_password" placeholder="输入新密码" />
              </div>
            </div>
            <div class="form-group">
              <label for="confirm_password">确认新密码</label>
              <div class="input-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="input-icon">
                  <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                </svg>
                <input type="password" id="confirm_password" v-model="passwordData.confirm_password" placeholder="再次输入新密码" />
              </div>
            </div>
            <button type="button" @click="changePassword" class="btn btn-primary change-password-btn">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon btn-icon">
                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
              </svg>
              修改密码
            </button>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '@/api';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

// 获取完整的头像URL
const getFullAvatarUrl = (avatarPath) => {
  if (!avatarPath) return '';
  if (avatarPath.startsWith('http')) return avatarPath;
  return `http://127.0.0.1:8000${avatarPath}`;
};

const user = reactive({
  username: '',
  email: '',
  bio: ''
});

const editableUser = ref({
  username: '',
  email: '',
  bio: ''
});

const passwordData = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
});

const isEditing = ref(false);
const loading = ref(true);
const isSaving = ref(false);
const isChangingPassword = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
const avatarFile = ref(null)
const avatarPreview = ref('')

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    loading.value = true;
    console.log('开始获取用户信息...');
    const response = await api.auth.getCurrentUser();
    console.log('获取用户信息响应:', response);
    
    if (response && response.data) {
      console.log('用户数据:', response.data);
      Object.assign(user, response.data);
      console.log('更新后的用户对象:', user);
      user.nickname = response.data.nickname
    } else {
      console.error('获取用户信息失败: 响应格式错误');
      errorMessage.value = '获取用户信息失败: 响应格式错误';
    }
  } catch (error) {
    console.error('获取用户信息出错:', error);
    if (error.response) {
      console.error('错误状态:', error.response.status);
      console.error('错误数据:', error.response.data);
      errorMessage.value = '获取用户信息出错: ' + (error.response.data?.message || error.message);
    } else {
      errorMessage.value = '获取用户信息出错: ' + error.message;
    }
  } finally {
    loading.value = false;
  }
};

// 开始编辑
const startEdit = () => {
  editableUser.value = {
    nickname: user.nickname,
    username: user.username,
    email: user.email,
    bio: user.bio
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
  isSaving.value = true;

  try {
    // 准备更新数据
    const formData = new FormData()
    formData.append('nickname', editableUser.value.nickname || '')
    formData.append('username', editableUser.value.username)
    formData.append('email', editableUser.value.email)
    formData.append('bio', editableUser.value.bio || '')
    if (avatarFile.value) {
      formData.append('avatar', avatarFile.value)
    }

    console.log('准备更新用户信息:', formData);
    const response = await api.auth.updateUser(formData);
    console.log('更新用户信息响应:', response);

    if (response && response.data) {
      // 更新本地用户数据
      Object.assign(user, response.data);
      successMessage.value = '个人信息更新成功';
      isEditing.value = false;
      userStore.setUser(response.data);
      // 清除头像预览
      avatarPreview.value = '';
      avatarFile.value = null;
    }
  } catch (error) {
    console.error('更新用户信息失败:', error);
    if (error.response) {
      const errorData = error.response.data;
      if (errorData.errors) {
        // 处理后端返回的具体错误信息
        if (errorData.errors.username) {
          errorMessage.value = errorData.errors.username[0];
        } else if (errorData.errors.email) {
          errorMessage.value = errorData.errors.email[0];
        } else {
          errorMessage.value = '更新失败: ' + (errorData.message || error.message);
        }
      } else {
        errorMessage.value = '更新失败: ' + (errorData.message || error.message);
      }
    } else {
      errorMessage.value = '更新失败: ' + error.message;
    }
  } finally {
    isSaving.value = false;
  }
};

const onAvatarChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    avatarFile.value = file
    avatarPreview.value = URL.createObjectURL(file)
  }
}

// 修改密码
const changePassword = async () => {
  // 验证密码
  if (!passwordData.value.old_password) {
    errorMessage.value = '请输入当前密码';
    return;
  }
  if (!passwordData.value.new_password) {
    errorMessage.value = '请输入新密码';
    return;
  }
  if (passwordData.value.new_password !== passwordData.value.confirm_password) {
    errorMessage.value = '两次输入的新密码不一致';
    return;
  }

  errorMessage.value = '';
  successMessage.value = '';
  isChangingPassword.value = true;

  try {
    const response = await api.auth.changePassword({
      old_password: passwordData.value.old_password,
      new_password: passwordData.value.new_password
    });

    // 清空密码字段
    passwordData.value = {
      old_password: '',
      new_password: '',
      confirm_password: ''
    };

    successMessage.value = '密码修改成功';
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  } catch (error) {
    console.error('修改密码失败:', error);
    if (error.response) {
      if (error.response.data.errors && error.response.data.errors.old_password) {
        errorMessage.value = '当前密码错误';
      } else {
        errorMessage.value = error.response.data.message || '修改密码失败';
      }
    } else {
      errorMessage.value = '修改密码失败: ' + error.message;
    }
  } finally {
    isChangingPassword.value = false;
  }
};

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUserInfo();
});
</script>

<style scoped>
.profile-container {
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s, color 0.3s;
}

.profile-header {
  background-color: var(--secondary-color);
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.3s, border-color 0.3s;
}

.profile-info {
  color: var(--text-color);
}

.profile-name {
  color: var(--text-color);
}

.profile-email {
  color: var(--text-color);
  opacity: 0.8;
}

.profile-stats {
  background-color: var(--secondary-color);
  border: 1px solid var(--border-color);
  transition: background-color 0.3s, border-color 0.3s;
}

.stat-item {
  color: var(--text-color);
}

.stat-value {
  color: var(--primary-color);
}

.profile-actions button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  transition: background-color 0.3s;
}

.profile-actions button:hover {
  background-color: var(--primary-color);
  opacity: 0.9;
}

.settings-section {
  background-color: var(--secondary-color);
  border: 1px solid var(--border-color);
  transition: background-color 0.3s, border-color 0.3s;
}

.settings-title {
  color: var(--text-color);
}

.settings-form input,
.settings-form textarea {
  background-color: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  transition: background-color 0.3s, color 0.3s, border-color 0.3s;
}

.settings-form input:focus,
.settings-form textarea:focus {
  border-color: var(--primary-color);
  outline: none;
}

.settings-form label {
  color: var(--text-color);
}

/* Global reset and base for full page */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  background-color: #1a1a1a;
  color-scheme: dark;
}

.profile-page-fullscreen {
  width: 100%;
  min-height: 100vh;
  background: var(--bg-color);
  color: var(--text-color);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  display: flex;
  flex-direction: column;
  line-height: 1.6;
  transition: background-color 0.3s, color 0.3s;
}

.profile-main-content {
  width: 100%;
  max-width: 900px;
  margin: 40px auto;
  padding: 40px;
  background-color: var(--secondary-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  transition: background-color 0.3s, border-color 0.3s, color 0.3s;
}

.welcome-message, .editing-intro {
  font-size: 1.2em;
  color: var(--text-color);
  opacity: 0.8;
  text-align: center;
  margin-bottom: 35px;
  padding: 15px;
  background-color: var(--bg-color);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  transition: background-color 0.3s, color 0.3s, border-color 0.3s;
}

/* Display Mode */
.info-card {
  background-color: var(--bg-color);
  padding: 25px;
  border-radius: 8px;
  margin-bottom: 35px;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  transition: background-color 0.3s, border-color 0.3s, color 0.3s;
}

.card-title {
  font-size: 1.8em;
  color: var(--primary-color);
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid var(--border-color);
  text-align: left;
  transition: color 0.3s, border-color 0.3s;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.info-item {
  background-color: var(--secondary-color);
  padding: 20px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.3s, border-color 0.3s, color 0.3s;
}

.info-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border-color: var(--primary-color);
}

.info-item-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.info-label {
  color: var(--text-color);
  opacity: 0.7;
  font-weight: 600;
  font-size: 1.2em;
  margin-left: 10px;
  transition: color 0.3s;
}

.info-value {
  color: var(--text-color);
  font-size: 1.2em;
  word-break: break-all;
  transition: color 0.3s;
}

.info-item-full-width {
  grid-column: 1 / -1; /* 占满整行 */
}

.bio-text {
  white-space: pre-wrap;
  line-height: 1.6;
  color: var(--text-color);
  background-color: var(--bg-color);
  padding: 15px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  transition: background-color 0.3s, color 0.3s, border-color 0.3s;
}

/* 头像样式 - 增强版 */
.avatar-container {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.user-avatar {
  width: 120px !important;
  height: 120px !important;
  border-radius: 50% !important;
  object-fit: cover !important;
  object-position: center !important;
  border: 3px solid var(--primary-color) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
  overflow: hidden !important;
  display: block !important;
}

.avatar-placeholder {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background-color: var(--secondary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid var(--border-color);
  color: var(--text-color);
  opacity: 0.7;
}

.avatar-placeholder svg {
  width: 60px;
  height: 60px;
}

/* 头像预览样式 - 增强版 */
.avatar-preview {
  width: 80px !important;
  height: 80px !important;
  border-radius: 50% !important;
  object-fit: cover !important;
  object-position: center !important;
  margin-top: 10px !important;
  border: 2px solid var(--primary-color) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
  overflow: hidden !important;
  display: block !important;
}

/* Edit Mode */
.edit-form .form-title {
  font-size: 1.8em;
  color: var(--primary-color);
  margin-bottom: 30px;
  text-align: center;
}

.form-section {
  margin-bottom: 30px;
  padding: 25px;
  background-color: var(--bg-color);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  transition: background-color 0.3s, border-color 0.3s, color 0.3s;
}

.section-title {
  font-size: 1.4em;
  color: var(--text-color);
  margin-bottom: 20px;
  font-weight: 600;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
  transition: color 0.3s, border-color 0.3s;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  color: var(--text-color);
  opacity: 0.7;
  margin-bottom: 10px;
  font-size: 1em;
  font-weight: 500;
  transition: color 0.3s;
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
  color: var(--text-color);
  transition: color 0.3s;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"],
.bio-input {
  width: 100%;
  padding: 12px 15px 12px 45px;
  background-color: var(--secondary-color);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-color);
  font-size: 1em;
  transition: all 0.3s ease;
}

.form-group input:focus,
.bio-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.15);
}

.bio-input {
  min-height: 120px;
  resize: vertical;
}

/* Buttons */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1em;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: var(--primary-color);
  opacity: 0.9;
}

.btn-success {
  background-color: var(--success-color);
  color: white;
  transition: background-color 0.3s;
}

.btn-success:hover {
  background-color: var(--success-color);
  opacity: 0.9;
}

.btn-secondary {
  background-color: var(--secondary-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background-color: var(--border-color);
  border-color: var(--text-color);
}

.btn-edit-profile {
  display: block;
  width: fit-content;
  margin: 25px auto 0;
  padding: 12px 30px;
}

.change-password-btn {
  margin-top: 20px;
  background-color: var(--primary-color);
  display: block;
  width: fit-content;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

/* Messages */
.error-message, .success-message {
  padding: 15px 20px;
  border-radius: 6px;
  margin: 20px 0;
  text-align: center;
  font-size: 1em;
  font-weight: 500;
}

.error-message {
  background-color: var(--error-color);
  opacity: 0.1;
  border: 1px solid var(--error-color);
  color: var(--error-color);
  transition: all 0.3s ease;
}

.success-message {
  background-color: var(--success-color);
  opacity: 0.1;
  border: 1px solid var(--success-color);
  color: var(--success-color);
  transition: all 0.3s ease;
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-color);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(74, 158, 255, 0.3);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-loading {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
}

.icon {
  width: 20px;
  height: 20px;
  color: var(--primary-color);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .profile-main-content {
    margin: 20px;
    padding: 20px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style> 