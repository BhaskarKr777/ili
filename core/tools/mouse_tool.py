"""
Mouse and keyboard control tool using pyautogui.
Input format:
  "click:<x>,<y>"         → left click at position
  "move:<x>,<y>"          → move mouse
  "type:<text>"           → type text
  "hotkey:<key1>+<key2>"  → press key combination
  "scroll:<up/down>"      → scroll
"""
from core.tools.base_tool import BaseTool


class MouseTool(BaseTool):

    @property
    def name(self) -> str:
        return "mouse_keyboard"

    @property
    def description(self) -> str:
        return (
            "Control mouse and keyboard. "
            "Input: 'click:<x>,<y>' or 'type:<text>' or 'hotkey:<keys>' or 'scroll:<up/down>'"
        )

    def run(self, input: str) -> str:
        try:
            import pyautogui
            pyautogui.FAILSAFE = True
        except ImportError:
            return "pyautogui not installed. Run: pip install pyautogui"

        input = input.strip()

        try:
            if input.startswith("click:"):
                coords = input[6:].split(",")
                x, y = int(coords[0].strip()), int(coords[1].strip())
                pyautogui.click(x, y)
                return f"Clicked at ({x}, {y})"

            elif input.startswith("move:"):
                coords = input[5:].split(",")
                x, y = int(coords[0].strip()), int(coords[1].strip())
                pyautogui.moveTo(x, y, duration=0.3)
                return f"Moved mouse to ({x}, {y})"

            elif input.startswith("type:"):
                text = input[5:]
                pyautogui.write(text, interval=0.05)
                return f"Typed: {text}"

            elif input.startswith("hotkey:"):
                keys = input[7:].split("+")
                keys = [k.strip() for k in keys]
                pyautogui.hotkey(*keys)
                return f"Pressed hotkey: {'+'.join(keys)}"

            elif input.startswith("scroll:"):
                direction = input[7:].strip().lower()
                amount = 3 if direction == "down" else -3
                pyautogui.scroll(amount)
                return f"Scrolled {direction}"

            else:
                return "Unknown mouse action. Use click:, move:, type:, hotkey:, or scroll:"

        except Exception as e:
            return f"Mouse/keyboard action failed: {e}"