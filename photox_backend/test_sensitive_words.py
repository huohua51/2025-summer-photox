#!/usr/bin/env python
"""
敏感词过滤功能测试脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_repo_backend.settings')
django.setup()

from utils.sensitive_words import sensitive_filter

def test_sensitive_words():
    """测试敏感词过滤功能"""
    print("=== 敏感词过滤功能测试 ===\n")
    
    # 测试用例
    test_cases = [
        "这是一张美丽的风景照片",
        "这张图片包含暴力内容",
        "色情图片分享",
        "赌博网站链接",
        "毒品交易信息",
        "政治敏感话题讨论",
        "傻逼图片",
        "fuck you",
        "正常的图片标题",
        "包含多个敏感词：暴力、色情、赌博",
    ]
    
    print("测试结果：")
    print("-" * 50)
    
    for i, text in enumerate(test_cases, 1):
        result = sensitive_filter.check_text(text)
        print(f"测试 {i}: {text}")
        print(f"  包含敏感词: {result['has_sensitive']}")
        if result['has_sensitive']:
            print(f"  敏感词: {result['sensitive_words']}")
            print(f"  过滤后: {result['filtered_text']}")
            print(f"  替换次数: {result['replacement_count']}")
        print()
    
    print("=== 敏感词库统计 ===")
    words = sensitive_filter.get_sensitive_words()
    print(f"敏感词总数: {len(words)}")
    print(f"前10个敏感词: {words[:10]}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_sensitive_words() 