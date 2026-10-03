"""
Abstract AI provider interface.
Makes it easy to swap Gemini ↔ OpenAI ↔ local models later.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from PIL import Image


class AIProvider(ABC):
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
