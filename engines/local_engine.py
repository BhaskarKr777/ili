import requests
from .base_engine import BaseEngine


class LocalEngine(BaseEngine):
    """
    Offline LLM engine using Ollama.
    Requires Ollama to be running locally: https://ollama.ai
    """

    def __init__(self, model: str = "phi3.5", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.ConnectionError:
            return (
                "[LocalEngine Error] Ollama is not running. "
                "Start it with: `ollama serve` and ensure model is pulled: `ollama pull mistral`"
            )
        except Exception as e:
            return f"[LocalEngine Error] {str(e)}"

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False