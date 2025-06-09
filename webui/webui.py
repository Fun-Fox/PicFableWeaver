import os
import gradio as gr
from agent.agent_start import caption_flow, weaver_flow
from database.db_manager import DatabaseManager

# 初始化数据库管理器
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db/image_database.db')
db_manager = DatabaseManager(db_path)

def run_caption_flow(image_dir):
    """运行 caption_flow 并返回结果"""
    caption_flow(image_dir, db_path)
    return "Caption Flow 执行完成！"

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
    scenes = "\n".join([f"Scene {scene['scene_number']}: {scene['narration_subtitle']}" for scene in script_data["scenes"]])
    return f"剧本主题: {script_data['story_theme']}\n分镜信息:\n{scenes}"

# 创建 Gradio Web UI
with gr.Blocks() as demo:
    # Tab1: 图片内容反推及识别
    with gr.Tab("图片内容反推及识别"):
        image_dir_input = gr.Text(label="图片文件夹路径", value=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "example"))
        run_button = gr.Button("执行 Caption Flow")
        output_text = gr.Textbox(label="执行结果")

        run_button.click(run_caption_flow, inputs=image_dir_input, outputs=output_text)

    # Tab2: 展示所有 image_info
    with gr.Tab("图片信息管理"):
        image_info_output = gr.Textbox(label="所有图片信息")
        image_id_checkboxes = gr.CheckboxGroup(choices=[], label="选择图片 ID")
        run_weaver_button = gr.Button("执行 Weaver Flow")
        weaver_output = gr.Textbox(label="执行结果")

        def update_image_info():
            image_info = db_manager.get_all_image_info()
            choices = [info["id"] for info in image_info]
            image_id_checkboxes.choices = choices
            return "\n".join([f"ID: {info['id']}, Name: {info['image_name']}" for info in image_info])

        image_info_output.value = update_image_info()
        run_weaver_button.click(run_weaver_flow, inputs=image_id_checkboxes, outputs=weaver_output)

    # Tab3: 查看剧本信息
    with gr.Tab("剧本信息查看"):
        script_dropdown = gr.Dropdown(choices=[], label="选择剧本 ID")
        script_details_output = gr.Textbox(label="剧本详细信息")

        def update_script_dropdown():
            script_ids = get_script_ids_and_themes()
            script_dropdown.choices = list(script_ids.keys())
            return script_ids

        script_dropdown.choices = update_script_dropdown()
        script_dropdown.change(get_script_details, inputs=script_dropdown, outputs=script_details_output)

# 启动 Gradio Web UI
if __name__ == "__main__":
    demo.launch()