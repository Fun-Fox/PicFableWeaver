import asyncio
import json

import websockets
from loguru import logger
from mcp.server.fastmcp import FastMCP
import torch
from contextlib import asynccontextmanager
from remote_caption_mcp_server.utils.fancyfeast_model import FancyFeastModel
from typing import AsyncIterator

# 使用单例模式加载模型
fancy_feast_model = FancyFeastModel()


class AppContext:
    def __init__(self, fancy_feast_model: FancyFeastModel):
        self.fancy_feast_client = fancy_feast_model


# 生命周期管理（占位符，供将来上下文支持使用）
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """管理应用程序生命周期"""
    logger.info("Starting MCP server lifecycle...")
    try:
        # 启动：未来可添加ComfyUI健康检查
        logger.info("图片返推模型已全局初始化")
        yield AppContext(fancy_feast_model=fancy_feast_model)
    finally:
        # 关闭：清理（如果需要）
        logger.info("正在关闭MCP服务器")


# 使用生命周期初始化FastMCP
mcp = FastMCP("Fancy_Feast_MCP_Server", lifespan=app_lifespan)


# 定义生成图像描述的工具函数
@mcp.tool()
def generate_image_caption(image_base64: str):
    """
    根据输入的Base64格式图像生成描述性文本或提示词。
    :param image_base64: Base64编码的图像数据
    :return: 生成的标题文本
    """
    logger.info("成功调用generate_image_caption")
    # 将Base64字符串解码为图像数据
    image = decode_base64_to_image(image_base64)
    logger.info("图片对象转换成功")
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
    logger.info("convo_string: {}", convo_string)
    # assert isinstance(convo_string, str)
    inputs = fancy_feast_model.get_processor()(text=[convo_string], images=[image], return_tensors="pt").to('cuda')
    inputs['pixel_values'] = inputs['pixel_values'].to(torch.bfloat16)

    # 生成输出
    logger.info("开始生成输出")
    outputs = fancy_feast_model.get_model().generate(**inputs, max_new_tokens=512, do_sample=True, temperature=0.6,
                                         top_p=0.9, use_cache=False, top_k=None)
    result = fancy_feast_model.get_processor().decode(outputs[0], skip_special_tokens=True)

    return {"result": result}


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


# WebSocket服务器
async def handle_websocket(websocket):
    logger.info("WebSocket客户端已连接")
    try:
        async for message in websocket:
            request = json.loads(message)
            logger.info(f"收到消息: {request}")
            if request.get("tool") == "generate_image_caption":
                result = generate_image_caption(request.get("image_base64", ""))
                await websocket.send(json.dumps(result))
            else:
                await websocket.send(json.dumps({"error": "未知工具"}))
    except websockets.ConnectionClosed:
        logger.info("WebSocket客户端已断开连接")


# 主服务器循环
async def main():
    logger.info("正在启动MCP服务器在 ws://0.0.0.0:9100...")
    async with websockets.serve(handle_websocket, "0.0.0.0", 9100):
        await asyncio.Future()  # 永远运行


if __name__ == "__main__":
    asyncio.run(main())
