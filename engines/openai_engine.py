import os
from .base_engine import BaseEngine


class OpenAIEngine(BaseEngine):
    """
    Cloud LLM engine using OpenAI's ChatGPT API.
    Requires: OPENAI_API_KEY environment variable.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            return (
                "[OpenAIEngine Error] OPENAI_API_KEY not set. "
                "Run: setx OPENAI_API_KEY 'your_key' (Windows) or export OPENAI_API_KEY='your_key' (Linux/Mac)"
            )
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except ImportError:
            return "[OpenAIEngine Error] openai package not installed. Run: pip install openai"
        except Exception as e:
            return f"[OpenAIEngine Error] {str(e)}"

    def is_available(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))