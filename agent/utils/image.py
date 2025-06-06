import os
import base64


# 新增函数：批量读取文件夹内的图片
def batch_read_images(folder_path: str) -> list[str]:
    """
    递归读取指定文件夹内的所有图片文件路径。

    :param folder_path: 文件夹路径
    :return: 包含图片文件路径的列表
    """
    image_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_paths.append(os.path.join(root, file))
    return image_paths


# 新增函数：批量将图片转换为 Base64 格式
def batch_convert_to_base64(image_paths: list[str]) -> list[str]:
    """
    将图片文件路径列表批量转换为 Base64 编码字符串。

    :param image_paths: 图片文件路径列表
    :return: 包含 Base64 编码字符串的列表
    """
    base64_images = []
    for image_path in image_paths:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode("utf-8")
            base64_images.append({"image_path": image_path, "base64_image": base64_image})
    return base64_images


# 新增函数：将单个图片转换为 Base64 格式（兼容性函数）
def convert_single_image_to_base64(image_path: str) -> str:
    """
    将单个图片文件转换为 Base64 编码字符串。

    :param image_path: 图片文件路径
    :return: Base64 编码字符串
    """
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        return base64.b64encode(image_data).decode("utf-8")


# 示例：使用上述函数进行批量处理
if __name__ == "__main__":
    folder_path = "path/to/your/images"  # 替换为实际的图片文件夹路径
    image_paths = batch_read_images(folder_path)
    base64_images = batch_convert_to_base64(image_paths)
    print(f"Total {len(base64_images)} images converted to Base64.")
