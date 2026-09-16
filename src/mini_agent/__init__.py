"""Shared interfaces for the Mini Agent admission task."""

from .agent import Agent
from .contracts import (
    ModelClient,
    ModelReply,
    PermissionDecision,
    PermissionPolicy,
    RunResult,
    Tool,
    ToolCall,
)
from .fake_model import FakeModel

__all__ = [
    "Agent",
    "FakeModel",
    "ModelClient",
    "ModelReply",
    "PermissionDecision",
    "PermissionPolicy",
    "RunResult",
    "Tool",
    "ToolCall",
]

