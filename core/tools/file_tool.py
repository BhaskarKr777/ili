"""
File tool — read and write files on the user's computer.
Input format:
  "read:<path>"        → read file contents
  "write:<path>|<content>"  → write content to file
  "list:<path>"        → list directory contents
"""
import os
import platform
from pathlib import Path
from core.tools.base_tool import BaseTool


class FileTool(BaseTool):

    @property
    def name(self) -> str:
        return "file"

    @property
    def description(self) -> str:
        return (
            "Read, write, or list files on the computer. "
            "Input format: 'read:<path>' or 'write:<path>|<content>' or 'list:<path>'"
        )

    def run(self, input: str) -> str:
        input = input.strip()

        if input.startswith("read:"):
            return self._read(input[5:].strip())
        elif input.startswith("write:"):
            parts = input[6:].split("|", 1)
            if len(parts) != 2:
                return "Error: write format is 'write:<path>|<content>'"
            return self._write(parts[0].strip(), parts[1])
        elif input.startswith("list:"):
            return self._list(input[5:].strip())
        else:
            return "Unknown file operation. Use read:, write:, or list:"

    def _read(self, path: str) -> str:
        path = self._resolve(path)
        if not os.path.isfile(path):
            return f"File not found: {path}"
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            # Limit output size
            if len(content) > 3000:
                content = content[:3000] + "\n...[truncated]"
            return f"Contents of {path}:\n{content}"
        except Exception as e:
            return f"Could not read file: {e}"

    def _write(self, path: str, content: str) -> str:
        path = self._resolve(path)
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File written: {path}"
        except Exception as e:
            return f"Could not write file: {e}"

    def _list(self, path: str) -> str:
        path = self._resolve(path)
        if not os.path.isdir(path):
            return f"Directory not found: {path}"
        try:
            items = os.listdir(path)
            dirs  = [f"📁 {i}" for i in items if os.path.isdir(os.path.join(path, i))]
            files = [f"📄 {i}" for i in items if os.path.isfile(os.path.join(path, i))]
            return f"Contents of {path}:\n" + "\n".join(dirs + files)
        except Exception as e:
            return f"Could not list directory: {e}"

    def _resolve(self, path: str) -> str:
        """Expand ~ and environment variables."""
        return str(Path(os.path.expandvars(os.path.expanduser(path))).resolve())