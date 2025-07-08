import axiosInstance from './axiosInstance';

export const sensitiveWordsService = {
    // 检测文本中的敏感词
    checkText: async (text) => {
        try {
            const response = await axiosInstance.post('/api/sensitive-words/check/', {
                text: text
            });
            return response.data;
        } catch (error) {
            console.error('敏感词检测失败:', error);
            throw error;
        }
    },

    // 获取敏感词列表（管理员功能）
    getSensitiveWords: async () => {
        try {
            const response = await axiosInstance.get('/api/sensitive-words/');
            return response.data;
        } catch (error) {
            console.error('获取敏感词列表失败:', error);
            throw error;
        }
    },

    // 添加敏感词（管理员功能）
    addSensitiveWord: async (word) => {
        try {
            const response = await axiosInstance.post('/api/sensitive-words/', {
                word: word
            });
            return response.data;
        } catch (error) {
            console.error('添加敏感词失败:', error);
            throw error;
        }
    },

    // 删除敏感词（管理员功能）
    removeSensitiveWord: async (word) => {
        try {
            const response = await axiosInstance.delete(`/api/sensitive-words/${word}/`);
            return response.data;
        } catch (error) {
            console.error('删除敏感词失败:', error);
            throw error;
        }
    }
}; 