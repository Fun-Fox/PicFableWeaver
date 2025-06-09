from pocketflow import Node
import yaml

from agent.utils.call_llm import call_llm
from loguru import logger

from database.db_manager import DatabaseManager
from database.image_manager import ImageDBManager


class PicWeaverNode(Node):
    def prep(self, shared):
        """Prepare tool execution parameters"""
        db_path = shared["db_path"]
        image_id_list = shared["image_id_list"]
        db = DatabaseManager(db_path=db_path)
        db.connect()
        image_db = ImageDBManager(db)
        image_info_list = image_db.get_all_processed_images(image_id_list)

        return image_info_list

    def exec(self, image_info_list):
        """Execute the chosen tool"""

        prompt = """你是一位专业的影视编剧，请基于以下图片信息，为一部科幻动画短片撰写完整的剧本与分镜脚本。

## 创作要求
1. 从提供的图片中选择3~5张最具表现力的画面进行创作。
2. 故事梗概需控制在150-200字之间，需包含主题、关键转折点、情感基调。
3. 每个分镜对应一张图片，包含镜头、构图、视觉风格、运镜方式、主体动作、转场效果等内容。
4. 输出格式为严格的YAML格式，使用|符号表示多行字段，缩进为4个空格。
5. 不得出现冒号: 或Markdown语法。

## 输出格式

```yaml
story_theme: |
    <故事主题>
plot_summary: |
    <150-200字的故事梗概>
key_plot_points: |
    <关键转折点>
emotional_tone: |
    <情感基调>
background_music_prompt: | 
    <AI生背景音乐的推荐提示词>

scenes:
  - scene_number: Scene 1
    image_id: <图片ID>
    camera_movement: |
        <运镜方式>
    subject_action: |
        <主体动作>
    transition_effect: |
        <转场效果建议>
    image_to_video_prompt: |
        <图生视频推荐提示词>
    narration_subtitle: | 
        <该画面的旁白字幕内容>
```
注意：你将看到多张图像，这些图像可能包含关键人物、场景或情绪线索，请结合图像内容进行剧本创作。

## 图片素材

"""
        for item in image_info_list:
            prompt += f"""
### 图片ID: {item["id"]}

镜头：{item['lens']}
构图：{item['composition']}
视觉风格：{item['visual_style']}
"""
        logger.info(prompt)
        result, success = call_llm(prompt)

        if success:
            yaml_str = result.split("```yaml")[1].split("```")[0].strip()
            logger.info(f"分析结果: {yaml_str}")
            analysis = yaml.safe_load(yaml_str)
            return analysis
        else:
            return "无法生成分析结果，请稍后再试。"

    def post(self, shared, prep_res, exec_res):
        if isinstance(exec_res, dict) and "scenes" in exec_res:
            db_path = shared.get("db_path")
            db = DatabaseManager(db_path=db_path)
            db.connect()
            db.create_script_table()  # 创建或确保剧本表存在

            # 设置唯一脚本ID（如时间戳）
            import time
            script_id = f"script_{int(time.time())}"
            exec_res["script_id"] = script_id

            # 插入剧本与分镜数据
            db.insert_script_scene_info(exec_res)

            db.close()
            logger.info("剧本与分镜信息已成功保存。")
            return "done"
        else:
            logger.warning("无法识别剧本格式，未执行保存。")
            return "failed"
        return "done"
