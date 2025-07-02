<template>
    <div class="like-comment-section">
        <div class="like-row">
            <button class="like-btn" :class="{ liked: likedByMe }" @click="$emit('toggle-like')">
                <!-- 点赞SVG图标 -->
                <svg class="like-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path v-if="likedByMe"
                        d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
                        fill="currentColor" />
                    <path v-else
                        d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <span>{{ likeCount }}</span>
            </button>
        </div>
        <div class="comment-row">
            <div class="comment-header">
                <!-- 评论标题带图标 -->
                <svg class="comment-title-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor"
                        stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <h3>评论</h3>
            </div>
            <div class="comment-list">
                <div v-if="comments.length === 0" class="no-comment">
                    <!-- 暂无评论图标 -->
                    <svg class="no-comment-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" />
                        <path d="M8 14s1.5 2 4 2 4-2 4-2" stroke="currentColor" stroke-width="2"
                            stroke-linecap="round" />
                        <line x1="9" y1="9" x2="9.01" y2="9" stroke="currentColor" stroke-width="2"
                            stroke-linecap="round" />
                        <line x1="15" y1="9" x2="15.01" y2="9" stroke="currentColor" stroke-width="2"
                            stroke-linecap="round" />
                    </svg>
                    <span>暂无评论，快来抢沙发~</span>
                </div>
                <div v-for="comment in comments" :key="comment.id" class="comment-item">
                    <div class="comment-author">
                        <div class="comment-avatar">
                            <!-- 用户头像SVG -->
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor"
                                    stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                                <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" />
                            </svg>
                        </div>
                        {{ comment.author }}
                    </div>
                    <div class="comment-content">{{ comment.content }}</div>
                    <div class="comment-time">
                        <!-- 时间图标 -->
                        <svg class="time-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" />
                            <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2"
                                stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                        {{ comment.time }}
                    </div>
                    <div class="comment-actions">
                        <button class="comment-like-btn" :class="{ liked: comment.likedByMe }"
                            @click="$emit('toggle-comment-like', comment)">
                            <!-- 点赞图标 -->
                            <svg class="action-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path v-if="comment.likedByMe"
                                    d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"
                                    fill="currentColor" />
                                <path v-else
                                    d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"
                                    stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" />
                            </svg>
                            <span>{{ comment.likeCount }}</span>
                        </button>
                        <button class="comment-reply-btn" @click="showReplyInput(comment)">
                            <!-- 回复图标 -->
                            <svg class="action-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <polyline points="9,17 4,12 9,7" stroke="currentColor" stroke-width="2"
                                    stroke-linecap="round" stroke-linejoin="round" />
                                <path d="m20 18v-2a4 4 0 0 0-4-4H4" stroke="currentColor" stroke-width="2"
                                    stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                            回复
                        </button>
                        <button
                          v-if="comment.author === props.currentUser.username"
                          class="comment-delete-btn"
                          @click="deleteComment(comment)"
                        >
                          删除
                        </button>
                    </div>
                    <!-- 回复输入框 -->
                    <div v-if="comment.showReplyInput" class="reply-input-row">
                        <input v-model="comment.replyContent" class="reply-input" placeholder="回复内容..."
                            @keyup.enter="submitReply(comment)" />
                        <button class="reply-submit-btn" @click="submitReply(comment)">
                            <!-- 发送图标 -->
                            <svg class="send-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <line x1="22" y1="2" x2="11" y2="13" stroke="currentColor" stroke-width="2" />
                                <polygon points="22,2 15,22 11,13 2,9 22,2" fill="currentColor" />
                            </svg>
                        </button>
                    </div>
                    <!-- 回复列表 -->
                    <div class="reply-list" v-if="comment.replies && comment.replies.length">
                        <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                            <span class="reply-author">{{ reply.author }}</span>：<span class="reply-content">{{
                                reply.content }}</span>
                            <span class="reply-time">{{ reply.time }}</span>
                            <button class="reply-like-btn" :class="{ liked: reply.likedByMe }"
                                @click="$emit('toggle-reply-like', comment, reply)">
                                <svg class="action-icon small" viewBox="0 0 24 24" fill="none"
                                    xmlns="http://www.w3.org/2000/svg">
                                    <path v-if="reply.likedByMe"
                                        d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"
                                        fill="currentColor" />
                                    <path v-else
                                        d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"
                                        stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round" />
                                </svg>
                                {{ reply.likeCount }}
                            </button>
                            <button
                              v-if="reply.author === props.currentUser.username"
                              class="reply-delete-btn"
                              @click="deleteReply(comment, reply)"
                            >
                              删除
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="comment-input-row">
                <input v-model="newComment" class="comment-input" placeholder="写下你的评论..."
                    @keyup.enter="submitComment" />
                <button class="comment-submit-btn" @click="submitComment">
                    <!-- 发送图标 -->
                    <svg class="send-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <line x1="22" y1="2" x2="11" y2="13" stroke="currentColor" stroke-width="2" />
                        <polygon points="22,2 15,22 11,13 2,9 22,2" fill="currentColor" />
                    </svg>
                    发送
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
const props = defineProps({
    comments: Array,
    likeCount: Number,
    likedByMe: Boolean,
    currentUser: Object
})
// console.log(props.currentUser)
const emit = defineEmits(['submit-comment', 'toggle-like', 'toggle-comment-like', 'toggle-reply-like', 'submit-reply', 'delete-comment', 'delete-reply'])

