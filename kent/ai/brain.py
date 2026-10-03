"""
KentBrain — smart router that prefers local (Ollama) then falls back to cloud.
"""

from typing import List, Optional
from PIL import Image

from kent.ai.engine import Engine
from kent.ai.ollama_engine import OllamaEngine
from kent.ai.gemini_engine import GeminiEngine


class KentBrain:
    """
    Selects the best available engine.
    Priority: Ollama (local) → Gemini (cloud)
    Automatically switches to a vision-capable engine when images are present.
    """

    def __init__(self):
        self.engines: List[Engine] = []
        self.active: Optional[Engine] = None

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

    def status_message(self) -> str:
        """Short human-friendly status for the chatbox."""
        if not self.active:
            return "No AI engine found"
        name = self.active.name
        if name == "ollama":
            return "Local (Ollama)"
        if name == "gemini":
            return "Cloud (Gemini)"
        return name

    def chat(
        self,
        messages: List[dict],
        images: Optional[List[Image.Image]] = None,
    ) -> str:
        if not self.active:
            self._select_best()
            if not self.active:
                raise RuntimeError(
                    "No AI engine available.\n"
                    "• Install Ollama (https://ollama.com) and run a model, or\n"
                    "• Add GEMINI_API_KEY to your .env file"
                )

        # Prefer a vision-capable engine when images are present
        if images:
            # First try the current engine if it supports vision
            if self.active.supports_vision():
                return self.active.chat(messages, images)

            # Otherwise look for any available vision engine
            for engine in self.engines:
                if engine.is_available() and engine.supports_vision():
                    print(f"[kent] Switching to {engine.name} for vision")
                    return engine.chat(messages, images)

            # No vision engine available — fall back to text-only with a note
            print("[kent] No vision engine available, answering text-only")
            return self.active.chat(messages, images=None)

        return self.active.chat(messages, images=None)
