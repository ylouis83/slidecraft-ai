"""
Designer Agent — Creates the visual design specification.

Determines the color palette, typography, layout templates, and
overall visual language for the presentation.
"""

from __future__ import annotations

import json
import logging

from slidecraft.agents.base import BaseAgent
from slidecraft.models import (
    DesignSpec,
    DesignStyle,
    GenerationRequest,
    PresentationPlan,
    SlideLayout,
)

logger = logging.getLogger("slidecraft")


# Pre-defined design palettes for quick reference
STYLE_PALETTES = {
    DesignStyle.BUSINESS: {
        "primary": "#1a56db",
        "secondary": "#047857",
        "accent": "#d97706",
        "background": "#ffffff",
        "surface": "#f3f4f6",
        "text_primary": "#111827",
        "text_secondary": "#6b7280",
    },
    DesignStyle.TECH: {
        "primary": "#0ea5e9",
        "secondary": "#22d3ee",
        "accent": "#f59e0b",
        "background": "#020617",
        "surface": "#0f172a",
        "text_primary": "#f1f5f9",
        "text_secondary": "#cbd5e1",
    },
    DesignStyle.MINIMAL: {
        "primary": "#18181b",
        "secondary": "#71717a",
        "accent": "#ef4444",
        "background": "#fafafa",
        "surface": "#f4f4f5",
        "text_primary": "#18181b",
        "text_secondary": "#71717a",
    },
    DesignStyle.CREATIVE: {
        "primary": "#ef4444",
        "secondary": "#f97316",
        "accent": "#0ea5e9",
        "background": "#fffaf2",
        "surface": "#fff1dc",
        "text_primary": "#1f2937",
        "text_secondary": "#6b7280",
    },
    DesignStyle.ACADEMIC: {
        "primary": "#1e40af",
        "secondary": "#166534",
        "accent": "#92400e",
        "background": "#fffbeb",
        "surface": "#fef3c7",
        "text_primary": "#1f2937",
        "text_secondary": "#4b5563",
    },
    DesignStyle.DARK: {
        "primary": "#38bdf8",
        "secondary": "#10b981",
        "accent": "#f59e0b",
        "background": "#0b1020",
        "surface": "#131a2d",
        "text_primary": "#f9fafb",
        "text_secondary": "#cbd5e1",
    },
    DesignStyle.GRADIENT: {
        "primary": "#0284c7",
        "secondary": "#14b8a6",
        "accent": "#f97316",
        "background": "#f8fafc",
        "surface": "#e0f2fe",
        "text_primary": "#0f172a",
        "text_secondary": "#334155",
    },
}


