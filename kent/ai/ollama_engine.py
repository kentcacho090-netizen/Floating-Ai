"""
Ollama local engine — primary brain (free, private, offline-capable).
"""

from typing import List, Optional
from PIL import Image
import json
import urllib.request
import urllib.error
from io import BytesIO
import base64

from kent.ai.engine import Engine
from kent.config import SYSTEM_PROMPT, OLLAMA_MODEL, OLLAMA_HOST


class OllamaEngine(Engine):
    name = "ollama"

    def __init__(self):
        self.host = OLLAMA_HOST.rstrip("/")
        self.model = OLLAMA_MODEL

    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def supports_vision(self) -> bool:
        # Many modern Ollama models support vision (llava, moondream, etc.)
        vision_models = ["llava", "moondream", "bakllava", "llama3.2-vision"]
        return any(v in self.model.lower() for v in vision_models)

    def chat(
        self,
        messages: List[dict],
        images: Optional[List[Image.Image]] = None,
    ) -> str:
        # Build Ollama-style messages
        ollama_messages = []

        # Put system prompt first
        ollama_messages.append({"role": "system", "content": SYSTEM_PROMPT})

        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                continue
            content = msg.get("content", "")
            entry = {"role": role, "content": content}

            # Attach images only to the last user message if vision is supported
            if images and role == "user" and self.supports_vision():
                b64_images = []
                for img in images:
                    buf = BytesIO()
                    img.save(buf, format="JPEG", quality=80)
                    b64_images.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
                entry["images"] = b64_images

            ollama_messages.append(entry)

        payload = {
            "model": self.model,
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
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return (result.get("message", {}) or {}).get("content", "").strip()
        except urllib.error.URLError as e:
            raise RuntimeError(f"Ollama not reachable at {self.host}. Is Ollama running?") from e
        except Exception as e:
            raise RuntimeError(f"Ollama error: {e}") from e
