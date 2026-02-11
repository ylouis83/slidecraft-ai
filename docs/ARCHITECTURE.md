# SlideCraft-AI 架构设计文档

## 1. 设计理念

### 1.1 多 Agent 协作 (受 Manus 启发)

SlideCraft-AI 的核心设计理念来源于 Manus 等多 Agent 系统：

- **执行监督模型 (Executive Oversight)**：Orchestrator 作为"总指挥"，接收用户需求后将其分解为子任务，分配给专业化的 Sub-Agent 执行
- **专业化分工**：每个 Agent 只负责一个领域（规划、写作、设计、图片、审查、构建），确保每个环节都有深度专业能力
- **迭代优化循环**：通过 Reviewer Agent 的质量审查，驱动修改-重建循环，确保输出质量
- **CodeAct 范式**：Agent 通过生成结构化 JSON 数据（而非自由文本）来操作 PPT 构建过程

### 1.2 多模态能力

框架充分利用最新多模态模型的能力：

| 能力 | 使用场景 | 模型 |
|------|---------|------|
| 图片理解 | 分析参考设计稿，复刻视觉风格 | GPT-4o / Claude 3.5 / Gemini 2.0 |
| 文本生成 | 内容规划、文案撰写、设计描述 | 同上 |
| 图片生成 | 为幻灯片生成配图 | DALL-E 3 / Stable Diffusion |
| 文档理解 | 从 PDF/DOCX 提取内容 | PyMuPDF + LLM |

## 2. 系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                        用户接口层                                 │
│                                                                   │
│   Python API  │  CLI  │  (future: Web UI / FastAPI)              │
└──────────┬───────────────────────────────────────────────────────┘
           │
┌──────────┴───────────────────────────────────────────────────────┐
│                     工作流编排层 (LangGraph)                       │
│                                                                   │
│   StateGraph → plan → write → design → image → build → review   │
│                          ↑                              │        │
│                          └──────── revise ──────────────┘        │
└──────────┬───────────────────────────────────────────────────────┘
           │
┌──────────┴───────────────────────────────────────────────────────┐
│                        Agent 层                                   │
│                                                                   │
│   Planner │ Writer │ Designer │ Image │ Builder │ Reviewer       │
│                                                                   │
│   每个 Agent 封装：                                                │
│   - 专业化 System Prompt                                          │
│   - 结构化输出解析 (Pydantic)                                      │
│   - 多模态消息构建                                                  │
└──────────┬───────────────────────────────────────────────────────┘
           │
┌──────────┴───────────────────────────────────────────────────────┐
│                       基础设施层                                   │
│                                                                   │
│   LLM Client │ python-pptx │ Image APIs │ Document Parser       │
└──────────────────────────────────────────────────────────────────┘
```

## 3. 数据流

```
GenerationRequest    用户请求
       │
       ▼
PresentationPlan     Planner → 大纲(标题、类型、要点、配图需求)
       │
       ├──────────────────┐
       ▼                  ▼
PresentationContent  DesignSpec
Writer → 文案          Designer → 视觉规范
       │                  │
       └────────┬─────────┘
                ▼
        GeneratedImage[]
        Image Agent → 配图
                │
                ▼
          .pptx 文件
          Builder → 组装
                │
                ▼
         ReviewFeedback
         Reviewer → 评审
                │
        ┌───────┴──────┐
        ▼              ▼
     Approved       Revise
     输出文件        回到 Writer
```

## 4. Agent 详细设计

### 4.1 Planner Agent
- **输入**: GenerationRequest
- **输出**: PresentationPlan
- **核心能力**: 信息架构、叙事设计、受众分析
- **设计决策**: 使用金字塔原理和 MECE 法则组织内容

### 4.2 Writer Agent
- **输入**: PresentationPlan + language
- **输出**: PresentationContent
- **核心能力**: 商务写作、信息提炼、多语言文案
- **设计决策**: 遵循"一页一主题"原则，控制信息密度

### 4.3 Designer Agent
- **输入**: PresentationPlan + GenerationRequest + 参考图片
- **输出**: DesignSpec (配色/字体/布局)
- **核心能力**: 色彩理论、排版设计、品牌设计
- **多模态能力**: 可以分析参考图片提取设计风格

### 4.4 Image Agent
- **输入**: PresentationPlan + DesignSpec
- **输出**: GeneratedImage[] (生成的配图)
- **核心能力**: 图片生成提示词优化、风格一致性控制
- **支持**: DALL-E 3, Stability AI, 占位符降级

### 4.5 BuilderV2 Agent
- **输入**: Plan + Content + Design + Images
- **输出**: .pptx 文件
- **核心能力**: 声明式渲染引擎、渐变背景、阴影卡片、自适应排版
- **线型类型**: 封面、目录、章节、内容、图文、结束页

### 4.6 Reviewer Agent
- **输入**: Plan + Content + Design
- **输出**: ReviewFeedback (评分+建议)
- **评审维度**: 内容质量、设计质量、整体连贯性
- **决策**: overall_score >= 9.5 且三个维度均 >= 9.5 才通过

## 5. 扩展计划

### Phase 2
- [ ] 支持 PPT 模板导入 (.pptx 模板文件)
- [ ] Web UI (FastAPI + React)
- [ ] Real-time streaming 进度展示
- [ ] Human-in-the-loop 审查界面

### Phase 3
- [ ] 支持更多图表类型 (python-pptx charts)
- [ ] 智能动画建议
- [ ] 演讲稿自动生成
- [ ] 品牌设计系统导入

### Phase 4
- [ ] 多人协作编辑
- [ ] 版本控制与历史回溯
- [ ] 与 Google Slides / MS Office 集成
- [ ] RAG 增强 (知识库检索)