const newComment = ref('')

function showReplyInput(comment) {
    props.comments.forEach(c => { c.showReplyInput = false })
    comment.showReplyInput = true
    if (!comment.replyContent) comment.replyContent = ''
}

function submitReply(comment) {
    if (!comment.replyContent || !comment.replyContent.trim()) return
    emit('submit-reply', comment, comment.replyContent)
    comment.replyContent = ''
    comment.showReplyInput = false
}

function submitComment() {
    if (!newComment.value.trim()) return
    emit('submit-comment', newComment.value)
    newComment.value = ''
}

function deleteComment(comment) {
    if (confirm('确定要删除这条评论吗？')) {
        emit('delete-comment', comment)
    }
}

function deleteReply(comment, reply) {
    if (confirm('确定要删除这条回复吗？')) {
        emit('delete-reply', comment, reply)
    }
}
</script>

<style scoped>
.like-comment-section {
    margin-top: 32px;
    background: var(--card-color);
    border-radius: 16px;
    padding: 28px 28px 20px 28px;
    box-shadow: 0 4px 24px var(--shadow-color);
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
    color: var(--text-color);
}

.like-row {
    display: flex;
    align-items: center;
    margin-bottom: 22px;
    justify-content: flex-end;
}

.like-btn {
    display: flex;
    align-items: center;
    background: none;
    border: none;
    color: var(--text-color);
    font-size: 1.15rem;
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 20px;
    padding: 8px 18px 8px 12px;
    gap: 8px;
}

.like-btn.liked {
    color: #e74c3c;
    background: rgba(231, 76, 60, 0.08);
    transform: scale(1.05);
}

.like-btn:hover {
    background: var(--primary-color);
    color: #fff;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(30, 144, 255, 0.2);
}

.like-icon {
    width: 24px;
    height: 24px;
    transition: all 0.3s ease;
}

.like-btn:hover .like-icon {
    transform: scale(1.1);
}

.comment-row {
    margin-top: 10px;
}

.comment-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
}

.comment-title-icon {
    width: 20px;
    height: 20px;
    color: var(--primary-color);
}

.comment-header h3 {
    margin: 0;
    color: var(--text-color);
    font-size: 18px;
}

.comment-list {
    margin-bottom: 16px;
}

.no-comment {
    color: #aaa;
    font-size: 14px;
    padding: 24px 0;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}

.no-comment-icon {
    width: 48px;
    height: 48px;
    opacity: 0.6;
}

.comment-item {
    background: var(--card-color);
    border-radius: 16px;
    box-shadow: 0 2px 12px var(--shadow-color);
    padding: 18px 20px 12px 20px;
    margin-bottom: 18px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    color: var(--text-color);
}

.comment-item:hover {
    box-shadow: 0 6px 20px rgba(30, 144, 255, 0.12);
    border: 1.5px solid var(--primary-color);
    transform: translateY(-2px);
}

.comment-author {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    color: var(--primary-color);
}

.comment-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--primary-gradient);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
}

.comment-avatar svg {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    padding: 2px;
    box-shadow: 0 2px 8px var(--shadow-color);
}

.comment-content {
    margin: 8px 0 6px 0;
    font-size: 15px;
    color: var(--text-color);
    word-break: break-all;
    line-height: 1.5;
}

.comment-time {
    font-size: 12px;
    color: var(--text-color);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 4px;
}

.time-icon {
    width: 12px;
    height: 12px;
}

.comment-actions {
    display: flex;
    gap: 16px;
    margin-top: 8px;
}

