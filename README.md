# 图片故事编织者

像漫画一样，给出几张线稿图
- AI对线稿进行图片分析，
- 在结合所有的线稿和描述，进行生成剧本。
- 生成AI生视频的所需运镜、首尾帧效果（AI生视频指导）


# 技术
基于MCP 及 A2A
Python 3.11版本


## 🛠️ 部署步骤
```commandline
pip install -r requirements.txt
# 将整个模型仓库下载到 ./llava_model/ 文件夹中。
set HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download fancyfeast/llama-joycaption-beta-one-hf-llava --repo-type=model --local-dir  ./llava_model/

```
