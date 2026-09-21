from .contracts import PermissionDecision

class ConfirmPermission:
    def __init__(self, ask=input):
        self.ask = ask

    def decide(self, tool, arguments):
        if not tool.consequential:
            return PermissionDecision(allowed=True)

        answer = self.ask(f"Allow Tool {tool.name}? [y/N]:")
        answer = answer.strip().lower()
        if answer == "y":
            return PermissionDecision(allowed=True)

        return PermissionDecision(
            allowed=False,
            reason="User denied the operation.",
        )