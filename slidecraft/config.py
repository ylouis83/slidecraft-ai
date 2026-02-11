"""
SlideCraft Configuration Management
Supports .env files and environment variables
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class ImageProvider(str, Enum):
    OPENAI = "openai"
    STABILITY = "stability"


@dataclass
class LLMConfig:
    """LLM provider configuration."""

    provider: LLMProvider = LLMProvider.OPENAI

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_image_model: str = "dall-e-3"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Google
    google_api_key: str = ""
    google_model: str = "gemini-2.0-flash"

    @property
    def active_model(self) -> str:
        if self.provider == LLMProvider.OPENAI:
            return self.openai_model
        elif self.provider == LLMProvider.ANTHROPIC:
            return self.anthropic_model
        elif self.provider == LLMProvider.GOOGLE:
            return self.google_model
        return self.openai_model

    @property
    def active_api_key(self) -> str:
        if self.provider == LLMProvider.OPENAI:
            return self.openai_api_key
        elif self.provider == LLMProvider.ANTHROPIC:
            return self.anthropic_api_key
        elif self.provider == LLMProvider.GOOGLE:
            return self.google_api_key
        return ""


@dataclass
class ImageConfig:
    """Image generation configuration."""

    provider: ImageProvider = ImageProvider.OPENAI
    stability_api_key: str = ""


@dataclass
class SlideCraftConfig:
    """Top-level configuration for SlideCraft."""

    llm: LLMConfig = field(default_factory=LLMConfig)
    image: ImageConfig = field(default_factory=ImageConfig)
    output_dir: str = "./output"
    default_language: str = "zh-CN"
    log_level: str = "INFO"
    max_iterations: int = 5  # Maximum review-revise iterations
    enable_human_review: bool = False  # Human-in-the-loop
    use_builder_v2: bool = True  # Use enhanced rendering engine by default
    quality_gate_min_overall: float = 9.5  # Minimum overall score required
    quality_gate_min_dimension: float = 9.5  # Minimum score per dimension required
    fail_on_quality_gate: bool = True  # Mark run as failed if gate unmet after max iterations

    @classmethod
    def from_env(cls, env_path: Optional[str | Path] = None) -> SlideCraftConfig:
        """Load configuration from environment variables / .env file."""
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        llm = LLMConfig(
            provider=LLMProvider(os.getenv("SLIDECRAFT_LLM_PROVIDER", "openai")),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            openai_image_model=os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            google_model=os.getenv("GOOGLE_MODEL", "gemini-2.0-flash"),
        )

        image = ImageConfig(
            provider=ImageProvider(os.getenv("IMAGE_PROVIDER", "openai")),
            stability_api_key=os.getenv("STABILITY_API_KEY", ""),
        )

        return cls(
            llm=llm,
            image=image,
            output_dir=os.getenv("OUTPUT_DIR", "./output"),
            default_language=os.getenv("DEFAULT_LANGUAGE", "zh-CN"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_iterations=int(os.getenv("MAX_ITERATIONS", "5")),
            use_builder_v2=os.getenv("USE_BUILDER_V2", "true").lower() == "true",
            quality_gate_min_overall=float(os.getenv("QUALITY_GATE_MIN_OVERALL", "9.5")),
            quality_gate_min_dimension=float(os.getenv("QUALITY_GATE_MIN_DIMENSION", "9.5")),
            fail_on_quality_gate=os.getenv("FAIL_ON_QUALITY_GATE", "true").lower() == "true",
        )
