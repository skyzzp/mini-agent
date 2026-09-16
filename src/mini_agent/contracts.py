from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Mapping, Protocol


@dataclass(frozen=True)
class ToolCall:
    """A provider-neutral request from the model to execute one tool."""

    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModelReply:
    """A provider-neutral model response."""

    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


class ModelClient(Protocol):
    """The Agent depends on this interface instead of a concrete model SDK."""

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelReply:
        ...


@dataclass(frozen=True)
class Tool:
    """A tool definition advertised to the model and executed by the Harness."""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., str]
    consequential: bool = False

    def as_model_spec(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    reason: str = ""


class PermissionPolicy(Protocol):
    """Injected so automated tests never need to call input()."""

    def decide(
        self,
        tool: Tool,
        arguments: Mapping[str, Any],
    ) -> PermissionDecision:
        ...


RunStatus = Literal["completed", "max_steps", "model_error"]


@dataclass
class RunResult:
    status: RunStatus
    output: str
    messages: list[dict[str, Any]]
    steps: int

