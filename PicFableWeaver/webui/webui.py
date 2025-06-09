
# Tab2: 展示所有 image_info 📸🔍
with gr.Tab("图片信息管理"):
    # 说明：展示所有图片信息并选择图片ID来执行 Weaver Flow
    def update_image_info():
        image_info = db_manager.get_all_image_info()
        markdown_content = "\n".join([f"ID: {info['id']}, Name: {info['image_name']}" for info in image_info])
        return f"## 所有图片信息\n{markdown_content}"

    image_info_output = gr.Markdown(value=update_image_info())

