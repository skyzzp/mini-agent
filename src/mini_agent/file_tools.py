from pathlib import Path


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

