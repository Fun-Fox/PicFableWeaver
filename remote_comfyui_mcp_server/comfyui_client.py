import requests
import json
import time
from loguru import logger
import os

current_dir = os.path.dirname(os.path.abspath(__file__))


class ComfyUIClient:
    def __init__(self, base_url):
        """初始化ComfyUI客户端
        
        Args:
            base_url (str): ComfyUI服务的基础URL
        """
        self.base_url = base_url  # 初始化基础URL
        self.available_models = self._get_available_models()  # 获取可用模型列表
        self.mappings_dir = "mappings"  # 参数映射表文件夹

    def _get_available_models(self):
        """获取ComfyUI中可用的检查点模型列表"""
        try:
            response = requests.get(f"{self.base_url}/object_info/CheckpointLoaderSimple")
            if response.status_code != 200:
                logger.warning("无法获取模型列表；使用默认处理")
                return []
            data = response.json()
            models = data["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
            logger.info(f"可用模型: {models}")
            return models
        except Exception as e:
            logger.warning(f"获取模型时出错: {e}")
            return []

    def _load_mapping(self, workflow_id):
        """加载指定工作流的参数映射表
        
        Args:
            workflow_id (str): 工作流ID
            
        Returns:
            dict: 参数映射表
            
        Raises:
            Exception: 如果映射表文件不存在或解析失败
        """
        mapping_path = os.path.join(self.mappings_dir, f"{workflow_id}.json")
        try:
            with open(mapping_path, "r") as f:
                mapping = json.load(f)
            logger.info(f"已加载工作流 '{workflow_id}' 的参数映射表")
            return mapping
        except FileNotFoundError:
            raise Exception(f"参数映射表文件 '{mapping_path}' 未找到")
        except json.JSONDecodeError:
            raise Exception(f"解析参数映射表文件 '{mapping_path}' 失败")

    def generate_image(self, prompt, width=512, height=512, workflow_id="basic_api", model=None):
        """生成图像
        
        Args:
            prompt (str): 提示文本
            width (int, optional): 图像宽度. 默认为512.
            height (int, optional): 图像高度. 默认为512.
            workflow_id (str, optional): 工作流ID. 默认为"basic_api".
            model (str, optional): 使用的模型. 默认为None.
            
        Returns:
            str: 生成的图像URL
            
        Raises:
            Exception: 如果图像生成过程中出现错误
        """
        try:
            workflow_file = os.path.join(current_dir, f"workflows/{workflow_id}.json")  # 构造工作流文件路径
            with open(workflow_file, "r", encoding="utf-8", errors="ignore") as f:
                workflow = json.load(f)
            logger.info(f"使用工作流 {workflow_id} 生成图像...")

            # 加载参数映射表
            mapping = self._load_mapping(workflow_id)

            params = {"prompt": prompt, "width": width, "height": height}  # 创建基本参数字典
            if model:
                # 验证或纠正模型名称
                if model.endswith("'"):  # 去除意外添加的引号
                    model = model.rstrip("'")
                    logger.info(f"纠正后的模型名称: {model}")
                if self.available_models and model not in self.available_models:
                    raise Exception(f"模型 '{model}' 不在可用模型中: {self.available_models}")
                params["model"] = model  # 添加模型参数

            # 将参数应用到工作流中的相应节点
            for param_key, value in params.items():
                if param_key in mapping:
                    node_id, input_key = mapping[param_key]  # 解析节点ID和输入键
                    if node_id not in workflow:
                        raise Exception(f"工作流 {workflow_id} 中未找到节点 {node_id}")
                    workflow[node_id]["inputs"][input_key] = value  # 设置节点输入值

            logger.info(f"提交工作流 {workflow_id} 到ComfyUI...")  # 日志记录
            response = requests.post(f"{self.base_url}/prompt", json={"prompt": workflow})  # 提交工作流
            if response.status_code != 200:
                raise Exception(f"提交工作流失败: {response.status_code} - {response.text}")  # 错误处理

            prompt_id = response.json()["prompt_id"]  # 获取提示ID
            logger.info(f"已排队的工作流，prompt_id: {prompt_id}")  # 日志记录

            max_attempts = 30  # 最大尝试次数
            for _ in range(max_attempts):
                history = requests.get(f"{self.base_url}/history/{prompt_id}").json()  # 获取历史记录
                if history.get(prompt_id):
                    outputs = history[prompt_id]["outputs"]  # 获取输出结果
                    logger.info("工作流输出: %s", json.dumps(outputs, indent=2))  # 记录输出
                    image_node = next((nid for nid, out in outputs.items() if "images" in out), None)  # 查找包含图像的节点
                    if not image_node:
                        raise Exception(f"未找到包含图像的输出节点: {outputs}")  # 错误处理
                    image_filename = outputs[image_node]["images"][0]["filename"]  # 获取图像文件名
                    # 构建图像URL
                    image_url = f"{self.base_url}/view?filename={image_filename}&subfolder=&type=output"
                    logger.info(f"生成的图像URL: {image_url}")  # 记录图像URL
                    return image_url  # 返回图像URL
                time.sleep(1)  # 等待1秒
            # 超时处理
            raise Exception(f"工作流 {prompt_id} 在 {max_attempts} 秒内未完成")

        except FileNotFoundError:
            raise Exception(f"工作流文件 '{workflow_file}' 未找到")  # 文件未找到错误
        except KeyError as e:
            raise Exception(f"工作流错误 - 无效的节点或输入: {e}")  # 键错误处理
        except requests.RequestException as e:
            raise Exception(f"ComfyUI API错误: {e}")  # 请求异常处理

    def generate_image_to_video(self, image_path, prompt, workflow_id="hy_image_to_video_api", ):
        """从图像生成视频
        
        Args:
            image_path (str): 输入图像的路径
            prompt (str): 提示文本
            workflow_id (str, optional): 工作流ID. 默认为"hy_image_to_video_api".
        Returns:
            str: 生成的视频URL
            
        Raises:
            Exception: 如果视频生成过程中出现错误
        """
        try:
            workflow_file = os.path.join(current_dir, f"workflows/{workflow_id}.json")  # 构造工作流文件路径
            with open(workflow_file, "r", encoding="utf-8", errors="ignore") as f:
                workflow = json.load(f)
            logger.info(f"使用工作流 {workflow_id} 生成视频...")
            logger.info(f"workflow_id:\n{json.dumps(workflow, indent=2, ensure_ascii=False)}")
            # 上传图像
            uploaded_filename = self.upload_image(image_path)
            logger.info(f"上传的图像文件名: {uploaded_filename}")

            # 加载参数映射表
            mapping = self._load_mapping(workflow_id)

            params = {"prompt": prompt, "image": uploaded_filename}  # 创建基本参数字典

            # 将参数应用到工作流中的相应节点
            for param_key, value in params.items():
                if param_key in mapping:
                    node_id, input_key = mapping[param_key]  # 解析节点ID和输入键
                    if node_id not in workflow:
                        raise Exception(f"工作流 {workflow_id} 中未找到节点 {node_id}")
                    workflow[node_id]["inputs"][input_key] = value  # 设置节点输入值

            logger.info(f"提交工作流 {workflow_id} 到ComfyUI...")  # 日志记录
            response = requests.post(f"{self.base_url}/prompt", json={"prompt": workflow})  # 提交工作流
            if response.status_code != 200:
                raise Exception(f"提交工作流失败: {response.status_code} - {response.text}")  # 错误处理

            prompt_id = response.json()["prompt_id"]  # 获取提示ID
            logger.info(f"已排队的工作流，prompt_id: {prompt_id}")  # 日志记录

            max_attempts = 60  # 增加最大尝试次数以适应视频生成
            for _ in range(max_attempts):
                history = requests.get(f"{self.base_url}/history/{prompt_id}").json()  # 获取历史记录
                if history.get(prompt_id):
                    outputs = history[prompt_id]["outputs"]  # 获取输出结果
                    logger.info("工作流输出: %s", json.dumps(outputs, indent=2))  # 记录输出
                    video_node = next((nid for nid, out in outputs.items() if "videos" in out), None)  # 查找包含视频的节点
                    if not video_node:
                        raise Exception(f"未找到包含视频的输出节点: {outputs}")  # 错误处理
                    video_filename = outputs[video_node]["videos"][0]["filename"]  # 获取视频文件名
                    # 构建视频URL
                    video_url = f"{self.base_url}/view?filename={video_filename}&subfolder=&type=output"
                    logger.info(f"生成的视频URL: {video_url}")  # 记录视频URL
                    return video_url  # 返回视频URL
                time.sleep(2)  # 等待2秒
            # 超时处理
            raise Exception(f"工作流 {prompt_id} 在 {max_attempts} 秒内未完成")

        except FileNotFoundError:
            raise Exception(f"工作流文件 '{workflow_file}' 未找到")  # 文件未找到错误
        except KeyError as e:
            raise Exception(f"工作流错误 - 无效的节点或输入: {e}")  # 键错误处理
        except requests.RequestException as e:
            raise Exception(f"ComfyUI API错误: {e}")  # 请求异常处理

    def upload_image(self, image_path):
        """上传图像到ComfyUI的input目录
        
        Args:
            image_path (str): 要上传的图像路径
            
        Returns:
            str: 上传后服务器上的文件名
            
        Raises:
            Exception: 如果上传失败
        """
        try:
            url = f"{self.base_url}/api/upload/image"
            filename = os.path.basename(image_path)
            with open(image_path, 'rb') as f:
                files = {'image': (filename, f)}
                data = {'overwrite': 'true'}
                response = requests.post(url, files=files, data=data)
                response.raise_for_status()
                return response.json()['name']
        except Exception as e:
            raise Exception(f"上传图像失败: {e}")
