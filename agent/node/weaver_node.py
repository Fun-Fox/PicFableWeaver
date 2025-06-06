from pocketflow import Node

from agent.utils.call_llm import call_local_llm


class PicWeaverNode(Node):
    def prep(self, shared):
        """Prepare tool execution parameters"""
        return shared["image_info_list"]

    def exec(self, image_info_list):
        """Execute the chosen tool"""
        prompt = """请根据以下图片描述创作一个创意短片方案，包含剧本和分镜两大部分：

## 剧本创作要求：
1. 从提供的图片中选择3-5张最具表现力的图片进行创作
2. 生成一个连贯的故事梗概（150-200字）
3. 需包含：故事主题、关键转折点、情感基调

## 分镜规范：
对每个选中的图片生成对应的分镜描述，每个分镜必须包含：
1. 分镜编号（Scene 1, Scene 2...）
2. 场景描述：基于图片的镜头(lens)、构图(composition)、视觉风格(visual_style)
3. 运镜描述：包含镜头运动方式（推拉摇移等）
4. 主体动作：描述画面主体的动态表现
5. 图片ID：对应原始图片的ID

## 特别要求：
- 使用Markdown格式返回结果
- 保持语言的艺术性和创造性
- 每个分镜描述需要4-6个具体细节
- 增加转场效果建议

## 图片素材：
"""
        for item in image_info_list:
            prompt += f"""
### 图片ID: {item["image_id"]}
镜头：{item['lens']}
构图：{item['composition']}
视觉风格：{item['visual_style']}
"""

        result, success = call_local_llm(prompt)
        if success:
            print(result)
            return result
        else:
            return "无法生成分析结果，请稍后再试。"

    def post(self, shared, prep_res, exec_res):

        return "done"
