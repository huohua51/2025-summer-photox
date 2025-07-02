<template>
  <div class="login-view">
    <form class="form" @submit.prevent="handleRegister">
      <div id="login-area">
        <div class="title-container">
          <p>注册</p>
          <p id="behind">注册以获得完整访问权限</p>
        </div>
      </div>

      <div id="username-area">
        <input placeholder="用户名" id="username" class="input" type="text" required v-model="username" />
      </div>

      <div id="email-area">
        <input 
          placeholder="邮箱" 
          id="email" 
          class="input" 
          type="email" 
          required 
          v-model="email" 
          @blur="validateEmail"
          :class="{'error-input': emailError}"
        />
        <span v-if="emailError" class="field-error">{{ emailError }}</span>
      </div>

      <div id="password-area">
        <input placeholder="密码" id="password" class="input" type="password" required v-model="password" />
      </div>

      <div id="confirm-password-area">
        <input placeholder="确认密码" id="confirm-password" class="input" type="password" required
          v-model="password_confirm" />
      </div>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <div id="footer-area">
        <button type="submit" :disabled="loading">{{ loading ? '注册中...' : '提交' }}</button>
        <div id="text-inside">
          <p>已有账户?</p>
          <router-link id="link" to="/login">立即登录</router-link>
        </div>
      </div>

      <div id="background-color"></div>
      <div id="whitefilter"></div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { onMounted, onUnmounted } from 'vue'
import api from '@/api'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const password_confirm = ref('')
const loading = ref(false)
const errorMessage = ref('')
const emailError = ref('')

// 添加邮箱格式验证
const isValidEmail = computed(() => {
  if (!email.value) return true // 空值不显示错误
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/
  return emailRegex.test(email.value)
})

// 验证邮箱格式并更新错误信息
const validateEmail = () => {
  if (!email.value) {
    emailError.value = ''
    return true
  }
  if (!isValidEmail.value) {
    emailError.value = '请输入有效的邮箱地址'
    return false
  }
  emailError.value = ''
  return true
}

const handleRegister = async () => {
  // 清空之前的错误信息
  errorMessage.value = ''
  emailError.value = ''
  
  // 检查邮箱格式
  if (!validateEmail()) {
    return
  }
  
  if (password.value !== password_confirm.value) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }
  
  loading.value = true
  try {
    const response = await api.auth.register({
      username: username.value,
      email: email.value,
      password: password.value,
      password_confirm: password_confirm.value
    })
    
    if (response.code === 0) {
      router.push('/login')
    } else {
      errorMessage.value = response.message || '注册失败，请重试'
    }
  } catch (error) {
    console.error('注册错误:', error)
    errorMessage.value = error.response?.data?.message || error.message || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}

// 添加事件处理函数
const handleAreaHover = (event) => {
  const behind = document.querySelector('#behind');
  if (behind) {
    behind.style.opacity = '1';
    behind.style.transform = 'translateX(0)';
  }
}

const handleAreaLeave = (event) => {
  const behind = document.querySelector('#behind');
  if (behind) {
    behind.style.opacity = '0';
    behind.style.transform = 'translateX(-10px)';
  }
}

// 组件挂载后添加事件监听
onMounted(() => {
  const usernameArea = document.querySelector('#username-area');
  const emailArea = document.querySelector('#email-area');
  const passwordArea = document.querySelector('#password-area');
  const confirmPasswordArea = document.querySelector('#confirm-password-area');
  const footerArea = document.querySelector('#footer-area');

  if (usernameArea) {
    usernameArea.addEventListener('mouseenter', handleAreaHover);
    usernameArea.addEventListener('mouseleave', handleAreaLeave);
  }

  if (emailArea) {
    emailArea.addEventListener('mouseenter', handleAreaHover);
    emailArea.addEventListener('mouseleave', handleAreaLeave);
  }

  if (passwordArea) {
    passwordArea.addEventListener('mouseenter', handleAreaHover);
    passwordArea.addEventListener('mouseleave', handleAreaLeave);
  }

  if (confirmPasswordArea) {
    confirmPasswordArea.addEventListener('mouseenter', handleAreaHover);
    confirmPasswordArea.addEventListener('mouseleave', handleAreaLeave);
  }

  if (footerArea) {
    footerArea.addEventListener('mouseenter', handleAreaHover);
    footerArea.addEventListener('mouseleave', handleAreaLeave);
  }
})

