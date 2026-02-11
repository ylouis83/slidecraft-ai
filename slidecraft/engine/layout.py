"""
Layout Engine — Smart auto-positioning based on content size.

The Layout Engine solves the core problem of the old Builder:
  hardcoded positions that don't adapt to content.

Key capabilities:
  1. Auto-fit font size based on text length
  2. Smart bullet spacing based on item count
  3. Content-aware column sizing
  4. Overflow detection and correction
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from slidecraft.engine.elements import (
    Position,
    SlideElement,
    SlideSpec,
    ElementType,
    TextStyle,
)


# ── Constants ─────────────────────────────────────────────────

SLIDE_W = 13.333  # inches
SLIDE_H = 7.5
MARGIN = 0.8
CONTENT_TOP = 1.5
TITLE_HEIGHT = 0.9
TOP_BAR_HEIGHT = 0.06


@dataclass
class ContentMetrics:
    """Measured properties of slide content."""
    title_chars: int = 0
    bullet_count: int = 0
    max_bullet_chars: int = 0
    total_text_chars: int = 0
    has_image: bool = False
    has_chart: bool = False
    body_text_chars: int = 0

    @property
    def content_density(self) -> float:
        """0.0 (empty) to 1.0 (very dense) content density score."""
        score = 0.0
        score += min(self.bullet_count / 8, 1.0) * 0.4
        score += min(self.total_text_chars / 500, 1.0) * 0.3
        score += (0.2 if self.has_image else 0.0)
        score += (0.1 if self.has_chart else 0.0)
        return min(score, 1.0)


def measure_content(spec: SlideSpec) -> ContentMetrics:
    """Analyze a SlideSpec to compute content metrics."""
    m = ContentMetrics()
    for el in spec.elements:
        if el.element_type == ElementType.TITLE:
            m.title_chars = len(el.content)
        elif el.element_type == ElementType.BULLETS:
            m.bullet_count = len(el.items)
            m.max_bullet_chars = max((len(b) for b in el.items), default=0)
            m.total_text_chars += sum(len(b) for b in el.items)
        elif el.element_type == ElementType.TEXT:
            m.body_text_chars = len(el.content)
            m.total_text_chars += len(el.content)
        elif el.element_type == ElementType.IMAGE:
            m.has_image = True
        elif el.element_type == ElementType.CHART:
            m.has_chart = True
    return m


# ══════════════════════════════════════════════════════════════
#  Auto-fit functions
# ══════════════════════════════════════════════════════════════

def auto_fit_title_size(text: str, base_size: float = 36) -> float:
    """Adjust title font size based on character count.

    Short titles get larger fonts for impact;
    long titles get smaller fonts to fit.
    """
    n = len(text)
    if n <= 8:
        return base_size + 6      # Very short → bigger impact
    elif n <= 15:
        return base_size + 2
    elif n <= 25:
        return base_size
    elif n <= 40:
        return base_size - 4
    else:
        return max(base_size - 8, 20)


def auto_fit_bullet_size(
    items: list[str],
    base_size: float = 18,
    available_height: float = 5.0,
) -> float:
    """Adjust bullet font size so all items fit in the available space.

    Uses a simple model: each bullet needs ~(font_size * 2) points of
    vertical space (line + spacing).
    """
    if not items:
        return base_size

    n = len(items)
    max_chars = max(len(b) for b in items)

    # Vertical constraint
    # available_height in inches = available_height * 72 points
    available_pts = available_height * 72
    max_size_by_count = available_pts / (n * 2.2)

    # Horizontal constraint (rough: ~1.2 chars per point at body size)
    # Not as binding usually, but check for very long bullets
    max_size_by_width = base_size  # default, only reduce for very long bullets
    if max_chars > 60:
        max_size_by_width = base_size - 2
    if max_chars > 80:
        max_size_by_width = base_size - 4

    fitted = min(base_size, max_size_by_count, max_size_by_width)
    return max(fitted, 12)  # Never go below 12pt


def auto_fit_spacing(
    item_count: int,
    available_height: float = 5.0,
    font_size: float = 18,
) -> float:
    """Calculate optimal spacing (in points) between bullet items."""
    if item_count <= 0:
        return 12

    available_pts = available_height * 72
    per_item = available_pts / item_count
    spacing = per_item - font_size * 1.3  # subtract line height

    return max(min(spacing, 24), 4)  # clamp to [4, 24] points


# ══════════════════════════════════════════════════════════════
#  Layout computation
# ══════════════════════════════════════════════════════════════

def compute_content_layout(
    metrics: ContentMetrics,
    has_image: bool = False,
    slide_width: float = SLIDE_W,
) -> dict:
    """Compute optimal layout positions for a content slide.

    Returns a dict of named positions that the renderer can use.
    """
    layout = {}

    # Title area
    layout["title"] = Position(
        left=MARGIN, top=0.4,
        width=slide_width - 2 * MARGIN, height=TITLE_HEIGHT,
    )

    # Content area — depends on whether there's an image
    if has_image:
        # Split: 55% text, 40% image, 5% gap
        text_width = (slide_width - 2 * MARGIN) * 0.55
        img_width = (slide_width - 2 * MARGIN) * 0.38
        gap = (slide_width - 2 * MARGIN) * 0.05

        layout["content"] = Position(
            left=MARGIN, top=CONTENT_TOP,
            width=text_width, height=5.2,
        )
        layout["image"] = Position(
            left=MARGIN + text_width + gap, top=CONTENT_TOP,
            width=img_width, height=5.2,
        )
    else:
        layout["content"] = Position(
            left=MARGIN, top=CONTENT_TOP,
            width=slide_width - 2 * MARGIN, height=5.2,
        )

    return layout


def compute_two_column_layout(
    left_items: int,
    right_items: int,
    slide_width: float = SLIDE_W,
) -> dict:
    """Compute layout for two-column slides.

    Adjusts column widths based on content balance.
    """
    usable = slide_width - 2 * MARGIN
    gap = 0.4  # gap between columns

    total = left_items + right_items
    if total == 0:
        ratio = 0.5
    else:
        # Weighted ratio, but clamped to avoid extreme asymmetry
        ratio = max(0.35, min(0.65, left_items / total))

    left_w = (usable - gap) * ratio
    right_w = (usable - gap) * (1 - ratio)

    return {
        "left_card": Position(
            left=MARGIN, top=CONTENT_TOP,
            width=left_w, height=5.2,
        ),
        "right_card": Position(
            left=MARGIN + left_w + gap, top=CONTENT_TOP,
            width=right_w, height=5.2,
        ),
        "divider_x": MARGIN + left_w + gap / 2,
    }


def compute_timeline_positions(
    milestone_count: int,
    slide_width: float = SLIDE_W,
) -> list[dict]:
    """Compute positions for timeline milestones."""
    n = max(milestone_count, 1)
    usable = slide_width - 2 * MARGIN
    spacing = usable / n
    bar_y = 3.8

    milestones = []
    for i in range(n):
        cx = MARGIN + spacing * i + spacing / 2
        milestones.append({
            "cx": cx,
            "bar_y": bar_y,
            "label_y_above": bar_y - 1.5,
            "label_y_below": bar_y + 0.5,
            "label_width": spacing - 0.2,
            "is_above": (i % 2 == 0),
        })

    return milestones
