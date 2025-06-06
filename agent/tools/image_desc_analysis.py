from agent.utils.call_llm import call_local_llm
import yaml


def analyze_image_description(image_description: str) -> str:
    """
    分析图片描述，将其分成镜头、构图、视觉风格三部分。

    :param image_description: 图片描述
    :return: 分析结果
    """
    prompt = f"""
##  请根据以下图片描述，按指定格式拆分出：
- 镜头 (lens)
- 构图 (composition)
- 视觉风格 (visual_style)

## 图片描述：

{image_description}

## 输出格式示例：

```yaml 
lens: |
    <镜头描述>
composition: |
    <构图描述>
visual_style: |
    <视觉风格描述>
```

重要：请确保：
- 使用中文描述
- 使用YAML格式返回响应
- 使用|字符表示多行文本字段
- 多行字段使用缩进（4个空格）
- 单行字段不使用|字符
- 非键值对不允许随意使用冒号: 
"""
    result, success = call_local_llm(prompt)
    if success:
        try:
            # 尝试将结果解析为 YAML 格式
            yaml_str = result.split("```yaml")[1].split("```")[0].strip()
            analysis = yaml.safe_load(yaml_str)
            if isinstance(analysis,
                          dict) and 'lens' in analysis and 'composition' in analysis and 'visual_style' in analysis:
                return analysis['lens'], analysis['composition'], analysis['visual_style']
            else:
                # 如果解析失败或格式不正确，返回错误信息
                return "错误: LLM 返回的结果格式不正确。"
        except yaml.YAMLError:
            return "错误: LLM 返回的结果格式不正确。"
    else:
        return "无法生成分析结果，请稍后再试。"
