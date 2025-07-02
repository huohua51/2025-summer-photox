<template>
    <div class="login-view">
        <form class="form" @submit.prevent="handleLogin">
            <div id="login-area">
                <div class="title-container">
                    <p>登录</p>
                    <p id="behind">登录以访问您的账户</p>
                </div>
            </div>

            <div id="email-area">
                <input placeholder="用户名" id="username" class="input" type="text" required v-model="username" />
            </div>

            <div id="password-area">
                <input placeholder="密码" id="password" class="input" type="password" required v-model="password" />
            </div>

            <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

            <div id="footer-area">
                <button type="submit" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
                <div id="text-inside">
                    <p>没有账户?</p>
                    <router-link id="link" to="/register">立即注册</router-link>
                </div>
            </div>

            <div id="background-color"></div>
            <div id="whitefilter"></div>
            
        </form>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
    if (!username.value || !password.value) {
        errorMessage.value = '请输入用户名和密码'
        return
    }

    loading.value = true
    errorMessage.value = ''

    try {
        const response = await api.auth.login(username.value, password.value)
        
        // 保存 token
        localStorage.setItem('token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        
        // 登录成功后获取完整用户信息
        const userInfoResp = await api.auth.getCurrentUser()
        userStore.setUser(userInfoResp.data) // 这里 userInfoResp.data 应该有 id、username 等
        // console.log(userInfoResp.data)
        // 获取重定向地址
        const redirect = router.currentRoute.value.query.redirect
        // 如果有重定向地址，跳转到该地址，否则跳转到首页
        router.push(redirect || '/')
    } catch (error) {
        console.error('登录失败:', error)
        errorMessage.value = error.response?.data?.detail || '登录失败，请重试'
        // 登录失败时不自动跳转，让用户可以点击返回按钮
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
    const emailArea = document.querySelector('#email-area');
    const passwordArea = document.querySelector('#password-area');
    const footerArea = document.querySelector('#footer-area');
    
    if (emailArea) {
        emailArea.addEventListener('mouseenter', handleAreaHover);
        emailArea.addEventListener('mouseleave', handleAreaLeave);
    }
    
    if (passwordArea) {
        passwordArea.addEventListener('mouseenter', handleAreaHover);
        passwordArea.addEventListener('mouseleave', handleAreaLeave);
    }
    
    if (footerArea) {
        footerArea.addEventListener('mouseenter', handleAreaHover);
        footerArea.addEventListener('mouseleave', handleAreaLeave);
    }
})

onUnmounted(() => {
    const emailArea = document.querySelector('#email-area');
    const passwordArea = document.querySelector('#password-area');
    const footerArea = document.querySelector('#footer-area');
    
    if (emailArea) {
        emailArea.removeEventListener('mouseenter', handleAreaHover);
        emailArea.removeEventListener('mouseleave', handleAreaLeave);
    }
    
    if (passwordArea) {
        passwordArea.removeEventListener('mouseenter', handleAreaHover);
        passwordArea.removeEventListener('mouseleave', handleAreaLeave);
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
    background-color: var(--bg-color);
    width: 20vw;
    height: 50vh;
    border: 2px solid var(--primary-color);
    border-bottom-left-radius: 1.5em;
    border-top-right-radius: 1.5em;
    box-shadow:
        -10px 0px 0px var(--primary-color),
        -10px 5px 5px rgba(0, 0, 0, 0.4);
    overflow: hidden;
    position: relative;
    transition: all 0.3s ease;
    transform: scale(1);
}

.form:hover {
    transform: scale(1.05);
    box-shadow:
        -12px 0px 0px var(--primary-color),
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
#email-area,
#password-area,
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

#email-area:hover ~ #background-color ~ #login-area #behind,
#password-area:hover ~ #background-color ~ #login-area #behind,
#footer-area:hover ~ #background-color ~ #login-area #behind,
#email-area:focus-within ~ #background-color ~ #login-area #behind {
    opacity: 1 !important;
    transform: translateX(0) !important;
}

#email-area {
    width: 85%;
    padding-left: 0;
    padding-right: 0;
    height: 10vh;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    margin: 1em auto 0;
    transition: all 0.25s ease;
}

#email-area input {
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

#password-area {
    width: 85%;
    padding-left: 0;
    padding-right: 0;
    height: 12vh;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    transition: all 0.25s ease;
    margin: 0 auto;
}

#password-area input {
    width: 80%;
    border: 2px solid #176fd4;
    font-size: 0.95em;
    border-radius: 0.5em;
    height: 5vh;
    transition: all 0.25s ease;
    outline: none;
    box-shadow: 0px 5px 5px -3px rgba(0, 0, 0, 0.2);
    text-align: center;
    background-color: #ffffff;
    color: #000000;
}

#password-area a {
    padding-top: 0.5em;
    font-size: 0.8em;
    font-weight: bold;
    transition: all 0.25s ease;
    color: #176fd4;
    cursor: pointer;
    align-self: flex-end;
    margin-right: 10%;
}

#footer-area {
    margin: 0 auto;
    padding-top: 0;
    width: 85%;
    padding-left: 0;
    padding-right: 0;
    height: 15vh;
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

#link-circle {
    width: 100%;
    height: 4.5em;
    display: flex;
    align-items: center;
    justify-content: space-around;
    padding-left: 15%;
    padding-right: 15%;
}

#link-circle svg {
    transition: all 0.25s ease;
}

#whitefilter {
    width: 3.5em;
    height: 3.5em;
    top: 2.5px;
    right: 2.5px;
    position: absolute;
    z-index: 2;
    border-top-right-radius: 1.25em;
    box-shadow: 35px -35px 0px -1px #1a1a1a;
}

::placeholder {
    color: #176fd4;
    font-weight: bold;
}

/* 修改悬停时的动画效果 */
#email-area:hover input,
#password-area:hover input {
    transition: all 0.3s ease;
}

#email-area:hover~#background-color {
    height: 10vh;
    transform: translateY(8vh);
    transition: all 0.3s ease;
}

#email-area:hover,
#password-area:hover,
#footer-area:hover {
    padding-left: 5%;
    padding-right: 5%;
}

#email-area:hover p {
    color: white;
}

#email-area:hover input {
    color: white;
    border: 2px solid white;
    background-color: #176fd4;
    height: 3em;
}

#email-area:hover ::placeholder {
    color: white;
}

#password-area:hover p {
    color: white;
}

#password-area:hover a {
    color: white;
    padding-right: 5%;
}

#password-area:hover input {
    color: white;
    border: 2px solid white;
    background-color: #176fd4;
    height: 3em;
}

#password-area:hover ::placeholder {
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

#link-circle svg:hover {
    transform: scale(1.25);
    margin: 0.5em;
}

/* 禁用按钮样式 */
#footer-area button:disabled {
    background-color: #5993d4;
    border-color: #5993d4;
    cursor: not-allowed;
}

#password-area:hover~#background-color {
    height: 12vh;
    transform: translateY(18vh);
    transition: all 0.3s ease;
}

#footer-area:hover~#background-color {
    height: 15vh;
    transform: translateY(29vh);
    transition: all 0.3s ease;
}
</style>