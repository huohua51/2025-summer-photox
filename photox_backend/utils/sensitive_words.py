# utils/sensitive_words.py
import re
import os
from typing import List, Set

class SensitiveWordFilter:
    """敏感词过滤器"""
    
    def __init__(self):
        self.sensitive_words: Set[str] = set()
        self.load_sensitive_words()
    
    def load_sensitive_words(self):
        """加载敏感词库"""
        # 基础敏感词库
        base_words = {
            # 政治敏感词
            '政治', '政府', '国家', '领导人', '官员', '腐败', '贪污', '受贿',
            # 暴力词汇
            '暴力', '血腥', '恐怖', '爆炸', '枪击', '杀人', '自杀', '死亡',
            # 色情词汇
            '色情', '黄色', '成人', '性', '裸体', '情色', '成人内容',
            # 赌博词汇
            '赌博', '博彩', '赌场', '彩票', '六合彩', '老虎机',
            # 毒品词汇
            '毒品', '吸毒', '大麻', '海洛因', '冰毒', '摇头丸',
            # 其他敏感词
            '诈骗', '传销', '邪教', '迷信', '谣言', '造谣',
            # 网络用语中的敏感词
            '傻逼', '狗屎', '混蛋', '王八蛋', '贱人', '婊子',
            # 英文敏感词
            'fuck', 'shit', 'bitch', 'asshole', 'porn', 'sex', 'drug', 'kill',
            # 数字敏感词
            '110', '120', '119', '911', '666', '888',
        }
        
        self.sensitive_words.update(base_words)
        
        # 尝试从文件加载额外的敏感词
        try:
            sensitive_file = os.path.join(os.path.dirname(__file__), 'sensitive_words.txt')
            if os.path.exists(sensitive_file):
                with open(sensitive_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        word = line.strip()
                        if word and not word.startswith('#'):
                            self.sensitive_words.add(word)
        except Exception as e:
            print(f"加载敏感词文件失败: {e}")
    
    def add_sensitive_word(self, word: str):
        """添加敏感词"""
        self.sensitive_words.add(word.strip())
    
    def remove_sensitive_word(self, word: str):
        """移除敏感词"""
        self.sensitive_words.discard(word.strip())
    
    def check_text(self, text: str) -> dict:
        """检查文本中的敏感词
        
        Returns:
            dict: {
                'has_sensitive': bool,  # 是否包含敏感词
                'sensitive_words': List[str],  # 发现的敏感词列表
                'filtered_text': str,  # 过滤后的文本
                'replacement_count': int  # 替换次数
            }
        """
        if not text:
            return {
                'has_sensitive': False,
                'sensitive_words': [],
                'filtered_text': text,
                'replacement_count': 0
            }
        
        found_words = []
        filtered_text = text
        replacement_count = 0
        
        # 检查每个敏感词
        for word in self.sensitive_words:
            if word.lower() in text.lower():
                found_words.append(word)
                # 替换敏感词为 *
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                filtered_text = pattern.sub('*' * len(word), filtered_text)
                replacement_count += 1
        
        return {
            'has_sensitive': len(found_words) > 0,
            'sensitive_words': found_words,
            'filtered_text': filtered_text,
            'replacement_count': replacement_count
        }
    
    def is_sensitive(self, text: str) -> bool:
        """简单检查是否包含敏感词"""
        if not text:
            return False
        
        text_lower = text.lower()
        for word in self.sensitive_words:
            if word.lower() in text_lower:
                return True
        return False
    
    def get_sensitive_words(self) -> List[str]:
        """获取所有敏感词列表"""
        return sorted(list(self.sensitive_words))
    
    def save_sensitive_words(self):
        """保存敏感词到文件"""
        try:
            sensitive_file = os.path.join(os.path.dirname(__file__), 'sensitive_words.txt')
            with open(sensitive_file, 'w', encoding='utf-8') as f:
                f.write("# 敏感词库\n")
                f.write("# 每行一个敏感词，以#开头的行为注释\n\n")
                for word in sorted(self.sensitive_words):
                    f.write(f"{word}\n")
        except Exception as e:
            print(f"保存敏感词文件失败: {e}")

# 全局敏感词过滤器实例
sensitive_filter = SensitiveWordFilter() 