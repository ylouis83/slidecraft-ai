"""
Workflow node functions for the SlideCraft LangGraph pipeline.

Each node function takes the current state, invokes the appropriate agent,
and returns state updates.
"""

from __future__ import annotations

import logging
from pathlib import Path

from slidecraft.agents.planner import PlannerAgent
from slidecraft.agents.writer import WriterAgent
from slidecraft.agents.designer import DesignerAgent
from slidecraft.agents.image_agent import ImageAgent
from slidecraft.agents.reviewer import ReviewerAgent
from slidecraft.agents.builder import BuilderAgent
from slidecraft.agents.builder_v2 import BuilderV2Agent
from slidecraft.config import SlideCraftConfig
from slidecraft.graph.state import WorkflowState

logger = logging.getLogger("slidecraft")


def create_nodes(config: SlideCraftConfig):
    """Create all node functions bound to the given config.

    Returns a dict of {node_name: async_function}.
    """

    planner = PlannerAgent(config)
    writer = WriterAgent(config)
    designer = DesignerAgent(config)
    image_agent = ImageAgent(config)
    reviewer = ReviewerAgent(config)
    builder = BuilderV2Agent(config) if config.use_builder_v2 else BuilderAgent(config)

    async def plan_node(state: dict) -> dict:
        """Planner Agent node."""
        logger.info("📋 [Planner] Generating presentation plan...")
        ws = WorkflowState(**state)
        try:
            plan = await planner.plan(ws.request)
            logger.info(f"📋 [Planner] Created plan with {len(plan.slides)} slides")
            return {"plan": plan, "current_phase": "planned"}
        except Exception as e:
            logger.error(f"📋 [Planner] Error: {e}")
            return {"error": str(e), "current_phase": "error"}

    async def write_node(state: dict) -> dict:
        """Writer Agent node."""
        logger.info("✍️  [Writer] Generating slide content...")
        ws = WorkflowState(**state)
        try:
            content = await writer.write(ws.plan, ws.request.language)
            logger.info(f"✍️  [Writer] Generated content for {len(content.slides)} slides")
            return {"content": content, "current_phase": "written"}
        except Exception as e:
            logger.error(f"✍️  [Writer] Error: {e}")
            return {"error": str(e), "current_phase": "error"}

    async def design_node(state: dict) -> dict:
        """Designer Agent node."""
        logger.info("🎨 [Designer] Creating design specification...")
        ws = WorkflowState(**state)
        try:
            ref_images = ws.request.reference_images if ws.request else []
            design = await designer.design(ws.plan, ws.request, ref_images or None)
            logger.info(f"🎨 [Designer] Design spec created: style={design.style.value}")
            return {"design": design, "current_phase": "designed"}
        except Exception as e:
            logger.error(f"🎨 [Designer] Error: {e}")
            return {"error": str(e), "current_phase": "error"}

    async def image_node(state: dict) -> dict:
        """Image Agent node."""
        logger.info("🖼️  [Image] Generating slide images...")
        ws = WorkflowState(**state)
        try:
            prompts = await image_agent.generate_image_prompts(ws.plan, ws.design)
            output_dir = str(Path(config.output_dir) / "images")
            images = await image_agent.generate_images(prompts, output_dir)
            logger.info(f"🖼️  [Image] Generated {len(images)} images")
            return {
                "image_prompts": prompts,
                "images": images,
                "current_phase": "images_generated",
            }
        except Exception as e:
            logger.error(f"🖼️  [Image] Error: {e}")
            return {"images": [], "current_phase": "images_generated"}

    def build_node(state: dict) -> dict:
        """Builder Agent node (synchronous)."""
        logger.info(f"🔧 [{builder.name}] Assembling .pptx file...")
        ws = WorkflowState(**state)
        try:
            out_dir = Path(config.output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(out_dir / f"{ws.plan.title}.pptx")
            path = builder.build(ws.plan, ws.content, ws.design, ws.images, output_path)
            logger.info(f"🔧 [{builder.name}] Built presentation: {path}")
            return {"output_path": path, "current_phase": "built"}
        except Exception as e:
            logger.error(f"🔧 [{builder.name}] Error: {e}")
            return {"error": str(e), "current_phase": "error"}

    async def review_node(state: dict) -> dict:
        """Reviewer Agent node."""
        logger.info("🔍 [Reviewer] Reviewing presentation quality...")
        ws = WorkflowState(**state)
        try:
            review = await reviewer.review(ws.plan, ws.content, ws.design)
            iteration = ws.iteration + 1
            quality_passed = (
                review.overall_score >= config.quality_gate_min_overall
                and review.content_score >= config.quality_gate_min_dimension
                and review.design_score >= config.quality_gate_min_dimension
                and review.coherence_score >= config.quality_gate_min_dimension
            )
            review.approved = quality_passed

            updates = {
                "review": review,
                "iteration": iteration,
                "current_phase": "reviewed",
            }
            if (
                config.fail_on_quality_gate
                and not quality_passed
                and iteration >= ws.max_iterations
            ):
                updates["error"] = (
                    "质量门槛未达标: "
                    f"overall={review.overall_score:.1f}, "
                    f"content={review.content_score:.1f}, "
                    f"design={review.design_score:.1f}, "
                    f"coherence={review.coherence_score:.1f}; "
                    f"门槛为 overall>={config.quality_gate_min_overall:.1f} 且 "
                    f"各维度>={config.quality_gate_min_dimension:.1f}"
                )

            logger.info(
                f"🔍 [Reviewer] Score: {review.overall_score}/10 "
                f"(iteration {iteration}/{ws.max_iterations}) "
                f"{'✅ Approved' if review.approved else '❌ Needs revision'}"
            )
            return updates
        except Exception as e:
            logger.error(f"🔍 [Reviewer] Error: {e}")
            return {"current_phase": "reviewed", "iteration": ws.iteration + 1}

    def should_continue(state: dict) -> str:
        """Conditional edge: decide whether to iterate or finish."""
        ws = WorkflowState(**state)
        if ws.review and ws.review.approved:
            return "complete"
        if ws.iteration >= ws.max_iterations:
            logger.info("⚠️  Max iterations reached, completing...")
            return "complete"
        if ws.error:
            return "complete"
        return "revise"

    def complete_node(state: dict) -> dict:
        """Final node — marks workflow as complete."""
        logger.info("✅ [Complete] Workflow finished!")
        return {"completed": True, "current_phase": "complete"}

    return {
        "plan": plan_node,
        "write": write_node,
        "design": design_node,
        "image": image_node,
        "build": build_node,
        "review": review_node,
        "should_continue": should_continue,
        "complete": complete_node,
    }
