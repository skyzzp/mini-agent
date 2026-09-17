from __future__ import annotations

from collections.abc import Sequence

from .contracts import ModelClient, PermissionPolicy, RunResult, Tool


class Agent:
    """Student implementation entry point.

    Keep this constructor and ``run`` signature compatible with the public
    tests. You may split the implementation into more modules.
    """

    def __init__(
        self,
        model: ModelClient,
        tools: Sequence[Tool],
        permission_policy: PermissionPolicy,
        max_steps: int = 8,
    ) -> None:
        self.model = model
        self.tools = list(tools)
        self.permission_policy = permission_policy
        self.max_steps = max_steps

    def run(self, query: str) -> RunResult:
        messages=[{"role":"user","content":query}]
        tool_specs= []
        for tool in self.tools:
            tool_specs.append(tool.as_model_spec())
        for step in range(1, self.max_steps + 1):
            reply=self.model.complete(messages,tool_specs)
            messages.append({"role":"assistant","content":reply.content})
            if  reply.tool_calls:
                for call in reply.tool_calls:
                    found_tool = None
                    for tool in self.tools:
                        if tool.name == call.name:
                            found_tool = tool
                            break
                    if found_tool == None:
                         messages.append({
                            "role": "tool",
                            "tool_call_id": call.id,
                            "name": call.name,
                            "content":"The tool does not exist." ,
                        })
                    else:
                        decision = self.permission_policy.decide(
                            found_tool,
                            call.arguments,
                        )
                        if decision.allowed:
                            try:
                                 tool_result = found_tool.handler(**call.arguments)
                            except Exception as error:
                                tool_result = f"Tool execution failed: {error}"
                            messages.append({
                                "role": "tool",
                                "tool_call_id": call.id,
                                "name": call.name,
                                "content": tool_result,
                            })
                        else:
                            tool_result = "Tool execution denied"
                            messages.append({
                                "role": "tool",
                                "tool_call_id": call.id,
                                "name": call.name,
                                "content": tool_result,
                            })

            if not reply.tool_calls:
                return RunResult(
                    status="completed",
                    output=reply.content,
                    messages=messages,
                    steps=step,
                )
        return RunResult(
            status="max_steps",
            output=reply.content,
            messages=messages,
            steps=self.max_steps,)



