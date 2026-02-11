"""
SlideCraft Core — The main entry point for the framework.

Provides a simple API:
    craft = SlideCraft()
    result = craft.generate(topic="...", ...)
"""

from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel

from slidecraft.config import SlideCraftConfig
from slidecraft.graph.workflow import build_workflow
from slidecraft.models import (
    DesignStyle,
    GenerationRequest,
    GenerationResult,
)

console = Console()


def _setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)],
    )


class SlideCraft:
    """Main SlideCraft-AI interface.

    Usage:
        craft = SlideCraft()
        result = craft.generate(topic="AI Trends 2025", slide_count=10)
        result.save("output.pptx")
    """

    def __init__(self, config: Optional[SlideCraftConfig] = None):
        self.config = config or SlideCraftConfig.from_env()
        _setup_logging(self.config.log_level)
        self.logger = logging.getLogger("slidecraft")

    def generate(
        self,
        topic: str,
        description: str = "",
        audience: str = "通用",
        slide_count: int = 10,
        style: str | DesignStyle = DesignStyle.BUSINESS,
        language: str = "",
        reference_images: list[str] | None = None,
        reference_documents: list[str] | None = None,
        custom_instructions: str = "",
        brand_colors: list[str] | None = None,
    ) -> GenerationResult:
        """Generate a PPT from natural language description.

        Args:
            topic: The main topic of the presentation.
            description: Additional context or details.
            audience: Target audience (e.g., "企业CTO", "大学生").
            slide_count: Number of slides to generate.
            style: Design style — one of DesignStyle enum values.
            language: Language code (defaults to config).
            reference_images: Paths to reference images.
            reference_documents: Paths to reference documents.
            custom_instructions: Any special instructions.
            brand_colors: Brand hex colors to incorporate.

        Returns:
            GenerationResult with the output .pptx path.
        """
        if isinstance(style, str):
            try:
                style = DesignStyle(style)
            except ValueError:
                style = DesignStyle.BUSINESS

        request = GenerationRequest(
            topic=topic,
            description=description,
            audience=audience,
            slide_count=slide_count,
            style=style,
            language=language or self.config.default_language,
            reference_images=reference_images or [],
            reference_documents=reference_documents or [],
            custom_instructions=custom_instructions,
            brand_colors=brand_colors or [],
        )

        return asyncio.run(self._run(request))

    async def _run(self, request: GenerationRequest) -> GenerationResult:
        """Execute the multi-agent workflow."""
        start = time.time()

        console.print(Panel(
            f"[bold]🎨 SlideCraft-AI[/bold]\n\n"
            f"主题: {request.topic}\n"
            f"受众: {request.audience}\n"
            f"页数: {request.slide_count}\n"
            f"风格: {request.style.value}",
            title="开始生成",
            border_style="bright_blue",
        ))

        try:
            workflow = build_workflow(self.config)

            initial_state = {
                "request": request,
                "plan": None,
                "content": None,
                "design": None,
                "image_prompts": [],
                "images": [],
                "output_path": "",
                "review": None,
                "iteration": 0,
                "max_iterations": self.config.max_iterations,
                "current_phase": "init",
                "error": "",
                "completed": False,
            }

            # Run the workflow
            final_state = await workflow.ainvoke(initial_state)

            elapsed = time.time() - start

            result = GenerationResult(
                success=not final_state.get("error"),
                output_path=final_state.get("output_path", ""),
                plan=final_state.get("plan"),
                design=final_state.get("design"),
                review=final_state.get("review"),
                error_message=final_state.get("error", ""),
                generation_time_seconds=round(elapsed, 2),
                total_iterations=final_state.get("iteration", 0),
            )

            if result.success:
                console.print(Panel(
                    f"[green]✅ 生成成功！[/green]\n\n"
                    f"输出文件: {result.output_path}\n"
                    f"用时: {result.generation_time_seconds}s\n"
                    f"迭代次数: {result.total_iterations}",
                    title="完成",
                    border_style="green",
                ))
            else:
                console.print(Panel(
                    f"[red]❌ 生成失败[/red]\n{result.error_message}",
                    title="错误",
                    border_style="red",
                ))

            return result

        except Exception as e:
            elapsed = time.time() - start
            self.logger.error(f"Workflow error: {e}", exc_info=True)
            return GenerationResult(
                success=False,
                error_message=str(e),
                generation_time_seconds=round(elapsed, 2),
            )

    def generate_from_image(
        self,
        image_path: str,
        topic: str = "",
        replicate_style: bool = True,
        **kwargs,
    ) -> GenerationResult:
        """Generate PPT using a reference image for style."""
        return self.generate(
            topic=topic or "基于参考图片的演示文稿",
            reference_images=[image_path],
            custom_instructions=(
                "请分析参考图片的设计风格，尽可能复刻其视觉效果" if replicate_style else ""
            ),
            **kwargs,
        )

    def generate_from_document(
        self,
        document_path: str,
        style: str | DesignStyle = DesignStyle.MINIMAL,
        **kwargs,
    ) -> GenerationResult:
        """Generate PPT from a document (PDF, DOCX, MD)."""
        return self.generate(
            topic=f"基于文档 {Path(document_path).name} 的演示文稿",
            reference_documents=[document_path],
            style=style,
            **kwargs,
        )