.comment-like-btn,
.comment-reply-btn,
.reply-like-btn {
    background: var(--primary-gradient);
    color: var(--button-text-color);
    border: none;
    border-radius: 16px;
    padding: 4px 16px;
    font-size: 0.95rem;
    font-weight: 600;
    box-shadow: 0 2px 8px var(--shadow-color);
    cursor: pointer;
    transition: all 0.2s;
    margin-right: 8px;
}

.comment-like-btn.liked,
.reply-like-btn.liked {
    color: #1e90ff;
    background: rgba(30, 144, 255, 0.08);
}

.comment-like-btn:hover,
.reply-like-btn:hover {
    background: var(--primary-gradient-reverse);
    transform: scale(1.08);
    box-shadow: 0 4px 16px var(--shadow-color-hover);
}

.comment-reply-btn:hover {
    background: #f0f7ff;
    color: var(--primary-color);
}

.action-icon {
    width: 16px;
    height: 16px;
    transition: transform 0.2s ease;
}

.action-icon.small {
    width: 14px;
    height: 14px;
}

.comment-like-btn:hover .action-icon,
.reply-like-btn:hover .action-icon {
    transform: scale(1.1);
}

.reply-list {
    margin-left: 32px;
    margin-top: 12px;
    border-left: 3px solid #f0f7ff;
    padding-left: 16px;
    background: rgba(240, 247, 255, 0.3);
    border-radius: 8px;
}

.reply-item {
    font-size: 14px;
    padding: 8px 0;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px dashed #e0e8f0;
}

.reply-item:last-child {
    border-bottom: none;
}

.reply-author {
    font-weight: bold;
    color: var(--primary-color);
}

.reply-content {
    margin: 0 2px;
    color: var(--text-color);
    flex: 1;
}

.reply-time {
    color: var(--text-color);
    font-size: 12px;
}

.reply-input-row {
    display: flex;
    gap: 8px;
    margin: 12px 0 4px 0;
}

.reply-input {
    flex: 1;
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    font-size: 14px;
    background: #f8faff;
    transition: all 0.3s ease;
}

.reply-input:focus {
    border: 1.5px solid var(--primary-color);
    outline: none;
    box-shadow: 0 0 0 3px rgba(30, 144, 255, 0.1);
}

.reply-submit-btn {
    background: var(--primary-color);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.reply-submit-btn:hover {
    background: #1e90ff;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(30, 144, 255, 0.2);
}

.send-icon {
    width: 16px;
    height: 16px;
}

.comment-input-row {
    display: flex;
    gap: 12px;
    margin-top: 18px;
    background: var(--bg-color);
    border-radius: 12px;
    padding: 12px 16px;
    box-shadow: 0 2px 8px rgba(30, 144, 255, 0.06);
    border: 1px solid rgba(30, 144, 255, 0.1);
}

.comment-input {
    flex: 1;
    padding: 10px 16px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    font-size: 15px;
    background: var(--bg-color);
    transition: all 0.3s ease;
    color: var(--text-color);
}

.comment-input:focus {
    border: 1.5px solid var(--primary-color);
    outline: none;
    box-shadow: 0 0 0 3px rgba(30, 144, 255, 0.1);
}

.comment-submit-btn {
    background: linear-gradient(135deg, var(--primary-color) 0%, #1e90ff 100%);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 15px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: bold;
    box-shadow: 0 4px 12px rgba(30, 144, 255, 0.2);
    display: flex;
    align-items: center;
    gap: 8px;
}

.comment-submit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(30, 144, 255, 0.3);
}

.comment-submit-btn:active {
    transform: translateY(0);
}

.comment-delete-btn {
    background: #ff4d4f;
    color: #fff;
    border: none;
    border-radius: 16px;
    padding: 4px 16px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    margin-left: 8px;
    transition: all 0.2s;
}

.comment-delete-btn:hover {
    background: #ff7875;
}

.reply-delete-btn {
    background: #ff4d4f;
    color: #fff;
    border: none;
    border-radius: 12px;
    padding: 2px 8px;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    margin-left: 8px;
    transition: all 0.2s;
}

.reply-delete-btn:hover {
    background: #ff7875;
}

@media (max-width: 900px) {
    .like-comment-section {
        padding: 12px 4px 8px 4px;
        max-width: 100vw;
    }

    .comment-item {
        padding: 10px 8px 8px 8px;
        border-radius: 8px;
    }
}
</style>