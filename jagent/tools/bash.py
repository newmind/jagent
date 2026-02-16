"""Bash command execution tool."""

import subprocess
import shlex
from typing import Optional
from pydantic import BaseModel, Field
from jagent.core.tool import Tool


class BashInput(BaseModel):
    """Input schema for Bash tool."""

    command: str = Field(
        description="Shell command to execute"
    )
    timeout: Optional[int] = Field(
        default=30,
        description="Timeout in seconds (default: 30)"
    )
    working_dir: Optional[str] = Field(
        default=None,
        description="Working directory for command execution"
    )


class Bash(Tool):
    """
    Execute bash commands.

    Runs shell commands and returns stdout/stderr.
    Includes timeout protection and working directory support.
    """

    name = "bash"
    description = "Execute a bash command and return the output. Use for system operations."
    input_schema = BashInput

    def execute(
        self,
        command: str,
        timeout: Optional[int] = 30,
        working_dir: Optional[str] = None,
    ) -> str:
        """
        Execute a bash command.

        Args:
            command: Command to execute
            timeout: Timeout in seconds
            working_dir: Working directory

        Returns:
            Command output or error message
        """
        try:
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir,
            )

            # Format output
            output_parts = []

            if result.stdout:
                output_parts.append(result.stdout.rstrip())

            if result.stderr:
                output_parts.append(f"[stderr]\n{result.stderr.rstrip()}")

            if result.returncode != 0:
                output_parts.append(f"[exit code: {result.returncode}]")

            output = '\n'.join(output_parts) if output_parts else "[no output]"

            return output

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds"

        except Exception as e:
            return f"Error executing command: {type(e).__name__}: {str(e)}"
