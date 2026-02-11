"""
LangGraph Workflow Definition for SlideCraft.

Defines the directed acyclic graph that orchestrates the multi-agent pipeline:

    ┌──────┐
    │ Plan │
    └──┬───┘
       │
    ┌──┴────────┐
    │  Write &   │  (parallel)
    │  Design    │
    └──┬────────┘
       │
    ┌──┴──┐
    │Image│
    └──┬──┘
       │
    ┌──┴──┐
    │Build│
    └──┬──┘
       │
    ┌──┴───┐       ┌────────┐
    │Review│──no──→│ Write  │ (revise loop)
    └──┬───┘       └────────┘
       │yes
    ┌──┴────┐
    │Complete│
    └───────┘
"""

from __future__ import annotations

from langgraph.graph import StateGraph, END

from slidecraft.config import SlideCraftConfig
from slidecraft.graph.nodes import create_nodes


def build_workflow(config: SlideCraftConfig) -> StateGraph:
    """Build and return the compiled LangGraph workflow."""
    nodes = create_nodes(config)

    # Define the graph with a dict state
    graph = StateGraph(dict)

    # Add nodes
    graph.add_node("plan", nodes["plan"])
    graph.add_node("write", nodes["write"])
    graph.add_node("design", nodes["design"])
    graph.add_node("image", nodes["image"])
    graph.add_node("build", nodes["build"])
    graph.add_node("review", nodes["review"])
    graph.add_node("complete", nodes["complete"])

    # Set entry point
    graph.set_entry_point("plan")

    # Define edges
    # Plan → Write & Design (sequential for now; can be parallelized)
    graph.add_edge("plan", "write")
    graph.add_edge("write", "design")
    graph.add_edge("design", "image")
    graph.add_edge("image", "build")
    graph.add_edge("build", "review")

    # Conditional: Review → Complete or Revise
    graph.add_conditional_edges(
        "review",
        nodes["should_continue"],
        {
            "complete": "complete",
            "revise": "write",  # Loop back to write for revision
        },
    )

    graph.add_edge("complete", END)

    return graph.compile()
