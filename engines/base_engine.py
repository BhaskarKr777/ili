from abc import ABC, abstractmethod


class BaseEngine(ABC):
    """
    Abstract interface for all LLM engines.
    Every engine MUST implement generate() and is_available().
    Tutor logic never cares which engine is underneath.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Send prompt to LLM, return response string."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if engine is configured and reachable."""
        pass

    @property
    def name(self) -> str:
        return self.__class__.__name__