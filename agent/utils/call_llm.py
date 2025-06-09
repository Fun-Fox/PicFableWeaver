import os
import requests
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


def call_llm(prompt):
    if os.getenv("MODEL_PLATFORM") == "cloud":
        return call_cloud_model(prompt)
    return call_local_llm(prompt)


def call_local_llm(prompt, ):
    # 支持视觉与非视觉模型  ·
    try:
        url = f"{os.getenv('LOCAL_LLM_URL')}"

        logger.info(f"使用本地模型{os.getenv('LOCAL_MODEL_NAME')},进行语言(非视觉)操作")
        payload = {
            "model": f"{os.getenv('LOCAL_MODEL_NAME')}",
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info(f"模型返回信息{response.json().get('response')}")
            return response.json().get("response", ""), True
        else:
            logger.error(f"错误: 无法从模型获取响应。状态码: {response.status_code}")
            return "错误: 无法从模型获取响应。", False
    except Exception as e:
        logger.error(f"调用LLM时发生异常: {e}")
        return "错误: 调用LLM时发生异常。", False


def call_cloud_model(prompt, max_retries=2):
    api_key = os.getenv("CLOUD_API_KEY")
    api_url = os.getenv("CLOUD_API_URL")
    model_name = os.getenv("CLOUD_MODEL_NAME")
    for attempt in range(max_retries):
        try:

            logger.info(f"使用云端模型{os.getenv('CLOUD_MODEL_NAME')},进行语言(非视觉)操作")

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            payload = _build_payload(prompt, model_name)
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code == 200:
                try:
                    # 解析 JSON 数据
                    json_data = response.json()
                    choices = json_data.get("choices", [])

                    if choices:  # 确保 choices 列表非空
                        first_choice = choices[0]  # 获取第一个选择
                        message = first_choice.get("message", {})
                        content = message.get("content", "无内容")  # 获取 content 字段，若不存在则返回默认值
                        reasoning_content = message.get("reasoning_content", "无推理内容")  # 获取 reasoning_content 字段

                        logger.info(f"API 响应: Content={content}\n, Reasoning Content={reasoning_content}")
                        return content, True  # 返回 content 字段
                    else:
                        logger.warning("API 响应中没有 choices 数据")
                        return "无内容", False
                except Exception as e:
                    logger.error(f"云端模型调用出现异常: {e}")
                    return "云端模型调用出现异常", False
            logger.warning(f"第 {attempt + 1} 次尝试失败，状态码: {response.status_code}")
        except Exception as e:
            logger.warning(f"第 {attempt + 1} 次尝试失败: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                logger.error("所有尝试均失败")
                raise Exception(f"评估图片相关性失败，尝试 {MAX_RETRIES} 次后仍未成功: {str(e)}")
    raise Exception("evaluate_image_relevance 方法中发生意外错误")


def _build_payload(prompt, model_name, ) -> dict:
    """构建评估请求负载。
    :type model_name: object
    """
    content = [
        {
            "type": "text",
            "text": prompt
        }
    ]

    return {
        "model": f"{model_name}",
        "enable_thinking": True,
        "frequency_penalty": 0,
        "max_tokens": 8192,
        "top_k": 20,
        "temperature": 0.6,
        "top_p": 0.95,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "stream": False
    }
