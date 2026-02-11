"""
Slide Element DSL — 幻灯片元素声明式描述语言

Design philosophy:
  Instead of imperatively calling python-pptx methods, agents describe
  WHAT should appear on each slide using structured `SlideElement` objects.
  The Rendering Engine then translates these into actual pptx shapes.

This approach allows:
  1. LLM agents to output layout specs (via JSON) without writing code
  2. Smart auto-layout based on content size
  3. Consistent styling across all elements
  4. Easy serialization/deserialization for review and revision
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field


class ElementType(str, Enum):
    """Types of elements that can be placed on a slide."""
    TEXT = "text"
    TITLE = "title"
    SUBTITLE = "subtitle"
    BULLETS = "bullets"
    IMAGE = "image"
    SHAPE = "shape"
    CHART = "chart"
    DIVIDER = "divider"
    ICON_CARD = "icon_card"
    SPACER = "spacer"


class Position(BaseModel):
    """Position of an element in inches (relative to slide)."""
    left: float = 0.0
    top: float = 0.0
    width: float = 10.0
    height: float = 1.0

    def shift(self, dx: float = 0, dy: float = 0) -> "Position":
        return Position(
            left=self.left + dx,
            top=self.top + dy,
            width=self.width,
            height=self.height,
        )


class TextStyle(BaseModel):
    """Styling for text elements."""
    font_size: Optional[float] = None        # If None, auto-calculated
    bold: bool = False
    italic: bool = False
    alignment: str = "left"                   # left, center, right
    color: Optional[str] = None               # hex, or None = use theme
    line_spacing: float = 1.2
    auto_fit: bool = True                     # Auto-shrink if overflow


class ShapeStyle(BaseModel):
    """Styling for shape elements."""
    fill_color: Optional[str] = None          # hex, None = transparent
    border_color: Optional[str] = None
    border_width: float = 0.0
    corner_radius: float = 0.0               # inches, 0 = sharp corners
    shadow: bool = False
    shadow_offset: float = 3.0               # points
    opacity: float = 1.0                     # 0.0 - 1.0


class GradientStop(BaseModel):
    """A single color stop in a gradient."""
    color: str                               # hex color
    position: float                          # 0.0 - 1.0


class GradientSpec(BaseModel):
    """Gradient fill specification."""
    angle: float = 270.0                     # degrees, 270 = top-to-bottom
    stops: list[GradientStop] = Field(default_factory=list)


class SlideElement(BaseModel):
    """A single element on a slide — the atomic unit of the DSL."""
    element_type: ElementType
    position: Position = Field(default_factory=Position)
    content: str = ""                         # Text content or image path
    items: list[str] = Field(default_factory=list)  # For bullets
    text_style: TextStyle = Field(default_factory=TextStyle)
    shape_style: ShapeStyle = Field(default_factory=ShapeStyle)
    z_order: int = 0                          # Layer ordering
    name: str = ""                            # Optional semantic name

    # Chart-specific
    chart_data: Optional[dict] = None

    # Shape-specific
    shape_type: str = "rectangle"             # rectangle, oval, rounded_rect


class SlideSpec(BaseModel):
    """Complete specification for a single slide.

    This is the intermediate representation that sits between
    the content/design agents and the rendering engine.
    """
    slide_number: int = 1
    layout_type: str = "content"
    background_color: Optional[str] = None
    background_gradient: Optional[GradientSpec] = None
    elements: list[SlideElement] = Field(default_factory=list)
    notes: str = ""
    transition: str = "none"                  # fade, push, wipe, none

    def add(self, element: SlideElement) -> "SlideSpec":
        """Fluent API for adding elements."""
        self.elements.append(element)
        return self


class PresentationSpec(BaseModel):
    """Complete specification for an entire presentation."""
    title: str = ""
    slide_width: float = 13.333
    slide_height: float = 7.5
    slides: list[SlideSpec] = Field(default_factory=list)


# ══════════════════════════════════════════════════════════════
#  Convenience builders — fluent API for creating elements
# ══════════════════════════════════════════════════════════════

def title_element(
    text: str,
    left: float = 0.8, top: float = 0.4,
    width: float = 11.0, height: float = 0.9,
    font_size: float = 36, color: Optional[str] = None,
) -> SlideElement:
    """Create a title text element."""
    return SlideElement(
        element_type=ElementType.TITLE,
        position=Position(left=left, top=top, width=width, height=height),
        content=text,
        text_style=TextStyle(font_size=font_size, bold=True, color=color),
        name="title",
    )


def subtitle_element(
    text: str,
    left: float = 0.8, top: float = 1.3,
    width: float = 11.0, height: float = 0.6,
    font_size: float = 22, color: Optional[str] = None,
) -> SlideElement:
    """Create a subtitle text element."""
    return SlideElement(
        element_type=ElementType.SUBTITLE,
        position=Position(left=left, top=top, width=width, height=height),
        content=text,
        text_style=TextStyle(font_size=font_size, color=color),
        name="subtitle",
    )


def text_element(
    text: str,
    left: float = 0.8, top: float = 1.5,
    width: float = 11.5, height: float = 5.0,
    font_size: float = 18, color: Optional[str] = None,
    alignment: str = "left", auto_fit: bool = True,
) -> SlideElement:
    """Create a body text element."""
    return SlideElement(
        element_type=ElementType.TEXT,
        position=Position(left=left, top=top, width=width, height=height),
        content=text,
        text_style=TextStyle(
            font_size=font_size, color=color,
            alignment=alignment, auto_fit=auto_fit,
        ),
    )


def bullets_element(
    items: list[str],
    left: float = 0.8, top: float = 1.5,
    width: float = 11.5, height: float = 5.0,
    font_size: Optional[float] = None, color: Optional[str] = None,
) -> SlideElement:
    """Create a bullet-point list element."""
    return SlideElement(
        element_type=ElementType.BULLETS,
        position=Position(left=left, top=top, width=width, height=height),
        items=items,
        text_style=TextStyle(font_size=font_size, color=color, auto_fit=True),
    )


def shape_element(
    shape_type: str = "rectangle",
    left: float = 0, top: float = 0,
    width: float = 13.333, height: float = 1.0,
    fill_color: Optional[str] = None,
    border_color: Optional[str] = None,
    shadow: bool = False,
    corner_radius: float = 0,
) -> SlideElement:
    """Create a shape (rectangle, oval, etc.)."""
    return SlideElement(
        element_type=ElementType.SHAPE,
        position=Position(left=left, top=top, width=width, height=height),
        shape_type=shape_type,
        shape_style=ShapeStyle(
            fill_color=fill_color,
            border_color=border_color,
            shadow=shadow,
            corner_radius=corner_radius,
        ),
    )


def image_element(
    path: str,
    left: float = 0, top: float = 0,
    width: float = 5.0, height: float = 5.0,
) -> SlideElement:
    """Create an image element."""
    return SlideElement(
        element_type=ElementType.IMAGE,
        position=Position(left=left, top=top, width=width, height=height),
        content=path,
        name="image",
    )


def divider_element(
    left: float = 0.8, top: float = 1.3,
    width: float = 2.5, height: float = 0.04,
    color: Optional[str] = None,
) -> SlideElement:
    """Create a horizontal divider line."""
    return SlideElement(
        element_type=ElementType.DIVIDER,
        position=Position(left=left, top=top, width=width, height=height),
        shape_style=ShapeStyle(fill_color=color),
    )
