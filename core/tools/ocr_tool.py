import io
import pyautogui
from .base_tool import BaseTool


class OCRTool(BaseTool):
    name = "ocr"
    description = (
        "Read text visible on the screen using OCR. "
        "Input: 'full' for full screen, or a region like '0,0,800,600' (left,top,width,height)."
    )

    # Lazy-load easyocr so startup stays fast
    _reader = None

    def _get_reader(self):
        if OCRTool._reader is None:
            try:
                import easyocr
                OCRTool._reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            except ImportError:
                raise ImportError(
                    "easyocr is not installed. Run: pip install easyocr"
                )
        return OCRTool._reader

    def run(self, input_text: str) -> str:
        inp = input_text.strip().lower()

        # ── Capture screenshot ─────────────────────────────────────────────────
        try:
            if inp == "full" or inp == "":
                screenshot = pyautogui.screenshot()
            else:
                # Parse "left,top,width,height"
                parts = [p.strip() for p in inp.split(",")]
                if len(parts) != 4:
                    return (
                        "Invalid region format. Use 'full' or 'left,top,width,height' "
                        "e.g. '0,0,800,600'."
                    )
                left, top, width, height = map(int, parts)
                screenshot = pyautogui.screenshot(region=(left, top, width, height))
        except Exception as e:
            return f"Error capturing screenshot: {e}"

        # ── Run OCR ────────────────────────────────────────────────────────────
        try:
            reader = self._get_reader()

            # Convert PIL image → bytes for easyocr
            buf = io.BytesIO()
            screenshot.save(buf, format="PNG")
            img_bytes = buf.getvalue()

            results = reader.readtext(img_bytes, detail=0, paragraph=True)

            if not results:
                return "No text detected on screen."

            text = "\n".join(results)
            # Truncate very long output
            if len(text) > 2000:
                text = text[:2000] + "\n… (truncated)"

            return f"🔍 Text found on screen:\n\n{text}"

        except Exception as e:
            return f"OCR error: {e}"