"""
Writer Agent — Generates the textual content for each slide.

Takes the presentation plan and produces polished copy for every slide,
including titles, body text, bullet points, and speaker notes.
"""

from __future__ import annotations

import logging

from slidecraft.agents.base import BaseAgent
from slidecraft.models import (
    PresentationContent,
    PresentationPlan,
    SlideContent,
    SlideType,
)

logger = logging.getLogger("slidecraft")


class WriterAgent(BaseAgent):
    """Content writer that produces slide text content."""

    name = "writer"
    description = "文案撰写师，负责为每张幻灯片生成专业文案"

    @property
    def system_prompt(self) -> str:
        return """你是 SlideCraft-AI 的文案撰写师（Writer Agent），专门负责 PPT 幻灯片的文案创作。

## 你的专长
- 商务写作与演示文稿文案
- 信息提炼与概括
- 多语言文案创作
- 数据叙事

## 写作原则

### 标题
- 精炼有力，一般不超过 10 个字
- 使用动词开头或数字开头增强吸引力
- 避免使用"关于"、"的分析"等冗余词

### 正文要点
- 每个要点控制在 1-2 行
- 使用并列结构，保持语法一致
- 包含具体数据或事实支撑
- 每页 3-6 个要点，避免空泛表述

### 演讲者备注
- 为演讲者提供口语化的讲解提示
- 包含过渡语和强调重点
- 预设可能的提问方向

### 文本层次
- **一级**: 核心观点（大字体，标题区域）
- **二级**: 支撑论点（中字体，要点）
- **三级**: 补充说明（小字体，注释）

### 质量底线
- 内容质量、逻辑连贯目标分数 >= 9.5/10
- 不允许口号化语句，必须有可执行信息或事实支撑
- 相邻页面必须有过渡关系，避免“页面孤岛”

## 输出要求
为每张幻灯片生成：
1. title - 精炼标题
2. subtitle - 副标题（可选）
3. body_text - 正文（Markdown 格式）
4. bullet_points - 要点列表
5. notes - 演讲者备注

以 JSON 格式返回 PresentationContent。"""

    async def write(self, plan: PresentationPlan, language: str = "zh-CN") -> PresentationContent:
        """Generate content for all slides based on the plan."""
        slides_info = []
        for s in plan.slides:
            slides_info.append({
                "slide_number": s.slide_number,
                "slide_type": s.slide_type.value,
                "title": s.title,
                "key_points": s.key_points,
                "notes_hint": s.notes,
            })

        import json
        prompt = f"""请根据以下 PPT 大纲，为每张幻灯片撰写完整的文案内容。

## PPT 信息
- **标题**: {plan.title}
- **副标题**: {plan.subtitle}
- **叙事主线**: {plan.narrative_arc}
- **目标受众**: {plan.target_audience}
- **语言**: {language}

## 幻灯片大纲
```json
{json.dumps(slides_info, indent=2, ensure_ascii=False)}
```

请为每张幻灯片生成精心打磨的文案，以 JSON 格式返回 PresentationContent。
确保：
1. 标题精炼有力
2. 要点清晰简洁
3. 前后衔接自然
4. 保持风格统一
5. 内容质量和逻辑连贯目标 >= 9.5/10"""

        content = await self.invoke_structured(prompt, PresentationContent)
        return self._enforce_quality_constraints(plan, content)

    def _enforce_quality_constraints(
        self,
        plan: PresentationPlan,
        content: PresentationContent,
    ) -> PresentationContent:
        """Normalize content so every slide satisfies minimum readability constraints."""
        by_number = {slide.slide_number: slide for slide in content.slides}
        normalized: list[SlideContent] = []

        for outline in plan.slides:
            current = by_number.get(outline.slide_number) or SlideContent(
                slide_number=outline.slide_number,
                title=outline.title,
                bullet_points=[],
            )
            if not current.title:
                current.title = outline.title

            if outline.slide_type in {
                SlideType.CONTENT,
                SlideType.TWO_COLUMN,
                SlideType.IMAGE_TEXT,
                SlideType.COMPARISON,
                SlideType.TIMELINE,
            }:
                source_points = current.bullet_points or outline.key_points
                current.bullet_points = self._normalize_bullets(source_points)
                if len(current.bullet_points) < 3:
                    current.bullet_points.extend(
                        self._normalize_bullets(outline.key_points)[: 3 - len(current.bullet_points)]
                    )

            if outline.slide_type == SlideType.CHART and not current.data:
                labels = outline.key_points[:5] or ["阶段一", "阶段二", "阶段三", "阶段四", "阶段五"]
                current.data = {
                    "labels": labels,
                    "values": [20, 40, 60, 80, 95][: len(labels)],
                    "series_name": "指标评分",
                }

            if not current.notes:
                current.notes = outline.notes or f"本页聚焦：{current.title}。"

            normalized.append(current)

        return PresentationContent(slides=normalized)

    def _normalize_bullets(self, items: list[str], max_items: int = 6) -> list[str]:
        cleaned: list[str] = []
        for item in items:
            text = " ".join(str(item).replace("\n", " ").split()).strip("•- ")
            if not text:
                continue
            if text in cleaned:
                continue
            if len(text) > 42:
                text = f"{text[:41]}…"
            cleaned.append(text)
            if len(cleaned) >= max_items:
                break
        return cleaned
