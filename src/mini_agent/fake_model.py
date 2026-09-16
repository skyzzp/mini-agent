from __future__ import annotations

from collections import deque
from copy import deepcopy
from typing import Any, Iterable

from .contracts import ModelReply


class FakeModel:
    """Returns scripted replies and records every request for assertions."""

    def __init__(self, replies: Iterable[ModelReply]) -> None:
        self._replies = deque(replies)
        self.requests: list[dict[str, Any]] = []

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelReply:
        self.requests.append(
            {
                "messages": deepcopy(messages),
                "tools": deepcopy(tools),
            }
        )
        if not self._replies:
            raise RuntimeError("FakeModel has no scripted reply left")
        return self._replies.popleft()

