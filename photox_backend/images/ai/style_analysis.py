import requests
import base64
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

def analyze_image_style(image_path, api_key):
    """分析图片的艺术风格和摄影风格"""
    try:
        # 预处理图片
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 调整大小
        max_size = 1024
        width, height = img.size
        if max(width, height) > max_size:
            ratio = max_size / max(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # 转换为base64
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='JPEG', quality=85)
        image_bytes = byte_arr.getvalue()
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        image_data_url = f"data:image/jpeg;base64,{encoded_image}"
        
        # 构建请求
        payload = {
            "model": "qwen2.5-vl-7b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的图像风格分析师，精通各种艺术流派和摄影风格。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """请分析这张图片的风格特征，返回JSON格式：
{
    "art_style": "艺术风格（如：写实主义、印象派、抽象派、超现实主义、极简主义等）",
    "photography_style": "摄影风格（如：人像摄影、风景摄影、街头摄影、纪实摄影、艺术摄影等）",
    "color_style": "色彩风格（如：暖色调、冷色调、高对比度、低饱和度、黑白等）",
    "composition": "构图方式（如：三分法、对称构图、引导线、框架构图等）",
    "mood": "情感氛围（如：宁静、活力、忧郁、神秘、温馨等）",
    "technique_features": ["特殊技法1", "特殊技法2"]
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_data_url}
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.qnaigc.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # 尝试解析JSON
            try:
                import json
                # 提取JSON部分
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    style_data = json.loads(json_str)
                    return style_data
            except:
                logger.error("Failed to parse JSON from response")
                
        return None
        
    except Exception as e:
        logger.error(f"Style analysis failed: {str(e)}")
        return None


def analyze_image_emotion(image_path, api_key):
    """分析图片的情感和意境"""
    try:
        # 预处理图片（同上）
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        max_size = 1024
        width, height = img.size
        if max(width, height) > max_size:
            ratio = max_size / max(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='JPEG', quality=85)
        image_bytes = byte_arr.getvalue()
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        image_data_url = f"data:image/jpeg;base64,{encoded_image}"
        
        payload = {
            "model": "qwen2.5-vl-7b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个情感分析专家，擅长解读图像传达的情感和意境。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """请深入分析这张图片的情感层面，返回JSON格式：
{
    "primary_emotion": "主要情感",
    "secondary_emotions": ["次要情感1", "次要情感2"],
    "atmosphere": "整体氛围描述",
    "story_hint": "图片可能讲述的故事",
    "viewer_feeling": "观看者可能产生的感受",
    "symbolic_elements": ["象征元素1", "象征元素2"]
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_data_url}
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.qnaigc.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            try:
                import json
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    emotion_data = json.loads(json_str)
                    return emotion_data
            except:
                logger.error("Failed to parse emotion JSON")
                
        return None
        
    except Exception as e:
        logger.error(f"Emotion analysis failed: {str(e)}")
        return None 