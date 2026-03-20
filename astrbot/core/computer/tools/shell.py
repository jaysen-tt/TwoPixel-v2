import json
import re
from dataclasses import dataclass, field

from astrbot.api import FunctionTool
from astrbot.core.agent.run_context import ContextWrapper
from astrbot.core.agent.tool import ToolExecResult
from astrbot.core.astr_agent_context import AstrAgentContext

from ..computer_client import get_booter, get_local_booter
from .permissions import check_admin_permission

_BLOCKED_COMMAND_PATTERNS = [
    r"(^|\s)rm\s+-rf\s+/(?:\s|$)",
    r"(^|\s)mkfs(\.|$|\s)",
    r"(^|\s)fdisk(\s|$)",
    r"(^|\s)shutdown(\s|$)",
    r"(^|\s)reboot(\s|$)",
    r"(^|\s)poweroff(\s|$)",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\};\s*:",
    r"(^|\s)dd\s+if=",
    r"(^|\s)chmod\s+-R\s+777\s+/(?:\s|$)",
]


def _is_blocked_command(command: str) -> bool:
    lowered = command.strip().lower()
    if not lowered:
        return True
    return any(re.search(pattern, lowered) for pattern in _BLOCKED_COMMAND_PATTERNS)


@dataclass
class ExecuteShellTool(FunctionTool):
    name: str = "astrbot_execute_shell"
    description: str = "Execute a command in the shell."
    parameters: dict = field(
        default_factory=lambda: {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute in the current runtime shell (for example, cmd.exe on Windows). Equal to 'cd {working_dir} && {your_command}'.",
                },
                "background": {
                    "type": "boolean",
                    "description": "Whether to run the command in the background.",
                    "default": False,
                },
                "env": {
                    "type": "object",
                    "description": "Optional environment variables to set for the file creation process.",
                    "additionalProperties": {"type": "string"},
                    "default": {},
                },
            },
            "required": ["command"],
        }
    )

    is_local: bool = False

    async def call(
        self,
        context: ContextWrapper[AstrAgentContext],
        command: str,
        background: bool = False,
        env: dict = {},
    ) -> ToolExecResult:
        if permission_error := check_admin_permission(context, "Shell execution"):
            return permission_error

        if _is_blocked_command(command):
            return "Error executing command: blocked by safety policy"

        if self.is_local:
            sb = get_local_booter()
        else:
            sb = await get_booter(
                context.context.context,
                context.context.event.unified_msg_origin,
            )
        try:
            result = await sb.shell.exec(command, background=background, env=env)
            return json.dumps(result)
        except Exception as e:
            return f"Error executing command: {str(e)}"
