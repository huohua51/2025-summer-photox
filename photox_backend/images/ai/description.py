from .ai_classify import load_model_map, process_image, logger
import base64
import requests

def generate_image_description(image_path, api_key):
    """生成图片的一句话描述"""
    #

    model_name="qwen-vl-max-latest"

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
        "请严格参考以下示例的风格和表达方式进行图片分析，不要输出任何标题、编号、markdown或html格式，只输出自然流畅的中文段落："
        "【示例】"
        "这是康尼岛的 “飓风” 过山车（Cyclone），位于美国纽约布鲁克林。\n"
        "从光线运用看，自然光为主，蓝天作为背景，光线明亮且均匀，营造出一种活力、欢快的氛围。充足的光线让过山车的金属结构、“CYCLONE” 字样以及人物都清晰呈现，光影在金属架上形成明暗对比，增强了结构的立体感。\n"
        "色调上，蓝天的蓝色与过山车的金属白、轨道红搭配，色彩鲜明且饱和度适中。蓝色传递出轻松，红色带来刺激感，白色让结构更醒目，这些色彩共同强化了游乐园的欢乐与冒险氛围，视觉上很有冲击力。\n"
        "焦点清晰落在过山车上，景深控制让背景蓝天稍显虚化，突出主体。人物虽在运动，但因焦点精准，神态动作清晰，观众视线自然被引导到过山车及乘客身上，强化了核心内容。\n"
        "拍摄角度是仰拍，突出过山车的高大与惊险。构图上，过山车的曲线、金属架的线条构成引导线，将视线带向高处的乘客，同时 “CYCLONE” 字样作为视觉中心，与过山车主体呼应，三分法布局让画面平衡又有动感。\n"
        "人物表情兴奋，肢体动作夸张，有的举手欢呼，传递出乘坐过山车时的刺激与愉悦，和过山车的冒险属性契合，让画面有了故事性，仿佛能感受到他们的尖叫与欢乐。\n"
        "纹理细节上，金属架的结构、轨道的质感、旗帜的飘动都被捕捉到，增强了画面真实感与沉浸感。后期处理应该是强化了色彩对比，让蓝天更蓝，红色更艳，锐化了金属结构，让细节更清晰，提升整体视觉效果。\n"
        "若要改进，可在光线更柔和的时段（如黄昏）拍摄，暖光会给画面增添别样氛围；利用慢门拍人物动态拖影，强化运动感。设备上，用广角镜头可更突出过山车的宏伟，偏振镜能让蓝天更纯净，色彩更饱和。\n"
        "从市场需求看，这类游乐园照片能吸引喜欢冒险、追求欢乐氛围的观众，传达刺激与快乐，可用于旅游宣传、游乐园推广。视觉策略上，强化色彩对比和动感元素，突出主题，让观众一眼感受到过山车的魅力与游玩的愉悦。"
        "【示例结束】"
        "请严格模仿上述示例的风格和结构，输出图片分析内容。"
        "每个分析角度都要单独成段，每个段落之间请用换行符（\n）分隔，不能合并为一段。"
        "不允许用编号、标题、分点、加粗、markdown等格式，只能用自然段落。"
        "每段结尾加上特殊分隔符（如[段落结束]）"

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
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
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
                # 按[段落结束]分割为段落数组
                paragraphs = [p.strip() for p in description.split('[段落结束]') if p.strip()]
                logger.info(f"生成描述: {paragraphs}")
                return {
                    "description": paragraphs,
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

