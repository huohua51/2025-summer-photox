from image_classifier import ImageClassifier
from torchvision import models
from MultiModelClassifier import MultiModelClassifier
import logging
import traceback
import os

logger = logging.getLogger(__name__)
def clean_tags(tags_raw):
    cleaned_tags = []
    for item in tags_raw:
        item = item.replace('\n', ' ')      # 替换换行
        item = item.strip(" '\"\t\r,")      # 去除首尾空格、引号、逗号、制表符等
        cleaned_tags.append(item)
    return cleaned_tags

# 通用类别映射（全局常量）
GENERIC_CATEGORIES = {
    '动物': ['bird', 'cat', 'dog', 'fish', 'shark', 'tiger', 'lion', 'bear', 'elephant', 'horse', 'zebra', 'whale',
             'dolphin'],
    '人物': ['person', 'groom', 'diver', 'player', 'baby'],
    '风景': ['mountain', 'beach', 'valley', 'volcano', 'cliff', 'coral', 'geyser', 'lake', 'coast', 'lakeside',
             'lakeshore'],
    '交通工具': ['car', 'bicycle', 'airplane', 'bus', 'train', 'ship', 'motorcycle', 'truck'],
    '植物': ['tree', 'flower', 'palm', 'cactus', 'mushroom', 'broccoli', 'cabbage', 'corn', 'apple', 'orange'],
    '电子设备': ['computer', 'laptop', 'monitor', 'keyboard', 'mouse', 'printer', 'scanner', 'camera'],
    '食物': ['pizza', 'burger', 'sushi', 'bread', 'cake', 'ice cream', 'coffee', 'wine', 'soup']
}


def get_generic_category(label):
    """将具体标签映射到通用类别"""
    label = label.lower()
    for category, keywords in GENERIC_CATEGORIES.items():
        if any(keyword in label for keyword in keywords):
            return category
    return '其他'


def ai_image(image_path, model_type="resnet50"):
    """
    对图片进行分类并返回标签列表和通用类别
    :param image_path: 图片路径
    :param model_type: 模型类型（可选："resnet50" 或 "inception_v3"）
    :return: (tags, category) 元组
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(image_path):
            logger.error(f"AI分析失败：图片文件不存在: {image_path}")
            return ["未分类"], "其他"
            
        logger.info(f"开始AI分析图片: {image_path}")
        logger.info(f"使用模型: {model_type}")
        
        # 检查文件大小
        file_size = os.path.getsize(image_path)
        if file_size == 0:
            logger.error(f"AI分析失败：图片文件为空: {image_path}")
            return ["未分类"], "其他"
        logger.info(f"图片大小: {file_size} 字节")
            
        # 初始化分类器
        try:
            if model_type == "inception_v3":
                classifier = MultiModelClassifier(model_name="inception_v3", weights="DEFAULT")
                logger.info("成功初始化inception_v3分类器")
            else:
                classifier = ImageClassifier()  # 默认使用 resnet50
                logger.info("成功初始化resnet50分类器")
        except Exception as e:
            logger.error(f"初始化分类器失败: {str(e)}")
            logger.error(traceback.format_exc())
            return ["未分类"], "其他"

        # 预测结果
        try:
            results = classifier.predict(image_path)
            logger.info(f"预测完成，获得 {len(results)} 个结果")
        except Exception as e:
            logger.error(f"预测图片失败: {str(e)}")
            logger.error(traceback.format_exc())
            return ["未分类"], "其他"

        # 提取标签列表和类别
        if not results:
            logger.warning("预测结果为空")
            return ["未分类"], "其他"
            
        tags = [label for label, _ in results]
        
        tags = clean_tags(tags)
        logger.info(f"提取的标签: {tags}")
        
        category = get_generic_category(tags[0]) if tags else '其他'
        logger.info(f"确定的通用类别: {category}")

        return tags, category
    except Exception as e:
        logger.error(f"AI图像分析过程中发生异常: {str(e)}")
        logger.error(traceback.format_exc())
        # 返回默认值
        return ["未分类"], "其他"


# 使用示例
if __name__ == "__main__":
    tags, category = ai_image("t2.jpg")
    print("标签列表:", tags)
    print("通用类别:", category)


