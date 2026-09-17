from collections.abc import Mapping
from typing import Any

from mini_agent import (
    Agent,
    FakeModel,
    ModelReply,
    PermissionDecision,
    Tool,
    ToolCall,
)


class AllowAll:
    def decide(
        self,
        tool: Tool,
        arguments: Mapping[str, Any],
    ) -> PermissionDecision:
        return PermissionDecision(allowed=True)


def test_agent_can_finish_without_using_a_tool() -> None:
    model = FakeModel([ModelReply(content="Hello!")])
    agent = Agent(model, tools=[], permission_policy=AllowAll(), max_steps=3)

    result = agent.run("Say hello.")

    assert result.status == "completed"
    assert result.output == "Hello!"
    assert result.steps == 1
    assert result.messages[0] == {"role": "user", "content": "Say hello."}
    assert result.messages[-1]["role"] == "assistant"


def test_agent_feeds_a_tool_result_back_to_the_model() -> None:
    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="echo",
                        arguments={"text": "hello"},
                    )
                ]
            ),
            ModelReply(content="The tool returned hello."),
        ]
    )
    echo = Tool(
        name="echo",
        description="Return the supplied text.",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
        handler=lambda text: text,
    )
    agent = Agent(model, tools=[echo], permission_policy=AllowAll(), max_steps=3)

    result = agent.run("Use echo.")
    assert model.requests[0]["tools"] == [echo.as_model_spec()]
    assert result.status == "completed"
    assert result.steps == 2
    second_request_messages = model.requests[1]["messages"]
    assert second_request_messages[-1] == {
        "role": "tool",
        "tool_call_id": "call_001",
        "name": "echo",
        "content": "hello",
    }
def test_agent_can_use_tools_for_multiple_rounds() -> None:
    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="echo",
                        arguments={"text": "hello"},
                    )
                ]
            ),
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_002",
                        name="echo",
                        arguments={"text": "hello"},
                    )
                ]
            ),
            ModelReply(content="The tool returned hello."),
        ]
    )
    echo = Tool(
        name="echo",
        description="Return the supplied text.",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
        handler=lambda text: text,
    )
    agent = Agent(model, tools=[echo], permission_policy=AllowAll(), max_steps=3)

    result = agent.run("Use echo.")

    assert result.status == "completed"
    assert result.steps == 3
    second_request_messages = model.requests[2]["messages"]
    assert second_request_messages[-1] == {
        "role": "tool",
        "tool_call_id": "call_002",
        "name": "echo",
        "content": "hello",
    }
def test_agent_stops_at_max_steps() -> None:
    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="echo",
                        arguments={"text": "hello"},
                    )
                ]
            ),
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_002",
                        name="echo",
                        arguments={"text": "hello"},
                    )
                ]
            ),
            ModelReply(content="The tool returned hello."),
        ]
    )
    echo = Tool(
        name="echo",
        description="Return the supplied text.",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
        handler=lambda text: text,
    )
    agent = Agent(model, tools=[echo], permission_policy=AllowAll(), max_steps=2)

    result = agent.run("Use echo.")

    assert result.status == "max_steps"
    assert result.steps == 2
    assert len(model.requests) == 2


def test_agent_handles_unknown_tool() -> None:
    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="missing_tool",
                        arguments={"text": "hello"},
                    )
                ]
            ),
            ModelReply(content="The tool does not exist."),
        ]
    )
    agent = Agent(model, tools=[], permission_policy=AllowAll(), max_steps=3)

    result = agent.run("Use missing_tool")
    assert model.requests[0]["tools"] == []#检查额外提供工具
    assert result.status == "completed"
    assert result.steps == 2
    assert model.requests[1]["messages"][-1] == {
        "role": "tool",
        "tool_call_id": "call_001",
        "name": "missing_tool",
        "content": "The tool does not exist.",
    }
def test_agent_handles_tool_execution_error() -> None:
    def failing_handler(text):
        raise ValueError("test failure")
    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="echo",
                        arguments={"text": "hello"},
                    )
                ]
            ),
            ModelReply(content="The tool returned hello."),
        ]
    )
    echo = Tool(
        name="echo",
        description="Return the supplied text.",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
        handler=failing_handler,
    )
    agent = Agent(model, tools=[echo], permission_policy=AllowAll(), max_steps=3)

    result = agent.run("Use echo.")
    assert model.requests[0]["tools"] == [echo.as_model_spec()]
    assert result.status == "completed"
    assert result.steps == 2
    second_request_messages = model.requests[1]["messages"]
    assert second_request_messages[-1] == {
        "role": "tool",
        "tool_call_id": "call_001",
        "name": "echo",
        "content": "Tool execution failed: test failure",
    }
