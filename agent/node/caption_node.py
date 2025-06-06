import os.path
from time import sleep

from pocketflow import Node

from agent.tools.image_desc_analysis import analyze_image_description
from agent.utils.db import DatabaseManager, ImageDBManager
from agent.utils.image import batch_read_images, batch_convert_to_base64
from agent.utils.mcp_client import mcp_call_tool


class ImageCaptionNode(Node):
    def prep(self, shared):
        """Prepare tool execution parameters"""
        return shared["image_dir"]

    def exec(self, image_dir):
        """Execute the chosen tool"""

        image_paths = batch_read_images(image_dir)

        image_base64_list = batch_convert_to_base64(image_paths)

        tool_name = "caption_generate_image_caption"
        image_descriptions = []
        for idx, item in enumerate(image_base64_list):
            parameters = {
                "image_base64": item["base64_image"]
            }
            image_desc = mcp_call_tool(tool_name, parameters)
            sleep(10)
            image_path = item['image_path']
            file_name = os.path.basename(image_path)
            image_descriptions.append({
                'image_path': image_path,
                "image_name": file_name,
                "image_desc": image_desc
            })



            return image_descriptions

    def post(self, shared, prep_res, exec_res):
        image_descriptions = exec_res
        db = DatabaseManager()
        db.connect()
        image_db = ImageDBManager(db)
        image_info_list = []
        for item in image_descriptions:
            lens, composition, visual_style = analyze_image_description(item['image_desc'])
            image_id = image_db.process_and_store_image(item['image_path'], item['image_name'], item['image_desc'],
                                                        lens=lens,
                                                        composition=composition, visual_style=visual_style)
            image_info_list.append({
                'image_id': image_id,
                'image_path': item['image_path'],
                'image_name': item['image_name'],
                'image_desc': item['image_desc'],
                'lens': lens,
                'composition': composition,
                'visual_style': visual_style
            })
        shared['image_info_list'] = image_info_list
        db.close()
        return "desc"
