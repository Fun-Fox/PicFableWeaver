import os
import sqlite3
from typing import List, Tuple
import threading

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DatabaseManager:
    def __init__(self, db_path: str = os.path.join(root_dir, 'db/image_database.db')):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.local = threading.local()  # 每个线程拥有自己的连接

    def connect(self):
        """连接到SQLite数据库"""
        if not self.conn or self.conn.closed:
            self.conn  = self._get_connection()
            self.cursor = self.conn.cursor()

    def _get_connection(self):
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.local.conn

    def close(self):
        """关闭数据库连接"""
        if self.conn and not self.conn.closed:
            self.conn.close()

    def create_image_info_table(self):
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

    def insert_image_info(self, image_name: str, image_path: str, image_description: str, lens: str, composition: str,
                          visual_style: str) -> int:
        """插入图片信息，并返回插入记录的ID"""
        self.cursor.execute('''
            INSERT INTO image_info (image_name, image_path, image_description, lens, composition, visual_style)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (image_name, image_path, image_description, lens, composition, visual_style))
        self.conn.commit()
        # 返回最后插入记录的ID
        return self.cursor.lastrowid

    def is_image_path_exists(self, image_path: str) -> bool:
        """检查指定的 image_path 是否存在于数据库中"""
        self.cursor.execute('SELECT 1 FROM image_info WHERE image_path = ?', (image_path,))
        result = self.cursor.fetchone()
        return result is not None

    def get_all_image_info(self, id_list: list = None) -> list:
        """获取指定ID列表的图片信息，如果id_list为空则获取所有图片"""

        if id_list and isinstance(id_list, list) and len(id_list) > 0:
            # 构建带IN查询的SQL语句
            query = f"SELECT * FROM image_info WHERE id IN ({','.join('?' * len(id_list))})"
            self.cursor.execute(query, id_list)
        else:
            self.cursor.execute("SELECT * FROM image_info")

        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_image_info_by_id(self, image_id: int) -> Tuple:
        """根据ID获取图片信息"""
        self.cursor.execute('SELECT * FROM image_info WHERE id = ?', (image_id,))
        return self.cursor.fetchone()

    # 新增函数：获取所有图片ID
    def get_all_image_ids(self) -> List[int]:
        """获取所有图片的ID"""
        self.cursor.execute('SELECT id FROM image_info')
        return [row[0] for row in self.cursor.fetchall()]

    def update_image_info(self, image_id: int, image_name: str = None, image_path: str = None,
                          image_description: str = None, lens: str = None, composition: str = None,
                          visual_style: str = None):
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

    # ==== 剧本及分镜 ===
    def create_script_table(self):
        """创建剧本与分镜信息表"""
        self.cursor.execute('''
               CREATE TABLE IF NOT EXISTS script_scene_info (
                   scene_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   story_theme TEXT,
                   plot_summary TEXT,
                   key_plot_points TEXT,
                   emotional_tone TEXT,
                   background_music_prompt TEXT,

                   scene_number TEXT,
                   image_id INTEGER,
                   camera_movement TEXT,
                   subject_action TEXT,
                   transition_effect TEXT,
                   image_to_video_prompt TEXT,
                   narration_subtitle TEXT,

                   script_id TEXT NOT NULL
               )
           ''')
        self.conn.commit()

    def insert_script_scene_info(self, script_data: dict):
        """插入剧本与分镜信息"""
        script_id = script_data.get("script_id")
        scenes = script_data.get("scenes", [])
        story_theme = script_data.get("story_theme")
        plot_summary = script_data.get("plot_summary")
        key_plot_points = script_data.get("key_plot_points")
        emotional_tone = script_data.get("emotional_tone")
        background_music_prompt = script_data.get("background_music_prompt")

        for scene in scenes:
            scene_number = scene.get("scene_number")
            image_id = scene.get("image_id")
            camera_movement = scene.get("camera_movement")
            subject_action = scene.get("subject_action")
            transition_effect = scene.get("transition_effect")
            image_to_video_prompt = scene.get("image_to_video_prompt")
            narration_subtitle = scene.get("narration_subtitle")

            self.cursor.execute('''
                INSERT INTO script_scene_info (
                    story_theme, plot_summary, key_plot_points, emotional_tone,
                    background_music_prompt, scene_number, image_id,
                    camera_movement, subject_action, transition_effect,
                    image_to_video_prompt, narration_subtitle, script_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                story_theme, plot_summary, key_plot_points, emotional_tone,
                background_music_prompt, scene_number, image_id,
                camera_movement, subject_action, transition_effect,
                image_to_video_prompt, narration_subtitle, script_id
            ))
        self.conn.commit()

    def get_all_script_scene_lists(self) -> dict:
        """获取所有剧本与分镜信息，按 script_id 分组"""
        self.cursor.execute('SELECT * FROM script_scene_info')
        rows = self.cursor.fetchall()

        scripts = {}
        for row in rows:
            scene_data = {
                "scene_id": row[0],
                "story_theme": row[1],
                "plot_summary": row[2],
                "key_plot_points": row[3],
                "emotional_tone": row[4],
                "background_music_prompt": row[5],
                "scene_number": row[6],
                "image_id": row[7],
                "camera_movement": row[8],
                "subject_action": row[9],
                "transition_effect": row[10],
                "image_to_video_prompt": row[11],
                "narration_subtitle": row[12]
            }
            script_id = row[13]
            if script_id not in scripts:
                scripts[script_id] = []
            scripts[script_id].append(scene_data)
        return scripts

    def get_script_by_script_id(self, script_id: str) -> dict:
        """根据 script_id 获取完整的剧本与分镜信息"""
        self.cursor.execute('''
               SELECT * FROM script_scene_info WHERE script_id = ?
           ''', (script_id,))
        rows = self.cursor.fetchall()

        if not rows:
            return {}

        scenes = []
        base_info = {
            "story_theme": rows[0][1],
            "plot_summary": rows[0][2],
            "key_plot_points": rows[0][3],
            "emotional_tone": rows[0][4],
            "background_music_prompt": rows[0][5]
        }

        for row in rows:
            scenes.append({
                "scene_id": row[0],
                "scene_number": row[6],
                "image_id": row[7],
                "camera_movement": row[8],
                "subject_action": row[9],
                "transition_effect": row[10],
                "image_to_video_prompt": row[11],
                "narration_subtitle": row[12]
            })

        return {
            **base_info,
            "scenes": scenes
        }

    def get_all_script_ids_with_theme(self) -> List[dict]:
        """获取所有剧本ID及其主题"""
        self.cursor.execute('''
            SELECT DISTINCT script_id, story_theme 
            FROM script_scene_info
        ''')
        rows = self.cursor.fetchall()

        return [
            {
                "script_id": row[0],
                "story_theme": row[1]
            }
            for row in rows
        ]


