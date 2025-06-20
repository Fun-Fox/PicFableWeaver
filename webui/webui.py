import os
import gradio as gr
import pandas as pd

from agent.agent_start import caption_flow, weaver_flow
from agent.flow.weaver_flow import i2v_flow
from database.db_manager import DatabaseManager

# 初始化数据库管理器
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db/image_database.db')
db_manager = DatabaseManager(db_path)
db_manager.connect()  # 确保连接已建立
db_manager.create_script_table()  # 创建或确保剧本表存在
db_manager.create_image_info_table()

def run_caption_flow(image_dir):
    """运行 caption_flow 并返回结果"""
    caption_flow(image_dir, db_path)
    return "Caption Flow 执行完成！"


def run_i2v_flow(selected_ids):
    """运行 weaver_flow 并返回结果"""
    i2v_flow(script_id=selected_ids, db_path=db_path)
    return f"i2v_flow执行完成！选择的剧本 ID: {selected_ids}"

def run_weaver_flow(selected_ids):
    """运行 weaver_flow 并返回结果"""
    weaver_flow(image_id_list=selected_ids, db_path=db_path)
    return f"Weaver Flow 执行完成！选择的图片 ID: {selected_ids}"
def get_all_image_info():
    """获取所有图片信息"""
    image_info = db_manager.get_all_image_info()
    return "\n".join([f"ID: {info['id']}, Name: {info['image_name']}" for info in image_info])


def get_script_ids_and_themes():
    """获取所有剧本 ID 及其主题"""
    scripts = db_manager.get_all_script_ids_with_theme()
    return {script["script_id"]: script["story_theme"] for script in scripts}


def get_script_details(script_id):
    """根据剧本 ID 获取剧本详细信息和分镜信息"""
    script_data = db_manager.get_script_by_script_id(script_id)
    if not script_data:
        return "未找到对应的剧本信息！"

    # 剧本基础信息（文本展示）
    base_info = f"""
    **剧本主题**: 
    
        {script_data['story_theme']}
    
    **剧情概要**: 
    
        {script_data['plot_summary']}
    
    **情感基调**: 
    
        {script_data['emotional_tone']}
    
    **背景音乐风格标签**: 
    
        {script_data['tags']}
        
    **背景音乐歌词**: 
    
        {script_data['lyrics']}
    
    """

    # 分镜信息（表格展示）
    scenes = script_data["scenes"]
    table_data = [
        [
            scene["scene_number"],
            scene["image_id"],
            scene["camera_movement"],
            scene["subject_action"],
            scene["transition_effect"],
            scene["image_to_video_prompt"],
            scene["narration_subtitle"]
        ]
        for scene in scenes
    ]
    df_table_data = pd.DataFrame(table_data, columns=[
        "分镜编号", "图片ID", "镜头运动", "主体动作", "转场效果", "图生视频提示", "旁白字幕"
    ])

    return [
        gr.Markdown(value=base_info, label="主题"),
        gr.Dataframe(
            label="分镜",
            value=df_table_data,
            wrap=True,
            column_widths=[1, 1, 2, 2, 2, 4, 3]
        )
    ]


# 创建 Gradio Web UI
with gr.Blocks() as demo:
    gr.Markdown("# 图片内容反推->构建剧本->查看剧本->图生视频->生音频->合成视频")
    # Tab1: 图片内容反推及识别 📂➡️🖼️
    with gr.Tab("图片内容识别"):
        # 说明：输入图片文件夹路径并执行 Caption Flow
        image_dir_input = gr.Text(label="图片文件夹路径",
                                  value=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                     "example"))
        run_button = gr.Button("执行图片识别")
        output_text = gr.Textbox(label="执行结果")

        run_button.click(run_caption_flow, inputs=image_dir_input, outputs=output_text)

    # Tab2: 展示所有 image_info 📸🔍
    with gr.Tab("选择图片->构建剧本"):
        # 说明：展示所有图片信息并选择图片ID来执行 Weaver Flow
        def update_image_info():
            image_info = db_manager.get_all_image_info()
            # 返回 pandas DataFrame 以适配 gr.Dataframe
            return pd.DataFrame({
                "ID": [info['id'] for info in image_info],
                "图片描述": [info['image_description'] for info in image_info],
                "图片存储位置": [info['image_name'] for info in image_info]
            })


        image_info_output = gr.Dataframe(
            headers=["ID", "图片描述", "图片存储位置"],
            value=update_image_info(),
            label="已完成返回的图片信息展示",
            column_widths=[1, 20, 5],
            wrap=True
        )


        # 优化：动态更新CheckboxGroup的choices
        def get_image_id_list():
            image_info = db_manager.get_all_image_info()
            choices = [str(info["id"]) for info in image_info]
            return choices


        image_id_checkboxes = gr.CheckboxGroup(choices=get_image_id_list(), label="选择剧本可能使用到的图片(ID)",
                                               interactive=True)  # 确保为交互式
        run_weaver_button = gr.Button("执行构建剧本")
        weaver_output = gr.Textbox(label="执行结果")

        run_weaver_button.click(run_weaver_flow, inputs=image_id_checkboxes, outputs=weaver_output)

    # Tab3: 查看剧本信息 📖🔍
    with gr.Tab("查看剧本"):
        # 说明：选择剧本ID来查看详细信息
        def get_script_dropdown():
            script_ids = get_script_ids_and_themes()
            return list(script_ids.keys())

        script_dropdown = gr.Dropdown(choices=[''] + get_script_dropdown(), label="选择剧本 ID")

        # 新增按钮
        generate_video_button = gr.Button("生成视频", variant="primary")


        script_details_output = [
            gr.Markdown(label="剧本"),
            gr.Dataframe(label="分镜详情")
        ]

        # 输出区域（可选）
        video_result_output = gr.Textbox(label="视频生成结果")

        script_dropdown.change(get_script_details, inputs=script_dropdown, outputs=script_details_output)

        # 按钮点击事件
        generate_video_button.click(
            fn=run_i2v_flow,
            inputs=script_dropdown,
            outputs=video_result_output
        )

# 启动 Gradio Web UI
if __name__ == "__main__":
    demo.launch()
