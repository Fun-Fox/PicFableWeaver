import asyncio
import json

from pocketflow import Node
from loguru import logger

from agent.mcp_client import comfyui_mcp_server
from database.db_manager import DatabaseManager
from database.image_manager import ImageDBManager


class BatchI2VideoAndAudio(Node):

    def prep(self, shared):
        script_id = shared["script_id"]
        db_path = shared["db_path"]

        db = DatabaseManager(db_path= db_path)
        db.connect()
        image_db = ImageDBManager(db)

        script_data = db.get_script_by_script_id(script_id)

        scenes = script_data.get("scenes", [])
        lyrics = script_data.get("lyrics")
        tags = script_data.get("tags")

        result = []
        for scene in scenes:
            image_id = scene["image_id"]
            video_prompt = scene["image_to_video_prompt"]
            # 旁白
            narration_subtitle = scene["narration_subtitle"]

            # 获取图片路径
            image_info = image_db.get_processed_image_by_id(image_id)
            image_path = image_info[2] if image_info else None
            # print(image_path)

            result.append({
                "image_id": image_id,
                "image_path": image_path,
                "video_prompt": video_prompt,
                "narration_subtitle": narration_subtitle
            })

        db.close()

        return result, tags, lyrics

    def exec(self, input):
        result, tags, lyrics = input
        audio_workflow_id = "audio_ace_step_api"

        payload = {
            "tool": "generate_image_to_video",
            "params": json.dumps({
                "tags": tags,
                "lyrics": lyrics,
                "workflow_id": audio_workflow_id
            })
        }
        asyncio.run(comfyui_mcp_server(payload))

        i2v_workflow_id = "hy_image_to_video_api"

        for ret in result:
            image_path = ret["image_path"]
            prompt = ret["video_prompt"]
            payload = {
                "tool": "generate_image_to_video",
                "params": json.dumps({
                    "prompt": prompt,
                    "image_path": image_path,
                    "workflow_id": i2v_workflow_id
                })
            }
            asyncio.run(comfyui_mcp_server(payload))
        return "finish"

    def post(self, shared, prep_res, exec_res):

        return "finish"
