import os
import gradio as gr
from agent.agent_start import caption_flow, weaver_flow
from database.db_manager import DatabaseManager

# 初始化数据库管理器
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db/image_database.db')
db_manager = DatabaseManager(db_path)
db_manager.connect()  # 确保连接已建立
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

        def update_image_info():
            image_info = db_manager.get_all_image_info()
            # 将 choices 转换为字符串列表
            return "\n".join([f"ID: {info['id']}, Name: {info['image_name']}" for info in image_info])

        image_info_output = gr.Textbox(label="所有图片信息",value=update_image_info(), interactive=False)
        # 修改: 确保 CheckboxGroup 的 choices 属性始终为字符串列表
        def get_image_id_list():
            image_info = db_manager.get_all_image_info()
            # 将 choices 转换为字符串列表
            choices = [str(info["id"]) for info in image_info]  # 确保每个元素为字符串
            return choices
        image_id_checkboxes = gr.CheckboxGroup(choices=get_image_id_list(), label="选择图片 ID")
        run_weaver_button = gr.Button("执行 Weaver Flow")
        weaver_output = gr.Textbox(label="执行结果")



        run_weaver_button.click(run_weaver_flow, inputs=image_id_checkboxes, outputs=weaver_output)

    # Tab3: 查看剧本信息
    with gr.Tab("剧本信息查看"):
        def gte_script_dropdown():
            script_ids = get_script_ids_and_themes()

            return list(script_ids.keys())

        script_dropdown = gr.Dropdown(choices=gte_script_dropdown(), label="选择剧本 ID")
        script_details_output = gr.Textbox(label="剧本详细信息")

        script_dropdown.change(get_script_details, inputs=script_dropdown, outputs=script_details_output)

# 启动 Gradio Web UI
if __name__ == "__main__":
    demo.launch()