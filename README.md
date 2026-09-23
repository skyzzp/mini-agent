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
- 递归列出工作区目录中的文件

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
```


## 安装依赖

本项目使用 Python 3.12 和 uv 管理环境。

```powershell
uv sync
```

如果 PowerShell 无法直接识别 `uv`，可以使用 uv 的完整路径：

```powershell
& "C:\Users\你的用户名\.local\bin\uv.exe" sync
```

## 配置真实模型

项目通过 OpenAI 兼容接口接入 DeepSeek。

在 PowerShell 中临时设置 API Key：

```powershell
$env:DEEPSEEK_API_KEY = "你的API Key"
```

API Key 仅对当前 PowerShell 窗口有效。请勿将真实 API Key 写入代码、README 或提交到 GitHub。

## 运行项目

在项目根目录执行：

```powershell
python -m mini_agent.cli
```

输入：

```text
exit
```

即可退出程序。

Agent 的文件工具只能访问项目根目录中的 `workspace/` 目录。

## 运行测试

运行全部测试：

```powershell
python -m pytest -q
```

当前测试结果：

```text
35 passed in 0.15s
```

测试覆盖的主要场景包括：

- 模型直接返回最终答案
- 单轮和多轮工具调用
- 达到最大步数后停止
- 未知工具处理
- 工具执行异常处理
- 模型请求异常处理
- 工具参数类型、缺失参数和多余参数校验
- 用户拒绝高影响工具
- 工作区路径隔离
- 文件读取、搜索和写入
- CLI 输入和退出

## 基本设计

Agent 使用与具体模型无关的 `ModelReply` 和 `ToolCall` 表示模型输出。核心循环位于 `Agent.run()` 中：

```text
接收用户请求
→ 将消息和工具说明发送给模型
→ 判断模型是否请求工具
→ 查找并校验工具
→ 检查执行权限
→ 执行工具
→ 将结果加入消息历史
→ 再次请求模型
→ 返回最终答案或达到最大步数
```

`DeepSeekModel` 是模型适配器，负责：

1. 将项目内部工具定义转换成 DeepSeek Function Calling 格式；
2. 将项目消息历史转换成 DeepSeek 所需格式；
3. 将 DeepSeek 返回的工具请求转换成项目内部的 `ToolCall`。

文件工具通过 `Path.resolve()` 获得规范路径，再使用 `is_relative_to()` 判断目标是否仍位于工作区内，从而拒绝绝对路径和 `../` 目录逃逸。

写文件工具设置了：

```python
consequential=True
```

因此执行前需要经过权限策略确认；读取和搜索工具属于只读操作，可以自动执行。

## 运行示例

### 读取文件

用户输入：

```text
You: 请读取 intro.txt，并告诉我文件内容。
```

执行流程：

```text
DeepSeek 请求 read_file
Agent 执行 read_file(path="intro.txt")
工具结果加入消息历史
DeepSeek 根据文件内容生成最终回答
```

### 写入并校验文件

用户输入：

```text
You: 请把“真实模型写入成功”写入 reports/summary.txt。
```

程序进行权限确认：

```text
Allow tool write_file? [y/N]: y
```

运行结果：

```text
Agent: 已完成：将「真实模型写入成功」写入
reports/summary.txt，并读回校验，文件内容正是该文本。
```

在这个过程中，模型先调用 `write_file`，然后调用 `read_file` 读取文件并校验结果，展示了多轮工具调用能力。

## 安全设计

- API Key 从环境变量读取，不写入源代码。
- 文件工具只允许使用相对路径。
- 绝对路径和工作区外路径会被拒绝。
- 工具参数在执行前经过 JSON Schema 校验。
- 写入类工具执行前需要用户确认。
- 模型错误和工具错误会被转换为可观察的运行结果。

## 当前已知问题

- CLI 每次输入都会创建一次独立的 Agent 运行，不保留不同用户输入之间的会话历史。
- 目前没有列出工作区目录内容的工具。
- `write_file` 会直接覆盖已有文件。
- 文件工具主要面向 UTF-8 文本，不支持二进制文件。
- 真实模型运行依赖网络、API 余额和 DeepSeek 服务状态。
- 自动化测试主要使用 FakeModel，没有在测试过程中请求真实 API。
