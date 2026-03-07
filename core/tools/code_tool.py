"""
Code runner tool — safely executes Python or shell snippets.
Input format:
  "python:<code>"   → run Python code
  "shell:<command>" → run shell command
"""
import subprocess
import sys
import tempfile
import os
from core.tools.base_tool import BaseTool

TIMEOUT = 10  # seconds max execution time


class CodeTool(BaseTool):

    @property
    def name(self) -> str:
        return "run_code"

    @property
    def description(self) -> str:
        return (
            "Run Python code or a shell command and return the output. "
            "Input: 'python:<code>' or 'shell:<command>'"
        )

    def run(self, input: str) -> str:
        input = input.strip()

        if input.startswith("python:"):
            return self._run_python(input[7:].strip())
        elif input.startswith("shell:"):
            return self._run_shell(input[6:].strip())
        else:
            # Assume Python if no prefix
            return self._run_python(input)

    def _run_python(self, code: str) -> str:
        # Write to temp file and run
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                tmp_path = f.name

            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )

            output = ""
            if result.stdout:
                output += result.stdout.strip()
            if result.stderr:
                output += f"\nError: {result.stderr.strip()}"
            if not output:
                output = "(no output)"

            # Limit output size
            if len(output) > 2000:
                output = output[:2000] + "\n...[truncated]"

            return output

        except subprocess.TimeoutExpired:
            return f"Code timed out after {TIMEOUT} seconds."
        except Exception as e:
            return f"Could not run code: {e}"
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def _run_shell(self, command: str) -> str:
        # Block dangerous commands
        dangerous = ["rm -rf", "format", "del /f", "shutdown", "mkfs",
                     "dd if=", ":(){", "fork bomb"]
        for d in dangerous:
            if d.lower() in command.lower():
                return f"Blocked: '{d}' is a dangerous command."

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )
            output = result.stdout.strip() or result.stderr.strip() or "(no output)"
            if len(output) > 2000:
                output = output[:2000] + "\n...[truncated]"
            return output
        except subprocess.TimeoutExpired:
            return f"Command timed out after {TIMEOUT} seconds."
        except Exception as e:
            return f"Could not run command: {e}"