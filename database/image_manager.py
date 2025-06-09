import os
import sqlite3
from typing import List, Tuple

from database.db_manager import DatabaseManager

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ImageDBManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def process_and_store_image(self, image_name: str, image_path: str, image_description: str, lens: str = "",
                                composition: str = "", visual_style: str = ""):
        """处理并存储图片信息"""
        image_id = self.db_manager.insert_image_info(image_name, image_path, image_description, lens, composition,
                                                     visual_style)
        return image_id

    def get_all_processed_images(self,image_id_list) -> List[Tuple]:
        """获取所有已处理的图片信息"""
        return self.db_manager.get_all_image_info(image_id_list)

    def get_processed_image_by_id(self, image_id: int) -> Tuple:
        """根据ID获取已处理的图片信息"""
        return self.db_manager.get_image_info_by_id(image_id)

    def update_processed_image(self, image_id: int, image_name: str = None, image_path: str = None,
                               image_description: str = None, lens: str = None, composition: str = None,
                               visual_style: str = None):
        """更新已处理的图片信息"""
        self.db_manager.update_image_info(image_id, image_name, image_path, image_description, lens, composition,
                                          visual_style)

    def delete_processed_image(self, image_id: int):
        """删除已处理的图片信息"""
        self.db_manager.delete_image_info(image_id)