"""
Tests for Agent base class and individual agents.
"""

import pytest
from slidecraft.config import SlideCraftConfig
from slidecraft.agents.planner import PlannerAgent
from slidecraft.agents.writer import WriterAgent
from slidecraft.agents.designer import DesignerAgent, STYLE_PALETTES
from slidecraft.agents.image_agent import ImageAgent
from slidecraft.agents.reviewer import ReviewerAgent
from slidecraft.agents.orchestrator import OrchestratorAgent
from slidecraft.agents.builder import BuilderAgent
from slidecraft.models import DesignStyle


@pytest.fixture
def config():
    return SlideCraftConfig()


class TestAgentInstantiation:
    """Test that all agents can be instantiated and have proper attributes."""

    def test_planner(self, config):
        agent = PlannerAgent(config)
        assert agent.name == "planner"
        assert "规划" in agent.description
        assert len(agent.system_prompt) > 100

    def test_writer(self, config):
        agent = WriterAgent(config)
        assert agent.name == "writer"
        assert "撰写" in agent.description

    def test_designer(self, config):
        agent = DesignerAgent(config)
        assert agent.name == "designer"
        assert "设计" in agent.description

    def test_image_agent(self, config):
        agent = ImageAgent(config)
        assert agent.name == "image_agent"
        assert "图片" in agent.description

    def test_reviewer(self, config):
        agent = ReviewerAgent(config)
        assert agent.name == "reviewer"
        assert "审查" in agent.description

    def test_orchestrator(self, config):
        agent = OrchestratorAgent(config)
        assert agent.name == "orchestrator"
        assert "总指挥" in agent.description

    def test_builder(self, config):
        agent = BuilderAgent(config)
        assert agent.name == "builder"
        assert "构建" in agent.description


class TestDesignerPalettes:
    """Test that all design styles have pre-defined palettes."""

    def test_all_styles_have_palettes(self):
        for style in DesignStyle:
            assert style in STYLE_PALETTES, f"Missing palette for {style.value}"

    def test_palettes_have_required_colors(self):
        required_keys = ["primary", "secondary", "accent", "background", "text_primary"]
        for style, palette in STYLE_PALETTES.items():
            for key in required_keys:
                assert key in palette, f"Missing {key} in {style.value} palette"
                assert palette[key].startswith("#"), f"Invalid color format in {style.value}.{key}"


class TestAgentRepr:
    def test_repr(self, config):
        agent = PlannerAgent(config)
        assert "PlannerAgent" in repr(agent)
        assert "planner" in repr(agent)
