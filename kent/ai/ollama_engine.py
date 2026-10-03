"""
Ollama local engine — primary brain (free, private, offline-capable).
Now smarter about vision models.
"""

from typing import List, Optional, Set
from PIL import Image
import json
import urllib.request
import urllib.error
from io import BytesIO
import base64

from kent.ai.engine import Engine
from kent.config import SYSTEM_PROMPT, OLLAMA_MODEL, OLLAMA_HOST


# Models known to support vision in Ollama
VISION_MODEL_HINTS = {
    "llava", "moondream", "bakllava", "llama3.2-vision",
    "minicpm-v", "qwen2.5vl", "gemma3", "granite3.2-vision",
}


class OllamaEngine(Engine):
    name = "ollama"

    def __init__(self):
        self.host = OLLAMA_HOST.rstrip("/")
        self.model = OLLAMA_MODEL
        self._available_models: Set[str] = set()
        self._refresh_models()

    def _refresh_models(self):
        """Query Ollama for the list of installed models."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = data.get("models", [])
                self._available_models = {m.get("name", "").split(":")[0].lower() for m in models}
                # Also keep full names
                for m in models:
                    full = m.get("name", "").lower()
                    self._available_models.add(full)
        except Exception:
            self._available_models = set()

    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    self._refresh_models()
                    return True
        except Exception:
            pass
        return False

    def supports_vision(self) -> bool:
        """True if the currently configured model (or any installed one) can do vision."""
        if self._model_is_vision(self.model):
            return True
        # Check if any installed model is a vision model
        return any(self._model_is_vision(m) for m in self._available_models)

    def _model_is_vision(self, name: str) -> bool:
        name = name.lower()
        return any(hint in name for hint in VISION_MODEL_HINTS)

    def _pick_vision_model(self) -> Optional[str]:
        """Return the best available vision model name, or None."""
        # Prefer the user-configured model if it is vision
        if self._model_is_vision(self.model):
            return self.model

        # Otherwise pick any installed vision model
        for m in self._available_models:
            if self._model_is_vision(m):
                return m
        return None

    def chat(
        self,
        messages: List[dict],
        images: Optional[List[Image.Image]] = None,
    ) -> str:
        model_to_use = self.model

        # If we have images, try to switch to a vision model
        if images:
            vision_model = self._pick_vision_model()
            if vision_model:
                model_to_use = vision_model
                print(f"[ollama] Using vision model: {model_to_use}")
            else:
                print("[ollama] No vision model found — answering without image")
                images = None  # fall back to text-only

        # Build Ollama messages
        ollama_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                continue
            content = msg.get("content", "")
            entry = {"role": role, "content": content}

            # Attach images only to the last user message
            if images and role == "user":
                b64_images = []
                for img in images:
                    buf = BytesIO()
                    img.save(buf, format="JPEG", quality=80)
                    b64_images.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
                entry["images"] = b64_images

            ollama_messages.append(entry)

        payload = {
            "model": model_to_use,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": 0.55,
                "num_predict": 1024,
            },
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.host}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return (result.get("message", {}) or {}).get("content", "").strip()
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Ollama not reachable at {self.host}.\n"
                "Make sure Ollama is running (just open the Ollama app)."
            ) from e
        except Exception as e:
            raise RuntimeError(f"Ollama error: {e}") from e
