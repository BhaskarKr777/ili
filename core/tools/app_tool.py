"""
App tool — open applications and URLs cross-platform.
Input: app name or URL e.g. "chrome", "calculator", "https://google.com"
"""
import os
import platform
import subprocess
import webbrowser
from core.tools.base_tool import BaseTool


OS = platform.system()

APP_MAP = {
    "windows": {
        "notepad":      "notepad.exe",
        "calculator":   "calc.exe",
        "paint":        "mspaint.exe",
        "explorer":     "explorer.exe",
        "cmd":          "cmd.exe",
        "terminal":     "cmd.exe",
        "chrome":       "chrome.exe",
        "firefox":      "firefox.exe",
        "edge":         "msedge.exe",
        "word":         "winword.exe",
        "excel":        "excel.exe",
        "powerpoint":   "powerpnt.exe",
        "vs code":      "code.exe",
        "vscode":       "code.exe",
        "task manager": "taskmgr.exe",
    },
    "darwin": {
        "terminal":   "Terminal",
        "calculator": "Calculator",
        "safari":     "Safari",
        "chrome":     "Google Chrome",
        "firefox":    "Firefox",
        "finder":     "Finder",
        "notes":      "Notes",
        "vs code":    "Visual Studio Code",
        "vscode":     "Visual Studio Code",
        "textedit":   "TextEdit",
    },
    "linux": {
        "terminal":   "gnome-terminal",
        "calculator": "gnome-calculator",
        "files":      "nautilus",
        "chrome":     "google-chrome",
        "firefox":    "firefox",
        "vs code":    "code",
        "vscode":     "code",
        "gedit":      "gedit",
    },
}


class AppTool(BaseTool):

    @property
    def name(self) -> str:
        return "open_app"

    @property
    def description(self) -> str:
        return (
            "Open an application or URL on the computer. "
            "Input: app name (e.g. 'chrome', 'calculator') or a URL (e.g. 'youtube.com')."
        )

    def run(self, input: str) -> str:
        target = input.strip()

        # If it already has https:// or http://
        if target.startswith("http://") or target.startswith("https://"):
            return self._open_url(target)

        # If it looks like a domain (has a dot, no spaces)
        if "." in target and " " not in target:
            return self._open_url("https://" + target)

        # Try app map
        os_key = OS.lower()
        apps   = APP_MAP.get(os_key, {})
        exe    = apps.get(target.lower())

        if exe:
            return self._launch(exe)

        # Try launching directly by name
        return self._launch(target)

    def _open_url(self, url: str) -> str:
        try:
            webbrowser.open(url)
            return f"Opened URL: {url}"
        except Exception as e:
            return f"Could not open URL: {e}"

    def _launch(self, exe: str) -> str:
        try:
            if OS == "Windows":
                os.startfile(exe)
            elif OS == "Darwin":
                subprocess.Popen(["open", "-a", exe])
            else:
                subprocess.Popen([exe])
            return f"Opened: {exe}"
        except Exception as e:
            return f"Could not open '{exe}': {e}"