"""
Image Agent — Generates, searches, and processes images for slides.

Uses multimodal model capabilities to:
1. Generate images via DALL-E 3 / Stability AI
2. Analyze reference images for style replication
3. Search for appropriate stock images
"""

from __future__ import annotations

import base64
import logging
from pathlib import Path

from slidecraft.agents.base import BaseAgent
from slidecraft.config import ImageProvider
from slidecraft.models import (
    DesignSpec,
    GeneratedImage,
    PresentationPlan,
)

logger = logging.getLogger("slidecraft")


class ImageAgent(BaseAgent):
    """Image agent that generates and processes images for slides."""

    name = "image_agent"
    description = "图片处理师，利用多模态模型生成/处理配图"

    @property
    def system_prompt(self) -> str:
        return """你是 SlideCraft-AI 的图片处理师（Image Agent），负责为 PPT 幻灯片生成和处理配图。

## 你的职责
1. 根据幻灯片内容描述，生成适合的配图提示词（DALL-E prompt）
2. 确保生成的图片与 PPT 整体设计风格一致
3. 图片应该是专业的、高质量的、与内容相关的

## 配图提示词设计原则
- 描述清晰具体，避免模糊描述
- 指定合适的艺术风格（如: flat illustration, isometric, photorealistic）
- 包含颜色偏好，与 PPT 配色方案一致
- 指定适合 PPT 的宽高比（通常 16:9 或 4:3）
- 避免包含文字（AI 生成的文字通常不准确）

## 风格映射
- business → professional corporate photography, clean lighting
- tech → futuristic digital art, neon accents, dark backgrounds
- minimal → simple geometric shapes, line art, muted colors
- creative → vibrant watercolor, hand-drawn style, playful
- academic → detailed diagrams, scholarly illustrations
- dark → dramatic lighting, high contrast, moody atmosphere
- gradient → smooth color transitions, abstract shapes

请以 JSON 格式返回图片生成的配置。"""

    async def generate_image_prompts(
        self,
        plan: PresentationPlan,
        design: DesignSpec,
    ) -> list[dict]:
        """Generate optimized image prompts for slides that need images."""
        slides_needing_images = [
            {
                "slide_number": s.slide_number,
                "title": s.title,
                "image_description": s.image_description,
                "slide_type": s.slide_type.value,
            }
            for s in plan.slides
            if s.needs_image
        ]

        if not slides_needing_images:
            return []

        import json

        prompt = f"""请为以下需要配图的幻灯片生成高质量的 DALL-E 提示词。

## 设计风格: {design.style.value}
## 配色方案:
- 主色: {design.colors.primary}
- 辅色: {design.colors.secondary}
- 背景: {design.colors.background}

## 需要配图的幻灯片
```json
{json.dumps(slides_needing_images, indent=2, ensure_ascii=False)}
```

请为每张幻灯片返回：
```json
[
  {{
    "slide_number": 1,
    "prompt": "详细的英文 DALL-E 提示词",
    "size": "1792x1024",
    "style": "natural"
  }}
]
```

注意：
1. 提示词必须是英文
2. 风格应与 PPT 整体设计一致
3. 避免在图片中包含任何文字
4. 选择适合幻灯片的构图"""

        raw = await self.invoke(prompt)

        # Parse the response
        raw = raw.strip()
        if "```" in raw:
            lines = raw.split("\n")
            json_lines = []
            in_block = False
            for line in lines:
                if line.strip().startswith("```") and not in_block:
                    in_block = True
                    continue
                if line.strip() == "```" and in_block:
                    break
                if in_block:
                    json_lines.append(line)
            raw = "\n".join(json_lines)

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(f"[{self.name}] Failed to parse image prompts, returning empty list")
            return []

    async def generate_images(
        self,
        prompts: list[dict],
        output_dir: str,
    ) -> list[GeneratedImage]:
        """Generate images using the configured image provider.

        This method calls the actual image generation API.
        """
        results = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for p in prompts:
            slide_num = p.get("slide_number", 0)
            img_prompt = p.get("prompt", "")
            size = p.get("size", "1792x1024")

            try:
                if self.config.image.provider == ImageProvider.OPENAI:
                    image_path = await self._generate_openai(
                        img_prompt, size, output_path, slide_num
                    )
                else:
                    image_path = await self._generate_placeholder(
                        img_prompt, output_path, slide_num
                    )

                results.append(GeneratedImage(
                    slide_number=slide_num,
                    image_path=str(image_path),
                    prompt_used=img_prompt,
                ))
                logger.info(f"[{self.name}] Generated image for slide {slide_num}")

            except Exception as e:
                logger.error(f"[{self.name}] Failed to generate image for slide {slide_num}: {e}")
                # Generate a placeholder instead
                placeholder = await self._generate_placeholder(
                    img_prompt, output_path, slide_num
                )
                results.append(GeneratedImage(
                    slide_number=slide_num,
                    image_path=str(placeholder),
                    prompt_used=img_prompt,
                ))

        return results

    async def _generate_openai(
        self, prompt: str, size: str, output_dir: Path, slide_num: int
    ) -> Path:
        """Generate image using OpenAI DALL-E."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.config.llm.openai_api_key)
        response = await client.images.generate(
            model=self.config.llm.openai_image_model,
            prompt=prompt,
            size=size,
            quality="hd",
            n=1,
            response_format="b64_json",
        )

        image_data = base64.b64decode(response.data[0].b64_json)
        image_path = output_dir / f"slide_{slide_num:02d}.png"
        image_path.write_bytes(image_data)
        return image_path

    async def _generate_placeholder(
        self, prompt: str, output_dir: Path, slide_num: int
    ) -> Path:
        """Generate a simple placeholder image when API is unavailable."""
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (1792, 1024), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)

        # Draw a centered placeholder text
        text = f"Slide {slide_num}\n{prompt[:60]}..."
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        except (OSError, IOError):
            font = ImageFont.load_default()

        draw.text((896, 512), text, fill=(150, 150, 150), anchor="mm", font=font)

        # Add a border
        draw.rectangle([(20, 20), (1772, 1004)], outline=(200, 200, 200), width=2)

        image_path = output_dir / f"slide_{slide_num:02d}_placeholder.png"
        img.save(str(image_path))
        return image_path
