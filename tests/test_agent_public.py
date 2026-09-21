from collections.abc import Mapping
from typing import Any
from mini_agent.file_tools import create_file_tools
from mini_agent.permissions import ConfirmPermission
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
class DenyAll:
    def decide(
        self,
        tool,
        arguments):
        return PermissionDecision(allowed=False)



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

def test_agent_denies_tool_execution() -> None:#拒绝权限测试
        executed = []

        def tracking_handler(text):
            executed.append(text)
            return text
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
            handler=tracking_handler,
        )
        agent = Agent(model, tools=[echo], permission_policy=DenyAll(), max_steps=3)

        result = agent.run("Use echo.")
        assert model.requests[0]["tools"] == [echo.as_model_spec()]
        assert result.status == "completed"
        assert result.steps == 2
        assert executed == []
        second_request_messages = model.requests[1]["messages"]
        assert second_request_messages[-1] == {
            "role": "tool",
            "tool_call_id": "call_001",
            "name": "echo",
            "content": "Tool execution denied",
        }
def test_agent_handles_model_error() -> None:
    class FailingModel:
        def complete(self, messages, tools):
            raise RuntimeError("connection failed")

    model = FailingModel()
    agent = Agent(model, tools=[], permission_policy=AllowAll(), max_steps=3)
    result = agent.run("Say hello.")
    assert result.status == "model_error"
    assert result.output == "Model request failed: connection failed"
    assert result.steps == 1
    assert result.messages == [
        {"role": "user", "content": "Say hello."},
    ]
def test_agent_rejects_invalid_arguments() -> None:
    executed = []

    def tracking_handler(text):
        executed.append(text)
        return text

    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="echo",
                        arguments={"text": 123},
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
        handler=tracking_handler,
    )
    agent = Agent(model, tools=[echo], permission_policy=AllowAll(), max_steps=3)

    result = agent.run("Use echo.")
    tool_message = model.requests[1]["messages"][-1]

    assert tool_message["role"] == "tool"
    assert tool_message["tool_call_id"] == "call_001"
    assert tool_message["name"] == "echo"
    assert tool_message["content"].startswith("Invalid tool arguments:")

def test_agent_rejects_missing_arguments() -> None:
    executed = []

    def tracking_handler(text):
        executed.append(text)
        return text

    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="echo",
                        arguments={},
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
        handler=tracking_handler,
    )
    agent = Agent(model, tools=[echo], permission_policy=AllowAll(), max_steps=3)

    result = agent.run("Use echo.")
    tool_message = model.requests[1]["messages"][-1]

    assert tool_message["role"] == "tool"
    assert tool_message["tool_call_id"] == "call_001"
    assert tool_message["name"] == "echo"
    assert tool_message["content"].startswith("Invalid tool arguments:")


def test_agent_rejects_extra_arguments() -> None:
    executed = []

    def tracking_handler(text):
        executed.append(text)
        return text

    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="echo",
                        arguments={"text":"hello","other":"world"},
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
        handler=tracking_handler,
    )
    agent = Agent(model, tools=[echo], permission_policy=AllowAll(), max_steps=3)

    result = agent.run("Use echo.")
    tool_message = model.requests[1]["messages"][-1]

    assert tool_message["role"] == "tool"
    assert tool_message["tool_call_id"] == "call_001"
    assert tool_message["name"] == "echo"
    assert tool_message["content"].startswith("Invalid tool arguments:")

def test_agent_reads_workspace_file(tmp_path) -> None:
    (tmp_path / "intro.txt").write_text("你好，Agent!", encoding="utf-8")
    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="read_file",
                        arguments={"path": "intro.txt"},
                    )
                ]
            ),
            ModelReply(content="The tool returned hello."),
        ]
    )
    agent = Agent(model, tools=create_file_tools(tmp_path), permission_policy=AllowAll(), max_steps=3)

    result = agent.run("Read intro.txt.")
    assert result.status == "completed"
    assert result.steps == 2
    second_request_messages = model.requests[1]["messages"]
    assert second_request_messages[-1] == {
        "role": "tool",
        "tool_call_id": "call_001",
        "name": "read_file",
        "content": "你好，Agent!",
    }

def test_agent_searches_workspace_file(tmp_path) -> None:
    (tmp_path / "fruit.txt").write_text(
        "苹果\n香蕉\n苹果派",
        encoding="utf-8",
    )
    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="search_text",
                        arguments={
                            "path": "fruit.txt",
                            "query": "苹果",
                        },
                    )
                ]
            ),
            ModelReply(content="The tool returned hello."),
        ]
    )
    agent = Agent(model, tools=create_file_tools(tmp_path), permission_policy=AllowAll(), max_steps=3)

    result = agent.run("Search for 苹果 in fruit.txt.")
    assert result.status == "completed"
    assert result.steps == 2
    assert model.requests[1]["messages"][-1] == {
        "role": "tool",
        "tool_call_id": "call_001",
        "name": "search_text",
        "content": "1:苹果\n3:苹果派",
    }

def test_agent_writes_workspace_file(tmp_path) -> None:
    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="write_file",
                        arguments={
                            "path": "reports/summary.txt",
                            "content": "测试总结",
                        },
                    )
                ]
            ),
            ModelReply(content="The tool returned hello."),
        ]
    )
    agent = Agent(model, tools=create_file_tools(tmp_path), permission_policy=AllowAll(), max_steps=3)
    result = agent.run("write summary.txt.")
    assert result.status == "completed"
    assert result.steps == 2
    assert model.requests[1]["messages"][-1] == {
        "role": "tool",
        "tool_call_id": "call_001",
        "name": "write_file",
        "content": "wrote file: reports/summary.txt",
    }
    assert (tmp_path/"reports"/"summary.txt").read_text(encoding="utf-8") == "测试总结"

def test_agent_writes_workspace_file_when_user_rejects(tmp_path) -> None:
    model = FakeModel(
        [
            ModelReply(
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="write_file",
                        arguments={
                            "path": "reports/summary.txt",
                            "content": "测试总结",
                        },
                    )
                ]
            ),
            ModelReply(content="The tool returned hello."),
        ]
    )
    agent = Agent(model, tools=create_file_tools(tmp_path), permission_policy=ConfirmPermission(ask=lambda prompt: "n"), max_steps=3)
    result = agent.run("write summary.txt.")
    assert result.status == "completed"
    assert result.steps == 2
    assert model.requests[1]["messages"][-1] == {
        "role": "tool",
        "tool_call_id": "call_001",
        "name": "write_file",
        "content": "Tool execution denied",
    }
    assert not (tmp_path / "reports" / "summary.txt").exists()