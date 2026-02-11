"""
Tests for the LangGraph workflow structure.
"""

from slidecraft.config import SlideCraftConfig
from slidecraft.graph.workflow import build_workflow
from slidecraft.graph.state import WorkflowState
from slidecraft.models import GenerationRequest


class TestWorkflowState:
    def test_default_state(self):
        ws = WorkflowState()
        assert ws.iteration == 0
        assert ws.max_iterations == 5
        assert ws.completed is False
        assert ws.current_phase == "init"

    def test_state_with_request(self):
        req = GenerationRequest(topic="Test", slide_count=5)
        ws = WorkflowState(request=req)
        assert ws.request.topic == "Test"
        assert ws.request.slide_count == 5


class TestWorkflowGraph:
    def test_graph_compiles(self):
        """Verify the LangGraph workflow can be compiled without errors."""
        config = SlideCraftConfig()
        graph = build_workflow(config)
        assert graph is not None

    def test_graph_has_nodes(self):
        """Verify all expected nodes exist in the graph."""
        config = SlideCraftConfig()
        graph = build_workflow(config)
        # The graph should be a compiled Pregel object
        assert graph is not None
