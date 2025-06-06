import os
import requests
from loguru import logger
from dotenv import load_dotenv
load_dotenv()

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
