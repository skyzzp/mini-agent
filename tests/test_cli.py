from mini_agent import Agent, FakeModel, ModelReply
from mini_agent.cli import run_cli
from mini_agent.permissions import ConfirmPermission

def test_cli_runs_query_and_exits():
    model = FakeModel([ModelReply(content="Hello!")])
    agent = Agent(
        model=model,
        tools=[],
        permission_policy=ConfirmPermission(),
    )
    answers = iter(["Say hello.","exit"])
    outputs = []
    run_cli(
        agent,
        ask=lambda prompt: next(answers),#next从迭代器取出下一个值
        show=outputs.append,
    )
    assert outputs[0] == "Mini Agent started. Type 'exit' to quit."
    assert outputs[1] == "Agent: Hello!"
    assert len(model.requests) == 1