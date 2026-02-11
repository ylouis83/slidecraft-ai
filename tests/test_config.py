"""
Tests for SlideCraft configuration management.
"""

from slidecraft.config import (
    ImageConfig,
    ImageProvider,
    LLMConfig,
    LLMProvider,
    SlideCraftConfig,
)


class TestLLMConfig:
    def test_defaults(self):
        cfg = LLMConfig()
        assert cfg.provider == LLMProvider.OPENAI
        assert cfg.openai_model == "gpt-4o"
        assert cfg.anthropic_model == "claude-3-5-sonnet-20241022"
        assert cfg.google_model == "gemini-2.0-flash"

    def test_active_model_openai(self):
        cfg = LLMConfig(provider=LLMProvider.OPENAI, openai_model="gpt-4o-mini")
        assert cfg.active_model == "gpt-4o-mini"

    def test_active_model_anthropic(self):
        cfg = LLMConfig(provider=LLMProvider.ANTHROPIC)
        assert cfg.active_model == "claude-3-5-sonnet-20241022"

    def test_active_model_google(self):
        cfg = LLMConfig(provider=LLMProvider.GOOGLE)
        assert cfg.active_model == "gemini-2.0-flash"

    def test_active_api_key(self):
        cfg = LLMConfig(
            provider=LLMProvider.OPENAI,
            openai_api_key="test-openai-key",
        )
        assert cfg.active_api_key == "test-openai-key"


class TestSlideCraftConfig:
    def test_defaults(self):
        cfg = SlideCraftConfig()
        assert cfg.max_iterations == 5
        assert cfg.enable_human_review is False
        assert cfg.default_language == "zh-CN"
        assert cfg.use_builder_v2 is True
        assert cfg.quality_gate_min_overall == 9.5
        assert cfg.quality_gate_min_dimension == 9.5
        assert cfg.fail_on_quality_gate is True

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("SLIDECRAFT_LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
        monkeypatch.setenv("OUTPUT_DIR", "/tmp/output")
        monkeypatch.setenv("DEFAULT_LANGUAGE", "en")
        monkeypatch.setenv("MAX_ITERATIONS", "4")
        monkeypatch.setenv("USE_BUILDER_V2", "false")
        monkeypatch.setenv("QUALITY_GATE_MIN_OVERALL", "9.2")
        monkeypatch.setenv("QUALITY_GATE_MIN_DIMENSION", "9.0")
        monkeypatch.setenv("FAIL_ON_QUALITY_GATE", "false")

        cfg = SlideCraftConfig.from_env()
        assert cfg.llm.provider == LLMProvider.ANTHROPIC
        assert cfg.llm.anthropic_api_key == "test-anthropic-key"
        assert cfg.output_dir == "/tmp/output"
        assert cfg.default_language == "en"
        assert cfg.max_iterations == 4
        assert cfg.use_builder_v2 is False
        assert cfg.quality_gate_min_overall == 9.2
        assert cfg.quality_gate_min_dimension == 9.0
        assert cfg.fail_on_quality_gate is False

    def test_image_config(self):
        cfg = ImageConfig(provider=ImageProvider.STABILITY, stability_api_key="test-stability-key")
        assert cfg.provider == ImageProvider.STABILITY
        assert cfg.stability_api_key == "test-stability-key"
