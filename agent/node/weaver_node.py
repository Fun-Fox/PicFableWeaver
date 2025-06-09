from pocketflow import Node

from agent.utils.call_llm import call_local_llm
from loguru import logger

from agent.utils.db import DatabaseManager, ImageDBManager


class PicWeaverNode(Node):
    def prep(self, shared):
        """Prepare tool execution parameters"""
        db_path = shared["db_path"]
        db = DatabaseManager(db_path=db_path)
        db.connect()
        db.create_table()
        image_db = ImageDBManager(db)
        image_info_list = image_db.get_all_processed_images()

        return image_info_list

    def exec(self, image_info_list):
        """Execute the chosen tool"""

        prompt = """请根据以下图片描述创作一个创意短片方案，包含剧本和分镜两大部分：

## 剧本创作要求：

1. 从提供的图片中选择3-5张最具表现力的图片进行创作
2. 生成一个连贯的故事梗概（150-200字）
3. 需包含：故事主题、关键转折点、情感基调
4. 保持语言的艺术性和创造性

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

scenes:
  - scene_number: Scene 1
    image_id: <图片ID>
    lens: |
        <镜头描述>
    composition: |
        <构图描述>
    visual_style: |
        <视觉风格描述>
    camera_movement: |
        <运镜方式>
    subject_action: |
        <主体动作>
    transition_effect: |
        <转场效果建议>
```

## 重要：请确保：

- 顶层字段（如 story_theme, plot_summary）用于剧本部分
- scenes 列表 包含多个分镜描述Scene 1，Scene 2，Scene 3等等
- 每个分镜对应一张图片
- 使用中文描述
- 使用YAML格式返回响应
- 使用|字符表示多行文本字段
- 多行字段使用缩进（4个空格）
- 非键值对不允许随意使用冒号: 

## 图片素材：

"""
        for item in image_info_list:
            prompt += f"""
### 图片ID: {item["id"]}

镜头：{item['lens']}
构图：{item['composition']}
视觉风格：{item['visual_style']}
"""
        logger.info(prompt)
        result, success = call_local_llm(prompt)
        if success:
            print(result)
            return result
        else:
            return "无法生成分析结果，请稍后再试。"

    def post(self, shared, prep_res, exec_res):

        return "done"
