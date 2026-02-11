"""
Tests for SlideCraft data models.
"""

import pytest
from slidecraft.models import (
    ColorPalette,
    DesignSpec,
    DesignStyle,
    FontScheme,
    GenerationRequest,
    GenerationResult,
    PresentationPlan,
    ReviewFeedback,
    SlideContent,
    SlideOutline,
    SlideType,
)


class TestSlideType:
    def test_all_types_exist(self):
        expected = [
            "cover", "toc", "section", "content", "two_column",
            "image_full", "image_text", "chart", "comparison",
            "timeline", "quote", "thank_you",
        ]
        for t in expected:
            assert SlideType(t) is not None

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            SlideType("nonexistent")


class TestDesignStyle:
    def test_all_styles_exist(self):
        expected = ["business", "tech", "minimal", "creative", "academic", "dark", "gradient"]
        for s in expected:
            assert DesignStyle(s) is not None


class TestGenerationRequest:
    def test_default_values(self):
        req = GenerationRequest(topic="Test Topic")
        assert req.topic == "Test Topic"
        assert req.slide_count == 10
        assert req.style == DesignStyle.BUSINESS
        assert req.language == "zh-CN"
        assert req.audience == "通用"

    def test_custom_values(self):
        req = GenerationRequest(
            topic="AI Trends",
            description="Deep dive into AI",
            audience="CTOs",
            slide_count=20,
            style=DesignStyle.TECH,
            language="en",
            brand_colors=["#FF0000", "#00FF00"],
        )
        assert req.slide_count == 20
        assert req.style == DesignStyle.TECH
        assert len(req.brand_colors) == 2

    def test_slide_count_validation(self):
        with pytest.raises(Exception):
            GenerationRequest(topic="Test", slide_count=0)
        with pytest.raises(Exception):
            GenerationRequest(topic="Test", slide_count=100)


class TestSlideOutline:
    def test_basic_outline(self):
        outline = SlideOutline(
            slide_number=1,
            slide_type=SlideType.COVER,
            title="Welcome",
            key_points=["Point 1", "Point 2"],
            needs_image=True,
            image_description="A futuristic city",
        )
        assert outline.slide_number == 1
        assert outline.slide_type == SlideType.COVER
        assert outline.needs_image is True
        assert len(outline.key_points) == 2


class TestPresentationPlan:
    def test_plan_creation(self):
        plan = PresentationPlan(
            title="Test Presentation",
            subtitle="A test",
            narrative_arc="Introduction → Analysis → Conclusion",
            slides=[
                SlideOutline(slide_number=1, slide_type=SlideType.COVER, title="Cover"),
                SlideOutline(slide_number=2, slide_type=SlideType.CONTENT, title="Content"),
                SlideOutline(slide_number=3, slide_type=SlideType.THANK_YOU, title="Thanks"),
            ],
        )
        assert len(plan.slides) == 3
        assert plan.title == "Test Presentation"

    def test_empty_plan(self):
        plan = PresentationPlan(title="Empty")
        assert len(plan.slides) == 0


class TestSlideContent:
    def test_content_creation(self):
        sc = SlideContent(
            slide_number=1,
            title="Introduction",
            subtitle="Getting Started",
            bullet_points=["Point A", "Point B", "Point C"],
            notes="Explain the context first",
        )
        assert sc.slide_number == 1
        assert len(sc.bullet_points) == 3
        assert sc.notes != ""


class TestColorPalette:
    def test_defaults(self):
        palette = ColorPalette()
        assert palette.primary.startswith("#")
        assert palette.background == "#ffffff"

    def test_custom_colors(self):
        palette = ColorPalette(primary="#FF0000", secondary="#00FF00")
        assert palette.primary == "#FF0000"


class TestDesignSpec:
    def test_defaults(self):
        spec = DesignSpec()
        assert spec.style == DesignStyle.BUSINESS
        assert spec.slide_width_inches == 13.333

    def test_custom_spec(self):
        spec = DesignSpec(
            style=DesignStyle.DARK,
            colors=ColorPalette(background="#111111"),
            fonts=FontScheme(title_font="Arial", body_font="Helvetica"),
            use_gradient_backgrounds=True,
        )
        assert spec.colors.background == "#111111"
        assert spec.fonts.title_font == "Arial"
        assert spec.use_gradient_backgrounds is True


class TestReviewFeedback:
    def test_approved(self):
        fb = ReviewFeedback(
            overall_score=8.5,
            content_score=9.0,
            design_score=8.0,
            coherence_score=8.5,
            approved=True,
        )
        assert fb.approved is True
        assert fb.overall_score >= 7

    def test_not_approved(self):
        fb = ReviewFeedback(
            overall_score=5.0,
            content_score=5.0,
            design_score=5.0,
            coherence_score=5.0,
            issues=["Too much text", "Colors clash"],
            suggestions=["Reduce text", "Use brand colors"],
            approved=False,
        )
        assert fb.approved is False
        assert len(fb.issues) == 2

    def test_score_validation(self):
        with pytest.raises(Exception):
            ReviewFeedback(
                overall_score=11,
                content_score=5,
                design_score=5,
                coherence_score=5,
            )


class TestGenerationResult:
    def test_success(self):
        result = GenerationResult(
            success=True,
            output_path="/tmp/test.pptx",
            generation_time_seconds=42.5,
            total_iterations=2,
        )
        assert result.success is True
        assert result.total_iterations == 2

    def test_failure(self):
        result = GenerationResult(
            success=False,
            error_message="API key missing",
        )
        assert result.success is False
        assert "API" in result.error_message
