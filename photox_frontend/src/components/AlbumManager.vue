<template>
    <div class="album-manager">
        <!-- 搜索框 -->
        <div class="search-input-wrapper">
            <div class="search-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </div>
            <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="搜索相册..." 
                class="search-input"
                @input="handleSearch"
            />
        </div>

        <!-- 相册列表 -->
        <div class="album-items" v-if="searchQuery">
            <div v-for="album in filteredAlbums" 
                 :key="album.id" 
                 class="album-item"
                 @click="handleAlbumClick(album)">
                <div class="album-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="3" y1="9" x2="21" y2="9"></line>
                        <line x1="9" y1="21" x2="9" y2="9"></line>
                    </svg>
                </div>
                <span class="album-title">{{ album.title.replace('相册', '').trim() }}</span>
            </div>
            <!-- 无搜索结果提示 -->
            <div v-if="filteredAlbums.length === 0" class="no-results">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <span>未找到相关相册</span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
    categories: {
        type: Array,
        required: true
    },
    albums: {
        type: Array,
        default: () => []
    }
})

const emit = defineEmits(['select-category'])

const searchQuery = ref('')
const searchTimeout = ref(null)

// 监听相册数据变化
watch(() => props.albums, (newAlbums) => {
    console.log('相册数据更新:', newAlbums)
}, { deep: true })

// 过滤相册列表
const filteredAlbums = computed(() => {
    const query = searchQuery.value.toLowerCase().trim()
    console.log('相册搜索条件:', {
        query: query,
        totalAlbums: props.albums.length,
        albums: props.albums
    })
    
    if (!query) {
        return []
    }
    
    const filtered = props.albums.filter(album => {
        if (!album) {
            console.warn('发现无效的相册数据:', album)
            return false
        }

        const title = (album.title || '').toLowerCase()
        const category = album.category ? album.category.toLowerCase() : ''
        
        const matches = title.includes(query) || category.includes(query)
        
        console.log('相册匹配结果:', {
            id: album.id,
            title: album.title,
            category: album.category,
            matches: matches,
            query: query
        })
        
        return matches
    })
    
    console.log('过滤后的相册数量:', filtered.length)
    return filtered
})

// 处理搜索
const handleSearch = () => {
    if (searchTimeout.value) {
        clearTimeout(searchTimeout.value)
    }
    searchTimeout.value = setTimeout(() => {
        console.log('搜索相册:', {
            query: searchQuery.value,
            albums: props.albums
        })
    }, 300)
}

// 处理相册点击
const handleAlbumClick = (album) => {
    searchQuery.value = ''
    const category = album.category || album.title.replace('相册', '').trim()
    console.log('选择相册:', {
        id: album.id,
        title: album.title,
        category: category
    })
    emit('select-category', category)
}
</script>

<style scoped>
.album-manager {
    margin-top: 10px;
    position: relative;
    background-color: var(--secondary-color);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border: 1px solid var(--border-color);
    transition: all 0.3s ease;
}

.search-input-wrapper {
    padding: 12px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 8px;
    background-color: var(--bg-color);
    transition: background-color 0.3s, border-color 0.3s;
}

.search-icon {
    color: var(--text-color);
    opacity: 0.6;
    display: flex;
    align-items: center;
    transition: color 0.3s;
}

.search-input {
    flex: 1;
    background: none;
    border: none;
    color: var(--text-color);
    font-size: 0.95em;
    padding: 4px 0;
    transition: color 0.3s;
}

.search-input:focus {
    outline: none;
}

.search-input::placeholder {
    color: var(--text-color);
    opacity: 0.6;
}

.album-items {
    max-height: 300px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: var(--border-color) var(--bg-color);
}

.album-items::-webkit-scrollbar {
    width: 6px;
}

.album-items::-webkit-scrollbar-track {
    background: var(--bg-color);
}

.album-items::-webkit-scrollbar-thumb {
    background-color: var(--border-color);
    border-radius: 3px;
}

.album-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-color);
    transition: all 0.3s ease;
    cursor: pointer;
}

.album-item:hover {
    background-color: var(--bg-color);
}

.album-item:last-child {
    border-bottom: none;
}

.album-icon {
    color: var(--text-color);
    opacity: 0.6;
    display: flex;
    align-items: center;
    transition: color 0.3s;
}

.album-title {
    font-size: 0.95em;
    color: var(--text-color);
    transition: color 0.3s;
}

.no-results {
    padding: 24px;
    text-align: center;
    color: var(--text-color);
    opacity: 0.6;
    font-size: 0.9em;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    transition: color 0.3s;
}

.no-results svg {
    color: var(--text-color);
    opacity: 0.4;
    transition: color 0.3s;
}
</style>