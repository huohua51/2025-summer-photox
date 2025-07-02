# community/tests.py
import requests
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from albums.models import Album
from .models import Comment, Like, Follow, Notification

User = get_user_model()


class CommunityAPITestCase(TestCase):
    """社区功能API测试用例"""
    
    def setUp(self):
        self.client = APIClient()
        
        # 创建测试用户
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # 创建测试相册
        self.album = Album.objects.create(
            title='Test Album',
            description='Test Description',
            user=self.user1
        )
    
    def test_comment_crud(self):
        """测试评论的增删改查"""
        # 登录
        self.client.force_authenticate(user=self.user2)
        
        # 创建评论
        response = self.client.post('/api/v1/community/comments/', {
            'album': self.album.id,
            'content': '这是一条测试评论'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment_id = response.data['id']
        
        # 获取评论列表
        response = self.client.get(f'/api/v1/community/comments/?album={self.album.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # 创建回复
        response = self.client.post('/api/v1/community/comments/', {
            'album': self.album.id,
            'content': '这是一条回复',
            'parent': comment_id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 获取评论的回复
        response = self.client.get(f'/api/v1/community/comments/{comment_id}/replies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_like_toggle(self):
        """测试点赞功能"""
        self.client.force_authenticate(user=self.user2)
        
        # 点赞相册
        response = self.client.post('/api/v1/community/likes/toggle/', {
            'like_type': 'album',
            'object_id': self.album.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        
        # 再次点击取消点赞
        response = self.client.post('/api/v1/community/likes/toggle/', {
            'like_type': 'album',
            'object_id': self.album.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        
        # 检查点赞状态
        response = self.client.get('/api/v1/community/likes/check/', {
            'like_type': 'album',
            'object_id': self.album.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
    
    def test_follow_toggle(self):
        """测试关注功能"""
        self.client.force_authenticate(user=self.user2)
        
        # 关注用户
        response = self.client.post(f'/api/v1/community/follows/{self.user1.id}/toggle/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['following'])
        
        # 再次点击取消关注
        response = self.client.post(f'/api/v1/community/follows/{self.user1.id}/toggle/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['following'])
        
        # 不能关注自己
        response = self.client.post(f'/api/v1/community/follows/{self.user2.id}/toggle/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_notifications(self):
        """测试通知功能"""
        self.client.force_authenticate(user=self.user2)
        
        # 创建评论（会产生通知）
        response = self.client.post('/api/v1/community/comments/', {
            'album': self.album.id,
            'content': '测试评论通知'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 切换到相册所有者查看通知
        self.client.force_authenticate(user=self.user1)
        
        # 获取通知列表
        response = self.client.get('/api/v1/community/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['notification_type'], 'comment')
        
        # 获取未读数量
        response = self.client.get('/api/v1/community/notifications/unread_count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)
        
        # 标记为已读
        notification_id = Notification.objects.first().id
        response = self.client.post(f'/api/v1/community/notifications/{notification_id}/mark_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 再次检查未读数量
        response = self.client.get('/api/v1/community/notifications/unread_count/')
        self.assertEqual(response.data['unread_count'], 0)


# 手动测试脚本（用于开发调试）
def manual_test_api():
    """手动测试API接口"""
    BASE_URL = 'http://localhost:8000/api/community'
    
    # 测试账号
    user1_token = 'your_user1_token_here'  # 需要先通过登录接口获取
    user2_token = 'your_user2_token_here'
    
    headers1 = {'Authorization': f'Bearer {user1_token}'}
    headers2 = {'Authorization': f'Bearer {user2_token}'}
    
    # 1. 测试评论功能
    print("=== 测试评论功能 ===")
    
    # 创建评论
    comment_data = {
        'album': 1,  # 假设存在ID为1的相册
        'content': '这张照片拍得真好！'
    }
    response = requests.post(f'{BASE_URL}/comments/', json=comment_data, headers=headers2)
    print(f"创建评论: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 201:
        comment_id = response.json()['id']
        
        # 创建回复
        reply_data = {
            'album': 1,
            'content': '谢谢你的夸奖！',
            'parent': comment_id
        }
        response = requests.post(f'{BASE_URL}/comments/', json=reply_data, headers=headers1)
        print(f"\n创建回复: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 获取评论列表
    response = requests.get(f'{BASE_URL}/comments/?album=1', headers=headers1)
    print(f"\n获取评论列表: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 2. 测试点赞功能
    print("\n\n=== 测试点赞功能 ===")
    
    # 点赞相册
    like_data = {
        'like_type': 'album',
        'object_id': 1
    }
    response = requests.post(f'{BASE_URL}/likes/toggle/', json=like_data, headers=headers2)
    print(f"点赞相册: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 检查点赞状态
    response = requests.get(f'{BASE_URL}/likes/check/?like_type=album&object_id=1', headers=headers2)
    print(f"\n检查点赞状态: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 3. 测试关注功能
    print("\n\n=== 测试关注功能 ===")
    
    # 关注用户
    response = requests.post(f'{BASE_URL}/follows/1/toggle/', headers=headers2)
    print(f"关注用户: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 获取粉丝列表
    response = requests.get(f'{BASE_URL}/follows/1/followers/', headers=headers1)
    print(f"\n获取粉丝列表: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 4. 测试通知功能
    print("\n\n=== 测试通知功能 ===")
    
    # 获取通知列表
    response = requests.get(f'{BASE_URL}/notifications/', headers=headers1)
    print(f"获取通知列表: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 获取未读通知数量
    response = requests.get(f'{BASE_URL}/notifications/unread_count/', headers=headers1)
    print(f"\n获取未读通知数量: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 5. 测试用户相关功能
    print("\n\n=== 测试用户功能 ===")
    
    # 获取当前用户信息
    response = requests.get(f'{BASE_URL}/users/me/', headers=headers1)
    print(f"获取当前用户信息: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 获取用户的相册列表
    response = requests.get(f'{BASE_URL}/users/1/albums/', headers=headers2)
    print(f"\n获取用户相册列表: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    # 运行手动测试
    manual_test_api()