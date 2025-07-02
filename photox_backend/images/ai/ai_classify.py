import requests
import base64
import re
from PIL import Image
import io
import os
import json
import logging
import django
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

try:
    django.setup()
    from tags.models import Tag  # 导入标签模型
    logger = logging.getLogger(__name__)
except Exception as e:
    print(f"Django初始化失败: {e}")
    Tag = None  # 定义空对象作为回退

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_category_map(file_path="classes.txt"):
    """从文件加载类别映射"""
    category_map = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 跳过空行和注释行
                if not line.strip() or line.strip().startswith('#'):
                    continue

                # 处理您提供的格式：数字:类别名
                if ':' in line:
                    parts = line.strip().split(':', 1)
                    if len(parts) == 2 and parts[0].strip().isdigit():
                        key = int(parts[0].strip())
                        value = parts[1].strip()
                        category_map[key] = value
    except FileNotFoundError:
        logger.warning(f"类别文件 {file_path} 未找到，使用默认类别")

        category_map = {
            0: "其他", 1: "风景", 2: "人物肖像", 3: "动物", 4: "食品",
            5: "建筑", 6: "电子产品", 7: "植物花卉", 8: "家具家居", 9: "服装鞋帽",
            10: "艺术创作", 11: "运动器材", 12: "交通工具", 13: "宠物用品", 14: "美妆用品"
        }
    return category_map


def load_model_map(file_path="model.txt"):
    """从文件加载模型映射 """
    model_map = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # 支持两种格式：1:"model-name" 或 key:value
                if ':' in line or '"' in line:
                    # 尝试提取数字和模型名称
                    match = re.search(r'(\d+)\s*[:=]?\s*"([^"]+)"', line)
                    if match:
                        key = int(match.group(1))
                        value = match.group(2)
                        model_map[key] = value
                    else:
                        # 尝试简单分割
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            try:
                                key = int(parts[0].strip())
                                value = parts[1].strip().strip('"')
                                model_map[key] = value
                            except ValueError:
                                logger.warning(f"忽略无效模型行: {line}")
    except FileNotFoundError:
        logger.warning(f"模型文件 {file_path} 未找到，使用默认模型")
        model_map = {
            1: "qwen2.5-vl-7b-instruct",
            2: "doubao-1.5-vision-pro",
            3: "qwen-vl-max-2025-01-25",
            4: "qwen2.5-omni-7b"
        }
    return model_map


def process_image(image_path, max_size=1024, quality=85):
    """优化的图片预处理函数"""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 快速缩放
        width, height = img.size
        if max(width, height) > max_size:
            ratio = max_size / max(width, height)
            img = img.resize((int(width * ratio), int(height * ratio)), Image.Resampling.NEAREST)

        # 优化存储
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='JPEG', quality=quality, optimize=True)
        return byte_arr.getvalue()
    except Exception as e:
        logger.error(f"图片处理失败: {e}")
        return None


def get_tags_from_database():
    """从数据库获取所有标签信息"""
    try:
        tags = Tag.objects.all()
        # 创建标签ID到名称的映射
        tag_map = {tag.id: tag.name for tag in tags}

        # 创建标签列表的字符串表示
        tag_list_str = "\n".join([f"{tag_id}: {name}" for tag_id, name in tag_map.items()])

        return tag_map, tag_list_str
    except Exception as e:
        logger.error(f"从数据库获取标签失败: {e}")
        # 返回默认标签集
        default_tags = {
            1: "家庭", 2: "旅行", 3: "婚礼", 4: "毕业", 5: "生日",
            6: "宠物", 7: "风景", 8: "海滩", 9: "山脉", 10: "城市景观"
        }
        tag_list_str = "\n".join([f"{tag_id}: {name}" for tag_id, name in default_tags.items()])
        return default_tags, tag_list_str


# def image_classification(image_path, api_key, model_id=1, classes_file="classes.txt", model_file="model.txt"):
#     """图像分类主函数，返回分类和标签信息"""
#     # 加载类别映射
#     category_map = load_category_map(classes_file)

#     # 从数据库获取标签信息
#     tag_map, tag_list_str = get_tags_from_database()

#     # 加载模型映射
#     model_map = load_model_map(model_file)

#     # 获取模型名称
#     if model_id in model_map:
#         model_name = model_map[model_id]
#         logger.info(f"使用模型: {model_name} (ID: {model_id})")
#     else:
#         model_name = model_map.get(1, "qwen2.5-vl-7b-instruct")  # 默认第一个模型
#         logger.warning(f"无效模型ID {model_id}，使用默认模型: {model_name}")

#     # 预处理图片
#     image_bytes = process_image(image_path)
#     if not image_bytes:
#         return {
#             "category_id": 0,
#             "category_name": category_map.get(0, "其他"),
#             "tags": [],
#             "error": "图片处理失败"
#         }

