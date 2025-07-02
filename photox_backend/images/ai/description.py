from .ai_classify import load_model_map, process_image, logger
import base64
import requests

def generate_image_description(image_path, api_key, model_id=1, model_file="model.txt"):
    """生成图片的一句话描述"""
    # 加载模型映射
    model_map = load_model_map(model_file)

    # 获取模型名称
    if model_id in model_map:
        model_name = model_map[model_id]
        logger.info(f"使用模型: {model_name} (ID: {model_id})")
    else:
        model_name = model_map.get(1, "qwen2.5-vl-7b-instruct")
        logger.warning(f"无效模型ID {model_id}，使用默认模型: {model_name}")

    # 预处理图片
    image_bytes = process_image(image_path)
    if not image_bytes:
        return {
            "description": "图片处理失败",
            "model_used": model_name
        }

    # 构建Data URL
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:image/jpeg;base64,{encoded_image}"

    # 构建系统提示词 - 要求生成自然语言描述
    system_prompt = (
        "1. 直接输出描述文本，不要包含任何冗余的格式或标记。"
        "2. 身份定位：资深摄影师，具有10年以上的拍摄经验，擅长多种摄影风格（如人像、风景、街拍、艺术摄影等）。"
        "如果是风景照片，你要告诉我这是哪个地点（如果可以识别的话），放在这段回复的最前端。"
        "3. 分析角度：从构图、光影、色彩、焦距、景深、曝光、质感、拍摄角度等专业技术层面进行深度分析。"
        "4. 深入探讨光线的使用与光影效果，分析如何通过自然光、人工光源或混合光来塑造画面的氛围与情感表达。"
        "5. 色彩搭配：分析色调、饱和度、对比度等色彩元素的运用，以及色彩如何影响整体的视觉效果与情感传达。"
        "6. 分析焦点与景深的控制，探讨如何通过焦外效果（如背景虚化）来引导观众的视线，突出主要元素。"
        "7. 构图技巧：分析拍摄角度、构图法则（如三分法、对称性、引导线等）的运用，以及这些手法如何提升画面的视觉冲击力。"
        "8. 如果照片包含人物，深入剖析人物的表情、姿态、肢体语言与镜头之间的互动，如何通过这些元素传达情感与故事。"
        "9. 深度分析图像中的纹理、细节与层次感，探讨如何通过镜头捕捉到细腻的质感，增强画面的沉浸感。"
        "10. 如果有后期处理，分析其对照片的影响，尤其是在锐度、色彩修正、对比度调整等方面的作用与效果。"
        "11. 根据不同的拍摄环境与场景，提供相应的改进建议，例如如何利用环境光、反射光、背景的选择等来增强照片的表达力。"
        "12. 如果有特定摄影风格（如黑白摄影、复古风格、极简主义等），分析该风格的体现方法及其独特的视觉语言。"
        "13. 如果适用，提出如何通过不同设备（如镜头、滤镜、相机设置等）来优化拍摄效果，提升画质与表现力。"
        "14. 针对摄影作品的市场需求与观众心理，提出与摄影目标相符的视觉传达策略。"

    )

    # 构建请求载荷
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请描述这张图片"},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }
        ]
    }

    # 发送请求
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.post(
            "https://api.qnaigc.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            try:
                # 获取描述文本
                description = response.json()['choices'][0]['message']['content'].strip()

                # 清理可能存在的引号
                description = description.strip('"').strip('“').strip('”')

                logger.info(f"生成描述: {description}")
                return {
                    "description": description,
                    "model_used": model_name
                }
            except (KeyError, ValueError) as e:
                logger.error(f"响应解析错误: {e}")
                return {
                    "description": "描述解析失败",
                    "model_used": model_name
                }
        else:
            logger.error(f"API错误: {response.status_code}, {response.text}")
            return {
                "description": "API请求失败",
                "model_used": model_name
            }
    except Exception as e:
        logger.error(f"请求异常: {e}")
        return {
            "description": "请求异常",
            "model_used": model_name
        }


if __name__ == "__main__":
    # 测试描述生成
    api_key = "sk-ff8f03a8cfbc03d7df75b7ddb6b1fb7f0bfc8116e02986306865aa9149741301"
    local_file = "img.png"

    desc_result = generate_image_description(
        image_path=local_file,
        api_key=api_key,
        model_id=3
    )

    print("\n图片描述结果:")
    print(f"模型: {desc_result['model_used']}")
    print(f"描述: {desc_result['description']}")

