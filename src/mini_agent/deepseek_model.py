import os
import json

from openai import OpenAI
from .contracts import ModelReply,ToolCall

class DeepSeekModel:
    def __init__(
        self,
        api_key=None,
        model="deepseek-flash",
    ):
        key = api_key or os.environ.get("DEEPSEEK_API_KEY")

        if not key:
            raise ValueError("DEEPSEEK_API_KEY is not set.")

        self.client = OpenAI(
            api_key=key,
            base_url="https://api.deepseek.com",
        )
        self.model = model

    def complete(self, messages, tools):
        """转换历史消息格式为deep seek兼容格式"""
        api_messages = []

        for message in messages:
            if message["role"] == "assistant" and message.get("tool_calls"):#get函数不会报错
                converted_message = {
                    "role": "assistant",
                    "content": message.get("content") or None,
                    "tool_calls": [],
                }

                for call in message["tool_calls"]:
                    converted_message["tool_calls"].append({
                        "id": call["id"],
                        "type": "function",
                        "function": {
                            "name": call["name"],
                            "arguments": json.dumps(
                                call["arguments"],
                                ensure_ascii=False,
                            ),
                        },
                    })

                api_messages.append(converted_message)

            elif message["role"] == "tool":
                api_messages.append({
                    "role": "tool",
                    "tool_call_id": message["tool_call_id"],
                    "content": str(message["content"]),
                })

            else:
                api_messages.append({
                    "role": message["role"],
                    "content": message["content"],
                })

        api_tools = []

        for tool in tools:
            api_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name":tool["name"],
                        "description":tool["description"],
                        "parameters": tool["input_schema"],
                    },
                }
            )
        request_arguments = {
            "model": self.model,
            "messages": api_messages,
            "stream": False,
        }

        if api_tools:
            request_arguments["tools"] = api_tools
        response = self.client.chat.completions.create(
            **request_arguments  #字典解包
        )

        message = response.choices[0].message

        tool_calls = []
        for call in message.tool_calls or []:
            tool_calls.append(
                ToolCall(
                    id = call.id,
                    name = call.function.name,
                    arguments = json.loads(call.function.arguments),
                )
            )


        return ModelReply(
            content=message.content or "",
            tool_calls=tool_calls,
        )

