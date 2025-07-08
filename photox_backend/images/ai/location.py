import requests
import base64
import json

def ai_recognize_location_from_image(image_path, api_key):
    """
    用 DashScope 大模型识别图片地点，返回 {'lat': ..., 'lng': ..., 'name': ...} 或 None
    """
    # 1. 读取图片并 base64 编码
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    image_data_url = f"data:image/jpeg;base64,{img_b64}"

    # 2. 构造多模态消息
    messages = [
        {
            "role": "system",
            "content": "你是一个专业的地理位置识别AI助手。"
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "请根据下方图片内容，推测图片的拍摄地点（如著名地标、城市、国家等），如果能推测出经纬度请返回经纬度，否则请返回null。请用如下JSON格式严格回复：{\"lat\": 纬度或null, \"lng\": 经度或null, \"name\": \"地点名或null\"}"},
                {"type": "image_url", "image_url": {"url": image_data_url}}
            ]
        }
    ]

    # 3. 构造请求
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen-vl-max",  # 推荐视觉大模型
        "messages": messages,
        "response_format": {"type": "json_object"}
    }

    # 4. 发送请求
    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        print("DashScope响应状态码：", resp.status_code)
        print("DashScope响应内容：", resp.text)
        if resp.status_code == 200:
            try:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                # 只提取JSON部分
                if content.startswith("```json"):
                    content = content[7:-3].strip()
                elif content.startswith("```"):
                    content = content[3:-3].strip()
                result = json.loads(content)
                if result.get("lat") and result.get("lng"):
                    return result
            except Exception as e:
                print("解析AI响应失败：", e)
        else:
            print("DashScope API请求失败：", resp.text)
    except Exception as e:
        print("DashScope请求异常：", e)
    return None

# 用法示例
if __name__ == "__main__":
    api_key = "sk-3658ae5ea3284ff4865227db05f4a214" # 你的DashScope API Key
    image_path = "test.jpg"
    result = ai_recognize_location_from_image(image_path, api_key)
    print(result)