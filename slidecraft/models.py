"""
SlideCraft Data Models
Defines the structured data exchanged between agents
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================
# Enums
# ============================================================

class SlideType(str, Enum):
    """Types of slides supported by the framework."""
    COVER = "cover"                  # 封面
    TABLE_OF_CONTENTS = "toc"        # 目录
    SECTION_HEADER = "section"       # 章节标题
    CONTENT = "content"              # 标准内容页
    TWO_COLUMN = "two_column"        # 双栏布局
    IMAGE_FULL = "image_full"        # 全屏图片
    IMAGE_TEXT = "image_text"        # 图文混排
    CHART = "chart"                  # 图表数据
    COMPARISON = "comparison"        # 对比页
    TIMELINE = "timeline"            # 时间线
    QUOTE = "quote"                  # 引用页
    THANK_YOU = "thank_you"          # 结束页


class DesignStyle(str, Enum):
    """Pre-defined design styles."""
    BUSINESS = "business"            # 商务正式
    TECH = "tech"                    # 科技感
    MINIMAL = "minimal"              # 极简
    CREATIVE = "creative"            # 创意
    ACADEMIC = "academic"            # 学术
    DARK = "dark"                    # 深色主题
    GRADIENT = "gradient"            # 渐变风格


# ============================================================
# Input Models
# ============================================================

class GenerationRequest(BaseModel):
    """User's request for PPT generation."""
    topic: str = Field(..., description="PPT 主题")
    description: str = Field(default="", description="详细描述/补充信息")
    audience: str = Field(default="通用", description="目标受众")
    slide_count: int = Field(default=10, ge=3, le=50, description="幻灯片数量")
    style: DesignStyle = Field(default=DesignStyle.BUSINESS, description="设计风格")
    language: str = Field(default="zh-CN", description="语言")
    reference_images: list[str] = Field(default_factory=list, description="参考图片路径列表")
    reference_documents: list[str] = Field(default_factory=list, description="参考文档路径列表")
    custom_instructions: str = Field(default="", description="自定义指令")
    brand_colors: list[str] = Field(default_factory=list, description="品牌色号列表")


# ============================================================
# Planning Models
# ============================================================

class SlideOutline(BaseModel):
    """Single slide outline produced by the Planner Agent."""
    slide_number: int
    slide_type: SlideType
    title: str
    key_points: list[str] = Field(default_factory=list)
    notes: str = Field(default="", description="演讲者备注提示")
    needs_image: bool = Field(default=False)
    image_description: str = Field(default="", description="配图描述（用于图片生成）")
    needs_chart: bool = Field(default=False)
    chart_description: str = Field(default="", description="图表描述")


class PresentationPlan(BaseModel):
    """The complete plan for the presentation."""
    title: str
    subtitle: str = ""
    narrative_arc: str = Field(default="", description="整体叙事主线")
    target_audience: str = ""
    slides: list[SlideOutline] = Field(default_factory=list)
    estimated_duration_minutes: int = Field(default=15)


# ============================================================
# Content Models
# ============================================================

class SlideContent(BaseModel):
    """Content for a single slide, produced by the Writer Agent."""
    slide_number: int
    title: str
    subtitle: str = ""
    body_text: str = Field(default="", description="正文文本/要点（Markdown 格式）")
    bullet_points: list[str] = Field(default_factory=list)
    notes: str = Field(default="", description="演讲者备注")
    data: Optional[dict[str, Any]] = Field(default=None, description="图表数据")


class PresentationContent(BaseModel):
    """All content for the entire presentation."""
    slides: list[SlideContent] = Field(default_factory=list)


# ============================================================
# Design Models
# ============================================================

class ColorPalette(BaseModel):
    """Color scheme for the presentation."""
    primary: str = Field(default="#1a73e8", description="主色")
    secondary: str = Field(default="#34a853", description="辅色")
    accent: str = Field(default="#fbbc04", description="强调色")
    background: str = Field(default="#ffffff", description="背景色")
    surface: str = Field(default="#f8f9fa", description="表面色")
    text_primary: str = Field(default="#202124", description="主要文字色")
    text_secondary: str = Field(default="#5f6368", description="次要文字色")


class FontScheme(BaseModel):
    """Typography configuration."""
    title_font: str = Field(default="微软雅黑", description="标题字体")
    body_font: str = Field(default="微软雅黑", description="正文字体")
    title_size_pt: int = Field(default=36)
    subtitle_size_pt: int = Field(default=24)
    body_size_pt: int = Field(default=18)
    caption_size_pt: int = Field(default=14)


class SlideLayout(BaseModel):
    """Layout specification for a single slide."""
    slide_number: int
    slide_type: SlideType
    layout_description: str = Field(default="", description="布局描述")
    elements: list[dict[str, Any]] = Field(default_factory=list, description="元素位置列表")


class DesignSpec(BaseModel):
    """Complete design specification for the presentation."""
    style: DesignStyle = DesignStyle.BUSINESS
    colors: ColorPalette = Field(default_factory=ColorPalette)
    fonts: FontScheme = Field(default_factory=FontScheme)
    slide_width_inches: float = Field(default=13.333)
    slide_height_inches: float = Field(default=7.5)
    layouts: list[SlideLayout] = Field(default_factory=list)
    use_gradient_backgrounds: bool = False
    corner_radius: int = Field(default=0, description="圆角半径")


# ============================================================
# Image Models
# ============================================================

class GeneratedImage(BaseModel):
    """Result of image generation for a slide."""
    slide_number: int
    image_path: str
    prompt_used: str = ""
    width: int = 0
    height: int = 0


# ============================================================
# Review Models
# ============================================================

class ReviewFeedback(BaseModel):
    """Feedback from the Reviewer Agent."""
    overall_score: float = Field(ge=0, le=10, description="总体评分 0-10")
    content_score: float = Field(ge=0, le=10)
    design_score: float = Field(ge=0, le=10)
    coherence_score: float = Field(ge=0, le=10)
    issues: list[str] = Field(default_factory=list, description="发现的问题")
    suggestions: list[str] = Field(default_factory=list, description="改进建议")
    slide_specific_feedback: dict[int, str] = Field(
        default_factory=dict, description="针对特定页的反馈"
    )
    approved: bool = Field(default=False, description="是否通过审查")


# ============================================================
# Output Models
# ============================================================

class GenerationResult(BaseModel):
    """Final result of PPT generation."""
    success: bool = True
    output_path: str = ""
    plan: Optional[PresentationPlan] = None
    design: Optional[DesignSpec] = None
    review: Optional[ReviewFeedback] = None
    error_message: str = ""
    generation_time_seconds: float = 0
    total_iterations: int = 0

    def save(self, path: str) -> None:
        """Convenience method; the file is already saved at output_path."""
        import shutil
        if self.output_path and self.output_path != path:
            shutil.copy2(self.output_path, path)
