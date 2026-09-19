from mini_agent.file_tools import resolve_workspace_path,read_file,create_file_tools
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