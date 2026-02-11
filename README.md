# 🎨 SlideCraft-AI

> **基于多模态大模型的多 Agent PPT 自动生成框架**

SlideCraft-AI 是一个受 Manus 等多 Agent 系统启发设计的 PPT 自动生成框架。它利用最新的多模态模型能力（GPT-4o / Claude 3.5 / Gemini 2.0），通过多个专业化 Agent 协作，从自然语言描述或参考素材自动生成高质量 PowerPoint 演示文稿。

---

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                  🎯 Orchestrator Agent                   │
│            (总指挥 - 任务分解与协调调度)                    │
├──────────┬──────────┬──────────┬──────────┬──────────────┤
│          │          │          │          │              │
│  📋      │  ✍️      │  🎨      │  🖼️      │  🔍          │
│ Planner  │ Writer   │ Designer │ Image    │ Reviewer     │
│ Agent    │ Agent    │ Agent    │ Agent    │ Agent        │
│          │          │          │          │              │
│ 内容规划  │ 文案撰写  │ 视觉设计  │ 图片生成  │ 质量审查     │
└──────────┴──────────┴──────────┴──────────┴──────────────┘
                          │
                    ┌─────┴─────┐
                    │ 🔧 Builder │
                    │   Agent    │
                    │  PPT 构建   │
                    └────────────┘
```

## 🌟 核心特性

### 多 Agent 协作
- **Orchestrator Agent** - 总指挥，负责任务分解、Agent 调度、状态管理
- **Planner Agent** - 内容规划师，分析需求生成 PPT 大纲与结构
- **Writer Agent** - 文案撰写师，为每张幻灯片生成专业文案
- **Designer Agent** - 视觉设计师，设计配色方案、版式布局、字体选择
- **Image Agent** - 图片处理师，利用多模态模型生成/搜索/编辑配图
- **Reviewer Agent** - 质量审查官，采用严格质量门槛（默认 9.5 分）驱动迭代优化
- **BuilderV2 Agent** - 增强版 PPT 构建师（渐变背景、阴影卡片、自适应排版、统一字体）

### 多模态能力
- 📷 **图片理解** - 上传参考 PPT 截图/设计稿, AI 自动分析并复刻风格
- 🖼️ **图片生成** - 根据内容自动生成配图（DALL-E 3 / Midjourney API）
- 📄 **文档理解** - 上传 PDF/Word/Markdown 文档自动提取关键内容
- 🎙️ **语音输入** - 支持语音描述需求（Whisper）

### 工作流引擎
- 基于 LangGraph 的有状态工作流程
- 支持人工介入 (Human-in-the-Loop)
- 迭代优化循环（审查→修改→再审查，默认最多 5 轮）
- 检查点与恢复机制

---

## 📁 项目结构

```
slidecraft-ai/
├── README.md                     # 项目说明
├── pyproject.toml                # 项目配置与依赖
├── .env.example                  # 环境变量模板
│
├── slidecraft/                   # 核心框架
│   ├── __init__.py
│   ├── config.py                 # 配置管理
│   ├── models.py                 # 数据模型定义
│   │
│   ├── agents/                   # Agent 定义
│   │   ├── __init__.py
│   │   ├── base.py               # Agent 基类
│   │   ├── orchestrator.py       # 总指挥 Agent
│   │   ├── planner.py            # 内容规划 Agent
│   │   ├── writer.py             # 文案撰写 Agent
│   │   ├── designer.py           # 视觉设计 Agent
│   │   ├── image_agent.py        # 图片处理 Agent
│   │   ├── reviewer.py           # 质量审查 Agent
│   │   ├── builder.py            # 基础 PPT 构建 Agent
│   │   └── builder_v2.py         # 增强渲染构建 Agent（默认）
│   │
│   ├── graph/                    # LangGraph 工作流
│   │   ├── __init__.py
│   │   ├── state.py              # 全局状态定义
│   │   ├── workflow.py           # 工作流编排
│   │   └── nodes.py              # 节点定义
│   │
│   ├── tools/                    # Agent 工具集
│   │   ├── __init__.py
│   │   ├── pptx_tools.py         # python-pptx 工具封装
│   │   ├── image_tools.py        # 图片生成/处理工具
│   │   ├── web_search.py         # 网络搜索工具
│   │   └── document_parser.py    # 文档解析工具
│   │
│   ├── templates/                # PPT 模板
│   │   ├── __init__.py
│   │   └── themes.py             # 主题配置
│   │
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── llm_client.py         # LLM 客户端封装
│       └── file_utils.py         # 文件处理工具
│
├── examples/                     # 使用示例
│   ├── basic_usage.py
│   ├── from_document.py
│   └── from_image.py
│
└── tests/                        # 测试
    ├── __init__.py
    ├── test_agents.py
    └── test_workflow.py
```

---

## 🚀 快速开始

### 安装

```bash
cd slidecraft-ai
pip install -e .
```

### 配置

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 基础使用

```python
from slidecraft import SlideCraft

# 初始化
craft = SlideCraft()

# 从自然语言描述生成 PPT
result = craft.generate(
    topic="2025年AI技术趋势",
    audience="企业CTO",
    slide_count=15,
    style="商务科技",
    language="zh-CN"
)

# 保存
result.save("ai_trends_2025.pptx")
```

### 从参考图片生成

```python
result = craft.generate_from_image(
    image_path="reference_slide.png",
    topic="我们的产品介绍",
    replicate_style=True
)
```

### 从文档生成

```python
result = craft.generate_from_document(
    document_path="quarterly_report.pdf",
    style="极简商务"
)
```

---

## ⚙️ 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Agent 框架 | LangGraph | 有状态多 Agent 工作流编排 |
| LLM 集成 | LangChain + OpenAI/Anthropic/Google | 多模态大模型调用 |
| PPT 生成 | python-pptx | PowerPoint 文件创建与操作 |
| 图片生成 | DALL-E 3 / Stable Diffusion | AI 配图生成 |
| 文档解析 | PyMuPDF + python-docx | PDF/Word 文档理解 |
| 状态管理 | LangGraph State | 工作流状态管理与检查点 |

---

## 📜 License

MIT License
