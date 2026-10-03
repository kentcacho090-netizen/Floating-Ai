"""
KentBrain — smart router that prefers local (Ollama) then falls back to cloud.
This is the only class the Controller talks to.
"""

from typing import List, Optional
from PIL import Image

from kent.ai.engine import Engine
from kent.ai.ollama_engine import OllamaEngine
from kent.ai.gemini_engine import GeminiEngine


class KentBrain:
    """
    Selects the best available engine at startup and on each request.
    Priority: Ollama (local) → Gemini (cloud)
    """

    def __init__(self):
        self.engines: List[Engine] = []
        self.active: Optional[Engine] = None

        # Register engines in preference order
        self.engines.append(OllamaEngine())
        self.engines.append(GeminiEngine())

        self._select_best()

    def _select_best(self):
        for engine in self.engines:
            if engine.is_available():
                self.active = engine
                print(f"[kent] Using engine: {engine.name}")
                return
        self.active = None
        print("[kent] No AI engine available")

    def is_ready(self) -> bool:
        return self.active is not None

    def current_engine_name(self) -> str:
        return self.active.name if self.active else "none"

    def chat(
        self,
        messages: List[dict],
        images: Optional[List[Image.Image]] = None,
    ) -> str:
        if not self.active:
            # Try re-selecting in case Ollama started later
            self._select_best()
            if not self.active:
                raise RuntimeError(
                    "No AI engine available.\n"
                    "• Install Ollama (https://ollama.com) and run a model, or\n"
                    "• Add GEMINI_API_KEY to your .env file"
                )

        # If the active engine doesn't support vision but we have images,
        # try to find one that does
        if images and not self.active.supports_vision():
            for engine in self.engines:
                if engine.is_available() and engine.supports_vision():
                    print(f"[kent] Switching to {engine.name} for vision")
                    return engine.chat(messages, images)

        return self.active.chat(messages, images)
