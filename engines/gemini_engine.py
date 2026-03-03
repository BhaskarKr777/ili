import os
from engines.base_engine import BaseEngine


class GeminiEngine(BaseEngine):
    """
    Cloud LLM engine using Google Gemini API.
    Uses the new google-genai package.
    Requires GEMINI_API_KEY in .env file.
    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model
        self._api_key = os.environ.get("GEMINI_API_KEY", "")

    def generate(self, prompt: str) -> str:
        if not self._api_key:
            return (
                "⚠ GEMINI_API_KEY not set.\n"
                "Add it to your .env file: GEMINI_API_KEY=AIza...\n"
                "Or switch to local: python main.py --engine local"
            )
        try:
            from google import genai

            client = genai.Client(api_key=self._api_key)
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            return response.text.strip()

        except ImportError:
            return "⚠ google-genai package missing. Run: pip install google-genai"
        except Exception as e:
            return f"⚠ GeminiEngine error: {e}"

    def is_available(self) -> bool:
        return bool(self._api_key)