# Mini Agent Starter

这是 Agent 免试题的前置代码，只提供统一接口、`FakeModel` 和待实现骨架，不包含题目答案。

## 环境

- Python 3.11+
- pytest 8+

## 运行 starter 自检

```bash
python3 -m pytest -q tests/test_starter.py
```

## 开始实现

需要补全：

- `src/mini_agent/agent.py`
- 工具注册与至少三类工具；
- JSON Schema 参数校验；
- 权限策略；
- CLI 和运行轨迹。

`tests/test_agent_public.py` 描述了 Agent 的最小公开行为。它在 starter 状态下会失败，完成基础 Agent Loop 后应通过。