onUnmounted(() => {
  const usernameArea = document.querySelector('#username-area');
  const emailArea = document.querySelector('#email-area');
  const passwordArea = document.querySelector('#password-area');
  const confirmPasswordArea = document.querySelector('#confirm-password-area');
  const footerArea = document.querySelector('#footer-area');

  if (usernameArea) {
    usernameArea.removeEventListener('mouseenter', handleAreaHover);
    usernameArea.removeEventListener('mouseleave', handleAreaLeave);
  }

  if (emailArea) {
    emailArea.removeEventListener('mouseenter', handleAreaHover);
    emailArea.removeEventListener('mouseleave', handleAreaLeave);
  }

  if (passwordArea) {
    passwordArea.removeEventListener('mouseenter', handleAreaHover);
    passwordArea.removeEventListener('mouseleave', handleAreaLeave);
  }

  if (confirmPasswordArea) {
    confirmPasswordArea.removeEventListener('mouseenter', handleAreaHover);
    confirmPasswordArea.removeEventListener('mouseleave', handleAreaLeave);
  }

  if (footerArea) {
    footerArea.removeEventListener('mouseenter', handleAreaHover);
    footerArea.removeEventListener('mouseleave', handleAreaLeave);
  }
})
</script>

<style scoped>
.login-view {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  width: 100vw;
  background-image: url("/img/QQ图片20231213202410.jpg");
  background-size: cover;
}

.form {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #ffffff;
  width: 25vw;
  height: 65vh;
  border: 2px solid #176fd4;
  border-bottom-left-radius: 1.5em;
  border-top-right-radius: 1.5em;
  box-shadow:
    -10px 0px 0px #003674,
    -10px 5px 5px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  position: relative;
  transition: all 0.3s ease;
  transform: scale(1);
}

.form:hover {
  transform: scale(1.05);
  box-shadow:
    -12px 0px 0px #003674,
    -12px 7px 10px rgba(0, 0, 0, 0.5);
}

.error-message {
  color: #ff4d4f;
  font-size: 0.8em;
  margin-bottom: 0.5em;
  z-index: 10;
  position: relative;
}

#login-area,
#username-area,
#email-area,
#password-area,
#confirm-password-area,
#footer-area {
  position: relative;
  z-index: 2;
}

#login-area {
  width: 90%;
  height: 6vh;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  position: relative;
}

.title-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  position: relative;
  transform: translateY(1vh);
}

#login-area p {
  font-size: 1.5em;
  font-weight: bold;
  z-index: 2;
  margin: 0;
  transition: all 0.3s ease;
}

#login-area #behind {
  font-size: 1em;
  font-weight: bold;
  z-index: 1;
  margin: 0;
  margin-left: 0.5em;
  color: #176fd4;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
}

/* 修复选择器，使用:hover-focus伪类和JS控制 */
.form:hover #behind {
  opacity: 0;
  transform: translateX(-10px);
}

#username-area,
#email-area,
#password-area,
#confirm-password-area {
  width: 85%;
  padding-left: 0;
  padding-right: 0;
  height: 8vh;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  margin: 1em auto 0;
  transition: all 0.25s ease;
}

#username-area input,
#email-area input,
#password-area input,
#confirm-password-area input {
  width: 80%;
  border: 2px solid #176fd4;
  border-radius: 0.5em;
  height: 5vh;
  font-size: 0.95em;
  font-weight: 100;
  transition: all 0.5s ease;
  outline: none;
  box-shadow: 0px 5px 5px -3px rgba(0, 0, 0, 0.2);
  text-align: center;
  background-color: #ffffff;
  color: #000000;
}

