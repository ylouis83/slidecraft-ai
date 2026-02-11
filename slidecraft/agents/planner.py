"""
Planner Agent — Designs the structure and outline of the presentation.

This agent analyzes the user's requirements and reference materials to
produce a detailed slide-by-slide plan including slide types, key points,
narrative arc, and image/chart needs.
"""

from __future__ import annotations

import logging

from slidecraft.agents.base import BaseAgent
from slidecraft.models import GenerationRequest, PresentationPlan

logger = logging.getLogger("slidecraft")


class PlannerAgent(BaseAgent):
    """Content planner that creates the presentation outline."""

    name = "planner"
    description = "内容规划师，负责分析需求并生成 PPT 的大纲与结构"

    @property
    def system_prompt(self) -> str:
        return """你是 SlideCraft-AI 的内容规划师（Planner Agent），专门负责设计 PPT 的整体结构和内容大纲。

## 你的专长
- 信息架构设计
- 叙事设计与故事线构建
- 受众分析与内容策略
- 视觉叙事规划

## 你的任务
根据用户需求，产出一份详细的 PPT 大纲，包括：

1. **整体叙事主线** - 一条贯穿所有幻灯片的故事线
2. **每张幻灯片的详细规划**：
   - 页码编号
   - 幻灯片类型（封面/目录/内容/图文/对比/时间线/引用/结束等）
   - 标题
   - 关键要点（3-5个）
   - 是否需要配图以及配图描述
   - 是否需要图表以及图表描述
   - 演讲者备注提示

## 设计原则
- **金字塔原理** - 先总后分，层层递进
- **MECE** - 相互独立、完全穷尽
- **一页一主题** - 每张幻灯片聚焦一个核心观点
- **视觉优先** - 多用图表和配图，减少文字堆砌
- **节奏感** - 内容页之间穿插视觉页，避免阅读疲劳
- **高管可读** - 先结论后论证，页间过渡自然
- **质量底线** - 内容质量与逻辑连贯目标 >= 9.5/10

## 常见结构模板
- **汇报型**: 封面 → 目录 → 背景/现状 → 分析 → 方案 → 计划 → 总结
- **提案型**: 封面 → 痛点 → 解决方案 → 优势 → 案例 → 下一步
- **教学型**: 封面 → 目标 → 概念 → 示例 → 练习 → 总结
- **演讲型**: 封面 → 开场故事 → 核心观点 → 论证 → 高潮 → 行动号召

请以 JSON 格式输出 PresentationPlan。"""

    async def plan(self, request: GenerationRequest) -> PresentationPlan:
        """Generate a presentation plan from the user request."""
        prompt = f"""请为以下需求规划一份 PPT 大纲：

## 需求信息
- **主题**: {request.topic}
- **详细描述**: {request.description or "无"}
- **目标受众**: {request.audience}
- **幻灯片数量**: {request.slide_count}
- **设计风格**: {request.style.value}
- **语言**: {request.language}
- **自定义指令**: {request.custom_instructions or "无"}

请产出完整的 PresentationPlan，包含每张幻灯片的详细规划，并满足：
1. 逻辑推进必须形成“背景→问题→方案→落地→总结”的闭环
2. 每页 key_points 具备信息价值，避免空泛标题党
3. 目标质量: 内容与逻辑维度 >= 9.5/10"""

        return await self.invoke_structured(
            prompt,
            PresentationPlan,
            images=None,  # Could pass reference images here
        )
