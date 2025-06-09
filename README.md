# PicFableWeaver - 将图片编织成故事的智能工具

## 项目简介

PicFableWeaver 能够将日常随手拍的图片转化为引人入胜的视频、短剧和微电影。
通过先进的AI技术，项目可以分析图片内容并生成创意视频剧本，
包括详细的分镜说明、运镜策略和背景音乐建议。

## 核心功能

- **图像分析**：使用LLaVA模型对图片进行深度分析
- **创意生成**：根据分析结果随机生成视频剧本创意
- **分镜规划**：将剧本转化为详细的分镜说明，包括运镜方式和AI图生视频技巧
- **多媒体合成**：整合图片、运镜效果和背景音乐生成完整视频

## 技术架构

```
[用户输入] → 图像分析模块 → 创意生成模块 → 分镜规划模块 → 多媒体合成模块 → [视频输出]
```

## 运镜策略映射表

| 原始意图 | 运镜方式     | 参数配置             |
|----------|--------------|----------------------|
| 动态展示 | 轨道平移     | speed=0.5s/m        |
| 情绪渲染 | 景深变化     | focus_range=2m      |
| 空间展示 | 360度环绕   | rotation_speed=15°/s|
| 细节聚焦 | 逐步缩放     | zoom_factor=1.5x    |

## 技术栈

- MCP (Model Control Protocol)
- A2A (Agent-to-Agent Communication)
- LLaVA Model: https://huggingface.co/fancyfeast/llama-joycaption-beta-one-hf-llava
- Python 3.11
- ComfyUI Integration

## 📁 项目结构

```
├── agent                  # 核心智能体模块
│   ├── flow               # 工作流程管理
│   ├── node               # 功能节点（描述生成、图像编织等）
│   ├── tools              # 辅助工具
│   └── utils              # 公共工具函数
├── remote_caption_mcp_server  # 远程字幕生成服务
├── remote_comfyui_mcp_server  # ComfyUI集成服务
└── README.md            # 项目文档
```

## 🛠️ 部署步骤

### 部署远程MCP服务

```commandline
# 安装图片反推模型（图片打标）依赖
cd remote_caption_mcp_server
pip install -r requirements.txt

# 下载LLaVA模型
set HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download fancyfeast/llama-joycaption-beta-one-hf-llava --repo-type=model --local-dir ./llava_model/

# 安装PyTorch
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu128
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# 安装Triton
#https://zhuanlan.zhihu.com/p/27131210741
#pip install -U triton-windows
#https://blog.csdn.net/a486259/article/details/146451953
#pip install liger-kernel --no-dependencies

# 安装comfyui-mcp
cd..
cd remote_comfyui_mcp_server
pip install -r requirements.txt
```

### 启动服务

```commandline
# 启动LLaVA图片描述生成服务
python remote_caption_mcp_server/start.py

# 启动ComfyUI集成服务
python remote_comfyui_mcp_server/server.py
```