#footer-area {
  margin: 0 auto;
  padding-top: 3vh;
  width: 85%;
  padding-left: 0;
  padding-right: 0;
  height: 12vh;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  color: #176fd4;
  transition: all 0.25s ease;
}

#footer-area button {
  width: 80%;
  border: 2px solid #176fd4;
  border-radius: 0.5em;
  height: 5vh;
  font-size: 0.95em;
  font-weight: 100;
  transition: all 0.25s ease;
  color: white;
  font-weight: bold;
  background-color: #176fd4;
  box-shadow: 0px 5px 5px -3px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  text-align: center;
}

#footer-area p,
#footer-area a {
  font-size: 0.8em;
  transition: all 0.25s ease;
}

#text-inside {
  padding-top: 0.5em;
  display: flex;
  align-items: center;
}

#link {
  padding-left: 0.1em;
  font-weight: bold;
  text-decoration: none;
  color: #176fd4;
}

#background-color {
  width: 100%;
  height: 8vh;
  background-color: #176fd4;
  position: absolute;
  top: 0;
  z-index: 1;
  transition: all 0.5s ease;
  box-shadow: inset 5px 0px #0c4c91;
}

#whitefilter {
  width: 3.5em;
  height: 3.5em;
  top: 2.5px;
  right: 2.5px;
  position: absolute;
  z-index: 2;
  border-top-right-radius: 1.25em;
  box-shadow: 35px -35px 0px -1px #ffffff;
}

::placeholder {
  color: #176fd4;
  font-weight: bold;
}

/* 修改悬停时的动画效果 */
#username-area:hover input,
#email-area:hover input,
#password-area:hover input,
#confirm-password-area:hover input {
  transition: all 0.3s ease;
}

#username-area:hover~#background-color {
  height: 10vh;
  transform: translateY(7vh);
  transition: all 0.3s ease;
}

#email-area:hover~#background-color {
  height: 10vh;
  transform: translateY(17vh);
  transition: all 0.3s ease;
}

#password-area:hover~#background-color {
  height: 10vh;
  transform: translateY(27vh);
  transition: all 0.3s ease;
}

#confirm-password-area:hover~#background-color {
  height: 10vh;
  transform: translateY(37vh);
  transition: all 0.3s ease;
}

#footer-area:hover~#background-color {
  height: 14vh;
  transform: translateY(47vh);
  transition: all 0.3s ease;
}

#username-area:hover,
#email-area:hover,
#password-area:hover,
#confirm-password-area:hover,
#footer-area:hover {
  padding-left: 5%;
  padding-right: 5%;
}

#username-area:hover input,
#email-area:hover input,
#password-area:hover input,
#confirm-password-area:hover input {
  color: white;
  border: 2px solid white;
  background-color: #176fd4;
  height: 3em;
}

#username-area:hover ::placeholder,
#email-area:hover ::placeholder,
#password-area:hover ::placeholder,
#confirm-password-area:hover ::placeholder {
  color: white;
}

#footer-area:hover p,
#footer-area:hover a {
  color: white;
}

#footer-area:hover button {
  border: 2px solid white;
  background-color: #176fd4;
  height: 3em;
}

#footer-area button:active {
  color: #176fd4;
  background-color: white;
  width: 90%;
}

/* 禁用按钮样式 */
#footer-area button:disabled {
  background-color: #5993d4;
  border-color: #5993d4;
  cursor: not-allowed;
}

.field-error {
  color: #ff4d4f;
  font-size: 0.75em;
  margin-top: 0.3em;
  align-self: flex-start;
  margin-left: 10%;
  font-weight: bold;
}

.error-input {
  border-color: #ff4d4f !important;
}

/* 调整悬停效果以适应错误提示 */
#email-area:hover .field-error {
  color: white;
  font-weight: bold;
}
</style>