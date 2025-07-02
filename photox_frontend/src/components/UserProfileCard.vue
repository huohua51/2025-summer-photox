<template>
    <div class="user-profile-card">
        <div class="profile-header">
            <div class="avatar-section">
                <div class="avatar">
                    <img v-if="userInfo.avatar" :src="userInfo.avatar" :alt="userInfo.username" />
                    <div v-else class="avatar-placeholder">
                        {{ userInfo.username ? userInfo.username.charAt(0).toUpperCase() : 'U' }}
                    </div>
                </div>
            </div>

            <div class="user-info">
                <h2 class="username">{{ userInfo.username || '未知用户' }}</h2>
                <p class="join-date" v-if="userInfo.date_joined">
                    加入时间：{{ formatDate(userInfo.date_joined) }}
                </p>
            </div>

            <div class="profile-actions" v-if="showFollowButton">
                <button class="follow-btn" :class="{ 'following': userInfo.is_following }" @click="handleFollowToggle"
                    :disabled="loading">
                    <span v-if="loading">处理中...</span>
                    <span v-else>{{ userInfo.is_following ? '取消关注' : '关注' }}</span>
                </button>
            </div>
        </div>

        <div class="profile-stats">
            <div class="stat-item">
                <span class="stat-number">{{ userInfo.follower_count || 0 }}</span>
                <span class="stat-label">粉丝</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ userInfo.following_count || 0 }}</span>
                <span class="stat-label">关注</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ imageCount }}</span>
                <span class="stat-label">图片</span>
            </div>
        </div>

    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiService from '../api/index.js'

const props = defineProps({
    userId: {
        type: [String, Number],
        required: true
    },
    imageCount: {
        type: Number,
        default: 0
    },
    showFollowButton: {
        type: Boolean,
        default: true
    }
})

const emit = defineEmits(['follow-changed'])

const userInfo = ref({})
const loading = ref(false)

// 格式化日期
const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })
}

// 获取用户信息
const fetchUserInfo = async () => {
    try {
        loading.value = true
        const response = await apiService.users.getUserById(props.userId)
        userInfo.value = response
    } catch (error) {
        console.error('获取用户信息失败:', error)
        ElMessage.error('获取用户信息失败')
    } finally {
        loading.value = false
    }
}

// 处理关注/取消关注
const handleFollowToggle = async () => {
    try {
        loading.value = true
        const response = await apiService.follow.toggleFollow(props.userId)

        // 更新关注状态
        userInfo.value.is_following = response.following

        // 更新粉丝数量
        if (response.following) {
            userInfo.value.follower_count = (userInfo.value.follower_count || 0) + 1
        } else {
            userInfo.value.follower_count = Math.max(0, (userInfo.value.follower_count || 0) - 1)
        }

        ElMessage.success(response.message || (response.following ? '关注成功' : '取消关注成功'))
        emit('follow-changed', response.following)
    } catch (error) {
        console.error('关注操作失败:', error)
        ElMessage.error('操作失败，请稍后重试')
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchUserInfo()
})
</script>

<style scoped>
.user-profile-card {
    background-color: var(--secondary-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    transition: all 0.3s ease;
}

.user-profile-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.profile-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.avatar-section {
    margin-right: 16px;
}

.avatar {
    width: 80px !important;
    height: 80px !important;
    border-radius: 50% !important;
    overflow: hidden !important;
    border: 3px solid var(--primary-color) !important;
    display: block !important;
}

.avatar img {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    object-position: center !important;
    border-radius: 50% !important;
    display: block !important;
}

.avatar-placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, var(--primary-color), #4a90e2);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 32px;
    font-weight: bold;
}

.user-info {
    flex: 1;
}

.username {
    margin: 0 0 8px 0;
    font-size: 24px;
    font-weight: bold;
    color: var(--text-color);
}

.join-date {
    margin: 0;
    color: var(--text-color);
    opacity: 0.7;
    font-size: 14px;
}

.profile-stats {
    display: flex;
    justify-content: space-around;
    margin-bottom: 20px;
    padding: 16px 0;
    border-top: 1px solid var(--border-color);
    border-bottom: 1px solid var(--border-color);
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.stat-number {
    font-size: 24px;
    font-weight: bold;
    color: var(--primary-color);
    margin-bottom: 4px;
}

.stat-label {
    font-size: 14px;
    color: var(--text-color);
    opacity: 0.7;
}

.profile-actions {
    display: flex;
    justify-content: center;
}

.follow-btn {
    padding: 12px 32px;
    border: 2px solid var(--primary-color);
    border-radius: 24px;
    background-color: var(--primary-color);
    color: white;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 120px;
}

.follow-btn:hover:not(:disabled) {
    background-color: transparent;
    color: var(--primary-color);
}

.follow-btn.following {
    background-color: transparent;
    color: var(--primary-color);
}

.follow-btn.following:hover:not(:disabled) {
    background-color: var(--primary-color);
    color: white;
}

.follow-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

@media (max-width: 768px) {
    .user-profile-card {
        padding: 16px;
    }

    .profile-header {
        flex-direction: column;
        text-align: center;
    }

    .avatar-section {
        margin-right: 0;
        margin-bottom: 16px;
    }

    .avatar {
        width: 60px;
        height: 60px;
    }

    .username {
        font-size: 20px;
    }

    .profile-stats {
        padding: 12px 0;
    }

    .stat-number {
        font-size: 20px;
    }
}
</style>