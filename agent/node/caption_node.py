import os.path
import time
from time import sleep

from loguru import logger
from pocketflow import Node

from agent.tools.image_desc_structure import analyze_image_structure
from agent.utils.image import batch_read_images, batch_convert_to_base64
from agent.mcp_client import mcp_call_tool
from database.db_manager import DatabaseManager
from database.image_manager import ImageDBManager


def extract_sections(text):
    # 分割文本为多个部分
    parts = text.split("\n\n")

    # 初始化变量存储结果
    user_content = ""
    assistant_content = ""
    result_content = ""

    # 提取 user 和 system 内容
    for part in parts:
        if "user" in part:
            user_content = part.replace("user", "").strip()
        elif "assistant" in part:
            assistant_content = part.replace("assistant", "").strip()
        else:
            result_content = part.replace("", "").strip()
    logger.info(f"用户内容：{user_content}")
    logger.info(f"助手内容：{assistant_content}")
    logger.info(f"结果内容：{result_content}")
    return user_content, assistant_content, result_content


class ImageCaptionNode(Node):
    """
    图片标注、反推描述
    """

    def prep(self, shared):
        """Prepare tool execution parameters"""
        return shared["image_dir"],shared["db_path"]

    def exec(self, input):
        """Execute the chosen tool"""
        image_dir,db_path=input
        logger.info(f"开始执行图片描述任务")
        image_paths = batch_read_images(image_dir)
        logger.info(f"图片数量：{len(image_paths)}")

        image_base64_list = batch_convert_to_base64(image_paths)

        tool_name = "generate_image_caption"
        image_descriptions = []
        db_manager = DatabaseManager(db_path=db_path)
        db_manager.connect()
        for idx, item in enumerate(image_base64_list):
            parameters = {
                "image_base64": item["base64_image"]
            }
            start_time = time.time()

            image_path = item['image_path']

            if db_manager.is_image_path_exists(image_path):
                logger.info(f"`{image_path}` 存在于数据库中,不做识别更新。")
                continue
            else:
                logger.info(f"`{image_path}` 不存在于数据库中。")

            result = mcp_call_tool(tool_name, parameters)
            _, _, image_desc = extract_sections(result)

            file_name = os.path.basename(image_path)
            # sleep(10)
            image_descriptions.append({
                'image_path': image_path,
                "image_name": file_name,
                "image_desc": image_desc
            })
            end_time = time.time()
            duration_time = (end_time - start_time) / 1000
            logger.info(f"第{idx}张图，图片文件名称：{file_name}，\n 图片描述：{image_desc}，\n 耗时：{duration_time}s")
        db_manager.close()
        return image_descriptions

    def post(self, shared, prep_res, exec_res):
        image_descriptions = exec_res
        db = DatabaseManager()
        db.connect()

        image_db = ImageDBManager(db)
        image_info_list = []
        for item in image_descriptions:
            image_id = image_db.process_and_store_image(item['image_name'], item['image_path'],item['image_desc'],
                                                        lens="",
                                                        composition="", visual_style="")
            image_info_list.append({
                'image_id': image_id,
                'image_path': item['image_path'],
                'image_name': item['image_name'],
                'image_desc': item['image_desc']
            })
        shared['image_info_list'] = image_info_list
        db.close()
        return "desc"


class ImageDescStructNode(Node):
    """
    图片描述格式化，更新数据库
    """

    def prep(self, shared):
        """Prepare tool execution parameters"""
        return shared["image_info_list"]

    def exec(self, image_info_list):
        for item in image_info_list:
            lens, composition, visual_style = analyze_image_structure(item['image_desc'])

            item['lens'] = lens
            item['composition'] = composition
            item['visual_style'] = visual_style
            logger.info(f"镜头：{lens}\n 图片结构：{composition}\n 视觉风格：{visual_style}")
        return image_info_list

    def post(self, shared, prep_res, exec_res):
        image_info_list = exec_res
        db = DatabaseManager()
        db.connect()
        image_db = ImageDBManager(db)
        for item in image_info_list:
            image_db.update_processed_image(item['image_id'], item['image_name'],item['image_path'],
                                            item['image_desc'],
                                            lens=item['lens'],
                                            composition=item['composition'],
                                            visual_style=item['visual_style'])
        db.close()
        return "finish"
