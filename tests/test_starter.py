from mini_agent import FakeModel, ModelReply, Tool, ToolCall


def test_fake_model_returns_scripted_replies_and_records_requests() -> None:
    reply = ModelReply(
        content="I need a file.",
        tool_calls=[
            ToolCall(
                id="call_001",
                name="read_file",
                arguments={"path": "materials/intro.txt"},
            )
        ],
    )
    model = FakeModel([reply])

    actual = model.complete(
        messages=[{"role": "user", "content": "Read the introduction."}],
        tools=[],
    )

    assert actual == reply
    assert model.requests[0]["messages"][0]["role"] == "user"


def test_tool_model_spec_does_not_expose_python_handler() -> None:
    tool = Tool(
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

    assert tool.as_model_spec() == {
        "name": "echo",
        "description": "Return the supplied text.",
        "input_schema": tool.input_schema,
    }

