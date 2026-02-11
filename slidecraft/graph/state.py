"""
Global workflow state definition for the SlideCraft LangGraph pipeline.

The state flows through nodes and accumulates results from each agent.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from slidecraft.models import (
    DesignSpec,
    GeneratedImage,
    GenerationRequest,
    PresentationContent,
    PresentationPlan,
    ReviewFeedback,
)


class WorkflowState(BaseModel):
    """The global state shared across all workflow nodes.

    Each agent node reads from and writes to specific fields.
    The Orchestrator coordinates state transitions.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # ── Input ──
    request: Optional[GenerationRequest] = None

    # ── Planner output ──
    plan: Optional[PresentationPlan] = None

    # ── Writer output ──
    content: Optional[PresentationContent] = None

    # ── Designer output ──
    design: Optional[DesignSpec] = None

    # ── Image Agent output ──
    image_prompts: list[dict] = Field(default_factory=list)
    images: list[GeneratedImage] = Field(default_factory=list)

    # ── Builder output ──
    output_path: str = ""

    # ── Reviewer output ──
    review: Optional[ReviewFeedback] = None

    # ── Control flow ──
    iteration: int = 0
    max_iterations: int = 5
    current_phase: str = "init"
    error: str = ""
    completed: bool = False