#     # 构建Data URL
#     encoded_image = base64.b64encode(image_bytes).decode("utf-8")
#     image_data_url = f"data:image/jpeg;base64,{encoded_image}"

#     # 构建系统提示词 - 要求返回分类和标签
#     system_prompt = (
#         f"你是一个专业的图像内容分析AI。请根据提供的图像，完成以下任务：\n"
#         f"1. 从以下分类中选择最合适的一个分类ID（必须是0-{len(category_map) - 1}之间的整数）：\n"
#         f"{json.dumps(category_map, indent=2, ensure_ascii=False)}\n"
#         f"2. 从以下标签中选择3-5个最相关的标签（必须返回标签ID，即数字）：\n"
#         f"{tag_list_str}\n"
#         f"返回格式必须是纯JSON：{{\"category_id\": 分类ID, \"tag_ids\": [标签ID1, 标签ID2, ...]}}"
#         f"注意：只能返回数字ID，不要返回标签名称！"
#     )

#     # 构建请求载荷
#     payload = {
#         "model": model_name,
#         "response_format": {"type": "json_object"},
#         "messages": [
#             {
#                 "role": "system",
#                 "content": system_prompt
#             },
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": "识别图片内容并返回指定的JSON格式"},
#                     {"type": "image_url", "image_url": {"url": image_data_url}}
#                 ]
#             }
#         ]
#     }

#     # 发送请求
#     headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
#     try:
#         response = requests.post(
#             "https://api.qnaigc.com/v1/chat/completions",
#             json=payload,
#             headers=headers,
#             timeout=30  # 延长超时时间
#         )

#         if response.status_code == 200:
#             try:
#                 # 尝试解析响应内容
#                 content = response.json()['choices'][0]['message']['content'].strip()
#                 logger.info(f"模型原始响应: {content}")

#                 # 去除可能的Markdown代码块标记
#                 if content.startswith('```json') and content.endswith('```'):
#                     content = content[7:-3].strip()  # 移除 ```json 和 ```
#                 elif content.startswith('```') and content.endswith('```'):
#                     content = content[3:-3].strip()  # 移除通用的 ```

#                 # 解析JSON响应
#                 result_data = json.loads(content)
#                 category_id = int(result_data.get('category_id', 0))
#                 tag_ids = result_data.get('tag_ids', [])

#                 # 验证分类ID
#                 if category_id not in category_map:
#                     logger.warning(f"无效分类ID: {category_id}, 使用默认分类")
#                     category_id = 0

#                 # 验证标签ID
#                 valid_tags = []
#                 for tag_id in tag_ids:
#                     try:
#                         tag_id_int = int(tag_id)
#                         if tag_id_int in tag_map:
#                             valid_tags.append({
#                                 "id": tag_id_int,
#                                 "name": tag_map[tag_id_int]
#                             })
#                         else:
#                             logger.warning(f"忽略无效标签ID: {tag_id}")
#                     except ValueError:
#                         logger.warning(f"忽略非数字标签ID: {tag_id}")

#                 # 如果没有有效标签，添加默认标签
#                 if not valid_tags:
#                     valid_tags.append({
#                         "id": 0,
#                         "name": "未分类"
#                     })

#                 return {
#                     "category_id": category_id,
#                     "category_name": category_map.get(category_id, category_map.get(0, "其他")),
#                     "tags": valid_tags,
#                     "model_used": model_name
#                 }

#             except (json.JSONDecodeError, KeyError, ValueError) as e:
#                 logger.error(f"响应解析错误: {e}")
#                 return {
#                     "category_id": 0,
#                     "category_name": category_map.get(0, "其他"),
#                     "tags": [{"id": 0, "name": "解析错误"}],
#                     "model_used": model_name
#                 }

#         else:
#             logger.error(f"API错误: {response.status_code}, {response.text}")
#             return {
#                 "category_id": 0,
#                 "category_name": category_map.get(0, "其他"),
#                 "tags": [{"id": 0, "name": "API错误"}],
#                 "model_used": model_name
#             }

#     except Exception as e:
#         logger.error(f"请求异常: {e}")
#         return {
#             "category_id": 0,
#             "category_name": category_map.get(0, "其他"),
#             "tags": [{"id": 0, "name": "请求异常"}],
#             "model_used": model_name
#         }

