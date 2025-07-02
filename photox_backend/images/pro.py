import cv2
import numpy as np
from PIL import Image, ImageEnhance
from skimage import restoration, color
import os

def enhance_image(image_path, output_path, brightness=1.2, contrast=1.2, sharpness=1.5):
    """图像增强：调整亮度、对比度和锐度"""
    img = Image.open(image_path)

    # 亮度增强
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness)

    # 对比度增强
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast)

    # 锐度增强
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(sharpness)
    img.save(output_path)
    print(f"图像增强完成，结果保存至: {output_path}")


def super_resolution(image_path, output_path, scale=2):
    """超分辨率重建（ESPCN模型）"""
    # 下载预训练模型 (首次使用会自动下载)
    model_path = f"ESPCN_x{scale}.pb"
    model_url = f"https://github.com/fannymonori/TF-ESPCN/raw/master/export/ESPCN_x{scale}.pb"

    import os
    if not os.path.exists(model_path):
        import urllib.request
        print("正在下载超分辨率模型...")
        urllib.request.urlretrieve(model_url, model_path)

    # 初始化超分辨率模型
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(model_path)
    sr.setModel("espcn", scale)  # 使用ESPCN算法

    # 处理图像，兼容中文路径
    from PIL import Image
    import numpy as np
    try:
        img = np.array(Image.open(image_path))
        # PIL是RGB，OpenCV需要BGR
        if img.ndim == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.ndim == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
    except Exception as e:
        raise ValueError(f"无法读取图片: {image_path}, 错误: {e}")
    print(f"原图尺寸: {img.shape}")
    result = sr.upsample(img)
    print(f"超分后尺寸: {result.shape}")
    # 直接写入output_path
    success = cv2.imwrite(output_path, result)
    if success:
        from PIL import Image
        with Image.open(output_path) as check_img:
            pass
    else:
        pass
    print(f"超分辨率完成 (x{scale})，结果保存至: {output_path}")


def denoise_image(image_path, output_path, method="nlm", strength=10):
    from PIL import Image
    import numpy as np
    from skimage import restoration
    import cv2

    try:
        img = np.array(Image.open(image_path))
        # OpenCV 默认是BGR，PIL是RGB，这里转成BGR以兼容OpenCV处理
        if img.ndim == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif img.ndim == 2:
            pass  # 灰度图
        elif img.ndim == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
    except Exception as e:
        raise ValueError(f"无法读取图片: {image_path}, 错误: {e}")

    if method == "nlm":
        # 保证为3通道（BGR）或4通道（BGRA）
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        img = img.astype('uint8')
        denoised = cv2.fastNlMeansDenoisingColored(img, None, strength, strength, 7, 21)
    elif method == "wavelet":
        img_float = img.astype(np.float32) / 255.0
        denoised = restoration.denoise_wavelet(
            img_float,
            channel_axis=-1,
            convert2ycbcr=True,
            rescale_sigma=True
        )
        denoised = np.clip(denoised * 255, 0, 255).astype(np.uint8)
    else:
        raise ValueError("Unsupported denoising method")

    cv2.imwrite(output_path, denoised)
    print(f"保存处理后图片到: {output_path}, 存在: {os.path.exists(output_path)}")
    print(f"图像降噪完成 ({method})，结果保存至: {output_path}")


def color_enhance_image(image_path, output_path, factor=1.5):
    """色彩增强：提升图片色彩饱和度，兼容中文路径和多种图片格式"""
    from PIL import Image, ImageEnhance
    import os
    try:
        img = Image.open(image_path)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(factor)
        # 保持原图格式，修正JPG为JPEG
        img_format = img.format if img.format else os.path.splitext(output_path)[-1][1:].upper()
        if img_format and img_format.upper() == 'JPG':
            img_format = 'JPEG'
        img.save(output_path, format=img_format)
    except Exception as e:
        raise ValueError(f"无法处理图片: {image_path}, 错误: {e}")

# 使用示例
if __name__ == "__main__":
    input_image = "img4.jpg"

    # 图像增强
    enhance_image(input_image,
                  "enhanced.jpg",
                  brightness=1.3,
                  contrast=1.2,
                  sharpness=1.8)

    # 超分辨率 (2倍放大)
    super_resolution(input_image, "super_resolution.jpg", scale=2)

    # 图像降噪
    denoise_image(input_image, "denoised_nlm.jpg", method="nlm", strength=15)
    denoise_image(input_image, "denoised_wavelet.jpg", method="wavelet")

    # 色彩增强
    color_enhance_image(input_image, "color_enhanced.jpg", factor=1.5)