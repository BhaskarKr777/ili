from engines.base_engine import BaseEngine
from engines.local_engine import LocalEngine
from engines.openai_engine import OpenAIEngine
from engines.gemini_engine import GeminiEngine


SUPPORTED_ENGINES = ["local", "openai", "gemini"]


def get_engine(engine_name: str) -> BaseEngine:
    """
    Factory function — returns the appropriate engine instance.

    Args:
        engine_name: One of 'local', 'openai', 'gemini'

    Returns:
        An engine instance implementing BaseEngine
    """
    engine_name = engine_name.lower().strip()

    if engine_name == "local":
        return LocalEngine()
    elif engine_name == "openai":
        return OpenAIEngine()
    elif engine_name == "gemini":
        return GeminiEngine()
    else:
        raise ValueError(
            f"Unknown engine '{engine_name}'. Choose from: {', '.join(SUPPORTED_ENGINES)}"
        )