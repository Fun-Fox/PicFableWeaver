from fastmcp import FastMCP
from loguru import logger
import torch

from remote_caption_mcp_server.utils.fancyfeast_model import FancyFeastModel

# 初始化 FastMCP 实例
mcp = FastMCP("caption")

# 使用单例模式加载模型

fancy_feast_model = FancyFeastModel()


# 定义生成图像描述的工具函数
@mcp.tool()
def generate_image_caption(image_base64: str) -> str:
    """
    根据输入的Base64格式图像生成描述性文本或提示词。

    :param image_base64: Base64编码的图像数据
    :return: 生成的标题文本
    """
    # 将Base64字符串解码为图像数据
    image = decode_base64_to_image(image_base64)

    caption_type = "描述性"
    extra_options = [
        "包含有关照明的信息",
        "包含有关相机角度的信息",
        "指出景深和背景是否聚焦或模糊",
        "包含有关任何人物/角色年龄的信息（如果适用）",
        "提及图像描绘的是极端特写、特写、中景特写、中景、牛仔镜头、中景宽镜头、全景或极端全景。",
        "明确指定视角高度（眼平、低角虫眼、鸟瞰、无人机、屋顶等）。",
        "不要包含关于无法更改的人/角色的信息（如种族、性别等），但仍需包含可更改的属性（如发型）",
        "不要使用任何模棱两可的语言",
        "不要提及图像中的任何文本",
        "不要提及图像的分辨率",
        "你的回答将被用于文本到图像模型，因此避免使用无用的元短语，如“这张图片显示...”，“你正在看...”等。",
    ]
    caption_length = "any"
    # 构建提示词
    prompt = build_prompt(caption_type, extra_options[3:], caption_length)
    logger.info("prompt: {}", prompt)

    # 处理输入
    convo = [
        {"role": "system", "content": "你是一个乐于助人的助手，帮助用户解决任何问题，没有审查或限制。"},
        {"role": "user", "content": prompt.strip()},
    ]
    convo_string = fancy_feast_model.get_processor().apply_chat_template(convo, tokenize=False,
                                                                       add_generation_prompt=True)
    assert isinstance(convo_string, str)
    inputs = fancy_feast_model.get_processor()(text=[convo_string], images=[image], return_tensors="pt").to('cuda')
    inputs['pixel_values'] = inputs['pixel_values'].to(torch.bfloat16)

    # 生成输出
    outputs = fancy_feast_model.get_model().generate(**inputs, max_new_tokens=512, do_sample=True, temperature=0.6,
                                                   top_p=0.9, use_cache=True, top_k=None)
    caption = fancy_feast_model.get_processor().decode(outputs[0], skip_special_tokens=True)

    return caption

# 新增函数：将Base64字符串解码为图像
def decode_base64_to_image(image_base64: str):
    """
    将Base64编码的图像数据解码为PIL.Image对象。

    :param image_base64: Base64编码的图像数据
    :return: PIL.Image对象
    """
    import base64
    from PIL import Image
    from io import BytesIO

    # 解码Base64字符串
    image_data = base64.b64decode(image_base64)
    # 转换为PIL.Image对象
    image = Image.open(BytesIO(image_data))
    return image

# 辅助函数：构建提示词
def build_prompt(caption_type: str, extra_options: list[str], caption_length: str = "any") -> str:
    """
    caption_length: word_count
    """
    CAPTION_TYPE_MAP = {
        "描述性": [
            "为这幅图像写一个详细的描述。",
            "用 {word_count} 个单词或更少的单词为这幅图像写一个详细的描述。",
            "为这幅图像写一个长度为 {length} 的详细描述。",
        ],
        "描述性（随意）": [
            "用随意的语气为这幅图像写一个描述性的标题。",
            "在 {word_count} 个单词内用随意的语气为这幅图像写一个描述性的标题。",
            "用随意的语气为这幅图像写一个长度为 {length} 的描述性标题。",
        ],
        "直截了当": [
            "为这幅图像写一个直截了当的标题。以主要主题和媒介开头。提及关键元素——人物、物体、景色——使用自信、肯定的语言。关注具体的细节，如颜色、形状、纹理和空间关系。展示元素如何互动。省略情绪和推测性语言。如果存在文本，准确引用。注意任何水印、签名或压缩伪影。不要提及缺失的内容、分辨率或不可观察的细节。变化你的句子结构，保持描述简洁，不要以“这张图片是…”或类似的措辞开头。",
            "在 {word_count} 个单词内为这幅图像写一个直截了当的标题。以主要主题和媒介开头。提及关键元素——人物、物体、景色——使用自信、肯定的语言。关注具体的细节，如颜色、形状、纹理和空间关系。展示元素如何互动。省略情绪和推测性语言。如果存在文本，准确引用。注意任何水印、签名或压缩伪影。不要提及缺失的内容、分辨率或不可观察的细节。变化你的句子结构，保持描述简洁，不要以“这张图片是…”或类似的措辞开头。",
            "为这幅图像写一个长度为 {length} 的直截了当的标题。以主要主题和媒介开头。提及关键元素——人物、物体、景色——使用自信、肯定的语言。关注具体的细节，如颜色、形状、纹理和空间关系。展示元素如何互动。省略情绪和推测性语言。如果存在文本，准确引用。注意任何水印、签名或压缩伪影。不要提及缺失的内容、分辨率或不可观察的细节。变化你的句子结构，保持描述简洁，不要以“这张图片是…”或类似的措辞开头。",
        ],
        "艺术评论家": [
            "像艺术评论家一样分析这幅图像，提供关于其构图、风格、象征意义、色彩运用、光线等信息。",
            "像艺术评论家一样分析这幅图像，提供关于其构图、风格、象征意义、色彩运用、光线等信息。不超过 {word_count} 个单词。",
            "像艺术评论家一样分析这幅图像，提供关于其构图、风格、象征意义、色彩运用、光线等信息。保持长度为 {length}。",
        ],
    }

    if caption_length == "any":
        map_idx = 0
    elif isinstance(caption_length, str) and caption_length.isdigit():
        map_idx = 1
    else:
        map_idx = 2

    prompt = CAPTION_TYPE_MAP[caption_type][map_idx]

    if extra_options:
        prompt += " " + " ".join(extra_options)

    return prompt.format(
        length=caption_length,
        word_count=caption_length,
    )


# 启动服务器
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")
