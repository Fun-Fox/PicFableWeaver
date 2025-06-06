探索从多日常随手拍的图片到视频、短剧、微电影的编织过程

# 视频创意灵感激发器

- llava_model对进行图片分析
- 在结合分析结果，随机生成创意 视频剧本，从视频剧本再到一些详细的、视频背景音乐、
- 将剧本转为 分镜详细说明(包含分镜所运用到的图片、运镜方式、AI图生视频技巧、)

运镜策略映射表：

| 原始意图 | 运镜方式 | 参数配置           | 
|------|------|----------------| 
| 动态展示 | 轨道平移 | speed=0.5s/m   | 
| 情绪渲染 | 景深变化 | focus_range=2m |

# 技术栈

- MCP
- A2A
- llava_model：https://huggingface.co/fancyfeast/llama-joycaption-beta-one-hf-llava
- Python 3.11

## 🛠️ 部署步骤

### 部署远程mcp服务

```commandline
cd remote_mcp_server
pip install -r requirements.txt
# 将整个模型仓库下载到 ./llava_model/ 文件夹中。
set HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download fancyfeast/llama-joycaption-beta-one-hf-llava --repo-type=model --local-dir  ./llava_model/
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu128
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
#https://zhuanlan.zhihu.com/p/27131210741
#pip install -U triton-windows
#https://blog.csdn.net/a486259/article/details/146451953
#pip install liger-kernel --no-dependencies
```
