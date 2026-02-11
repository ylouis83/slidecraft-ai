"""
Reviewer Agent — Quality assurance for the generated presentation.
"""

from __future__ import annotations

import json
import logging

from slidecraft.agents.base import BaseAgent
from slidecraft.models import (
    DesignSpec, PresentationContent, PresentationPlan, ReviewFeedback,
)

logger = logging.getLogger("slidecraft")


class ReviewerAgent(BaseAgent):
    name = "reviewer"
    description = "质量审查官，评审整体质量并提出修改建议"

    @property
    def system_prompt(self) -> str:
        gate_overall = self.config.quality_gate_min_overall
        gate_dim = self.config.quality_gate_min_dimension
        return (
            "你是 SlideCraft-AI 的质量审查官（Reviewer Agent），负责评审 PPT 质量。\n"
            "评审维度: 内容质量(0-10), 设计质量(0-10), 逻辑连贯性(0-10)。\n"
            "评分标准必须严格，不允许宽松打分。\n"
            "仅当 overall_score、content_score、design_score、coherence_score 全部 >= "
            f"{min(gate_overall, gate_dim):.1f} 时，approved 才能为 true。\n"
            "以 JSON 格式返回 ReviewFeedback。"
        )

    async def review(
        self, plan: PresentationPlan, content: PresentationContent, design: DesignSpec,
    ) -> ReviewFeedback:
        gate_overall = self.config.quality_gate_min_overall
        gate_dim = self.config.quality_gate_min_dimension
        slides_summary = [
            {
                "slide_number": sc.slide_number,
                "title": sc.title,
                "subtitle": sc.subtitle,
                "bullet_points": sc.bullet_points[:4],
                "has_data": bool(sc.data),
            }
            for sc in content.slides
        ]
        prompt = (
            f"审查以下PPT:\n标题: {plan.title}\n受众: {plan.target_audience}\n"
            f"风格: {design.style.value}\n主色: {design.colors.primary}\n"
            f"幻灯片:\n{json.dumps(slides_summary, indent=2, ensure_ascii=False)}\n"
            "请严格按高标准评审，重点检查：\n"
            "1) 内容是否有空话、重复、信息密度过低\n"
            "2) 版式是否有拥挤、层级不清、视觉重心混乱\n"
            "3) 叙事是否存在跳跃、断层、前后冲突\n"
            f"通过门槛: overall_score >= {gate_overall:.1f} 且三个维度都 >= {gate_dim:.1f}。\n"
            "请从内容、设计、连贯性三个维度评审，返回 ReviewFeedback JSON。"
        )
        review = await self.invoke_structured(prompt, ReviewFeedback)
        review.approved = self._is_approved(review)
        return review

    def _is_approved(self, review: ReviewFeedback) -> bool:
        return (
            review.overall_score >= self.config.quality_gate_min_overall
            and review.content_score >= self.config.quality_gate_min_dimension
            and review.design_score >= self.config.quality_gate_min_dimension
            and review.coherence_score >= self.config.quality_gate_min_dimension
        )
