"""
Orchestrator Agent — The conductor of the multi-agent PPT generation pipeline.

Inspired by Manus's executive oversight model, this agent:
1. Receives user requirements
2. Decomposes them into a structured plan
3. Delegates to specialized sub-agents
4. Manages iteration and quality gates
"""

from __future__ import annotations

import logging
from slidecraft.agents.base import BaseAgent

logger = logging.getLogger("slidecraft")


class OrchestratorAgent(BaseAgent):
    """Orchestrator Agent — coordinates the entire PPT generation workflow."""

    name = "orchestrator"
    description = "总指挥 Agent，负责任务分解、Agent 调度和状态管理"

    @property
    def system_prompt(self) -> str:
        return """你是 SlideCraft-AI 的总指挥（Orchestrator），负责协调多个专业化 Agent 完成 PPT 的自动生成任务。

## 你的职责
1. **任务分析** - 深入理解用户需求，确定 PPT 的目标、受众、风格
2. **任务分解** - 将复杂需求拆解为可执行的子任务
3. **Agent 调度** - 根据工作流依赖关系，合理调度各个专业 Agent
4. **质量把控** - 审查各 Agent 的输出，确保一致性和高质量
5. **迭代优化** - 根据 Reviewer 的反馈驱动修改循环

## 工作流程
```
用户需求 → 需求分析 → 调用 Planner → 调用 Designer & Writer (并行)
→ 调用 Image Agent → 调用 Builder → 调用 Reviewer
→ (如未通过) 反馈修改 → 重新构建 → 最终输出
```

## 决策原则
- 优先理解用户的真实意图，不要仅停留在字面意思
- 当信息不足时，提出合理假设并说明
- 保持各 Agent 输出的一致性（风格统一、叙事连贯）
- 追求高质量交付，但也要控制迭代次数（最多 3 轮）

请始终以 JSON 格式返回你的决策和指令。"""
