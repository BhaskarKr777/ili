"""
Screenshot tool — takes a screenshot and saves it.
Input: optional file path, defaults to Desktop/ili_screenshot.png
"""
import os
import platform
from pathlib import Path
from core.tools.base_tool import BaseTool


class ScreenshotTool(BaseTool):

    @property
    def name(self) -> str:
        return "screenshot"

    @property
    def description(self) -> str:
        return (
            "Take a screenshot of the screen and save it. "
            "Input: optional save path, or leave blank for Desktop."
        )

    def run(self, input: str) -> str:
        try:
            import PIL.ImageGrab as ImageGrab
        except ImportError:
            try:
                from PIL import ImageGrab
            except ImportError:
                return (
                    "PIL not installed. Run: pip install Pillow\n"
                    "Then try again."
                )

        # Determine save path
        if input.strip():
            path = Path(os.path.expanduser(input.strip()))
        else:
            desktop = Path.home() / "Desktop"
            if not desktop.exists():
                desktop = Path.home()
            path = desktop / "ili_screenshot.png"

        try:
            screenshot = ImageGrab.grab()
            path.parent.mkdir(parents=True, exist_ok=True)
            screenshot.save(str(path))
            return f"Screenshot saved to: {path}"
        except Exception as e:
            return f"Screenshot failed: {e}"