def image_classification(image_path, api_key,  classes_file="classes.txt"):
    """图像分类主函数，返回分类和标签信息"""
    # 加载类别映射
    category_map = load_category_map(classes_file)

    # 从数据库获取标签信息
    tag_map, tag_list_str = get_tags_from_database()


    model_name="qwen-vl-max-latest"
    # 预处理图片
    image_bytes = process_image(image_path)
    if not image_bytes:
        return {
            "category_id": 0,
            "category_name": category_map.get(0, "其他"),
            "tags": [],
            "error": "图片处理失败"
        }

    # 构建Data URL
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:image/jpeg;base64,{encoded_image}"

    # 构建系统提示词 - 要求返回分类和标签
    system_prompt = (
        f"你是一个专业的图像内容分析AI。请根据提供的图像，完成以下任务：\n"
        f"1. 从以下分类中选择最合适的一个分类ID（必须是0-{len(category_map) - 1}之间的整数），如果不是非常确定分入其他：\n"
        f"{json.dumps(category_map, indent=2, ensure_ascii=False)}\n"
        f"2. 从以下标签中选择4-6个最相关的标签（必须返回标签ID，即数字）,要求只输出最准确最确定的标签，"
        f"并且如果不是非常确定可以减少输出的标签，需要尽量避免错误：\n"
        f"{tag_list_str}\n"
        f"返回格式必须是纯JSON：{{\"category_id\": 分类ID, \"tag_ids\": [标签ID1, 标签ID2, ...]}}"
        f"注意：只能返回数字ID，不要返回标签名称！"
    )

    # 构建请求载荷
    payload = {
        "model": model_name,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "识别图片内容并返回指定的JSON格式"},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }
        ]
    }

    # 发送请求
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30  # 延长超时时间
        )

        if response.status_code == 200:
            try:
                # 尝试解析响应内容
                content = response.json()['choices'][0]['message']['content'].strip()
                logger.info(f"模型原始响应: {content}")

                # 去除可能的Markdown代码块标记
                if content.startswith('```json') and content.endswith('```'):
                    content = content[7:-3].strip()  # 移除 ```json 和 ```
                elif content.startswith('```') and content.endswith('```'):
                    content = content[3:-3].strip()  # 移除通用的 ```

                # 解析JSON响应
                result_data = json.loads(content)
                category_id = int(result_data.get('category_id', 0))
                tag_ids = result_data.get('tag_ids', [])

                # 验证分类ID
                if category_id not in category_map:
                    logger.warning(f"无效分类ID: {category_id}, 使用默认分类")
                    category_id = 0

                # 验证标签ID
                valid_tags = []
                for tag_id in tag_ids:
                    try:
                        tag_id_int = int(tag_id)
                        if tag_id_int in tag_map:
                            valid_tags.append({
                                "id": tag_id_int,
                                "name": tag_map[tag_id_int]
                            })
                        else:
                            logger.warning(f"忽略无效标签ID: {tag_id}")
                    except ValueError:
                        logger.warning(f"忽略非数字标签ID: {tag_id}")

                # 如果没有有效标签，添加默认标签
                if not valid_tags:
                    valid_tags.append({
                        "id": 0,
                        "name": "未分类"
                    })

                return {
                    "category_id": category_id,
                    "category_name": category_map.get(category_id, category_map.get(0, "其他")),
                    "tags": valid_tags,
                    "model_used": model_name
                }

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.error(f"响应解析错误: {e}")
                return {
                    "category_id": 0,
                    "category_name": category_map.get(0, "其他"),
                    "tags": [{"id": 0, "name": "解析错误"}],
                    "model_used": model_name
                }

        else:
            logger.error(f"API错误: {response.status_code}, {response.text}")
            return {
                "category_id": 0,
                "category_name": category_map.get(0, "其他"),
                "tags": [{"id": 0, "name": "API错误"}],
                "model_used": model_name
            }

    except Exception as e:
        logger.error(f"请求异常: {e}")
        return {
            "category_id": 0,
            "category_name": category_map.get(0, "其他"),
            "tags": [{"id": 0, "name": "请求异常"}],
            "model_used": model_name
        }


# if __name__ == "__main__":
#     api_key = "sk-ff8f03a8cfbc03d7df75b7ddb6b1fb7f0bfc8116e02986306865aa9149741301"
#     local_file = "img_1.png"

#     # 进行分类
#     result = image_classification(
#         image_path=local_file,
#         api_key=api_key,
#         model_id=3,
#         classes_file="classes.txt",
#         model_file="model.txt"
#     )
#     #models_id表示使用模型的编号
#     # 输出结果
#     print("\n分类结果:")
#     print(f"模型: {result['model_used']}")
#     print(f"类别ID: {result['category_id']}")
#     print(f"类别名称: {result['category_name']}")
#     print("标签:")
#     for tag in result['tags']:
#         print(f"  - {tag['id']}: {tag['name']}")
if __name__ == "__main__":
    api_key = "sk-3658ae5ea3284ff4865227db05f4a214"
    local_file = "img3.png"

    # 进行分类
    result = image_classification(
        image_path=local_file,
        api_key=api_key,
        classes_file="classes.txt",
    )
    #models_id表示使用模型的编号
    # 输出结果
    print("\n分类结果:")
    print(f"模型: {result['model_used']}")
    print(f"类别ID: {result['category_id']}")
    print(f"类别名称: {result['category_name']}")
    print("标签:")
    for tag in result['tags']:
        print(f"  - {tag['id']}: {tag['name']}")