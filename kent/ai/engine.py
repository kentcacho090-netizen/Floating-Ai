"""
Abstract Engine interface (local-first design).
All AI backends implement this.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from PIL import Image


class Engine(ABC):
    """Base class for any AI backend (Ollama, Gemini, future models)."""

    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this engine can be used right now."""
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[dict],
        images: Optional[List[Image.Image]] = None,
    ) -> str:
        """
        messages: list of {"role": "user"|"assistant"|"system", "content": str}
        images: optional list of PIL Images (vision)
        returns: assistant reply text
        """
        pass

    def supports_vision(self) -> bool:
        """Whether this engine can accept images."""
        return False
