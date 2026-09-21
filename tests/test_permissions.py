from mini_agent.file_tools import create_file_tools
from mini_agent.permissions import ConfirmPermission
def test_allows_consequential_tool_when_user_confirms(tmp_path):
    write_tool = create_file_tools(tmp_path)[2]
    confirm_permission = ConfirmPermission(ask=lambda prompt: "y")
    decision = confirm_permission.decide(write_tool, {"path": "summary.txt", "content": "test"  })
    assert decision.allowed

def test_denies_consequential_tool_when_user_rejects(tmp_path):
    write_tool = create_file_tools(tmp_path)[2]
    confirm_permission = ConfirmPermission(ask=lambda prompt: "n")
    decision = confirm_permission.decide(write_tool, {"path": "summary.txt", "content": "test"})
    assert not decision.allowed
    assert decision.reason == "User denied the operation."

def test_allows_read_only_tool_without_confirmation(tmp_path):
    read_tool = create_file_tools(tmp_path)[0]
    def fail_if_ask(prompt):
        raise AssertionError("Read-only tool should not ask for confirmation")#断言失败
    confirm_permission = ConfirmPermission(ask=fail_if_ask)
    decision = confirm_permission.decide(read_tool, {"path": "summary.txt"})
    assert decision.allowed
