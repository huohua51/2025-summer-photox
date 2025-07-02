<template>
    <div class="user-profile">
      <div class="avatar-box">
        <img :src="user.avatar || defaultAvatar" class="avatar" alt="用户头像" />
      </div>
      <div class="user-info">
        <div class="username">{{ user.username }}</div>
        <div class="bio" v-if="user.bio">{{ user.bio }}</div>
        <div class="meta">
          <span>粉丝 {{ user.follower_count }}</span>
          <span>关注 {{ user.following_count }}</span>
        </div>
        <div v-if="showFollowBtn" class="follow-btn-box">
          <button class="follow-btn" @click="toggleFollow">
            {{ user.is_following ? '已关注' : '关注TA' }}
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, toRefs } from 'vue'
  
  const props = defineProps({
    user: {
      type: Object,
      required: true
    },
    showFollowBtn: {
      type: Boolean,
      default: false
    }
  })
  
  const defaultAvatar = '/img/default-avatar.png' // 你可以换成项目内的默认头像路径
  
  const emit = defineEmits(['follow-change'])
  
  const toggleFollow = () => {
    // 这里可以发请求，或直接emit事件让父组件处理
    emit('follow-change', user)
  }
  </script>
  
  <style scoped>
  .user-profile {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24px 0 16px 0;
    background: none;
  }
  
  .avatar-box {
    width: 90px;
    height: 90px;
    margin-bottom: 12px;
  }
  
  .avatar {
    width: 90px !important;
    height: 90px !important;
    border-radius: 50% !important;
    object-fit: cover !important;
    object-position: center !important;
    border: 2px solid var(--primary-color, #2180ea) !important;
    background: #fff;
    overflow: hidden !important;
    display: block !important;
  }
  
  .user-info {
    text-align: center;
    width: 100%;
  }
  
  .username {
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 6px;
    color: var(--text-color);
  }
  
  .bio {
    font-size: 0.95em;
    color: #aaa;
    margin-bottom: 8px;
    word-break: break-all;
  }
  
  .meta {
    font-size: 0.9em;
    color: #888;
    margin-bottom: 10px;
    display: flex;
    justify-content: center;
    gap: 16px;
  }
  
  .follow-btn-box {
    margin-top: 8px;
  }
  
  .follow-btn {
    background: var(--primary-color, #2180ea);
    color: #fff;
    border: none;
    border-radius: 16px;
    padding: 6px 20px;
    font-size: 1em;
    cursor: pointer;
    transition: background 0.2s;
  }
  
  .follow-btn:hover {
    background: #176fd4;
  }
  </style>