class DesignerAgent(BaseAgent):
    """Visual designer that creates the design specification."""

    name = "designer"
    description = "视觉设计师，负责配色方案、版式布局和字体选择"

    @property
    def system_prompt(self) -> str:
        return """你是 SlideCraft-AI 的视觉设计师（Designer Agent），专门负责 PPT 的视觉设计。

## 你的专长
- 色彩理论与配色方案设计
- 版式设计与布局规划
- 字体选择与排版设计
- 设计趋势与风格把控

## 设计原则
1. **一致性** - 所有页面保持统一的视觉语言
2. **层次感** - 通过大小、颜色、间距建立信息层次
3. **留白** - 给内容足够的呼吸空间
4. **对比** - 用颜色和大小的对比引导视线
5. **对齐** - 元素应沿网格严格对齐
6. **高端感** - 避免模板感，标题区、内容区、强调区必须有明确视觉节奏
7. **可读性优先** - 保证远距离投影可读，避免浅色字与浅色背景叠加

## 配色规则
- 主色(Primary): 品牌色/主题色，用于标题和重要元素
- 辅色(Secondary): 补充色，用于图表和次要元素
- 强调色(Accent): 用于 CTA 和需要突出的地方
- 背景色(Background): 页面底色
- 文字色: 主色确保 4.5:1 以上对比度
- 页面层次: 背景/表面/强调层至少有三级明度差

## 版式模板
你需要为每种幻灯片类型定义布局：
- cover: 封面 - 大标题居中，副标题下方
- toc: 目录 - 编号列表或网格布局
- content: 内容页 - 左文右图或上标题下要点
- two_column: 双栏 - 左右等分或6:4分
- image_full: 全图 - 配文字叠加
- comparison: 对比 - 左右对称布局
- timeline: 时间线 - 水平或垂直时间轴
- quote: 引用 - 大字号居中，引号装饰
- thank_you: 结尾 - 致谢信息居中

## 输出要求
以 JSON 格式返回完整的 DesignSpec，并确保设计质量目标 >= 9.5/10。"""

    async def design(
        self,
        plan: PresentationPlan,
        request: GenerationRequest,
        reference_images: list[str] | None = None,
    ) -> DesignSpec:
        """Create a complete design specification."""
        # Start with a base palette from the requested style
        base_palette = STYLE_PALETTES.get(request.style, STYLE_PALETTES[DesignStyle.BUSINESS])

        slide_types = [
            {"slide_number": s.slide_number, "slide_type": s.slide_type.value, "title": s.title}
            for s in plan.slides
        ]

        brand_info = ""
        if request.brand_colors:
            brand_info = f"品牌色: {', '.join(request.brand_colors)}。请以品牌色为基础设计配色方案。"

        prompt = f"""请为以下 PPT 设计完整的视觉规范。

## PPT 信息
- **标题**: {plan.title}
- **设计风格**: {request.style.value}
- **受众**: {request.audience}
- **语言**: {request.language}
{f'- **品牌要求**: {brand_info}' if brand_info else ''}

## 参考配色
```json
{json.dumps(base_palette, indent=2)}
```

## 幻灯片列表
```json
{json.dumps(slide_types, indent=2, ensure_ascii=False)}
```

请基于以上信息，设计完整的 DesignSpec，包括：
1. 配色方案（colors）
2. 字体方案（fonts）- 根据语言选择合适的字体
3. 每张幻灯片的布局描述（layouts）
4. `use_gradient_backgrounds` 和 `corner_radius`（提升质感）
5. 每页布局描述必须可执行，避免“通用描述”

严格要求：
- 版面设计质量目标至少 9.5/10
- 不允许大段文字堆叠，必须有清晰信息层级
- 图文页保证图文比例与留白平衡

{'请分析参考图片的设计风格，尽可能复刻其视觉效果。' if reference_images else ''}"""

        design = await self.invoke_structured(
            prompt,
            DesignSpec,
            images=reference_images,
        )
        return self._apply_quality_defaults(design, plan, request, base_palette)

    def _apply_quality_defaults(
        self,
        design: DesignSpec,
        plan: PresentationPlan,
        request: GenerationRequest,
        base_palette: dict[str, str],
    ) -> DesignSpec:
        """Apply deterministic quality guards for layout readability and consistency."""
        # Ensure palette fields are always complete and coherent.
        for key, value in base_palette.items():
            if not getattr(design.colors, key, ""):
                setattr(design.colors, key, value)

        if request.brand_colors:
            design.colors.primary = request.brand_colors[0]
            if len(request.brand_colors) > 1:
                design.colors.secondary = request.brand_colors[1]

        # Enforce readable typography baseline.
        if request.language.lower().startswith("zh"):
            design.fonts.title_font = design.fonts.title_font or "微软雅黑"
            design.fonts.body_font = design.fonts.body_font or "微软雅黑"
        else:
            design.fonts.title_font = design.fonts.title_font or "Calibri"
            design.fonts.body_font = design.fonts.body_font or "Calibri"

        design.fonts.title_size_pt = max(design.fonts.title_size_pt, 38)
        design.fonts.subtitle_size_pt = max(design.fonts.subtitle_size_pt, 22)
        design.fonts.body_size_pt = max(design.fonts.body_size_pt, 18)
        design.fonts.caption_size_pt = max(design.fonts.caption_size_pt, 14)

        # Automatically enable gradients for styles that benefit from depth.
        if request.style in {DesignStyle.TECH, DesignStyle.DARK, DesignStyle.GRADIENT}:
            design.use_gradient_backgrounds = True

        # Prefer soft cards for modern visuals.
        design.corner_radius = max(design.corner_radius, 10)

        # Ensure each slide has at least one layout descriptor.
        existing = {layout.slide_number for layout in design.layouts}
        for slide in plan.slides:
            if slide.slide_number not in existing:
                design.layouts.append(
                    SlideLayout(
                        slide_number=slide.slide_number,
                        slide_type=slide.slide_type,
                        layout_description="保持标题区、主体区、辅助区三级结构与一致留白。",
                        elements=[],
                    )
                )

        return design
