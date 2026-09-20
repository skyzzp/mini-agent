from pathlib import Path
from .contracts import Tool


def resolve_workspace_path(workspace, user_path):
    root = Path(workspace).resolve()
    requested = Path(user_path)
    if requested.is_absolute():
        raise ValueError("Absolute path not allowed")
    target = (root / requested).resolve()#“/”为路径拼接
    if not target.is_relative_to(root) :#判断是否不在路径内
        raise ValueError("Path is outside the workpath")
    return target

def read_file(workspace, path):
    resolved = resolve_workspace_path(workspace, path)
    content = resolved.read_text(encoding="utf-8")
    return content

def create_file_tools(workspace):
    def read_handler(path):#闭包
        return read_file(workspace,path)
    read_tool = Tool(
        name="read_file",
        description="Read a UTF-8 text file inside the workspace.",
        input_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}, },
                "required": ["path"],
                "additionalProperties": False,
        },
        handler=read_handler,
    )
    def search_handler(path,query):
        return search_text(workspace,path,query)
    search_tool = Tool(
        name="search_text",
        description="Search for text in a UTF-8 file inside the workspace.",
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "query": {"type": "string"},
            },
            "required": ["path", "query"],
            "additionalProperties": False,
        },
        handler=search_handler,
    )
    return [read_tool, search_tool]
def search_text(workspace, path, query):
    content = read_file(workspace, path)
    matches = []

    for line_number, line in enumerate(content.splitlines(),start=1):
        if query in line:
            matches.append(f"{line_number}:{line}")
    if not matches:
        return "No matches found."
    return "\n".join(matches)





