import sqlite3
from typing import List, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = 'image_database.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """连接到SQLite数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

    def create_table(self):
        """创建图片信息表"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_name TEXT NOT NULL,
                image_path TEXT NOT NULL,
                image_description TEXT,
                lens TEXT,
                composition TEXT,
                visual_style TEXT
            )
        ''')
        self.conn.commit()

    def insert_image_info(self, image_name: str, image_path: str, image_description: str, lens: str, composition: str, visual_style: str):
        """插入图片信息"""
        self.cursor.execute('''
            INSERT INTO image_info (image_name, image_path, image_description, lens, composition, visual_style)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (image_name, image_path, image_description, lens, composition, visual_style))
        self.conn.commit()

    def get_all_image_info(self) -> List[Tuple]:
        """获取所有图片信息"""
        self.cursor.execute('SELECT * FROM image_info')
        return self.cursor.fetchall()

    def get_image_info_by_id(self, image_id: int) -> Tuple:
        """根据ID获取图片信息"""
        self.cursor.execute('SELECT * FROM image_info WHERE id = ?', (image_id,))
        return self.cursor.fetchone()

    def update_image_info(self, image_id: int, image_name: str = None, image_path: str = None, image_description: str = None, lens: str = None, composition: str = None, visual_style: str = None):
        """更新图片信息"""
        update_fields = []
        update_values = []
        if image_name:
            update_fields.append('image_name = ?')
            update_values.append(image_name)
        if image_path:
            update_fields.append('image_path = ?')
            update_values.append(image_path)
        if image_description:
            update_fields.append('image_description = ?')
            update_values.append(image_description)
        if lens:
            update_fields.append('lens = ?')
            update_values.append(lens)
        if composition:
            update_fields.append('composition = ?')
            update_values.append(composition)
        if visual_style:
            update_fields.append('visual_style = ?')
            update_values.append(visual_style)
        
        if update_fields:
            query = f"UPDATE image_info SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(image_id)
            self.cursor.execute(query, tuple(update_values))
            self.conn.commit()

    def delete_image_info(self, image_id: int):
        """删除图片信息"""
        self.cursor.execute('DELETE FROM image_info WHERE id = ?', (image_id,))
        self.conn.commit()


class ImageProcessingManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def process_and_store_image(self, image_name: str, image_path: str, image_description: str, lens: str, composition: str, visual_style: str):
        """处理并存储图片信息"""
        self.db_manager.insert_image_info(image_name, image_path, image_description, lens, composition, visual_style)

    def get_all_processed_images(self) -> List[Tuple]:
        """获取所有已处理的图片信息"""
        return self.db_manager.get_all_image_info()

    def get_processed_image_by_id(self, image_id: int) -> Tuple:
        """根据ID获取已处理的图片信息"""
        return self.db_manager.get_image_info_by_id(image_id)

    def update_processed_image(self, image_id: int, image_name: str = None, image_path: str = None, image_description: str = None, lens: str = None, composition: str = None, visual_style: str = None):
        """更新已处理的图片信息"""
        self.db_manager.update_image_info(image_id, image_name, image_path, image_description, lens, composition, visual_style)

    def delete_processed_image(self, image_id: int):
        """删除已处理的图片信息"""
        self.db_manager.delete_image_info(image_id)