from mini_agent.file_tools import resolve_workspace_path,read_file,create_file_tools,search_text,write_file
import pytest


def test_resolves_path_inside_workspace(tmp_path):
    result = resolve_workspace_path(tmp_path, "materials/intro.txt")

    assert result == tmp_path / "materials" / "intro.txt"

def test_rejects_absolute_path(tmp_path):
    with pytest.raises(ValueError):
        resolve_workspace_path(tmp_path, str(tmp_path / "intro.txt"))

def test_rejects_outside_path(tmp_path):
    with pytest.raises(ValueError):
        resolve_workspace_path(tmp_path, "../outside.txt")

def test_reads_file_content(tmp_path):
    file_path = tmp_path / "intro.txt"
    file_path.write_text("你好，Agent！", encoding="utf-8")#写入内容

    result = read_file(tmp_path, "intro.txt")

    assert result == "你好，Agent！"

def test_reads_non_existing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_file(tmp_path, "missing.txt")

def test_read_tool_handler(tmp_path):
    (tmp_path / "intro.txt").write_text("你好，Agent！", encoding="utf-8")

    tools = create_file_tools(tmp_path)
    read_tool= tools[0]
    result = read_tool.handler(path="intro.txt")

    assert read_tool.name == "read_file"
    assert result == "你好，Agent！"

def test_searches_text_with_line_numbers(tmp_path):
    content = "苹果\n香蕉\n苹果派"
    (tmp_path / "fruit.txt").write_text(content, encoding="utf-8")

    result = search_text(tmp_path, "fruit.txt", "苹果")

    assert result == "1:苹果\n3:苹果派"

def test_search_text_returns_message_when_no_match(tmp_path):
    (tmp_path / "fruit.txt").write_text(
        "苹果\n香蕉\n苹果派",
        encoding="utf-8",
    )

    result = search_text(tmp_path, "fruit.txt", "西瓜")

    assert result == "No matches found."

def test_search_tool_handler(tmp_path):
    content = "苹果\n香蕉\n苹果派"
    (tmp_path / "fruit.txt").write_text(content, encoding="utf-8")

    tools = create_file_tools(tmp_path)
    search_tool = tools[1]
    result = search_tool.handler(path="fruit.txt", query="苹果")

    assert search_tool.name == "search_text"
    assert result == "1:苹果\n3:苹果派"

def test_writes_file_content(tmp_path):
    result = write_file(
        tmp_path,
        "reports/summary.txt",
        "这是总结内容",
    )

    written_file = tmp_path / "reports" / "summary.txt"

    assert written_file.read_text(encoding="utf-8") == "这是总结内容"
    assert result == "wrote file: reports/summary.txt"

def test_write_file_rejects_outside_path(tmp_path):
    with pytest.raises(ValueError):
        write_file(tmp_path, "../outside.txt", "不能写出去")

def test_work_tool_handler(tmp_path):
    content = "苹果\n香蕉\n苹果派"
    (tmp_path / "fruit.txt").write_text(content, encoding="utf-8")

    tools = create_file_tools(tmp_path)
    search_tool = tools[1]
    result = search_tool.handler(path="fruit.txt", query="苹果")

    assert search_tool.name == "search_text"
    assert result == "1:苹果\n3:苹果派"

def test_write_tool_handler(tmp_path):
    tools = create_file_tools(tmp_path)
    write_tool = tools[2]
    result = write_tool.handler(path="reports/summary.txt",content="测试总结")
    written_file = tmp_path / "reports" / "summary.txt"
    assert written_file.read_text(encoding="utf-8") == "测试总结"
    assert write_tool.name == "write_file"
    assert result == "wrote file: reports/summary.txt"
    assert write_tool.consequential == True