# Mini Agent

一个基于南京邮电大学SAST 2026届软研部python组免试题使用 Python 实现的轻量级 AI Agent。项目支持模型循环、工具调用、参数校验、权限确认、工作区文件操作，并可接入 DeepSeek 真实模型。

## 项目简介

Mini Agent 接收用户请求，将消息和工具说明发送给模型。模型可以直接回答，也可以请求调用工具。Agent 会校验工具参数、检查权限、执行工具，再将执行结果返回模型，直到模型给出最终答案或达到最大步数。

项目同时提供 FakeModel，测试时无需调用真实 API。

## 已实现功能

- 基础 Agent Loop
- 多轮工具调用
- 最大步数限制
- 工具参数 JSON Schema 校验
- 未知工具处理
- 工具执行异常处理
- 模型请求异常处理
- 只读工具自动允许
- 写入工具执行前询问用户
- 工作区路径隔离
- 拒绝绝对路径和目录逃逸
- UTF-8 文件读取
- 文件内容搜索并返回行号
- 文件写入和父目录创建
- FakeModel 自动化测试
- DeepSeek 真实模型接入
- 交互式命令行界面

## 项目结构

```text
src/mini_agent/
├── agent.py            # Agent Loop
├── contracts.py        # Tool、ToolCall、ModelReply等数据结构
├── fake_model.py       # 测试使用的假模型
├── deepseek_model.py   # DeepSeek模型适配器
├── file_tools.py       # 文件读取、搜索和写入工具
├── permissions.py      # 权限确认策略
└── cli.py              # 命令行入口

tests/
├── test_agent_public.py
├── test_file_tools.py
├── test_permissions.py
├── test_cli.py
└── test_starter.py

