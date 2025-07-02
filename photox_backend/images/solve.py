from PIL import Image, ImageEnhance, ImageFilter
import numpy as np


def adjust_brightness(image, factor):
    """
    调整图像亮度
    :param image: PIL图像对象
    :param factor: 亮度系数 (0.0-2.0)
        - 0.0 = 全黑
        - 1.0 = 原始亮度
        - 2.0 = 最大亮度
    """
    factor = float(factor)
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def adjust_contrast(image, factor):
    """
    调整图像对比度
    :param image: PIL图像对象
    :param factor: 对比度系数 (0.0-2.0)
        - 0.0 = 全灰图像
        - 1.0 = 原始对比度
        - 2.0 = 最大对比度
    """
    factor = float(factor)
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def adjust_saturation(image, factor):
    """
    调整图像饱和度
    :param image: PIL图像对象
    :param factor: 饱和度系数 (0.0-3.0)
        - 0.0 = 黑白图像
        - 1.0 = 原始饱和度
        - 3.0 = 最大饱和度
    """
    factor = float(factor)
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)


def adjust_hue(image, shift):
    """
    调整图像色调
    :param image: PIL图像对象
    :param shift: 色相偏移值 (0.0-1.0)
        - 0.0 = 原始色调
        - 0.33 = 120°偏移 (蓝→绿)
        - 0.66 = 240°偏移 (绿→红)
        - 1.0 = 360°偏移 (返回原色)
    """
    try:
        shift = float(shift)
        img = image.convert('HSV')
        channels = img.split()
        
        # 确保有3个通道
        if len(channels) != 3:
            print(f"Warning: Expected 3 channels, got {len(channels)}")
            return image
            
        h, s, v = channels

        # 将色相偏移应用到H通道
        h_data = np.array(h)
        h_data = (h_data + int(shift * 255)) % 255
        h_new = Image.fromarray(h_data.astype('uint8'), 'L')

        # 确保所有通道都是正确的模式
        if h_new.mode != 'L':
            h_new = h_new.convert('L')
        if s.mode != 'L':
            s = s.convert('L')
        if v.mode != 'L':
            v = v.convert('L')

        merged = Image.merge('HSV', (h_new, s, v))
        return merged.convert('RGB')
    except Exception as e:
        print(f"Error in adjust_hue: {e}")
        # 如果出错，返回原图
        return image


def adjust_sharpness(image, factor):
    """
    调整图像锐度
    :param image: PIL图像对象
    :param factor: 锐化系数 (0.0-5.0)
        - 0.0 = 模糊图像
        - 1.0 = 原始锐度
        - 2.0 = 明显锐化
        - 5.0 = 过度锐化
    """
    factor = float(factor)
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(factor)


def adjust_blur(image, radius):
    """
    应用高斯模糊
    :param image: PIL图像对象
    :param radius: 模糊半径 (0.0-20.0)
        - 0.0 = 无模糊
        - 1.0 = 轻微模糊
        - 5.0 = 中等模糊
        - 20.0 = 重度模糊
    """
    radius = float(radius)
    return image.filter(ImageFilter.GaussianBlur(radius))


# 使用示例
if __name__ == "__main__":
    img = Image.open("img4.jpg")

    bright_img = adjust_brightness(img, 2.0)
    bright_img.save("bright.jpg")

    low_contrast_img = adjust_contrast(img, 2.0)

    # 增强饱和度 (增加到2.0倍)
    saturated_img = adjust_saturation(img, 2.0)

    # 色相偏移 (120°变化)
    hue_shifted_img = adjust_hue(img, 0.33)

    # 锐化图像 (增强2.5倍)
    sharp_img = adjust_sharpness(img, 2.5)

    # 应用模糊 (半径3.0)
    blurred_img = adjust_blur(img, 3.0)