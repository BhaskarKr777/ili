import pyperclip
from .base_tool import BaseTool


class ClipboardTool(BaseTool):
    name = "clipboard"
    description = (
        "Read text from the clipboard or write text to the clipboard. "
        "Input format: 'read' to get clipboard content, or 'write: <text>' to set it."
    )

    def run(self, input_text: str) -> str:
        inp = input_text.strip()

        # ── WRITE ──────────────────────────────────────────────────────────────
        if inp.lower().startswith("write:"):
            text_to_write = inp[6:].strip()
            if not text_to_write:
                return "Error: nothing to write — provide text after 'write:'."
            try:
                pyperclip.copy(text_to_write)
                preview = text_to_write[:80] + ("…" if len(text_to_write) > 80 else "")
                return f"✅ Copied to clipboard: \"{preview}\""
            except Exception as e:
                return f"Error writing to clipboard: {e}"

        # ── READ ───────────────────────────────────────────────────────────────
        try:
            content = pyperclip.paste()
            if not content:
                return "Clipboard is empty."
            preview = content[:500] + ("… (truncated)" if len(content) > 500 else "")
            return f"📋 Clipboard contents:\n{preview}"
        except Exception as e:
            return f"Error reading clipboard: {e}"