import os
import random
from PIL import Image

from image_caption_agent.mcp_server.main import generate_image_caption

if __name__ == "__main__":
    import triton

    print(triton.__version__)
    # 获取example目录下的所有图片文件
    # 修改：使用os.path.join和os.path.dirname确保路径的绝对性
    script_dir = os.path.dirname(os.path.abspath(__file__))

    example_dir = os.path.join(script_dir, "example")
    image_files = [f for f in os.listdir(example_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # 随机选择一个图片文件
    selected_image = random.choice(image_files)
    image_path = os.path.join(example_dir, selected_image)

    # 打开随机选择的图片
    image = Image.open(image_path)

    # 调用generate_image_caption函数
    # extra_options = [
    #     "包含有关照明的信息",
    #     "包含有关相机角度的信息",
    #     "指出景深和背景是否聚焦或模糊",
    #     "包含有关任何人物/角色年龄的信息（如果适用）",
    #     "提及图像描绘的是极端特写、特写、中景特写、中景、牛仔镜头、中景宽镜头、全景或极端全景。",
    #     "明确指定视角高度（眼平、低角虫眼、鸟瞰、无人机、屋顶等）。",
    #     "不要包含关于无法更改的人/角色的信息（如种族、性别等），但仍需包含可更改的属性（如发型）",
    #     "不要使用任何模棱两可的语言",
    #     "不要提及图像中的任何文本",
    #     "不要提及图像的分辨率",
    #     "你的回答将被用于文本到图像模型，因此避免使用无用的元短语，如“这张图片显示...”，“你正在看...”等。",
    # ]
    caption = generate_image_caption(image)
    print(caption)