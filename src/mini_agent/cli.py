from pathlib import Path

from .agent import Agent
from .deepseek_model import DeepSeekModel
from .file_tools import create_file_tools
from .permissions import ConfirmPermission
def run_cli(agent, ask=input, show=print):
    show("Mini Agent started. Type 'exit' to quit.")

    while True:
        query = ask("You: ")
        if query.strip().lower() == "exit":
            break
        else:
            result = agent.run(query)
        show(f"Agent: {result.output}")
def main():
    workspace = Path.cwd() / "workspace"#取得终端目录
    workspace.mkdir(parents=True, exist_ok=True)

    model = DeepSeekModel()
    tools = create_file_tools(workspace)
    permission_policy = ConfirmPermission()

    agent = Agent(
        model=model,
        tools=tools,
        permission_policy=permission_policy,
        max_steps=8,
    )

    run_cli(agent)

if __name__ == "__main__":
    main()