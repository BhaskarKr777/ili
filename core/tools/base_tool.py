"""
Base class for all ili agent tools.
Every tool must implement: name, description, run()
"""
from abc import ABC, abstractmethod


class BaseTool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """Short tool name e.g. 'web_search'"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """One line description for the LLM to understand when to use this tool."""
        pass

    @abstractmethod
    def run(self, input: str) -> str:
        """Execute the tool and return result as string."""
        pass

    def safe_run(self, input: str) -> str:
        """Run with error handling."""
        try:
            return self.run(input)
        except Exception as e:
            return f"[Tool error: {e}]"